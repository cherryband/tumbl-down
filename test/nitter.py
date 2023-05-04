import unittest
from service import nitter


class MyTestCase(unittest.TestCase):

    # noinspection SpellCheckingInspection
    def test_get_recent_twitter_posts(self):
        recent_posts = nitter.get_recent_posts("instagram")
        recent_5_posts = nitter.get_recent_posts("dorrismccomics", 5)
        recent_55_posts = nitter.get_recent_posts("foxes_in_love", 55)

        self.assertEqual(len(recent_posts), 20)
        for post, _ in recent_posts:
            self.assertRegex(post, r"^\d{19}$")

        self.assertEqual(len(recent_5_posts), 5)
        for post, _ in recent_5_posts:
            self.assertRegex(post, r"^\d{19}$")

        self.assertEqual(len(set(recent_55_posts)), 55)
        for post, _ in recent_55_posts:
            self.assertRegex(post, r"^\d{19}$")

    def test_extract_single_tweet_image(self):
        # Normal image
        self.assertEqual(
            [
                f"{nitter.INSTANCE}/pic/orig/media%2FFpKCEr0akAAbwZg.png"
            ],
            nitter.extract_images("crazymlpmoments", "1627042771906482177")
        )

        # "GIF" (processed as .mp4)
        self.assertEqual(
            [
                f"{nitter.INSTANCE}/pic/video.twimg.com%2Ftweet_video%2FFoXa4TgXEAAAXVm.mp4"
            ],
            nitter.extract_images("daily_foxington", "1622943905057587201")
        )

    def test_extract_tweet_no_image(self):
        # Tweet with embedded video.
        # Twitter saves these as "m3u8" (or HTTP Live Streaming, HLS) format,
        # which is a format for streaming video with adaptive bitrates
        # (you can only download a playlist file).
        # To download the actual video file, you will need an external tool such as ffmpeg.
        self.assertEqual(
            [],
            nitter.extract_images("imagesdeltarune", "1597598571674890242")
        )


if __name__ == '__main__':
    unittest.main()
