'''
ImageCache
Cache of images used by the UI
'''

from .cairosg import ImagePaint

from pyarts.container import component

@component
class ImageCache(object):
    depends = ['datasrc']

    def __init__(self):
        self.images = {}

    def inject(self, datasrc):
        self.datasrc = datasrc

    def getimage(self, fname):
        try:
            return self.images[fname]
        except KeyError:
            res = self.datasrc.getresource(fname)
            img = ImagePaint(res)
            self.images[fname] = img
            return img
