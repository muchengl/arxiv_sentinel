import os
from email import encoders
from email.mime.base import MIMEBase

import urllib3
import urllib.parse
import fitz
import smtplib
import logging
import re
import PyPDF2
import openai
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from xml.etree import ElementTree as ET
from utils.llm import invoke_llm
from utils.calendar import create_ics_file, estimate_reading_time

http = urllib3.PoolManager(cert_reqs='CERT_NONE')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

client = openai.OpenAI(
    api_key=openai.api_key,
)

PAPER_TOPIC  = os.getenv('PAPER_TOPIC')

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

TARGET_ADDRESS = os.getenv('TARGET_ADDRESS')

PAPER_DIR = '/tmp/papers'

def fetch_today_papers(topic=PAPER_TOPIC):
    logger.info("Fetching today's papers from arXiv...")
    url = "https://export.arxiv.org/api/query"
    # today = datetime.today().strftime('%Y%m%d')
    params = {
        "search_query": f"cat:{topic}",
        "sortBy": "submittedDate",
        "max_results": 1
    }

    # encoded_params = urllib3.request.urlencode(params)
    encoded_params = urllib.parse.urlencode(params)

    response = http.request("GET", f"{url}?{encoded_params}")
    if response.status != 200:
        raise Exception(f"Failed to fetch papers: Status code {response.status}")

    logger.info("Fetched papers successfully.")
    return response.data.decode('utf-8')


def parse_and_download_papers(xml_data):
    logger.info("Parsing XML data and downloading papers...")
    root = ET.fromstring(xml_data)
    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
    papers = []
    for entry in entries:
        title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
        pdf_link = None
        for link in entry.findall("{http://www.w3.org/2005/Atom}link"):
            if link.attrib.get('title') == 'pdf':
                pdf_link = link.attrib['href']
                break
        if pdf_link:
            def sanitized_filename(t):
                return re.sub(r'[\\/*?\"<>|]', '', t)

            filename = os.path.join(PAPER_DIR, f"{sanitized_filename(title)}.pdf")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            download_pdf(pdf_link, filename)
            papers.append({'title': title, 'filename': filename})
            logger.info(f"Downloaded paper: {title}")
    return papers


def download_pdf(url, filename):
    """Download PDF file"""
    response = http.request("GET", url)
    if response.status != 200:
        raise Exception(f"Failed to download PDF: Status code {response.status}")

    with open(filename, 'wb') as f:
        f.write(response.data)
    logger.info(f"Downloaded: {filename}")


def extract_images_from_pdf(pdf_path):
    logger.info(f"Extracting images from {pdf_path}...")
    images = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            images.append(image_bytes)
            logger.info(f"Extracted image {img_index} from page {page_num}")
    doc.close()
    logger.info("Image extraction completed.")
    return images


def extract_text_and_images(pdf_path):
    logger.info(f"Extracting text and images from {pdf_path}...")
    text_content = ""
    # images = []
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(reader.pages):
            text_content += page.extract_text() + "\n"
    logger.info("Extraction completed.")

    images = extract_images_from_pdf(pdf_path)

    return text_content, images


def split_into_chunks(text):
    logger.info("Splitting text into chunks...")
    chapters = re.split(r'\n\s*(\d+\.\s.*)', text)
    chunks = []
    for i in range(1, len(chapters), 2):
        chapter_title = chapters[i].strip()
        chapter_content = chapters[i+1].strip()
        chunks.append({'title': chapter_title, 'content': chapter_content})

        print("==========================")
        print(chapters)
        print(chapter_title)

    logger.info("Text split into chunks.")
    return chunks

def summarize_chunks(chunks):
    logger.info("Summarizing chunks...")
    summaries = []
    for chunk in chunks:
        prompt = f"""
This is a chapter of the paper. Please summarize the content from the following aspects:
1. What was done
2. The process
3. What was the result

{chunk['content']}"""

        summary = invoke_llm(prompt)
        logger.debug(f"Summary for chunk {chunk['title']}: {summary}")
        summaries.append({'title': chunk['title'], 'summary': summary})
    logger.info("Chunks summarized.")
    return summaries

