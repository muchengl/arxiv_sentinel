# url_call.py

import requests

def call_api(url, params=None, headers=None):
    c = input(f"Call url: {url}. Params: {params}. (y/n)")
    if c == "n":
        return "User refused to call url"

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Check HTTP status code
        return response.json()  # Assuming the response is in JSON format
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return None
