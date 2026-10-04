"""
Tests for gwplot.

Run from outside the repository root (after installing gwplot), so the installed package is
imported rather than the source directory:
    python -m unittest discover -s <repo>/tests -t <repo>/tests
"""
import gc
import json
import os
import tempfile
import unittest

import numpy as np

from gwplot import Gw, GwPalette, GLFW

try:
    import matplotlib.pyplot as plt
    from PIL import Image
    have_plotting = True
except ImportError:
    have_plotting = False

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
        gw.save_png("out.png")
        print("test_run_save_png done")

    def test_to_ndarray(self):
        arr = np.array(gw)
        assert arr.shape[0] > 0
        print("test_to_ndarray done")

    @unittest.skipUnless(have_plotting, "needs matplotlib and pillow")
    def test_run_draw_no_buffer(self):
        gw.apply_command("ylim 30")
        gw.set_low_memory(1)
        gw.draw()
        img = Image.fromarray(gw.array())
        plt.figure()
        plt.imshow(img)
        # plt.show()
        print("test_run_draw_no_buffer done")

    @unittest.skipUnless(have_plotting, "needs matplotlib and pillow")
    def test_run_draw_image(self):
        img = gw.draw_image()
        plt.figure()
        plt.imshow(img)
        # plt.show()
        print("test_run_draw_image done")

    def test_set_paint(self):
        gw.set_paint_ARBG(GwPalette.NORMAL_READ, 255, 0, 0, 255)
        print("test_set_paint done")

    def test_set_repaint(self):
        gw.set_paint_ARBG(GwPalette.BACKGROUND, 55, 255, 0, 0)
        gw.draw()
        gw.save_png("out2.png")
        print("test_set_repaint done")

    # def test_pysam(self):
    #     if not have_pysam:
    #         return
    #     af = pysam.AlignmentFile(root + "/small.bam")
    #     region = ("chr1", 1, 20000)
    #     bam_itr = af.fetch(*region)
    #
    #     gw.clear_alignments()
    #     gw.clear_regions()
    #     gw.add_region(*region)
    #
    #     gw.add_pysam_alignments(bam_itr)
    #
    #     print(dir(bam_itr))
    #     print(bam_itr)
    #     print("test_pysam done")


# --- gw 2.x features, on fresh instances over gw's own test data ---------------------

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gw", "test")
FASTA = os.path.join(TEST_DIR, "test.fa")
BAM = os.path.join(TEST_DIR, "test.bam")
BED = os.path.join(TEST_DIR, "test.bed")

# A region with reads in the test BAM
CHROM = "chr1"
START = 9900
END = 11000


def make_gw(**kwargs):
    gw = Gw(FASTA, **kwargs)
    gw.set_canvas_size(800, 600)
    return gw


def make_plot(*regions, track=False):
    gw = make_gw()
    gw.add_bam(BAM)
    for start, end in regions or [(START, END)]:
        gw.add_region(CHROM, start, end)
    if track:
        gw.add_track(BED)
    return gw


def render(gw):
    gw.draw()
    return gw.encode_as_png()


