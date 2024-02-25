#!/usr/bin/python
from __future__ import annotations

import json
import re

from common import debug_out, get_bs_document, request_get, get_extension, File

NAME="Tumblr"
SLUG="tumblr"

def _safe_contains(tag, attr, val, on_null=True) -> bool:
    if tag.has_attr(attr):
        return val in tag[attr]
    return on_null


def _find_image_link(tag):
    return (
            _safe_contains(tag, "srcset", "64.media.tumblr.com")
            and not _safe_contains(tag, "srcset", "s64x64u_c1")
            and not _safe_contains(tag, "srcset", "64.media.tumblr.com/avatar_")
    )


def _find_post_image(tag) -> bool:
    return tag.name == "img" and _find_image_link(tag)


def _select_best_tag(img) -> str:
    if img.has_attr("srcset"):
        return img["srcset"].split()[-2]

    return img["src"]


def _extract_from_post(post) -> list[str]:
    return [_select_best_tag(img) for img in post.find_all(_find_post_image)]


def _extract_from_viewer(document) -> str:
    if img := document.find("main").find("img"):
        return img["srcset"].split()[-2]
    return ""


def _parse_res(link: str) -> int:
    debug_out("\t\t_parse_res()")
    if not link:
        return -1
    resolution = link.strip("https://").split('/')

    if len(resolution) < 3:  # Avatars or possibly even older tumblr image
        res_str = resolution[1].split('.')[0].split('_')[-1]
        if "frame" in res_str:
            return -1
        resolution = int(res_str)
    elif len(resolution) == 3:  # Older tumblr image
        resolution = int(resolution[2].split('.')[0].split('_')[-1])
    else:  # Newer/current tumblr image
        resolution = int(resolution[3].split('x')[0].strip('s'))
    debug_out(f"\t\tresolution: {resolution}")

    if resolution < 100:
        debug_out("\t\timage too tiny (likely a blog avatar); not downloading.")
        return 0

    if link.endswith(".jpg") or link.endswith(".jpeg"):
        resolution -= 2
        debug_out("\t\tjpg format; de-ranked.")
    return resolution


def _best_res(links: list[str]) -> str | None:
    debug_out("\t_best_res()")
    best_res = ""
    res = 0
    debug_out("\tComparing: " + ', '.join(links))

    for link in links:
        # Tumblr tries to "optimise" PNG downloads with .pnj;
        # since this format is essentially a JPEG wrapped in a PNG container,
        # we replace .pnj for .png to get the best quality.
        # This doesn't always work, however, and may still end up to be .jpg regardless.
        if link.endswith(".pnj"):
            link = link.removesuffix(".pnj") + ".png"
            debug_out("\t'pnj' file detected, converted to png.")
        if (link_res := _parse_res(link)) > res:
            debug_out("\tThis is the better image (as of now).")
            best_res = link
            res = link_res
    debug_out("\tComparison complete.")

    if not best_res:
        return None
    return best_res


def _query_api(blog_id: str, **kwargs) -> str:
    query_url = f"https://{blog_id}.tumblr.com/api/read/json"

    req = request_get(query_url, params=kwargs)
    raw_json = req.text.removeprefix("var tumblr_api_read =").strip().removesuffix(";")

    return raw_json


IMAGE_RE = r"https:\\/\\/64\.media\.tumblr\.com\\/(?:[-a-f0-9]+\\/){0,2}" \
           r"(?:s\d+x|tumblr\w+_)\d+\b(?:\\/)?[\w.]+"


def _extract_from_api(raw_resp) -> list[str]:
    debug_out("_extract_from_api()")
    # performing naive filtering
    # since there doesn't seem to be a standard form of photos
    image_links = re.findall(IMAGE_RE, raw_resp)
    image_links = [link.replace("\\/", "/") for link in image_links]
    debug_out(f"Found {len(image_links)} image candidate(s).")

    def get_unique(link):
        split_link = link.strip("https://").split('/')
        if len(split_link) < 2:
            return split_link[1].split('_')[1]
        return split_link[1]

    image_links = [(get_unique(link), link) for link in image_links]
    images = []
    unique_count = 0
    last_unique = ""
    debug_out("Sieving through for the best resolution of each photos...")
    for unique, image_link in image_links:
        if unique != last_unique:
            images.append(image_link)
            unique_count += 1 if last_unique else 0
            last_unique = unique
        else:
            images[unique_count] = _best_res([images[unique_count], image_link])

    debug_out(f"Collected {len(images)} links.")

    return images


