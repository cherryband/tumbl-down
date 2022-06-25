#!/usr/bin/python
import json

from util import request_get


def _print_err(message, error):
    print(message)
    print("The error message below may give you (or someone else) a clue.")
    print(error)


def get_recent_tumblr_posts(blog_id: str, amount: int = 20, offset: int = 0) -> list[str]:
    if not blog_id.replace('-', '').replace('_', '').isalnum():
        raise ValueError("blog_id seems to be incorrect. Is there spaces?")

    blog_url = f"https://{blog_id}.tumblr.com"
    query_url = f"{blog_url}/api/read/json"

    req = request_get(query_url, {"num": amount, "filter": "text", "start": offset})
    raw_json = req.text.removeprefix("var tumblr_api_read =").strip().removesuffix(";")
    response = json.loads(raw_json)

    posts = response["posts"]

    to_append = []
    if amount > 50:
        total_post = response["posts-total"]
        if total_post < amount:
            print("The requested amount exceeds the post count")
            amount = total_post
        to_append = get_recent_tumblr_posts(blog_id, amount - 50, offset + 50)

    return [post["url"].split('/')[4] for post in posts] + to_append
