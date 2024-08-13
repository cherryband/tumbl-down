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


def get_post_count(acct_id: str) -> int:
    return _query_api("app.bsky.actor.getProfile", actor=acct_id)['postsCount']


MAX_POSTS_PER_REQUEST = 100
def get_recent_posts(acct_id: str, amount: int = 50, incl_reblog=False) -> list[str]:
    index = 0
    offset = 0
    total_posts = get_post_count(acct_id)

    if amount < 0 or total_posts < amount:
        amount = total_posts
        print(f"Notice: Number of posts adjusted to {total_posts}.")

    limit = amount if amount < MAX_POSTS_PER_REQUEST else MAX_POSTS_PER_REQUEST
    response = _query_api("app.bsky.feed.getAuthorFeed", actor=acct_id,
                      limit=limit, filter="posts_with_media")
    debug_out(response)
    posts = response["feed"]
    cursor = response["cursor"] if 'cursor' in response.keys() else ''

    while index < amount:
        cur_index = index - offset
        if cur_index >= MAX_POSTS_PER_REQUEST:
            offset += MAX_POSTS_PER_REQUEST
            response = _query_api("app.bsky.feed.getAuthorFeed", actor=acct_id,
                              limit=limit, cursor=cursor, filter="posts_with_media")
            posts = response["feed"]
            cursor = response["cursor"] if 'cursor' in response.keys() else ''
            cur_index = 0

        post = posts[cur_index]['post']
        yield extract_images(acct_id, post)

        index += 1

