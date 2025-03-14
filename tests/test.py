
import unittest
import os
from gwplot import Gw, GwPaint
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

try:
    import pysam
    have_pysam = True
except ImportError:
    have_pysam = False

try:
    import skia
    have_skia = True
except ImportError:
    have_skia = False

root = os.path.abspath(os.path.dirname(__file__))
fa = root + "/ref.fa"
gw = Gw(fa)


class TestConstruct(unittest.TestCase):
    """ Test construction and alignment"""
    def test_make_raster_surface(self):
        gw.make_raster_surface()
        print("test_make_raster_surface done")

    def test_set_theme(self):
        gw.set_theme("dark")
        print("test_set_theme done")

    def test_set_image_number(self):
        gw.set_image_number(1, 1)
        print("test_set_image_number done")

    def test_add_bam(self):
        gw.add_bam(root + "/small.bam")
        print("test_add_bam done")

    def test_remove_bam(self):
        gw.remove_bam(0)
        gw.add_bam(root + "/small.bam")
        print("test_remove_bam done")

    def test_add_remove_track(self):
        gw.add_track(root + "/test.gff3")
        gw.remove_track(0)
        print("test_add_remove_track done")

    def test_add_region(self):
        gw.add_region("chr1", 1, 20000)
        print("test_add_region done")

    def test_remove_region(self):
        gw.remove_region(0)
        gw.add_region("chr1", 1, 20000)
        print("test_remove_region done")

    def test_run_save_png(self):
        gw.draw()
        gw.raster_to_png("out.png")
        print("test_run_save_png done")

    def test_to_ndarray(self):
        arr = np.array(gw)
        assert arr.shape[0] > 0
        print("test_to_ndarray done")

    def test_run_draw_no_buffer(self):
        gw.apply_command("ylim 30")
        gw.draw_stream()
        img = Image.fromarray(gw.array())
        plt.figure()
        plt.imshow(img)
        # plt.show()
        print("test_run_draw_no_buffer done")

    def test_run_draw_image(self):
        img = gw.draw_image()
        plt.figure()
        plt.imshow(img)
        # plt.show()
        print("test_run_draw_image done")

    def test_set_paint(self):
        gw.set_paint_ARBG(GwPaint.fcNormal, 255, 0, 0, 255)
        print("test_set_paint done")

    def test_set_repaint(self):
        gw.set_paint_ARBG(GwPaint.bgPaint, 55, 255, 0, 0)
        gw.draw()
        gw.raster_to_png("out2.png")
        print("test_set_repaint done")

    def test_pysam(self):
        if not have_pysam:
            return
        af = pysam.AlignmentFile(root + "/small.bam")
        region = ("chr1", 1, 20000)
        bam_itr = af.fetch(*region)

        gw.clear_alignments()
        gw.clear_regions()
        gw.add_region(*region)

        gw.add_pysam_alignments(bam_itr)

        print(dir(bam_itr))
        print(bam_itr)
        print("test_pysam done")

def main():
    unittest.main()


if __name__ == "__main__":
    unittest.main()