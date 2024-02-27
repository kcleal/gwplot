
import unittest
import os
from gwplot import Gw, GwPaint
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image



root = os.path.abspath(os.path.dirname(__file__))
fa = root + "/ref.fa"
plot = Gw(fa)

class TestConstruct(unittest.TestCase):
    """ Test construction and alignment"""
    def test_make_raster_surface(self):
        assert plot.make_raster_surface()

    def test_set_theme(self):
        plot.set_theme("dark")

    def test_set_image_number(self):
        plot.set_image_number(1, 1)

    def test_add_bam(self):
        plot.add_bams_from_iter((root + "/small.bam", ))

    def test_add_region(self):
        plot.add_regions_from_iter((("chr1", 1, 20000),))

    def test_run_save_png(self):
        plot.draw()
        plot.raster_to_png("out.png")

    def test_to_ndarray(self):
        arr = np.array(plot)
        assert arr.shape[0] > 0

    def test_run_draw_no_buffer(self):
        plot.draw()
        img = Image.fromarray(plot.RGBA_array())
        plt.figure()
        plt.imshow(img)
        # plt.show()

    def test_set_paint(self):
        plot.set_paint_ARBG(GwPaint.fcNormal, 255, 0, 0, 255)

    def test_set_repaint(self):
        plot.set_paint_ARBG(GwPaint.bgPaint, 55, 255, 0, 0)
        plot.draw()
        plot.raster_to_png("out2.png")



def main():
    unittest.main()


if __name__ == "__main__":
    unittest.main()