class TestRendering(unittest.TestCase):

    def assertPng(self, data):
        self.assertIsInstance(data, bytes)
        self.assertGreater(len(data), 100)
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")

    def test_basic_render(self):
        self.assertPng(render(make_plot()))

    def test_canvas_size(self):
        gw = make_gw()
        gw.set_canvas_size(1280, 720)
        self.assertEqual(gw.canvas_size, (1280, 720))

    def test_canvas_size_renders(self):
        small = make_plot()
        small.set_canvas_size(400, 300)
        large = make_plot()
        large.set_canvas_size(1280, 800)
        self.assertNotEqual(len(render(small)), len(render(large)))

    def test_themes(self):
        for theme in ("dark", "igv", "slate"):
            gw = make_plot()
            gw.set_theme(theme)
            self.assertEqual(gw.theme, theme)
            self.assertPng(render(gw))
        with self.assertRaises(ValueError):
            make_gw().set_theme("neon")

    def test_theme_command(self):
        # The theme command styles ImGui, which needs a context
        gw = make_plot()
        gw.apply_command("theme igv")
        self.assertPng(render(gw))

    def test_theme_command_after_other_instance_freed(self):
        # Freeing one instance must not leave another without an ImGui context
        first = make_gw()
        second = make_plot()
        del first
        gc.collect()
        second.apply_command("theme dark")
        self.assertPng(render(second))

    def test_paint_override(self):
        gw = make_plot()
        gw.set_paint_ARGB(GwPalette.DELETION, 255, 255, 0, 0)
        gw.set_paint_ARBG(GwPalette.DELETION, 255, 255, 0, 0)
        self.assertPng(render(gw))

    def test_save_theme_json_round_trip(self):
        gw = make_gw()
        gw.set_paint_ARGB(GwPalette.DELETION, 255, 10, 20, 30)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "theme.json")
            gw.save_theme_to_json(path)
            with open(path) as f:
                self.assertEqual(json.load(f)["DELETION"], [255, 10, 20, 30])
            other = make_plot()
            other.load_theme_from_json(path)
            self.assertPng(render(other))

    def test_options(self):
        gw = make_gw()
        gw.set_ylim(30).set_indel_length(5).set_log2_cov(True).set_sv_arcs(True)
        gw.set_soft_clip_threshold(20).set_snp_threshold(5000).set_tlen_yscale(True)
        gw.set_threads(4)
        self.assertEqual((gw.ylim, gw.sam_max_y), (30, 30))
        self.assertEqual(gw.indel_length, 5)
        self.assertTrue(gw.log2_cov and gw.sv_arcs and gw.tlen_yscale)
        self.assertEqual((gw.soft_clip_threshold, gw.snp_threshold, gw.threads), (20, 5000, 4))

    def test_data_labels(self):
        # The default comes from .gw.ini; the keyword overrides it either way.
        self.assertTrue(make_gw(data_labels=True).data_labels)
        gw = make_gw(data_labels=False)
        self.assertFalse(gw.data_labels)
        gw.add_bam(BAM)
        gw.add_region(CHROM, START, END)
        self.assertPng(render(gw))

    def test_encode_before_draw_returns_none(self):
        self.assertIsNone(make_gw().encode_as_png())

    def test_encode_as_jpeg(self):
        gw = make_plot()
        gw.draw()
        self.assertEqual(gw.encode_as_jpeg(quality=85)[:2], b"\xff\xd8")

    def test_numpy_array(self):
        gw = make_plot()
        gw.draw()
        arr = gw.array()
        self.assertEqual(arr.shape, (600, 800, 4))
        self.assertEqual(arr.dtype, np.uint8)
        self.assertEqual(np.asarray(gw).shape, (600, 800, 4))

    def test_multiple_and_removed_bams(self):
        gw = make_gw()
        gw.add_bam(BAM)
        gw.add_bam(BAM)
        gw.remove_bam(1)
        gw.add_region(CHROM, START, END)
        self.assertPng(render(gw))

    def test_save_png(self):
        gw = make_plot()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.png")
            gw.save_png(path)
            with open(path, "rb") as f:
                self.assertPng(f.read())

    def test_flush_log(self):
        gw = make_plot()
        gw.draw()
        self.assertIsInstance(gw.flush_log(), str)

    def test_redraw_flag(self):
        gw = make_plot()
        self.assertTrue(gw.redraw)
        gw.draw()
        gw.set_redraw(False)
        self.assertFalse(gw.redraw)


