# web_navigation.py

import webbrowser

def open_webpage(url):
    try:
        webbrowser.open(url)
        print(f"Opening {url}")
    except Exception as e:
        print(f"Unable to open webpage: {e}")
