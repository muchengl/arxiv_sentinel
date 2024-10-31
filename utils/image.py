import fitz  # PyMuPDF
from PIL import Image
import os

def extract_images_from_pdf(pdf_path, output_dir=None):
    """
    Extracts all images from a PDF file and saves them to a specified directory.

    Parameters:
        pdf_path (str): The file path of the PDF from which images are to be extracted.
        output_dir (str, optional): Directory to save the extracted images. Defaults to the same directory as the PDF.

    Returns:
        list: A list of file paths of the saved images.
    """
    # Open the PDF file
    pdf_file = fitz.open(pdf_path)
    image_paths = []

    # Set the output directory
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over PDF pages
    for page_index in range(len(pdf_file)):
        page = pdf_file.load_page(page_index)
        image_list = page.get_images(full=True)

        # Iterate through all images on the page
        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Define the image file name and path
            image_name = f"image{page_index + 1}_{image_index}.{image_ext}"
            image_path = os.path.join(output_dir, image_name)

            # Save the image to disk
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
                print(f"[+] Image saved as {image_name}")

            # Store the image path in the list
            image_paths.append(image_path)

    pdf_file.close()
    return image_paths


# import fitz  # PyMuPDF
# import io
# from PIL import Image
#
# # STEP 2
# # file path you want to extract images from
# file = "/Users/lhz/Desktop/Papers/tree-search.pdf"
#
# # open the file
# pdf_file = fitz.open(file)
#
# # STEP 3
# # iterate over PDF pages
# for page_index in range(len(pdf_file)):
#
#     # get the page itself
#     page = pdf_file.load_page(page_index)  # load the page
#     image_list = page.get_images(full=True)  # get images on the page
#
#     # printing number of images found in this page
#     if image_list:
#         print(f"[+] Found a total of {len(image_list)} images on page {page_index}")
#     else:
#         print("[!] No images found on page", page_index)
#
#     for image_index, img in enumerate(image_list, start=1):
#         # get the XREF of the image
#         xref = img[0]
#
#         # extract the image bytes
#         base_image = pdf_file.extract_image(xref)
#         image_bytes = base_image["image"]
#
#         # get the image extension
#         image_ext = base_image["ext"]
#
#         # save the image
#         image_name = f"image{page_index + 1}_{image_index}.{image_ext}"
#         with open(image_name, "wb") as image_file:
#             image_file.write(image_bytes)
#             print(f"[+] Image saved as {image_name}")