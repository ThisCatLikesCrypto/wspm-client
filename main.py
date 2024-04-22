import requests
import json
import os
from time import sleep

def getMetadata(name) -> list:
    download_file("https://wspm.pages.dev/" + name + "/metadata", "metdata")
    with open("metdata", "r") as f:
        metadata = json.loads(f.readlines()[0])
        pkgFiles = metadata['files'].replace("'", "").removesuffix("]").removeprefix("[").split(",")
    return pkgFiles

def download_file(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print("File downloaded successfully.")
    else:
        print("Failed to download file.")

def dl(packageName):
    files = getMetadata(packageName)
    print(files)
    for file in files:
        download_file("https://wspm.pages.dev/" + packageName + "/" + file, file)

dl("allwords")