def _combine_best(*link_lists: list[str]) -> list[str]:
    sizes = [len(link_list) for link_list in link_lists]
    list_size = len(link_lists)
    max_length = max(sizes)
    best_links = []

    def limit_index(current: int, list_index: int) -> str:
        return link_lists[list_index][current] if current < sizes[list_index] else ""

    for index in range(max_length):
        links_to_compare = [limit_index(index, i) for i in range(list_size)]
        best_link = _best_res(links_to_compare)
        if best_link:
            best_links.append(best_link)

    return best_links


def _extract_from_image_viewer(image_viewer_url: str) -> list[str]:
    try:
        link_from_image_viewer = [_extract_from_viewer(get_bs_document(image_viewer_url))]
        debug_out("OK.")
        return link_from_image_viewer

    except ValueError:  # Normal if image viewer is not available
        debug_out("Image viewer not available.")
    return []


def extract_images(acct_id: str, post_id: str) -> list[File]:
    debug_out("\nextract_tumblr_images()")

    post_viewer_url = f"https://tumblr.com/{acct_id}/{post_id}"
    image_viewer_url = f"https://{acct_id}.tumblr.com/image/{post_id}"
    debug_out(f"Requesting page for URL: {post_viewer_url}")

    if not (viewer_doc := get_bs_document(post_viewer_url)):
        debug_out("Request unsuccessful: network error or invalid input")
        raise ValueError("Unable to load post. "
                         "Check your internet connection, "
                         "and whether the given information is correct.")

    debug_out("Document loaded.")

    response = _query_api(acct_id, id=post_id)
    post = json.loads(response)["posts"][0]

    # New method. Best resolution, even for multiple images.
    # Unable to fetch (especially multiple) animated images.
    debug_out("1. Extracting links from post viewer (tumblr.com/blog/...) ...")
    links_from_viewer = _extract_from_post(viewer_doc.find(name="article"))
    debug_out(f"OK, found {len(links_from_viewer)} image(s).")

    # Most reliable; not always the best quality.
    debug_out("2. Extracting links from API response (blog.tumblr.com/api/read/...) ...")
    links_from_meta = _extract_from_api(response)
    debug_out(f"OK, found {len(links_from_meta)} image(s).")

    # Guaranteed the best resolution, however only provides the first image.
    debug_out("3. Extracting from the image viewer (blog.tumblr.com/image/...) ...")
    link_from_image_viewer = _extract_from_image_viewer(image_viewer_url)

    debug_out("4. Combining all links and finding best resolution...")
    image_links = _combine_best(link_from_image_viewer, links_from_meta, links_from_viewer)
    debug_out(f"Extraction complete; {len(image_links)} image(s) found.")

    title = post['slug'] if post['slug'] else acct_id

    def get_filename():
        for i, _ in enumerate(image_links):
            yield f"{title}-{post['id']}-{i+1}"
    name = get_filename()

    return [File(post_id, link, int(post["unix-timestamp"]),
                 name=next(name) + get_extension(link)) for link in image_links]


def get_recent_posts(acct_id: str, amount: int = 20, offset: int = 0) -> list[str]:
    raw_response = _query_api(acct_id, num=amount if amount > 0 else 0, start=offset)
    response = json.loads(raw_response)

    posts = response["posts"]

    to_append = []
    if amount > 50 or amount < 0:
        total_post = response["posts-total"]
        if total_post < amount or amount < 0:
            amount = total_post
        to_append = get_recent_posts(acct_id, amount - 50, offset + 50)

    return [post["id"] for post in posts] + to_append
