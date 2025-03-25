# cython: c_string_type=unicode, c_string_encoding=utf8

from libcpp.string cimport string
from libcpp.vector cimport vector
import numpy as np
cimport numpy as np
from enum import Enum
from cython.operator cimport dereference as deref, preincrement as inc
from libc.stdint cimport uint8_t

cdef extern from "utils.h" namespace "Utils" nogil:
    cdef struct Dims:
        int x, y

    cdef cppclass Region:
        Region() nogil
        string chrom
        int start, end
        int markerPos, markerPosEnd


cdef extern from "themes.h" namespace "Themes" nogil:

    cpdef enum GwPaint:
        bgPaint, bgPaintTiled, bgMenu, fcNormal, fcDel, fcDup, fcInvF, fcInvR, fcTra, fcIns, fcSoftClip,
        fcA, fcT, fcC, fcG, fcN, fcCoverage, fcTrack, fcNormal0, fcDel0, fcDup0, fcInvF0, fcInvR0, fcTra0,
        fcSoftClip0, fcBigWig, fcRoi, mate_fc, mate_fc0, ecMateUnmapped, ecSplit, ecSelected,
        lcJoins, lcCoverage, lcLightJoins, lcGTFJoins, lcLabel, lcBright, tcDel, tcIns, tcLabels, tcBackground,
        fcMarkers, fc5mc, fc5hmc, fcOther

    cdef cppclass BaseTheme:
        BaseTheme() nogil
        string name;
        float lwMateUnmapped, lwSplit, lwCoverage;
        void setAlphas();
        void setPaintARGB(int paint_name, int alpha, int red, int green, int blue);
        void getPaintARGB(int paint_name, int& alpha, int& red, int& green, int& blue);

    cdef cppclass IniOptions:
        IniOptions() nogil
        BaseTheme theme
        Dims dimensions, number
        string genome_tag, theme_str, parse_label, labels, font_str

        int canvas_width, canvas_height;
        int indel_length, ylim, split_view_size, threads, pad, link_op, max_coverage, max_tlen
        bint log2_cov, tlen_yscale, expand_tracks, vcf_as_tracks, sv_arcs
        float scroll_speed, tab_track_height
        int scroll_right, scroll_left, scroll_down, scroll_up
        int next_region_view, previous_region_view
        int zoom_out, zoom_in
        int start_index
        int soft_clip_threshold, small_indel_threshold, snp_threshold, variant_distance, low_memory
        int font_size
        void setTheme(string &theme_str)

    cdef cppclass Fonts:
        Fonts() nogil
        int fontTypefaceSize;
        void setTypeface(string &fontStr, int size)
        void setOverlayHeight(float yScale)



cdef extern from "include/core/SkCanvas.h" nogil:
    cdef cppclass SkCanvas:
        pass


# cdef extern from "include/core/SkSurface.h" nogil:
#     cdef cppclass sk_sp:
#         SkCanvas *getCanvas();
#     cdef cppclass SkSurface:
#         pass


cdef extern from "plot_manager.h" namespace "Manager" nogil:
    cdef cppclass GwPlot:
        GwPlot(string reference, vector[string] &bampaths, IniOptions &opts, vector[Region] &regions, vector[string] &track_paths);

        IniOptions opts
        Fonts fonts
        vector[char] pixelMemory
        vector[Region] regions
        bint drawToBackWindow, terminalOutput
        bint redraw
        int fb_width, fb_height
        int regionSelection
        float monitorScale, gap, refSpace
        double xPos_fb, yPos_fb  # mouse position

        bint processed

        string inputText

        void initBack(int width, int height)

        void clearCollections()

        void addBam(string &bam_path)

        void removeBam(int index)

        void addTrack(string &track_path, bint print_message, bint vcf_as_track, bint bed_as_track)

        void removeTrack(int index)

        void addVariantTrack(string & path, int startIndex, bint cacheStdin, bint useFullPath)

        void removeRegion(int index)

        void commandProcessed()

        void fetchRefSeq(Region &rgn)

        void setScaling()

        void setImageSize(int width, int height)

        int makeRasterSurface()

        void syncImageCacheQueue()

        void drawScreen()

        void drawScreenNoBuffer()

        void runDrawNoBuffer()

        void runDraw()

        void rasterToPng(const char * path)

        vector[uint8_t]* encodeToPngVector(int compression_level)

        vector[uint8_t]* encodeToJpegVector(int quality)

        vector[uint8_t]* encodeToWebPVector(int quality)

        void keyPress(int key, int scancode, int action, int mods)

        void windowResize(int x, int y)

        void loadIdeogramTag()

        string flushLog()

        void mouseButton(int button, int action, int mods)

        void mousePos(double x, double y)

        bint collectionsNeedRedrawing()


cdef class Gw:

    cdef GwPlot *thisptr

    cdef Py_ssize_t shape[1]
    cdef Py_ssize_t strides[1]

    cdef public bint raster_surface_created