class TestRegions(unittest.TestCase):

    def regions(self, gw):
        return [(r["chrom"], r["start"], r["end"]) for r in gw.get_viewport()["regions"]]

    def test_split_view(self):
        gw = make_plot((START, END), (START + 500, END + 500))
        self.assertEqual(len(self.regions(gw)), 2)
        render(gw)

    def test_clear_regions(self):
        gw = make_plot((START, END), (START + 100, END + 100), (START + 200, END + 200))
        gw.clear_regions()
        self.assertEqual(self.regions(gw), [])
        render(gw)

    def test_set_region_list_with_add_command(self):
        gw = make_plot()
        gw.clear_regions()
        gw.apply_command(f"add {CHROM}:{START}-{END}")
        gw.apply_command(f"add {CHROM}:{START + 500}-{END + 500}")
        self.assertEqual([r[1] for r in self.regions(gw)], [START, START + 500])
        render(gw)
        gw.clear_regions()
        gw.apply_command(f"add {CHROM}:{START}-{END}")
        self.assertEqual(len(self.regions(gw)), 1)
        render(gw)

    def test_view_region(self):
        gw = make_plot((START, END), (START + 500, END + 500))
        gw.view_region(CHROM, START + 100, END + 100)
        self.assertEqual(self.regions(gw), [(CHROM, START + 100, END + 100)])

    def test_set_active_region_index(self):
        gw = make_plot((START, END), (START + 500, END + 500))
        gw.set_active_region_index(0)
        gw.apply_command(f"goto {CHROM}:{START + 200}-{END + 200}")
        self.assertEqual(self.regions(gw)[0][1], START + 200)

    def test_get_viewport(self):
        gw = make_plot()
        gw.draw()
        vp = gw.get_viewport()
        self.assertTrue(vp["scale_bar_enabled"])
        self.assertLess(vp["scale_bar_top"], vp["scale_bar_bottom"])
        self.assertGreater(vp["gap"], 0)
        self.assertEqual(vp["regions"][0], {"index": 0, "chrom": CHROM, "start": START, "end": END})


class TestMarkers(unittest.TestCase):

    def test_marker_api(self):
        gw = make_plot()
        gw.add_marker(CHROM, 10000).add_marker(CHROM, 10500, 10600)
        self.assertEqual(gw.markers, [(CHROM, 10000, 10001), (CHROM, 10500, 10600)])
        gw.remove_marker(CHROM, 10000)
        self.assertEqual(gw.markers, [(CHROM, 10500, 10600)])
        gw.clear_markers()
        self.assertEqual(gw.markers, [])

    def test_marker_commands(self):
        gw = make_plot()
        gw.apply_command(f"marker {CHROM}:10000-10010")
        gw.apply_command(f"marker {CHROM} 10500")
        self.assertEqual(gw.markers, [(CHROM, 10000, 10010), (CHROM, 10500, 10501)])
        gw.apply_command("clear-markers")
        self.assertEqual(gw.markers, [])

    def test_marker_is_drawn(self):
        plain = render(make_plot())
        marked = make_plot()
        marked.add_marker(CHROM, 10500)
        self.assertNotEqual(render(marked), plain)

    def test_marker_draws_in_second_pane(self):
        # Pane 0 is 9900-11000, pane 1 is 10400-11500; 11200 is only inside pane 1
        panes = ((START, END), (START + 500, END + 500))
        marked = make_plot(*panes)
        marked.add_marker(CHROM, 11200)
        self.assertNotEqual(render(marked), render(make_plot(*panes)))

    def test_marker_persists_across_navigation(self):
        gw = make_plot()
        gw.add_marker(CHROM, 10500)
        gw.apply_command(f"goto {CHROM}:{START + 100}-{END + 100}")
        after_goto = render(gw)
        fresh = make_plot((START + 100, END + 100))
        fresh.add_marker(CHROM, 10500)
        self.assertEqual(after_goto, render(fresh))

    def test_removed_marker_is_not_drawn(self):
        gw = make_plot()
        gw.add_marker(CHROM, 10500)
        render(gw)
        gw.remove_marker(CHROM, 10500)
        self.assertEqual(render(gw), render(make_plot()))

    def test_region_marker_kept_with_persistent_markers(self):
        def plot(region_marker):
            gw = make_gw()
            gw.add_bam(BAM)
            gw.add_marker(CHROM, 10000)
            if region_marker:
                gw.add_region(CHROM, START, END, 10500, 10501)
            else:
                gw.add_region(CHROM, START, END)
            return render(gw)
        self.assertNotEqual(plot(True), plot(False))

    def test_remove_marker_command(self):
        gw = make_plot()
        gw.apply_command(f"marker {CHROM} 10000")
        gw.apply_command(f"marker {CHROM}:10500-10600")
        gw.apply_command(f"remove-marker {CHROM}:10000")
        self.assertEqual(gw.markers, [(CHROM, 10500, 10600)])
        gw.apply_command(f"remove-marker {CHROM} 10500")
        self.assertEqual(gw.markers, [])

    def test_command_marker_persists_when_regions_replaced(self):
        # Replacing every region, e.g. on a chromosome change, drops region markers but not
        # the persistent ones
        gw = make_plot()
        gw.apply_command(f"marker {CHROM} 10500")
        gw.clear_regions()
        gw.add_region(CHROM, START, END)
        self.assertEqual(gw.markers, [(CHROM, 10500, 10501)])
        fresh = make_plot()
        fresh.add_marker(CHROM, 10500)
        self.assertEqual(render(gw), render(fresh))
        self.assertNotEqual(render(gw), render(make_plot()))

    def test_clear_markers_command_keeps_region_markers(self):
        def plot(command_marker):
            gw = make_gw()
            gw.add_bam(BAM)
            gw.add_region(CHROM, START, END, 10500, 10501)
            if command_marker:
                gw.apply_command(f"marker {CHROM} 10000")
                gw.apply_command("clear-markers")
            return render(gw)
        self.assertEqual(plot(True), plot(False))


