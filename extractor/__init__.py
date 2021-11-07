from __future__ import annotations
from bs4 import BeautifulSoup
import requests
import re


def _find_post(tag):
    return tag.name == 'article' or \
           (tag.has_attr('id') and tag['id'] == 'post') or \
           (tag.has_attr('class') and 'post' in tag['class'])


def _find_post_image(tag):
    return tag.name == 'img' \
           and "64.media.tumblr.com" in tag['src'] \
           and not (tag.has_attr('class') and 'avatar' in tag['class'])


def _find_post_iframe(tag):
    return tag.name == 'iframe' and tag.has_attr('src') and tag['src'].startswith("/post/")


def _extract_tumblr_image_viewer(link):
    if document := _get_bs_document(link):
        if main := document.find("main"):
            return main.find("img")['srcset'].split()[-2]


def _get_bs_document(link):
    r = requests.get(link)
    if r.status_code == 200:
        return BeautifulSoup(r.text, 'html.parser')


def extract_tumblr_images(tumblr_post_link: str) -> list[str]:
    if not re.match(r'^https://\S+\.tumblr\.com/post/\d+(/(\S+)?)?$', tumblr_post_link):
        raise ValueError("URL does not point to a Tumblr post")

    blog_url = tumblr_post_link.split("/post/")[0]
    document = _get_bs_document(tumblr_post_link)
    if iframe := document.find(_find_post_iframe):
        src_link = blog_url + iframe['src']
        post = _get_bs_document(src_link)
    else:
        post = document.find(_find_post)

    image_links = []
    for img in post.find_all(_find_post_image):
        if (parent := img.parent).has_attr('href'):
            if "64.media.tumblr.com" in (href := parent['href']):
                image_links.append(href)
            elif href.startswith(blog_url):
                image_links.append(_extract_tumblr_image_viewer(href))
        elif img.has_attr("data-highres"):
            image_links.append(img['data-highres'])
        else:
            image_links.append(img['src'])

    return image_links
