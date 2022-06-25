#!/usr/bin/python
import unittest
import feed.tumblr_feed as feed


class MyTestCase(unittest.TestCase):
    # noinspection SpellCheckingInspection
    def test_get_recent_tumblr_posts(self):
        recent_posts = feed.get_recent_tumblr_posts("loish")
        recent_5_posts = feed.get_recent_tumblr_posts("pascalcampion", 5)
        recent_55_posts = feed.get_recent_tumblr_posts("thelatestkate", 55)

        self.assertEqual(len(recent_posts), 20)
        for post in recent_posts:
            self.assertRegex(post, r"\d{18}")

        self.assertEqual(len(recent_5_posts), 5)
        for post in recent_5_posts:
            self.assertRegex(post, r"\d{18}")

        self.assertEqual(len(set(recent_55_posts)), 55)
        for post in recent_55_posts:
            self.assertRegex(post, r"\d{18}")


if __name__ == "__main__":
    unittest.main()
