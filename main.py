import time

import requests
from datetime import datetime

from models import Article

LIST_URL = "https://mapping-test.fra1.digitaloceanspaces.com/data/list.json"
DETAIL_URL = "https://mapping-test.fra1.digitaloceanspaces.com/data/articles/{}.json"
MEDIA_URL = "https://mapping-test.fra1.digitaloceanspaces.com/data/media/{}.json"

FMT = "%Y-%m-%d-%H:%M:%S"


# fetch list of articles
# for every article in the list fetch its details and print mapped Article object


def fetch_article_list() -> list:
    """
    Fetches list of articles, maps them into an Article model and prints the outcome.
    """
    try:
        list_response = requests.get(LIST_URL)
        list_response.raise_for_status()
        return [article["id"] for article in list_response.json()]
    except requests.exceptions.RequestException as err:
        # example handling of the error
        SystemExit(err)


def fetch_media(article_id: str) -> list:
    """
    Fetches media for a given article.
    """
    try:
        media_response = requests.get(MEDIA_URL.format(article_id))
        media_response.raise_for_status()
        json = media_response.json()
        media_list = []
        for item in json:
            if item["type"] == "image":
                item.pop("id")
                media_list.append(item)
            elif item["type"] == "media":
                item["publication_date"] = item.pop("pub_date")
                item["publication_date"] = datetime.strptime(item["publication_date"].replace(";", ":"), FMT)
                media_list.append(item)
        return media_list
    except requests.exceptions.RequestException as err:
        SystemExit(err)


def print_mapped_articles(article_list: list):
    """
    Prints mapped articles.
    """
    for article_id in article_list:
        try:
            detail_response = requests.get(DETAIL_URL.format(article_id))
            detail_response.raise_for_status()
            json = detail_response.json()
            sections = [section for section in json["sections"] if section["type"] not in ["media", "image"]]
            media = fetch_media(article_id)
            if not media:
                media = []

            article_input = {
                "id": json["id"],
                "original_language": json["original_language"],
                "url": DETAIL_URL.format(article_id),
                "thumbnail": json["thumbnail"],
                "categories": (json["category"],),
                "tags": json["tags"],
                "author": json["author"],
                "publication_date": datetime.strptime(json["pub_date"].replace(";", ":"), FMT),
                "modification_date": datetime.strptime(json["mod_date"], FMT),
                "sections": sections + media
            }
            print(Article(**article_input))
        except requests.exceptions.RequestException as err:
            SystemExit(err)


if __name__ == '__main__':
    while (True):
        print_mapped_articles(fetch_article_list())
        time.sleep(300)

