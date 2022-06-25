#!/usr/bin/python
from __future__ import annotations
from extractor import _get_bs_document, _tag_attr


def _find_post(tag):
    return (tag.name == "article"
            or (_tag_attr(tag, "id") in ("post", "posts") and tag.name != "section")
            or (tag.has_attr("class") and "post" in tag["class"]))


def _find_meta_image(tag):
    return tag.name == "meta" and _tag_attr(tag, "property") == "og:image"


def _find_post_image(tag):
    return (tag.name == "img"
            and "64.media.tumblr.com" in tag["src"]
            and not (tag.has_attr("class") and "avatar" in tag["class"]))


def _find_post_iframe(tag):
    return tag.name == "iframe" and (tag.has_attr("src") and tag["src"].startswith("/post/"))


def _select_best_tag(img):
    if (parent := img.parent).has_attr("data-big-photo"):
        return parent["data-big-photo"]

    if img.has_attr("data-highres"):
        return img["data-highres"]

    return img["src"]


def _extract_from_meta(document) -> list[str]:
    return [link["content"] for link in document.find_all(_find_meta_image)]


def _extract_from_post(post) -> list[str]:
    return [_select_best_tag(img) for img in post.find_all(_find_post_image)]


def _extract_from_viewer(document) -> str:
    if img := document.find("main").find("img"):
        return img["srcset"].split()[-2]
    return ""


def _parse_res(link: str) -> int:
    resolution = link.strip("https://").split('/')

    if len(resolution) < 3:
        return 0

    resolution = int(resolution[3].split('x')[0].strip('s'))

    if link.endswith(".jpg"):
        resolution -= 2
    return resolution


def _best_res(links: list[str] | tuple[str, str]) -> str | None:
    best_res = ""
    res = 0

    for link in links:
        # Tumblr tries to "optimise" PNG downloads with .pnj;
        # since this format is essentially a JPEG wrapped in a PNG container,
        # we replace .pnj for .png to get the best quality.
        if link.endswith(".pnj"):
            link = link.replace(".pnj", ".png")
        if (link_res := _parse_res(link)) > res:
            best_res = link
            res = link_res

    return best_res


def extract_tumblr_images(blog_id: str, post_id: str) -> list[str]:
    if not post_id.isdecimal():
        raise ValueError("post_id should contain digits (0-9) only.")
    if not blog_id.replace('-', '').replace('_', '').isalnum():
        raise ValueError("blog_id seems to be incorrect. Is there spaces?")

    blog_url = f"https://{blog_id}.tumblr.com"
    post_url = f"{blog_url}/post/{post_id}"
    viewer_url = f"{blog_url}/image/{post_id}"

    if not (document := _get_bs_document(post_url)):
        raise ValueError("Invalid blog ID or post ID")

    if iframe := document.find(_find_post_iframe):
        src_link = blog_url + iframe["src"]
        post = _get_bs_document(src_link)
    else:
        post = document.find(_find_post)

    image_links = _extract_from_meta(document)
    post_images = _extract_from_post(post)
    image_links = [_best_res(links) for links in zip(image_links, post_images)]

    try:
        viewer = _get_bs_document(viewer_url)
        image_link = _extract_from_viewer(viewer)

        image_links[0] = _best_res([image_links[0], image_link])
    except ValueError: # Normal if image viewer is not available
        pass

    return image_links
