#!/usr/bin/python
import unittest
import extractor.tumblr_post as extractor


class TumblrPostTestCase(unittest.TestCase):
    png1280 = "https://64.media.tumblr.com/somelongandrandomandmeaningless/hexvalues-01/s1280x1920" \
        "/filenameisalsoastringofrandomhexvalues.png"
    jpg1280 = "https://64.media.tumblr.com/somelongandrandomandmeaningless/hexvalues-01/s1280x1920" \
        "/filenameisalsoastringofrandomhexvalues.jpg"
    gif1280 = "https://64.media.tumblr.com/somelongandrandomandmeaningless/hexvalues-01/s1280x1920" \
              "/filenameisalsoastringofrandomhexvalues.gifv"
    png2048 = "https://64.media.tumblr.com/somelongandrandomandmeaningless/hexvalues-01/s2048x3072" \
        "/differentresolutionshavedifferenthexvalues.png"
    jpg2048 = "https://64.media.tumblr.com/somelongandrandomandmeaningless/hexvalues-01/s2048x3072" \
        "/differentresolutionshavedifferenthexvalues.jpg"
    
    other_jpg1280 = "https://64.media.tumblr.com/anotherlongandrandomandmeaningless/hexvalues-02/s1280x1920" \
        "/thisimageisnotliketheother.jpg"
    
    icon16 = "https://64.media.tumblr.com/yetanotherlongandrandomandmeaningless/hexvalues-03/s16x16u_c1/thisissupposedtobeasmallicon.pnj"
    avatar16 = "https://64.media.tumblr.com/avatar_someavatarshavethisformat_16.pnj"

    def test_extract_tumblr_best_res_same_extension(self):
        self.assertEqual(extractor._best_res([self.png1280, self.png2048]), self.png2048)
        self.assertEqual(extractor._best_res([self.jpg2048, self.jpg1280]), self.jpg2048)
    
    def test_extract_tumblr_best_res_mixed_extension(self):
        self.assertEqual(extractor._best_res([self.png1280, self.jpg2048]), self.jpg2048)
        self.assertEqual(extractor._best_res([self.png2048, self.jpg1280]), self.png2048)
        self.assertEqual(extractor._best_res([self.png2048, self.jpg2048]), self.png2048)
        self.assertEqual(extractor._best_res([self.jpg1280, self.png1280]), self.png1280)

