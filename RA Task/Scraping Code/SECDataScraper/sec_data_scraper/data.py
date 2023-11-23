import requests


def download_file(url):
    return requests.get(url)


def get_content(url):
    return download_file(url).content
