"""
Chat Scraper

This is just an old console script that scraped the chat window
for a poker client.

TODO: turn this script into a real example
"""
from PIL import ImageGrab, ImageOps
from . import scrape
import difflib
import _thread as thread  # TODO: upgrade to threading module ?
from .fontdata import FontData


def get_text(image):
    font = FontData("w:/app/poker/ps-chat.fontd")
    for top, base, bottom in scrape.guess_lines(image):

        def has_ink(a, b):
            return image.getpixel((a, b + top + 1)) == 0  # TODO: replace 0 (black) with color param

        # TODO re-add train=True parameter, based on gui checkbox
        yield scrape.getstring(w, bottom-top, font, has_ink)


def scrape_loop(callback=(lambda image: None), show_diffs: bool = False):

    prev_data = None
    prev_text = []

    while True:
        im = ImageGrab.grab((x, y, x+w, y+h))

        data = list(im.getdata())
        if data != prev_data:
            prev_data = data
            callback(im)

            if show_diffs:
                bw = ImageOps.autocontrast(im, 0).convert('1')
                text = list(get_text(bw))
                for diff in difflib.ndiff(prev_text, text):
                    if diff.startswith("+"):
                        print(diff)
                prev_text = text


if __name__ == "__main__":
    # default location of chat window:
    w, h = 362, 80
    x, y = 14, 482
    thread.start_new_thread(scrape_loop)
