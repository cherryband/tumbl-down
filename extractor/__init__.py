from __future__ import annotations
from bs4 import BeautifulSoup
import requests
import re


def _find_post(tag):
    return (tag.has_attr('id') and tag['id'] == 'post') or (tag.has_attr('class') and 'post' in tag['class'])


def _find_post_image(tag):
    return tag.name == 'img' \
           and '.svg' not in tag['src'] \
           and not (tag.has_attr('class') and 'avatar' in tag['class'])


def _extract_tumblr_image_viewer(link):
        return _get_bs_document(link).find("main").find("img")['srcset'].split()[-2]

def _get_bs_document(link):
    r = requests.get(link)
    if r.status_code == 200:
        return BeautifulSoup(r.text, 'html.parser')

def extract_tumblr_images(tumblr_post_link: str) -> list[str]:
    if not re.match(r'^https://\S+\.tumblr\.com/post/\d+(/(\S+)?)?$', tumblr_post_link):
        raise ValueError("URL does not point to a Tumblr post")

    image_links = []
    document = _get_bs_document(tumblr_post_link)
    if (post := document.find(_find_post)) is not None:
        if (iframe := post.find("iframe")) is not None:
            if (src_link := iframe['src']).startswith("/post/"):
                src_link = tumblr_post_link.split("/post/")[0] + src_link
                post = _get_bs_document(src_link)
            elif "assets.tumblr.com" not in src_link:
                raise ValueError

        for img in post.find_all(_find_post_image):
            image_links.append(_get_img_link(img))

    return image_links


def _get_img_link(img):
    if (parent := img.parent).name == 'a':
        if "64.media.tumblr.com" in (link := parent['href']):
            return link
        else:
            return _extract_tumblr_image_viewer(link)
    else:
        return img['src']