def construct_report(paper_summaries):
    logger.info("Constructing HTML report with images...")
    html_content = "<html><body>"
    for paper in paper_summaries:
        html_content += f"<h2>{paper['title']}</h2>"

        for chapter in paper['summaries']:
            html_content += f"<h3>{chapter['title']}</h3>"
            # html_content += f"<p>{chapter['summary'].replace('\n', '<br>')}</p>"

            s = chapter['summary'].replace('\n', '<br>')
            html_content += f"<p>{s}</p>"

        # Add images (modify this if you have specific images per section)
        html_content += '<img src="cid:image0" alt="Image 0"><br>'

    html_content += "</body></html>"
    logger.info("Report construction with images completed.")
    return html_content

from email.mime.image import MIMEImage

def send_email(subject, html_content, to_addr, images=[], ics_path=None):
    logger.info("Sending email...")
    message = MIMEMultipart()
    message['From'] = EMAIL_ADDRESS
    message['To'] = to_addr
    message['Subject'] = subject

    message.attach(MIMEText(html_content, 'html'))

    # for i, image_content in enumerate(images):
    #     mime_image = MIMEImage(image_content, _subtype='png')
    #     mime_image.add_header('Content-ID', f'<image{i}>')
    #     mime_image.add_header('Content-Disposition', 'inline', filename=f'image{i}.png')
    #     message.attach(mime_image)

     # Attach the ICS file if available
    if ics_path and os.path.exists(ics_path):
        with open(ics_path, 'rb') as f:
            mime_ics = MIMEBase('application', 'octet-stream')
            mime_ics.set_payload(f.read())
            encoders.encode_base64(mime_ics)
            mime_ics.add_header('Content-Disposition', 'attachment', filename=os.path.basename(ics_path))
            message.attach(mime_ics)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(message)
    logger.info("Email sent successfully.")

def delete_papers():
    """Delete all downloaded papers after email is sent."""
    logger.info("Deleting downloaded papers...")
    if os.path.exists(PAPER_DIR):
        for filename in os.listdir(PAPER_DIR):
            file_path = os.path.join(PAPER_DIR, filename)
            try:
                os.remove(file_path)
                logger.info(f"Deleted: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete {file_path}. Reason: {e}")

def run():
    logger.info("Job started")
    try:
        xml_data = fetch_today_papers()
        papers = parse_and_download_papers(xml_data)

        all_images = []
        total_text_content = ""

        paper_summaries = []
        for paper in papers:
            logger.info(f"Processing paper: {paper['title']}")
            text_content, images = extract_text_and_images(paper['filename'])
            total_text_content += text_content

            all_images.extend(images)

            chunks = split_into_chunks(text_content)

            # print("================================")
            # for chunk in chunks:
            #     print("================================")
            #     print(f"Chunk: {chunk['content']}")

            summaries = summarize_chunks(chunks)
            # print(summaries)

            paper_summaries.append({
                    'title': paper['title'],
                    'summaries': summaries
                })

        # Estimate reading time
        reading_time_minutes = estimate_reading_time(total_text_content)
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=reading_time_minutes)

        # Create ICS file with estimated reading time
        ics_file_name = "reading_schedule.ics"
        create_ics_file(
                event_name="arXiv Paper Reading",
                start_time=start_time,
                end_time=end_time,
                description="Scheduled time for reading today's arXiv papers.",
                location="Anywhere",
                file_name=ics_file_name
        )

        report = construct_report(paper_summaries)
        send_email(
            "Daily arXiv Paper News 🚀",
            report,
            TARGET_ADDRESS,
            images=[image_content for image_content in all_images],
            ics_path=ics_file_name)
        delete_papers()

    except Exception as e:
        logger.error(f"An error occurred during the job: {e}")

if __name__ == "__main__":
    run()