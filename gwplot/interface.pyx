# cython: c_string_type=unicode, c_string_encoding=utf8
import os.path

from libcpp.string cimport string
from libcpp.vector cimport vector
import numpy as np
cimport numpy as np

np.import_array()

cdef class Gw:
    """Interface to GW"""
    def __cinit__(self, str reference, str theme="slate", width=None, height=None):
        cdef string ref = reference.encode("utf-8")
        cdef IniOptions opts = IniOptions()
        opts.threads = 1
        cdef vector[string] bampaths, track_paths
        cdef vector[Region] regions
        if width is not None:
            assert isinstance(width, int)
            opts.dimensions.x = <int>width
        if height is not None:
            assert isinstance(height, int)
            opts.dimensions.y = <int>height
        self.thisptr = new GwPlot(ref, bampaths, opts, regions, track_paths)
        self.thisptr.drawToBackWindow = <bint>True
        # self.thisptr.initBack(opts.dimensions.x, opts.dimensions.y)

    def __init__(self, str reference, str theme="slate", width=None, height=None):
        self.raster_surface_created = False
        self.set_theme(theme)

    @property
    def canvas_width(self):
        return self.thisptr.opts.dimensions.x

    def set_canvas_width(self, int width):
        self.thisptr.fb_width = width
        self.thisptr.opts.dimensions.x = width
        self.thisptr.makeRasterSurface()

    @property
    def canvas_height(self):
        return self.thisptr.opts.dimensions.y

    def set_canvas_height(self, int height):
        self.thisptr.fb_height = height
        self.thisptr.opts.dimensions.y = height
        self.thisptr.makeRasterSurface()

    @property
    def canvas_size(self):
        return self.thisptr.opts.dimensions.x, self.thisptr.opts.dimensions.y

    def set_canvas_size(self, int width, int height):
        self.thisptr.fb_width = width
        self.thisptr.opts.dimensions.x = width
        self.thisptr.fb_height = height
        self.thisptr.opts.dimensions.y = height
        self.thisptr.makeRasterSurface()

    @property
    def theme(self):
        return self.thisptr.opts.theme.name

    def set_theme(self, theme_name):
        if theme_name not in ("slate", "dark", "igv"):
            raise ValueError("Theme must be one of slate, dark, igv")
        self.thisptr.opts.setTheme(theme_name)
        self.thisptr.opts.theme.setAlphas()

    @property
    def threads(self):
        return self.thisptr.opts.threads

    def set_threads(self, int threads):
        self.thisptr.opts.threads = threads # if threads > 1 else 1

    @property
    def indel_length(self):
        return self.thisptr.opts.indel_length

    def set_indel_length(self, indel_length):
        self.thisptr.opts.indel_length = indel_length

    @property
    def ylim(self):
        return self.thisptr.opts.ylim

    def set_ylim(self, ylim):
        self.thisptr.opts.ylim = ylim

    @property
    def split_view_size(self):
        return self.thisptr.opts.split_view_size

    def set_split_view_size(self, split_view_size):
        self.thisptr.opts.split_view_size = split_view_size

    @property
    def pad(self):
        return self.thisptr.opts.pad

    def set_pad(self, pad):
        self.thisptr.opts.pad = pad

    @property
    def max_coverage(self):
        return self.thisptr.opts.max_coverage

    def set_max_coverage(self, max_coverage):
        self.thisptr.opts.max_coverage = max_coverage

    @property
    def max_tlen(self):
        return self.thisptr.opts.max_tlen

    def set_max_tlen(self, max_tlen):
        self.thisptr.opts.max_tlen = max_tlen

    @property
    def log2_cov(self):
        return self.thisptr.opts.log2_cov

    def set_log2_cov(self, log2_cov):
        self.thisptr.opts.log2_cov = log2_cov

    @property
    def tlen_yscale(self):
        return self.thisptr.opts.tlen_yscale

    def set_tlen_yscale(self, tlen_yscale):
        self.thisptr.opts.tlen_yscale = tlen_yscale

    @property
    def expand_tracks(self):
        return self.thisptr.opts.expand_tracks

    def set_expand_tracks(self, expand_tracks):
        self.thisptr.opts.expand_tracks = expand_tracks

    @property
    def vcf_as_tracks(self):
        return self.thisptr.opts.vcf_as_tracks

    def set_vcf_as_tracks(self, vcf_as_tracks):
        self.thisptr.opts.vcf_as_tracks = vcf_as_tracks

    @property
    def sv_arcs(self):
        return self.thisptr.opts.sv_arcs

    def set_sv_arcs(self, sv_arcs):
        self.thisptr.opts.sv_arcs = sv_arcs

    @property
    def scroll_speed(self):
        return self.thisptr.opts.scroll_speed

    def set_scroll_speed(self, scroll_speed):
        self.thisptr.opts.scroll_speed = scroll_speed

    @property
    def tab_track_height(self):
        return self.thisptr.opts.tab_track_height

    def set_tab_track_height(self, tab_track_height):
        self.thisptr.opts.tab_track_height = tab_track_height

    @property
    def start_index(self):
        return self.thisptr.opts.start_index

    def set_start_index(self, start_index):
        self.thisptr.opts.start_index = start_index

    @property
    def soft_clip_threshold(self):
        return self.thisptr.opts.soft_clip_threshold

    def set_soft_clip_threshold(self, soft_clip_threshold):
        self.thisptr.opts.soft_clip_threshold = soft_clip_threshold

    @property
    def small_indel_threshold(self):
        return self.thisptr.opts.small_indel_threshold

    def set_small_indel_threshold(self, small_indel_threshold):
        self.thisptr.opts.small_indel_threshold = small_indel_threshold

    @property
    def snp_threshold(self):
        return self.thisptr.opts.snp_threshold

    def set_snp_threshold(self, snp_threshold):
        self.thisptr.opts.snp_threshold = snp_threshold

    @property
    def variant_distance(self):
        return self.thisptr.opts.variant_distance

    def set_variant_distance(self, variant_distance):
        self.thisptr.opts.variant_distance = variant_distance

    @property
    def low_memory(self):
        return self.thisptr.opts.low_memory

    def set_low_memory(self, low_memory):
        self.thisptr.opts.low_memory = low_memory

    def set_image_number(self, int x, int y):
        self.thisptr.opts.number.x = x
        self.thisptr.opts.number.y = y

    def set_paint_ARBG(self, int paint_enum, int a, int r, int g, int b):
        self.thisptr.opts.theme.setPaintARGB(paint_enum, a, r, g, b)

    def add_bam(self, path):
        cdef string b
        assert os.path.exists(path)
        b = path.encode("utf-8")
        self.thisptr.addBam(b)

    def add_bams_from_iter(self, paths):
        try:
            iterator = iter(paths)
        except TypeError:
            raise TypeError("bam_path is not iterable")
        else:
            for p in paths:
                self.add_bam(p)

    def remove_bam(self, int index):
        self.thisptr.removeBam(index)

    def add_track(self, path, bint vcf_as_track=True, bint bed_as_track=True):
        cdef string b
        assert os.path.exists(path)
        b = path.encode("utf-8")
        self.thisptr.addTrack(b, <bint>False, vcf_as_track, bed_as_track)

    def add_tracks_from_iter(self, paths):
        try:
            iterator = iter(paths)
        except TypeError:
            raise TypeError("bam_path is not iterable")
        else:
            for p in paths:
                self.add_track(p)

    def remove_track(self, int index):
        self.thisptr.removeTrack(index)

    def add_region(self, chrom, int start, int end, int marker_start=-1, int marker_end=-1):
        cdef string c = chrom.encode("utf-8")
        cdef Region reg = Region()
        reg.chrom = c
        reg.start = start
        reg.end = end
        reg.markerPos = marker_start
        reg.markerPosEnd = marker_end
        self.thisptr.regions.push_back(reg)

    def add_regions_from_iter(self, regions):
        try:
            iterator = iter(regions)
        except TypeError:
            raise TypeError("bam_path is not iterable")
        else:
            for item in regions:
                self.add_region(*item)

    def remove_region(self, int index):
        self.thisptr.removeRegion(index)

    def apply_command(self, str command):
        cdef string c = command.encode("utf-8")
        self.thisptr.inputText = c
        self.thisptr.commandProcessed()

    def key_press(self, int key, int scancode, int action, int mods):
        self.thisptr.keyPress(key, scancode, action, mods)

    def make_raster_surface(self, width=None, height=None):
        if width is not None:
            assert isinstance(width, int)
            self.thisptr.opts.dimensions.x = <int>width
        if height is not None:
            assert isinstance(height, int)
            self.thisptr.opts.dimensions.y = <int>height
        self.thisptr.setImageSize(self.thisptr.opts.dimensions.x, self.thisptr.opts.dimensions.y)
        size = self.thisptr.makeRasterSurface()
        if size == 0:
            raise RuntimeError("Could not create raster image. Size was 0")
        self.raster_surface_created = True

    def raster_to_png(self, path):
        cdef string c = path.encode("utf-8")
        self.thisptr.rasterToPng(c.c_str())

    def draw(self):
        if not self.raster_surface_created:
            self.make_raster_surface()
        self.thisptr.processed = False
        self.thisptr.runDraw()

    def draw_stream(self):
        if not self.raster_surface_created:
            self.make_raster_surface()
        self.thisptr.processed = False
        self.thisptr.runDrawNoBuffer()

    # def __array__(self):
    #     print("In array")
    #     # https://stackoverflow.com/questions/45133276/passing-c-vector-to-numpy-through-cython-without-copying-and-taking-care-of-me
    #     # Memory is managed on the c++ side, so I assume this wrapper does not need to call free, or reference count
    #     cdef np.npy_intp shape[1]
    #     shape[0] = <np.npy_intp> self.thisptr.pixelMemory.size()
    #     ndarray = np.PyArray_SimpleNewFromData(1, shape, np.NPY_INT8, self.thisptr.pixelMemory.data())
    #     return ndarray
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        """
        Buffer protocol is called when numpy tries to make an array out of this
        """
        cdef Py_ssize_t itemsize = sizeof(self.thisptr.pixelMemory[0])
        self.shape[0] = self.thisptr.pixelMemory.size()
        self.strides[0] = sizeof(char)
        buffer.buf = &(self.thisptr.pixelMemory[0])  # char *
        buffer.format = 'B'
        buffer.internal = NULL
        buffer.itemsize = itemsize
        buffer.len = self.shape[0] * itemsize
        buffer.ndim = 1
        buffer.obj = self
        buffer.readonly = 0
        buffer.shape = self.shape
        buffer.strides = self.strides
        buffer.suboffsets = NULL

    def __dealloc__(self):
        """ Frees the array. This is called by Python when all the
        references to the object are gone. Freeing of the array is left to the c++ layer"""
        pass

    def array(self):
        if not self.raster_surface_created:
            return None
        return np.array(self).reshape(self.canvas_height, self.canvas_width, 4)
