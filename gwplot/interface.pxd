# cython: c_string_type=unicode, c_string_encoding=utf8

from libcpp.string cimport string
from libcpp.vector cimport vector
from cython.operator cimport dereference as deref, preincrement as inc

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
        bgPaint, fcNormal, fcDel, fcDup, fcInvF, fcInvR, fcTra, fcIns, fcSoftClip,
        fcA, fcT, fcC, fcG, fcN, fcCoverage, fcTrack, fcNormal0, fcDel0, fcDup0, fcInvF0, fcInvR0, fcTra0,
        fcSoftClip0, fcBigWig, mate_fc, mate_fc0, ecMateUnmapped, ecSplit, ecSelected,
        lcJoins, lcCoverage, lcLightJoins, insF, insS, lcLabel, lcBright, tcDel, tcIns, tcLabels, tcBackground,
        marker_paint

    cdef cppclass BaseTheme:
        BaseTheme() nogil
        string name;
        float lwMateUnmapped, lwSplit, lwCoverage;
        void setAlphas();
        void setPaintARGB(GwPaint paint_name, int alpha, int red, int green, int blue);

    cdef cppclass IniOptions:
        IniOptions() nogil
        BaseTheme theme
        Dims dimensions, number

        string genome_tag, theme_str, parse_label, labels

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


cdef extern from "plot_manager.h" namespace "Manager" nogil:
    cdef cppclass GwPlot:
        GwPlot(string reference, vector[string] &bampaths, IniOptions &opts, vector[Region] &regions, vector[string] &track_paths);

        void initBack(int width, int height)

cdef class GWplot:

    cdef GwPlot *thisptr
    cdef IniOptions opts
    cdef vector[string] __bampaths, __track_paths
    cdef vector[Region] __regions
    cdef int message