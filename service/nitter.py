#!/usr/bin/python
from __future__ import annotations
from datetime import datetime
from typing import Optional
from bs4 import Tag
from slugify import slugify

from common import debug_out, get_bs_document, get_extension
from common import File

INSTANCE = "https://nitter.kavin.rocks"


def parse_timestamp(timestamp: str) -> str:
    debug_out(f'Parsing "{timestamp}"')
    return str(datetime.strptime(timestamp, "%b %d, %Y · %I:%M %p %Z").timestamp())


def _find_tweets(tag: Tag):
    return tag.has_attr("class") \
        and "timeline-item" in tag["class"] \
        and "show-more" not in tag["class"] \
        and tag.find(class_='tweet-link')


def _find_next_page(tag: Tag):
    return tag.has_attr("class") \
        and "show-more" in tag["class"] \
        and "timeline-item" not in tag["class"]


def _get_tweet(tweet: Tag) -> str:
    debug_out("_get_tweet")
    tweet_link = tweet.find(class_='tweet-link')['href']
    debug_out(f"Parsing Tweet: {tweet_link}")
    tweet_link = tweet_link.split('/')[-1]
    if '#' in tweet_link:
        tweet_link = tweet_link.split('#')[0]

    debug_out(f"Link Parsed: {tweet_link}")

    return tweet_link


def _get_feeds(acct_id: str):
    def get_feed(cursor: str = "") -> tuple[list[str], Optional[str]]:
        debug_out("get_feed")
        feed = get_bs_document(f"{INSTANCE}/{acct_id}/media/", {'cursor': cursor})
        debug_out("Feed retrieval")

        timeline = feed.find(class_="timeline")
        debug_out("Extracting Timeline")
        tweets = [_get_tweet(tweet) for tweet in timeline.find_all(_find_tweets)]
        next_page = timeline.find(_find_next_page)
        debug_out("Extracting Link for Next Page")

        if next_page:
            cursor = next_page.find('a')['href'].split('=')[1]
            debug_out(f"Cursor: {cursor}")
        else:
            cursor = None
        return tweets, cursor

    tweet_page, next_cursor = get_feed()
    yield tweet_page

    while next_cursor:
        tweet_page, next_cursor = get_feed(next_cursor)
        yield tweet_page

    debug_out("End of Timeline. Terminating...")


def get_recent_posts(acct_id: str, amount: int = 20, offset: int = 0) -> list[str]:
    if amount <= 0:
        return []

    target = amount + offset
    tweets = []
    feed = _get_feeds(acct_id)
    while len(tweets) < target:
        next_feed = next(feed)
        if not next_feed:
            break
        tweets += next_feed

    end = min(target, len(tweets))
    return tweets[offset:end]


def extract_images(acct_id: str, post_id: str) -> list[File]:
    image_list = []
    tweet_link = f"{INSTANCE}/{acct_id}/status/{post_id}"
    debug_out(f"Parsing Tweet: {tweet_link}")
    tweet = get_bs_document(tweet_link).find(class_="main-tweet")

    post_time = tweet.find('span', class_='tweet-date').find('a')['title']
    post_time = parse_timestamp(post_time)
    debug_out("Parsed Date: " + post_time)

    attachments = tweet.find(class_="attachments").find_all(class_='attachment')
    title = tweet.find('div', class_='tweet-content').text
    title = slugify(title) if title else acct_id
    if len(title) > 100:
        title = title[:100]

    def gen_name():
        for i in range(4):
            yield f"{title}-{post_id}-{i + 1}"
    name = gen_name()

    for attachment in attachments:
        image_link = ""
        if attachment.find(class_='gif'):
            debug_out("Embedded Moving Image Detected; Will Be Downloaded As Video")
            image_link = INSTANCE + attachment.source['src']
        elif 'image' in attachment['class']:
            debug_out("Embedded Image Detected")
            image_link = INSTANCE + attachment.a['href']
        # elif attachment.find(class_='video'):
        #    debug_out("Embedded Video Detected.")

        #    video_src = INSTANCE + attachment.find('video')['data-url']
        #    image_list.append(video_src)

        if image_link:
            debug_out(f"Image Link: {image_link}")
            image_list.append(
                File(image_link, post_time,
                     name=next(name) + get_extension(image_link)
                     )
            )

    debug_out(f"{len(image_list)} Attachments Extracted")
    return image_list
