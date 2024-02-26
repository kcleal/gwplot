
import unittest
import os
from gwplot import Gw, GwPaint
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


root = os.path.abspath(os.path.dirname(__file__))
fa = root + "/ref.fa"

class TestConstruct(unittest.TestCase):
    """ Test construction and alignment"""
    def test_init(self):
        _ = Gw(fa)

    def test_make_raster_surface(self):
        plot = Gw(fa)
        assert plot.make_raster_surface()

    def test_set_theme(self):
        plot = Gw(fa)
        plot.set_theme("dark")

    def test_set_image_number(self):
        plot = Gw(fa)
        plot.set_image_number(1, 1)

    def test_set_paint(self):
        plot = Gw(fa)
        plot.set_paint_ARBG(GwPaint.fcNormal, 25, 255, 0, 255)

    def test_add_bam(self):
        plot = Gw(fa)
        plot.add_bam(root + "/small.bam")

    def test_add_region(self):
        plot = Gw(fa)
        plot.add_region("chr1", 1, 20000)

    def test_to_ndarray(self):
        plot = Gw(fa)
        plot.add_bam(root + "/small.bam")
        plot.make_raster_surface()
        arr = np.array(plot)
        assert arr.shape[0] > 0

    def test_run_draw_no_buffer(self):
        plot = Gw(fa)
        plot.add_bam(root + "/small.bam")
        plot.add_region("chr1", 1, 20000)
        plot.make_raster_surface()
        plot.run_draw_no_buffer()
        arr = np.array(plot)
        arr = np.reshape(arr, (plot.canvas_height, plot.canvas_width, 4))
        arr += 128
        arr = arr.astype(np.uint8)
        img = Image.fromarray(arr)
        plt.figure()
        plt.imshow(img)
        plt.show()

    def test_run_save_png(self):
        plot = Gw(fa, theme="dark")
        plot.add_bam(root + "/small.bam")
        plot.add_region("chr1", 1, 20000)
        plot.make_raster_surface()
        plot.run_draw_no_buffer()
        plot.raster_to_png("out.png")


def main():
    unittest.main()


if __name__ == "__main__":
    unittest.main()