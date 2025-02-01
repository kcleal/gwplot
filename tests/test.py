
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
        plot.make_raster_surface()
        print("test_make_raster_surface done")

    def test_set_theme(self):
        plot.set_theme("dark")
        print("test_set_theme done")

    def test_set_image_number(self):
        plot.set_image_number(1, 1)
        print("test_set_image_number done")

    def test_add_bam(self):
        plot.add_bams_from_iter((root + "/small.bam", ))
        print("test_add_bam done")

    def test_remove_bam(self):
        plot.remove_bam(0)
        plot.add_bam(root + "/small.bam")
        print("test_remove_bam done")

    def test_add_remove_track(self):
        plot.add_track(root + "/test.gff3")
        plot.remove_track(0)
        print("test_add_remove_track done")

    def test_add_region(self):
        plot.add_regions_from_iter([("chr1", 1, 20000)])
        print("test_add_region done")

    def test_remove_region(self):
        plot.remove_region(0)
        plot.add_region("chr1", 1, 20000)
        print("test_remove_region done")

    def test_run_save_png(self):
        plot.draw()
        plot.raster_to_png("out.png")
        print("test_run_save_png done")

    def test_to_ndarray(self):
        arr = np.array(plot)
        assert arr.shape[0] > 0
        print("test_to_ndarray done")

    def test_run_draw_no_buffer(self):
        plot.apply_command("ylim 30")
        plot.draw()
        img = Image.fromarray(plot.array())
        plt.figure()
        plt.imshow(img)
        # plt.show()
        print("test_run_draw_no_buffer done")

    def test_set_paint(self):
        plot.set_paint_ARBG(GwPaint.fcNormal, 255, 0, 0, 255)
        print("test_set_paint done")

    def test_set_repaint(self):
        plot.set_paint_ARBG(GwPaint.bgPaint, 55, 255, 0, 0)
        plot.draw()
        plot.raster_to_png("out2.png")
        print("test_set_repaint done")



def main():
    unittest.main()


if __name__ == "__main__":
    unittest.main()