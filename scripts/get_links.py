"""
This script fetches the links from a Linktree page and generates markdown files
in the containing site's _links directory.

This will almost certainly break in the future when Linktree changes their
payload format. The way of web-scraping.

If so, please file an issue here, including the URL you were trying to capture:
https://github.com/paulroub/linky/issues

usage:
    python3 get_links.py <linktree-url>
"""

import json
import re
import sys

import requests
from bs4 import BeautifulSoup

LINKS_CONTAINER_ID = "links-container"
LINK_ROOT = "../_links"
IMAGE_ROOT = "../images"
IMAGE_WEB_ROOT = "/images"

if len(sys.argv) == 2:
    linktree_url = sys.argv[1]
else:
    raise ValueError("usage: python3 get-links.py <linktree-url>")


def create_link_file(url, priority, title, img_fn, image_link, link_fn):
    """
    Creates a markdown file with metadata for a link.

    Args:
        url (str): The URL of the link.
        priority (int): The priority of the link.
        title (str): The title of the link.
        img_fn (str): The filename of the image (if any).
        image_link (str): The URL of the image.
        link_fn (str): The filename of the link file to be created.

    Writes:
        A markdown file with the provided metadata.
    """
    with open(link_fn, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"title: {title}\n")
        f.write(f"link: {url}\n")
        f.write(f"priority: {priority}\n")

        if img_fn:
            f.write(f"image: {image_link}\n")

        f.write("---\n")
        f.write("\n")


def stub_title(title):
    """
    Converts a given title into a URL-friendly stub.

    Args:
        title (str): The title to be converted into a stub.

    Returns:
        str: A URL-friendly stub generated from the given title.
    """
    stub = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower())
    stub = re.sub(r"^-+|-+$", "", stub)
    return stub


def capture_link(link_root, image_root, image_web_root, link):
    """
    Captures a link and its associated thumbnail image, if available, and creates a markdown file
    for the link.

    Args:
        link_root (str): The root directory where the markdown file for the link will be saved.
        image_root (str): The root directory where the thumbnail image will be saved.
        image_web_root (str): The web root directory for accessing the thumbnail image.
        link (dict): A dictionary containing information about the link. Expected keys are:
            - "position" (int): The position of the link.
            - "title" (str): The title of the link.
            - "url" (str): The URL of the link.
            - "thumbnail" (str, optional): The URL of the thumbnail image.
            - "modifiers" (dict, optional): A dictionary that may contain a "thumbnailImage"
                key with the URL of the thumbnail image.

    Raises:
        requests.exceptions.RequestException: If we can't download the thumbnail.
    """
    priority = link["position"] + 1  # originals are 0-based, ours are 1-based
    img_fn = None
    image_link = None
    link_fn = None

    print(f"Collecting {link["title"]}...")

    if "thumbnail" in link:
        img = link["thumbnail"]
    elif "modifiers" in link and "thumbnailImage" in link["modifiers"]:
        img = link["modifiers"]["thumbnailImage"]
    else:
        img = None

    if img:
        print("   ...downloading thumbnail")
        img_name = img.split("/")[-1]
        img_fn = f"{image_root}/{img_name}"
        image_link = f"{image_web_root}/{img_name}"

        img_response = requests.get(img, timeout=30)
        with open(img_fn, "wb") as f:
            f.write(img_response.content)

    stub = stub_title(link["title"])
    link_fn = f"{link_root}/{stub}.md"

    create_link_file(link["url"], priority, link["title"], img_fn, image_link, link_fn)


def collect_link_definitions(linktree_page_url):
    """
    Collects link definitions from a given Linktree page URL.

    Args:
        linktree_page_url (str): The URL of the Linktree page to collect link definitions from.

    Returns:
        list: A list of dictionaries, each containing information about a valid link.
    """
    response = requests.get(linktree_page_url, timeout=30)
    soup = BeautifulSoup(response.content, "html.parser")

    data_block = soup.find_all("script", type="application/json")
    data_json = data_block[0].string
    data = json.loads(data_json)

    all_links = data["props"]["pageProps"]["links"]
    valid_links = [link for link in all_links if "url" in link]

    return valid_links


links = collect_link_definitions(linktree_url)


for source_link in links:
    capture_link(LINK_ROOT, IMAGE_ROOT, IMAGE_WEB_ROOT, source_link)
