#!/usr/bin/python
from __future__ import annotations

import json
from functools import cache
from dateutil.parser import isoparse
from slugify import slugify

from common import debug_out, request_get, File

NAME="Bluesky"
SLUG="bluesky"


def _query_api(function, **params) -> str:
    query_url = f"https://api.bsky.app/xrpc/{function}"

    req = request_get(query_url, params=params)
    raw_json = req.text.strip()

    return json.loads(raw_json)


def parse_timestamp(timestamp: str) -> int:
    debug_out(f'Parsing "{timestamp}"')
    return int(isoparse(timestamp).timestamp())


def _fetch_post(ident, post):
    return _query_api('app.bsky.feed.getPostThread',
                      uri=f'at://{ident}/app.bsky.feed.post/{post}',
                      depth=0, parentHeight=0)['thread']['post']


@cache
def _resolve_did(ident):
    if ident.startswith("did:"):
        return ident
    return _query_api("app.bsky.actor.getProfile", actor=ident)['did']


def _resolve_post(ident, post):
    if isinstance(post, dict):
        return post
    did = _resolve_did(ident)
    return _fetch_post(did, post)


def _get_extension(image_link: str) -> str:
    return '.' + image_link.split('@')[-1]


def extract_images(acct_id: str, post) -> list[File]:
    post = _resolve_post(acct_id, post)

    post_id = post["uri"].split('/')[-1]
    image_links = [image['fullsize'] for image in post['embed']['images']]

    record_text = post['record']['text']
    title = slugify(record_text, max_length=80, allow_unicode=True)
    timestamp = parse_timestamp(post['record']['createdAt'])

    def gen_name():
        for i in range(len(image_links)):
            yield f"{title}-{post_id}-{i + 1}"
    name = gen_name()

    return [File(post_id, link, timestamp,
                 name=next(name) + _get_extension(link)) for link in image_links]


def get_recent_posts(acct_id: str, amount: int = 50, cursor: str = "") -> list[str]:
    limit = 100 if amount > 100 or amount < 0 else amount
    response = _query_api("app.bsky.feed.getAuthorFeed", actor=acct_id,
                          limit=limit, cursor=cursor, filter="posts_with_media")

    posts = response["feed"]

    to_append = []
    if amount > 100 or amount < 0:
        total_post = len(posts)
        if total_post < amount or amount < 0:
            amount = total_post
        to_append = get_recent_posts(acct_id, amount - 100, cursor)

    return [post["post"]["uri"].split('/')[-1] for post in posts] + to_append
