#!/usr/bin/python
import unittest
import feed.tumblr_feed as feed


class MyTestCase(unittest.TestCase):
    # noinspection SpellCheckingInspection
    def test_get_recent_tumblr_posts(self):
        recent_posts = feed.get_recent_tumblr_posts("loish", 20)

        self.assertEqual(len(recent_posts), 20)
        for post in recent_posts:
            self.assertRegexpMatches(post, r"\d{18}")


if __name__ == "__main__":
    unittest.main()
