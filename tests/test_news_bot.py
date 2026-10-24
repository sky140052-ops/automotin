import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
import bbcc_news_bot as bot

class NewsBotTests(unittest.TestCase):
    def test_wrap_keeps_text(self):
        image = Image.new("RGB", (100, 100))
        draw = ImageDraw.Draw(image)
        lines = bot.wrap(draw, "BBCC Skill Hub daily news", bot.font(12), 45)
        self.assertGreater(len(lines), 1)
        self.assertEqual(" ".join(lines), "BBCC Skill Hub daily news")

    def test_poster_dimensions_and_branding(self):
        sample = {
            "headline": "बिहार शिक्षा से जुड़ी ताज़ा खबर",
            "summary": "यह परीक्षण के लिए स्रोत आधारित हिंदी सारांश है। कोई काल्पनिक भर्ती संख्या शामिल नहीं है।",
            "bullets": ["पहली मुख्य बात", "दूसरी मुख्य बात", "तीसरी मुख्य बात"]
        }
        with tempfile.TemporaryDirectory() as tmp:
            old_out = bot.OUT
            bot.OUT = Path(tmp)
            try:
                path = bot.make_poster(sample)
                self.assertTrue(path.exists())
                with Image.open(path) as img:
                    self.assertEqual(img.size, (1080, 1350))
                    self.assertEqual(img.format, "PNG")
            finally:
                bot.OUT = old_out

if __name__ == "__main__":
    unittest.main()
