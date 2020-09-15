from requests import request
from pprint import pprint
from functools import reduce
import re

# Traverse file tree recursively and get all raw file download urls
def get_download_urls(url):
    contents = request("GET", url)
    contents = contents.json()
    dir_urls = []
    download_urls = []

    for e in contents:
        if e["type"] == "file":
            download_urls.append(e["download_url"])
        elif e["type"] == "dir":
            dir_urls.append(e["url"])

    if len(dir_urls) == 0:
        return download_urls
    else:
        for url in dir_urls:
            download_urls.extend(get_download_urls(url))
    
    return download_urls

# So far pretty useless information
def analysis(download_urls):
    info = []

    for url in download_urls:
        file_name = url.split("/")[-1]
        response = request("GET", url)
        content_type = response.headers["Content-Type"]
        parseable = re.search("text|plain", content_type)
        if parseable:
            character_count = len(response.text)
        else:
            character_count = None
        file_info = {"file_name": file_name, "content_type": content_type, "character_count": character_count}
        info.append(file_info)

    total_characters = reduce(lambda a, b: a + b, [file["character_count"] if file["character_count"] != None else 0 for file in info])

    for file in info:
        if file["character_count"] != None:
            file["percentage"] = file["character_count"] / total_characters
        else:
            file["percentage"] = None

    return info

# <input type="text" placeholder="user/repo" /> 
repo = "vxxce/learning-docker"
api_base = "https://api.github.com/repos/"
source_url = api_base + repo + "/contents"

pprint(analysis(get_download_urls(source_url)))