class TestTracks(unittest.TestCase):

    def test_get_tracks(self):
        gw = make_plot(track=True)
        gw.draw()
        tracks = gw.get_tracks()
        self.assertEqual(len(tracks), 1)
        self.assertEqual(set(tracks[0]), {"index", "name", "kind", "bam_index", "height_fraction"})
        self.assertEqual(tracks[0]["index"], 0)
        self.assertEqual(tracks[0]["bam_index"], -1)

    def test_set_track_height(self):
        gw = make_plot(track=True)
        gw.draw()
        gw.set_track_height(0, 0.4)
        self.assertAlmostEqual(gw.get_tracks()[0]["height_fraction"], 0.4)
        with self.assertRaises(IndexError):
            gw.set_track_height(5, 0.4)
        render(gw)

    def test_set_tab_track_height(self):
        gw = make_plot(track=True)
        before = render(gw)
        gw.set_tab_track_height(0.5)
        self.assertAlmostEqual(gw.tab_track_height, 0.5)
        self.assertNotEqual(render(gw), before)
        with self.assertRaises(ValueError):
            gw.set_tab_track_height(1.5)

    def test_expand_tracks_command(self):
        gw = make_plot(track=True)
        gw.apply_command("expand-tracks on")
        self.assertTrue(gw.expand_tracks)
        gw.apply_command("expand-tracks on")
        self.assertTrue(gw.expand_tracks)
        gw.apply_command("expand-tracks off")
        self.assertFalse(gw.expand_tracks)

    def test_translation_track(self):
        gw = make_plot()
        off = render(gw)
        gw.set_translation(True).set_translation_frame(2).set_translation_strand("-")
        gw.set_translation_code(1)
        self.assertNotEqual(render(gw), off)
        gw.set_translation(False)
        render(gw)

    def test_translation_validation(self):
        gw = make_gw()
        for frame in (0, 4, -1):
            with self.assertRaises(ValueError):
                gw.set_translation_frame(frame)
        with self.assertRaises(ValueError):
            gw.set_translation_strand("sideways")
        with self.assertRaises(ValueError):
            gw.set_translation_code(0)

    def test_translation_palette(self):
        for name in ("CODON_START", "CODON_STOP", "CODON_OTHER", "CODON_SELECTED_BG", "LINE_GAP"):
            self.assertTrue(hasattr(GwPalette, name), name)
        make_gw().set_paint_ARGB(GwPalette.CODON_START, 255, 0, 200, 0)


