import requests
import os

def get_cookie()-> str:
    """Retrieves the cookie from the environment variable 'BILIBILI_COOKIE'.
    Returns:
        str: The cookie string.
    """
    with open('cookie.txt', 'r', encoding='utf-8') as f:
        cookie = f.read().strip()
        return cookie    

def requests_get(url:str,params = None ):
    """Sends a GET request to the specified URL with optional parameters.
    Args:
        url (str): The URL to send the GET request to.
        params (dict, optional): A dictionary of query parameters to include in the request.
    Returns:
        dict: The JSON response from the server.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Cookie': get_cookie()
    }
    response = requests.get(url,params=params, headers=headers)
    if response.status_code != 200:
        raise requests.RequestException(f"HTTP Error: {response.status_code}")
    return response.json()
