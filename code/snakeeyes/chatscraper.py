"""
Chat Scraper (Pokerstars only, for now)
"""
from PIL import ImageGrab, ImageOps
from . import scrape
import difflib
import _thread as thread # TODO: upgrade to threading module ?
from .fontdata import FontData

def getText(image):
    chatfont = FontData("w:/app/poker/ps-chat.fontd")
    for top,base,bottom in scrape.guess_lines(image):

        def hasInk(a,b):
            return image.getpixel((a,b+top+1)) == 0

        yield scrape.getstring(w, bottom-top, chatfont, hasInk,
                               )#train=True)

def scrape_loop(callback=lambda image: None):

    prevData = None
    prevText = []

    while True:
        im = ImageGrab.grab((x, y, x+w, y+h))

        data = list(im.getdata())
        if data != prevData:
            prevData = data
            callback(im)
            continue

            bw = ImageOps.autocontrast(im, 0).convert('1')
            text = list(getText(bw))
            for diff in difflib.ndiff(prevText, text):
                if diff.startswith("+"):
                    print(diff)
            prevText = text



if __name__=="__main__":
    # default location of chat window:
    w, h = 362,80
    x, y = 14,482
    thread.start_new_thread(scrape_loop)
