#!/usr/bin/python
import unittest

from service import tumblr


class TumblrServiceTestCase(unittest.TestCase):
    # noinspection SpellCheckingInspection
    def test_get_recent_tumblr_posts(self):
        recent_posts = tumblr.get_recent_posts("loish")
        recent_5_posts = tumblr.get_recent_posts("pascalcampion", 5)
        recent_55_posts = tumblr.get_recent_posts("thelatestkate", 55)

        self.assertEqual(len(recent_posts), 20)
        for post in recent_posts:
            self.assertRegex(post, r"^\d{18}$")

        self.assertEqual(len(recent_5_posts), 5)
        for post in recent_5_posts:
            self.assertRegex(post, r"^\d{18}$")

        self.assertEqual(len(set(recent_55_posts)), 55)
        for post in recent_55_posts:
            self.assertRegex(post, r"^\d{18}$")

    # noinspection SpellCheckingInspection
    def test_extract_tumblr_single_image(self):
        # test single image
        self.assertEqual(
            "https://64.media.tumblr.com/656c1b0e9008c5daa813c1530c7b4610/f994f9125257a26d-3f/s2048x3072"
            "/4a9f313d9f73f21bcc53facda98ad2fb681530c2.jpg",
            tumblr.extract_images("kiminukii", "656015203710976000")[0].link,
        )

        self.assertEqual(
            "https://64.media.tumblr.com/6f508a4fc1a07ca20cdf786b730c982d/61ae23b5425caadf-52/s2048x3072"
            "/cf2cbfec7d5323d1cbd345eeb442d70eeed8c5d9.png",
            tumblr.extract_images("dailyskyfox", "656342309663801344")[0].link,
        )

        # test single image without direct viewer access
        self.assertEqual(
            "https://64.media.tumblr.com/bdf1a1b5dd22c7bb961452c86994e9bb/f4a9103f1a6f2e3c-6c/s1280x1920"
            "/3319e9b6809c8f9d7d56d3da49951762d0e70e54.jpg",
            tumblr.extract_images("maruti-bitamin", "663149423546777600")[0].link,
        )

        # test q&a post with image (no viewer available)
        self.assertEqual(
            "https://64.media.tumblr.com/3c96628aa389c486888533119eb44e1b/668384efb8b110a4-46/s2048x3072"
            "/6a81be1f7fe0e16f7c4981eaf3329cf14a68bbf2.png",
            tumblr.extract_images("spritzeedaily", "683083918501707776")[0].link,
        )

        # test post only available in new tumblr viewer
        self.assertEqual(
            "https://64.media.tumblr.com/583634942103df51291116282ceb4af1/e90c46c670b6794e-01/s2048x3072"
            "/999003de35d0168224f4702be3f40a34930da29b.png",
            tumblr.extract_images("mymunefanartaccount", "708294594717270016")[0].link,
        )

    def test_extract_tumblr_multiple_image(self):
        # test multiple images
        png1 = tumblr.extract_images("zandraart", "662604327475707904")
        self.assertEqual(3, len(png1))
        self.assertEqual(
            "https://64.media.tumblr.com/7ce02d1c06accb2db65ffae410592807/b718ff429b370a25-d4"
            "/s640x960/dff9bb177424a46c598be9768abf6d7ace8276af.png",
            png1[0].link,
        )
        self.assertEqual(
            "https://64.media.tumblr.com/8173aec87f24dad743c8607721c5fe06/b718ff429b370a25-c4"
            "/s640x960/f64312a68a8f8999dc3efad84b7777f8f62db00a.png",
            png1[1].link,
        )
        self.assertEqual(
            "https://64.media.tumblr.com/c95be592fed81a52e597f524930207f8/b718ff429b370a25-36"
            "/s640x960/189ff2d22791c6110e2d2bbf9c0c8f5338b3a786.png",
            png1[2].link,
        )

        gif1 = tumblr.extract_images("kittenwitchandthebadvibes", "661792902683525120")

        self.assertEqual(3, len(gif1))
        self.assertRegex(
            gif1[0].link,
            r"https://64\.media\.tumblr\.com/c1500c8ad3c53c8dd3768b70bed09134/ccffdfdc14aead67-2f/s1280x1920"
            r"/1837f31750522ceaed01f0b6679fc71492de6afe\.gifv?",
        )
        self.assertRegex(
            gif1[1].link,
            r"https://64\.media\.tumblr\.com/0b3958305e93b69bd446fa5ad8c6f4b2/ccffdfdc14aead67-f6/s1280x1920"
            r"/e0e346f72539cf303e9ea3a7cb8e2185ace9c2f3\.gifv?",
        )
        self.assertRegex(
            gif1[2].link,
            r"https://64\.media\.tumblr\.com/b8a53976248ae44c1a595ffacbbe483d/ccffdfdc14aead67-e4/s1280x1920"
            r"/53b3a4f0e34550b07dd0da44e2f25caa1ad18612\.gifv?",
        )

    def test_extract_tumblr_no_photos(self):

        # test video
        self.assertEqual(
            [], tumblr.extract_images("simonalkenmayer", "664168073150988288"),
        )

        # test post without media
        self.assertEqual(
            [], tumblr.extract_images("stuckwith-harry", "640948223894290432"),
        )

        # test ask without media (has profile picture)
        self.assertEqual(
            [], tumblr.extract_images("mymunefanartaccount", "709722828554027008")
        )

        # test invalid blog and post id
        with self.assertRaises(ValueError):
            tumblr.extract_images("temmiechang", "temmiechang")
        with self.assertRaises(ValueError):
            tumblr.extract_images("I am a teapot.", "346409543733251134")


if __name__ == '__main__':
    unittest.main()