class TestInteraction(unittest.TestCase):

    def test_vscroll(self):
        gw = make_plot()
        gw.set_ylim(5)
        gw.draw()
        self.assertEqual(gw.vscroll, 0)
        self.assertGreater(gw.pileup_depth, 5)
        gw.set_vscroll(3)
        self.assertEqual(gw.vscroll, 3)
        render(gw)

    def test_click_selects_read(self):
        gw = make_plot()
        gw.set_canvas_size(800, 600)
        gw.draw()
        gw.clear_selected_align()
        gw.clear_selected_intron()
        gw.clear_selected_feature()
        x, y = 400, 300  # the middle of the alignment pane
        gw.mouse_event(x, y, GLFW.MOUSE_BUTTON_LEFT, GLFW.PRESS)
        gw.mouse_event(x, y, GLFW.MOUSE_BUTTON_LEFT, GLFW.RELEASE)
        self.assertEqual(len(gw.selected_align.split("\t")) >= 11, True, gw.selected_align)
        self.assertEqual(gw.selected_intron, "")
        gw.clear_selected_align()
        self.assertEqual(gw.selected_align, "")

    def test_key_press(self):
        gw = make_plot()
        gw.draw()
        gw.key_press(GLFW.KEY_RIGHT, 0, GLFW.PRESS, 0)
        self.assertGreater(gw.get_viewport()["regions"][0]["start"], START)


class TestThresholdToggles(unittest.TestCase):
    """soft-clips, insertions, mismatches and edges switch a threshold off and back on.

    Switching back reads the [view_thresholds] section of gw's .gw.ini, which Gw now loads
    like standalone gw does. Without it the second press aborted the process.
    """

    def test_each_toggle_switches_off_and_back_on(self):
        gw = make_plot()
        start = {
            "soft-clips": gw.soft_clip_threshold,
            "insertions": gw.small_indel_threshold,
            "mismatches": gw.snp_threshold,
        }
        current = {
            "soft-clips": lambda: gw.soft_clip_threshold,
            "insertions": lambda: gw.small_indel_threshold,
            "mismatches": lambda: gw.snp_threshold,
        }
        for command, value in start.items():
            with self.subTest(command=command):
                self.assertGreater(value, 0)
                gw.apply_command(command)
                self.assertEqual(current[command](), 0)
                gw.apply_command(command)
                self.assertEqual(current[command](), value)

    def test_settings_come_from_an_ini_file(self):
        """Like standalone gw: an existing .gw.ini is read, or a default one is written."""
        gw = make_gw()
        self.assertTrue(gw.ini_path)
        self.assertTrue(os.path.isfile(gw.ini_path))

    def test_ini_option_loads_that_file(self):
        default_ini = make_gw().ini_path  # a complete ini, written by gw if needed
        with tempfile.TemporaryDirectory() as tmp:
            custom = os.path.join(tmp, "custom.ini")
            with open(default_ini) as src, open(custom, "w") as dst:
                for line in src:
                    if line.startswith("theme="):
                        line = "theme=igv\n"
                    elif line.startswith("threads="):
                        line = "threads=2\n"
                    dst.write(line)
            gw = Gw(FASTA, ini=custom)
            self.assertEqual(gw.ini_path, custom)
            self.assertEqual(gw.theme, "igv")
            self.assertEqual(gw.threads, 2)
            # keyword arguments still override the file
            self.assertEqual(Gw(FASTA, ini=custom, theme="slate").theme, "slate")

    def test_missing_ini_file_is_an_error(self):
        with self.assertRaises(FileNotFoundError):
            Gw(FASTA, ini="/no/such/gw.ini")

    def test_edges_and_aliases_survive_repeated_use(self):
        gw = make_plot()
        for command in ("edges", "edges", "ins", "ins", "mm", "mm", "edges"):
            gw.apply_command(command)
        self.assertIsNotNone(render(gw))


def main():
    unittest.main()


if __name__ == "__main__":
    unittest.main()
