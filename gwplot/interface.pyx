# cython: c_string_type=unicode, c_string_encoding=utf8
import os
import json
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
cdef bint HAVE_PILLOW = False
try:
    from PIL import Image
    HAVE_PILLOW = True
except (ImportError, ModuleNotFoundError):
    pass

from libcpp.string cimport string
from libcpp.vector cimport vector
from cpython.bytes cimport PyBytes_FromStringAndSize
from pysam.libcalignedsegment cimport AlignedSegment

__all__ = ["Gw", "GwPalette"]


class GwPalette:
    """
    Paint types for GW visualisation elements.

    This class provides constants for all color and paint types
    used in GW visualisations. Use these constants with the
    set_paint_ARGB method to customize the appearance of GW.
    """

    # Background colors
    BACKGROUND = GwPaint.bgPaint
    """Main background color for the visualisation"""

    BACKGROUND_TILED = GwPaint.bgPaintTiled
    """Tiled background color"""

    BACKGROUND_MENU = GwPaint.bgMenu
    """Menu background color"""

    # Primary read feature colors
    NORMAL_READ = GwPaint.fcNormal
    """Normal read color"""

    DELETION = GwPaint.fcDel
    """Deletion color"""

    DUPLICATION = GwPaint.fcDup
    """Duplication color"""

    INVERSION_FORWARD = GwPaint.fcInvF
    """Forward inversion color"""

    INVERSION_REVERSE = GwPaint.fcInvR
    """Reverse inversion color"""

    TRANSLOCATION = GwPaint.fcTra
    """Translocation color"""

    INSERTION = GwPaint.fcIns
    """Insertion color"""

    SOFT_CLIP = GwPaint.fcSoftClip
    """Soft clip color"""

    # Nucleotide colors
    NUCLEOTIDE_A = GwPaint.fcA
    """Adenine (A) nucleotide color"""

    NUCLEOTIDE_T = GwPaint.fcT
    """Thymine (T) nucleotide color"""

    NUCLEOTIDE_C = GwPaint.fcC
    """Cytosine (C) nucleotide color"""

    NUCLEOTIDE_G = GwPaint.fcG
    """Guanine (G) nucleotide color"""

    NUCLEOTIDE_N = GwPaint.fcN
    """N (any/unknown) nucleotide color"""

    # Coverage and track colors
    COVERAGE = GwPaint.fcCoverage
    """Coverage plot color"""

    TRACK = GwPaint.fcTrack
    """Generic data track color"""

    NORMAL_READ_MQ0 = GwPaint.fcNormal0
    """Map-quality=0 normal read color"""

    DELETION_MQ0 = GwPaint.fcDel0
    """Map-quality=0 deletion color"""

    DUPLICATION_MQ0 = GwPaint.fcDup0
    """Map-quality=0 duplication color"""

    INVERSION_FORWARD_MQ0 = GwPaint.fcInvF0
    """Map-quality=0 forward inversion color"""

    INVERSION_REVERSE_MQ0 = GwPaint.fcInvR0
    """Map-quality=0 reverse inversion color"""

    TRANSLOCATION_MQ0 = GwPaint.fcTra0
    """Map-quality=0 translocation color"""

    SOFT_CLIP_MQ0 = GwPaint.fcSoftClip0
    """Map-quality=0 soft clip color"""

    # BigWig and other special features
    BIGWIG = GwPaint.fcBigWig
    """BigWig track display color"""

    REGION_OF_INTEREST = GwPaint.fcRoi
    """Region of interest highlight color"""

    # Mate-related colors
    MATE_PRIMARY = GwPaint.mate_fc
    """Primary mate pair color"""

    MATE_SECONDARY = GwPaint.mate_fc0
    """Secondary mate pair color"""

    MATE_UNMAPPED = GwPaint.ecMateUnmapped
    """Unmapped mate color"""

    # Edge and line colors
    SPLIT_READ = GwPaint.ecSplit
    """Split read edge color"""

    SELECTED_ELEMENT = GwPaint.ecSelected
    """Selected element highlight color"""

    LINE_JOINS = GwPaint.lcJoins
    """Line color for join connections"""

    LINE_COVERAGE = GwPaint.lcCoverage
    """Line color for coverage plots"""

    LINE_LIGHT_JOINS = GwPaint.lcLightJoins
    """Light line color for join connections"""

    LINE_GTF_JOINS = GwPaint.lcGTFJoins
    """Line color for GTF feature joins"""

    LINE_LABEL = GwPaint.lcLabel
    """Line color for labels"""

    LINE_BRIGHT = GwPaint.lcBright
    """Bright line color for emphasis"""

    # Text colors
    TEXT_DELETION = GwPaint.tcDel
    """Text color for deletion annotations"""

    TEXT_INSERTION = GwPaint.tcIns
    """Text color for insertion annotations"""

    TEXT_LABELS = GwPaint.tcLabels
    """Text color for general labels"""

    TEXT_BACKGROUND = GwPaint.tcBackground
    """Text background color"""

    # Markers and modifications
    MARKERS = GwPaint.fcMarkers
    """Color for genomic markers"""

    METHYLATED_C = GwPaint.fc5mc
    """5-methylcytosine (5mC) color for epigenetic modification"""

    HYDROXYMETHYLATED_C = GwPaint.fc5hmc
    """5-hydroxymethylcytosine (5hmC) color for epigenetic modification"""

    OTHER_MODIFICATION = GwPaint.fcOther
    """Color for other base modifications"""


cdef class Gw:
    """
    Python interface to GW, a high-performance interactive genome browser.

    GW enables rapid visualisation of aligned sequencing reads, data tracks,
    and genome-variation datasets. This wrapper provides access to libgw.

    Parameters
    ----------
    reference : str
        Path to reference genome file
    **kwargs : dict, optional
            Additional parameters to configure the browser
    """
    def __cinit__(self, reference: str, **kwargs: Any) -> None:
        """Initialise the C++ GwPlot object with minimal required parameters."""

        cdef vector[string] bampaths, track_paths
        cdef vector[Region] regions

        # Initialise with defaults
        cdef IniOptions iopts
        iopts.threads = 1
        iopts.theme.setAlphas()
        cdef string theme = string(b"dark")
        iopts.setTheme(theme)
        tmp = bytes(reference.encode("utf-8"))
        cdef string tag = string(tmp)
        if not os.path.exists(reference): # Try and use genome_tag
            online = self.onlineGenomeTags()
            if reference.lower() in online:
                iopts.genome_tag = tag
                reference = online[reference.lower()]
            else:
                raise FileNotFoundError("Reference genome path or tag not understood")

        ref = reference.encode("utf-8")

        # Create the C++ object
        self.thisptr = new GwPlot(ref, bampaths, iopts, regions, track_paths)
        self.thisptr.drawToBackWindow = <bint> True
        self.thisptr.redraw = <bint> True
        self.thisptr.terminalOutput = <bint> False
        self.raster_surface_created = False
        self.thisptr.opts.theme.setAlphas()
        if not iopts.genome_tag.empty():
            self.thisptr.loadIdeogramTag()

    def __init__(self, reference: str, **kwargs: Any) -> None:
        """
        Python-level initialisation for the GW object with flexible parameters.

        Parameters
        ----------
        reference : str
            Path to reference genome file
        **kwargs : dict, optional
            Additional parameters to configure the browser

        Examples
        --------
        >>> # Initialise with multiple options
        >>> gw = Gw("reference.fa", theme="dark", threads=4,
        ...         sv_arcs=True, canvas_width=800, canvas_height=600)
        """
        # Process kwargs using the appropriate setters
        for key, value in kwargs.items():
            setter_name = f"set_{key}"
            adder_name = f"add_{key}"
            if hasattr(self, setter_name):
                setter = getattr(self, setter_name)
                try:
                    setter(value)
                except Exception as e:
                    raise ValueError(f"Error setting {key}={value}: {str(e)}")
            elif hasattr(self, adder_name):
                adder = getattr(self, adder_name)
                if isinstance(value, tuple):
                    try:
                        adder(*value)
                    except Exception as e:
                        raise ValueError(f"Error setting {key}={value}: {str(e)}")
                else:
                    try:
                        adder(value)
                    except Exception as e:
                        raise ValueError(f"Error setting {key}={value}: {str(e)}")
            else:
                raise ValueError(f"Unknown parameter: {key}")
        self.thisptr.opts.theme.setAlphas()

    def __repr__(self) -> str:
        """
        Return a string representation of the Gw object.

        This representation shows key attributes of the object and
        approximates the constructor call needed to recreate it.
        """
        try:
            genome_tag = self.thisptr.opts.genome_tag
            ref_tag = genome_tag if not genome_tag.empty() else "<reference>"
            return (f"Gw(reference='{ref_tag}', "
                    f"canvas_width={self.canvas_width}, "
                    f"canvas_height={self.canvas_height}, "
                    f"theme='{self.theme}', "
                    f"threads={self.threads})")
        except Exception as e:
            return f"Gw(<error: {str(e)}>)"

    def __enter__(self) -> 'Gw':
        """
        Enter the runtime context for the Gw object.

        This allows using the Gw instance in a 'with' statement.

        Returns
        -------
        Gw
            Self reference for context management

        Examples
        --------
        >>> with Gw("reference.fa") as gw:
        ...     gw.add_bam("sample.bam")
        ...     gw.add_region("chr1", 1000000, 1100000)
        ... # Resources automatically cleaned up when exiting the with block
        """
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """
        Exit the runtime context for the Gw object.

        This handles cleanup of resources when exiting a 'with' statement.

        Parameters
        ----------
        exc_type : type
            Exception type, if an exception occurred
        exc_val : Exception
            Exception instance, if an exception occurred
        exc_tb : traceback
            Exception traceback, if an exception occurred
        """
        pass  # Taken care of in the c++ layer

    @staticmethod
    def onlineGenomeTags() -> Dict[str, str]:
        """
        A dict of online reference genome paths

        Returns
        -------
        dict
            Keys are genome-tag, values are genome-path
        """
        base = "https://github.com/kcleal/ref_genomes/releases/download/v0.1.0"
        return {
            "ce11": f"{base}/ce11.fa.gz",
            "danrer11": f"{base}/danRer11.fa.gz",
            "dm6": f"{base}/dm6.fa.gz",
            "hg19": f"{base}/hg19.fa.gz",
            "hg38": f"{base}/hg38.fa.gz",
            "grch37": f"{base}/Homo_sapiens.GRCh37.dna.toplevel.fa.gz",
            "grch38": f"{base}/Homo_sapiens.GRCh38.dna.toplevel.fa.gz",
            "t2t": f"{base}/hs1.fa.gz",
            "mm39": f"{base}/mm39.fa.gz",
            "pantro6": f"{base}/panTro6.fa.gz",
            "saccer3": f"{base}/sacCer3.fa.gz"
        }

    def glfw_init(self) -> 'Gw':
        """
        Initialise GLFW backend.

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.initBack(self.canvas_width, self.canvas_height)
        return self

    #todo reset_to_defaults function

    def flush_log(self) -> str:
        """
        Returns and clears the GW log.

        Returns
        -------
        string
            GW log as a python string
        """
        cdef string s = self.thisptr.flushLog()
        return str(s)

    @property
    def clear_buffer(self) -> bool:
        """
        Whether the read buffer should be cleared on the next draw.

        Returns
        -------
        bool
            Read buffer needs clearing
        """
        return not self.thisptr.processed

    def set_clear_buffer(self, state: bool) -> None:
        """
        Set the clear_buffer status
        """
        self.thisptr.processed = not state

    @property
    def redraw(self) -> bool:
        """
        Whether a re-draw needs to occur. Check this after some event e.g. command or mouse button.

        Returns
        -------
        bool
            Image needs to be re-drawn
        """
        return self.thisptr.redraw

    def set_redraw(self, state: bool) -> None:
        """
        Set the redraw status. For dynamic applications, set this to False after a drawing call
        """
        self.thisptr.redraw = state

    def mouse_event(self, x_pos: float, y_pos: float, button: int, action: int) -> None:
        """
        Parameters
        ----------
        x_pos : int
            Mouse x-position
        y_pos : int
            Mouse y-position
        button : str
            "left", "right"
        """
        self.thisptr.xPos_fb = x_pos
        self.thisptr.yPos_fb = y_pos
        self.thisptr.mouseButton(button, action, 0)


    @property
    def canvas_width(self) -> int:
        """
        Get the current canvas width in pixels.

        Returns
        -------
        int
            Canvas width
        """
        return self.thisptr.opts.dimensions.x

    def set_canvas_width(self, width: int) -> 'Gw':
        """
        Set the canvas width and recreate the raster surface.

        Parameters
        ----------
        width : int
            New canvas width in pixels

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.fb_width = width
        self.thisptr.opts.dimensions.x = width
        self.thisptr.makeRasterSurface()
        return self

    @property
    def canvas_height(self) -> int:
        """
        Get the current canvas height in pixels.

        Returns
        -------
        int
            Canvas height
        """
        return self.thisptr.opts.dimensions.y

    def set_canvas_height(self, height: int) -> 'Gw':
        """
        Set the canvas height and recreate the raster surface.

        Parameters
        ----------
        height : int
            New canvas height in pixels

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.fb_height = height
        self.thisptr.opts.dimensions.y = height
        self.thisptr.makeRasterSurface()
        return self

    @property
    def canvas_size(self) -> Tuple[int, int]:
        """
        Get the current canvas dimensions.

        Returns
        -------
        tuple
            (width, height) in pixels
        """
        return self.thisptr.opts.dimensions.x, self.thisptr.opts.dimensions.y

    def set_canvas_size(self, width: int, height: int) -> 'Gw':
        """
        Set both canvas width and height and recreate the raster surface.

        Parameters
        ----------
        width : int
            New canvas width in pixels
        height : int
            New canvas height in pixels

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.fb_width = width
        self.thisptr.opts.dimensions.x = width
        self.thisptr.fb_height = height
        self.thisptr.opts.dimensions.y = height
        self.thisptr.makeRasterSurface()
        return self

    @property
    def font_size(self) -> int:
        """
        Get the current font size.

        Returns
        -------
        int
            Font size
        """
        return self.thisptr.opts.font_size

    def set_font_size(self, size: int) -> 'Gw':
        """
        Set the font size.

        Parameters
        ----------
        size : int
            Sets the font size

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.font_size = size
        self.thisptr.fonts.setTypeface(self.thisptr.opts.font_str, size)
        self.thisptr.fonts.setOverlayHeight(1)
        self.thisptr.setScaling()
        return self

    @property
    def font_name(self) -> str:
        """
        Get the current font name.

        Returns
        -------
        int
            Font size
        """
        return self.thisptr.opts.font_str

    def set_font_name(self, name: str) -> 'Gw':
        """
        Set the font name.

        Parameters
        ----------
        name : str
            Sets the font name

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.font_str = name.encode('utf-8')
        self.thisptr.fonts.setTypeface(self.thisptr.opts.font_str, self.thisptr.opts.font_size)
        return self

    @property
    def theme(self) -> str:
        """
        Get the current theme name.

        Returns
        -------
        str
            Current theme name ("slate", "dark", or "igv")
        """
        return self.thisptr.opts.theme.name

    def set_theme(self, theme_name: str) -> 'Gw':
        """
        Set a predefined visualisation theme.

        Parameters
        ----------
        theme_name : str
            Theme name, must be one of "slate", "dark", or "igv"

        Returns
        -------
        Gw
            Self for method chaining

        Raises
        ------
        ValueError
            If theme_name is not one of the supported themes
        """
        if theme_name not in ("slate", "dark", "igv"):
            raise ValueError("Theme must be one of slate, dark, igv")
        self.thisptr.opts.setTheme(theme_name)
        self.thisptr.opts.theme.setAlphas()
        return self

    def apply_theme(self, theme_dict: Dict[int, Tuple[int, int, int, int]]) -> 'Gw':
        """
        Apply a custom theme using a dictionary of paint types and colors.

        Parameters
        ----------
        theme_dict : dict
            Dictionary mapping Paint constants to ARGB tuples (alpha, red, green, blue)

        Returns
        -------
        Gw
            Self for method chaining

        Examples
        --------
        >>> custom_theme = {
        ...     GwPalette.BACKGROUND: (255, 240, 240, 240),
        ...     GwPalette.NORMAL_READ: (255, 100, 100, 100),
        ...     GwPalette.DELETION: (255, 255, 0, 0)
        ... }
        >>> gw.apply_theme(custom_theme)
        """
        for paint_type, color in theme_dict.items():
            a, r, g, b = color
            self.set_paint_ARBG(paint_type, a, r, g, b)
        return self

    def load_theme_from_json(self, filepath: str) -> 'Gw':
        """
        Load and apply a theme from a JSON file.

        Parameters
        ----------
        filepath : str
            Path to the JSON theme file

        Returns
        -------
        Gw
            Self for method chaining

        Raises
        -------
        ValueError
            If the color name is not recognised


        Examples
        --------
        Create a JSON theme file (example: 'custom_theme.json'):

        ```json
        {
            "BACKGROUND": [255, 30, 30, 35],
            "NORMAL_READ": [255, 180, 180, 180],
            "DELETION": [255, 230, 50, 50],
            "DUPLICATION": [255, 50, 180, 50],
            "NUCLEOTIDE_A": [255, 50, 220, 50],
            "NUCLEOTIDE_T": [255, 220, 50, 50],
            "NUCLEOTIDE_G": [255, 50, 50, 220],
            "NUCLEOTIDE_C": [255, 220, 220, 50],
            "COVERAGE": [255, 100, 170, 230]
        }
        ```

        Then load it in your code:
        >>> gw = Gw("reference.fa")
        >>> gw.load_theme_from_json("custom_theme.json")
        >>> gw.add_bam("sample.bam")

        Note: Each color is specified as an ARGB array [alpha, red, green, blue]
        with values from 0-255.
        """

        # Get a mapping from string names to Paint constants
        paint_by_name = {name: getattr(GwPalette, name) for name in dir(GwPalette)
                         if not name.startswith('_') and name.isupper()}
        with open(filepath, 'r') as f:
            theme_data = json.load(f)
        theme_dict = {}
        for paint_name, color in theme_data.items():
            if paint_name not in paint_by_name:
                raise ValueError(f"Unknown paint type '{paint_name}'")
            a, r, g, b = color
            theme_dict[paint_by_name[paint_name]] = (a, r, g, b)

        return self.apply_theme(theme_dict)

    def save_theme_to_json(self, filepath: str) -> 'Gw':
        """
        Save the current theme settings to a JSON file.

        This function exports all paint colors from the current theme
        to a JSON file that can later be loaded with load_theme_from_json.

        Parameters
        ----------
        filepath : str
            Path where the JSON theme file should be saved

        Returns
        -------
        Gw
            Self for method chaining

        Examples
        --------
        >>> gw = Gw("reference.fa", theme="dark")
        >>> # Customize some colors
        >>> gw.set_paint_ARBG(GwPalette.DELETION, 255, 255, 0, 0)
        >>> gw.set_paint_ARBG(GwPalette.NUCLEOTIDE_A, 255, 0, 220, 0)
        >>> # Save the customized theme
        >>> gw.save_theme_to_json("my_custom_theme.json")

        The resulting JSON file can be shared and loaded in other sessions:
        >>> new_gw = Gw("reference.fa")
        >>> new_gw.load_theme_from_json("my_custom_theme.json")
        """
        import json
        paint_constants = {name: getattr(GwPalette, name) for name in dir(GwPalette)
                           if not name.startswith('_') and name.isupper()
                           and not callable(getattr(GwPalette, name))}
        paint_names = {value: name for name, value in paint_constants.items()}
        theme_data = {}

        # Get color values for each paint type
        cdef int a, r, g, b;
        a = 0; r = 0; g = 0; b = 0
        for paint_value, paint_name in paint_names.items():
            self.thisptr.opts.theme.getPaintARGB(paint_value, a, r, b, b)
            theme_data[paint_name] = [a, r, g, b]

        # Write the theme to a JSON file
        with open(filepath, 'w') as f:
            json.dump(theme_data, f, indent=2)

        return self

    @property
    def threads(self) -> int:
        """
        Get the number of threads used for processing.

        Returns
        -------
        int
            Number of threads
        """
        return self.thisptr.opts.threads

    def set_threads(self, threads: int) -> 'Gw':
        """
        Set the number of threads for data processing.

        Parameters
        ----------
        threads : int
            Number of threads to use

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.threads = threads # if threads > 1 else 1
        return self

    @property
    def indel_length(self) -> int:
        """
        Get the current indel length setting.

        Returns
        -------
        int
            Current indel length threshold
        """
        return self.thisptr.opts.indel_length

    def set_indel_length(self, indel_length: int) -> 'Gw':
        """
        Set the indel length threshold for visualisation. Indels with length greater than
        this threshold will be labelled with text.

        Parameters
        ----------
        indel_length : int
            New indel length threshold

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.indel_length = indel_length
        return self

    @property
    def ylim(self) -> float:
        """
        Get the current y-axis limit.

        Returns
        -------
        float
            Current y-axis limit
        """
        return self.thisptr.opts.ylim

    def set_ylim(self, ylim: int) -> 'Gw':
        """
        Set the y-axis limit for visualisation.

        Parameters
        ----------
        ylim : float
            New y-axis limit

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.ylim = ylim
        return self

    @property
    def split_view_size(self) -> int:
        """
        Get the current split view size.

        Returns
        -------
        int
            Current split view size
        """
        return self.thisptr.opts.split_view_size

    def set_split_view_size(self, split_view_size: int) -> 'Gw':
        """
        Set the split view size for multi-region visualisation.

        Parameters
        ----------
        split_view_size : int
            New split view size

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.split_view_size = split_view_size
        return self

    @property
    def pad(self) -> int:
        """
        Get the current padding value.

        Returns
        -------
        int
            Current padding value
        """
        return self.thisptr.opts.pad

    def set_pad(self, pad: int) -> 'Gw':
        """
        Set the padding between elements in visualisation.

        Parameters
        ----------
        pad : int
            New padding value

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.pad = pad
        return self

    @property
    def max_coverage(self) -> int:
        """
        The maximum coverage for calculating coverage track.
        Note, se ylim to set the display coverage value.

        Returns
        -------
        int
            Current maximum coverage value
        """
        return self.thisptr.opts.max_coverage

    def set_max_coverage(self, max_coverage: int) -> 'Gw':
        """
        Get the maximum coverage for calculating coverage track.
        Note, se ylim to set the display coverage value.

        Parameters
        ----------
        max_coverage : int
            New maximum coverage value

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.max_coverage = max_coverage
        return self

    @property
    def max_tlen(self) -> int:
        """
        Get the maximum template length scale when using tlen-y mode.

        Returns
        -------
        int
            Current maximum template length
        """
        return self.thisptr.opts.max_tlen

    def set_max_tlen(self, max_tlen: int) -> 'Gw':
        """
        Set the maximum template length tlen-y mode for paired reads.

        Parameters
        ----------
        max_tlen : int
            New maximum template length

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.max_tlen = max_tlen
        return self

    @property
    def log2_cov(self) -> bool:
        """
        Get the log2 coverage display setting.

        Returns
        -------
        bool
            True if log2 coverage display is enabled
        """
        return self.thisptr.opts.log2_cov

    def set_log2_cov(self, log2_cov: bool) -> 'Gw':
        """
        Set whether to use log2 scale for coverage display.

        Parameters
        ----------
        log2_cov : bool
            True to enable log2 coverage display

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.log2_cov = log2_cov
        return self

    @property
    def tlen_yscale(self) -> bool:
        """
        Get the template length y-scale factor.

        Returns
        -------
        float
            Current template length y-scale factor
        """
        return self.thisptr.opts.tlen_yscale

    def set_tlen_yscale(self, tlen_yscale: bool) -> 'Gw':
        """
        Set the scaling factor for template length on the y-axis.

        Parameters
        ----------
        tlen_yscale : float
            New template length y-scale factor

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.tlen_yscale = <bint>tlen_yscale
        return self

    @property
    def expand_tracks(self) -> bool:
        """
        Get the expand tracks setting.

        Returns
        -------
        bool
            True if tracks are expanded
        """
        return self.thisptr.opts.expand_tracks

    def set_expand_tracks(self, expand_tracks: bool) -> 'Gw':
        """
        Set whether to expand data tracks in the visualisation.

        Parameters
        ----------
        expand_tracks : bool
            True to expand tracks, False to collapse

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.expand_tracks = expand_tracks
        return self

    @property
    def vcf_as_tracks(self) -> bool:
        """
        Get the VCF as tracks setting.

        Returns
        -------
        bool
            True if VCF files are displayed as tracks
        """
        return self.thisptr.opts.vcf_as_tracks

    def set_vcf_as_tracks(self, vcf_as_tracks: bool) -> 'Gw':
        """
        Set whether to display VCF files as tracks.

        Parameters
        ----------
        vcf_as_tracks : bool
            True to display VCF files as tracks

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.vcf_as_tracks = vcf_as_tracks
        return self

    @property
    def sv_arcs(self) -> bool:
        """
        Get the structural variant arcs display setting.

        Returns
        -------
        bool
            True if structural variant arcs are displayed
        """
        return self.thisptr.opts.sv_arcs

    def set_sv_arcs(self, sv_arcs: bool) -> 'Gw':
        """
        Set whether to display structural variants as arcs.

        Parameters
        ----------
        sv_arcs : bool
            True to display structural variants as arcs

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.sv_arcs = sv_arcs
        return self

    @property
    def scroll_speed(self) -> float:
        """
        Get the scroll speed value.

        Returns
        -------
        float
            Current scroll speed
        """
        return self.thisptr.opts.scroll_speed

    def set_scroll_speed(self, scroll_speed: float) -> 'Gw':
        """
        Set the scroll speed for navigation.

        Parameters
        ----------
        scroll_speed : float
            New scroll speed value

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.scroll_speed = scroll_speed
        return self

    @property
    def tab_track_height(self) -> float:
        """
        Get the height of track tabs.

        Returns
        -------
        int
            Current track tab height
        """
        return self.thisptr.opts.tab_track_height

    def set_tab_track_height(self, tab_track_height: float) -> 'Gw':
        """
        Set the height of track tabs in the visualisation.

        Parameters
        ----------
        tab_track_height : int
            New track tab height

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.tab_track_height = tab_track_height
        return self

    @property
    def start_index(self) -> int:
        """
        Get the start index in the file when viewing tiled images.

        Returns
        -------
        int
            Current start index
        """
        return self.thisptr.opts.start_index

    def set_start_index(self, start_index: int) -> 'Gw':
        """
        Set the start index for genome coordinates (0 or 1-based).

        Parameters
        ----------
        start_index : int
            Start index (0 or 1)

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.start_index = start_index
        return self

    @property
    def soft_clip_threshold(self) -> int:
        """
        Get the soft clip threshold (in base-pairs).

        Returns
        -------
        int
            Current soft clip threshold
        """
        return self.thisptr.opts.soft_clip_threshold

    def set_soft_clip_threshold(self, soft_clip_threshold: int) -> 'Gw':
        """
        Set the threshold for highlighting soft-clipped reads (in base-pairs).

        Parameters
        ----------
        soft_clip_threshold : int
            New soft clip threshold

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.soft_clip_threshold = soft_clip_threshold
        return self

    @property
    def small_indel_threshold(self) -> int:
        """
        Get the small indel threshold (in base-pairs).

        Returns
        -------
        int
            Current small indel threshold
        """
        return self.thisptr.opts.small_indel_threshold

    def set_small_indel_threshold(self, small_indel_threshold: int) -> 'Gw':
        """
        Set the threshold for classifying small indels (in base-pairs).

        Parameters
        ----------
        small_indel_threshold : int
            New small indel threshold

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.small_indel_threshold = small_indel_threshold
        return self

    @property
    def snp_threshold(self) -> int:
        """
        Get the SNP threshold (in base-pairs).

        Returns
        -------
        int
            Current SNP threshold
        """
        return self.thisptr.opts.snp_threshold

    def set_snp_threshold(self, snp_threshold: int) -> 'Gw':
        """
        Set the threshold for SNP display and highlighting (in base-pairs).

        Parameters
        ----------
        snp_threshold : int
            New SNP threshold

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.snp_threshold = snp_threshold
        return self

    @property
    def variant_distance(self) -> int:
        """
        Get the variant distance threshold (in base-pairs). When fetching data from
        indexed tracks this threshold determines how much padding is added to each side.

        Returns
        -------
        int
            Current variant distance threshold
        """
        return self.thisptr.opts.variant_distance

    def set_variant_distance(self, variant_distance: int) -> 'Gw':
        """
        Set the variant distance threshold (in base-pairs). When fetching data from
        indexed tracks this threshold determines how much padding is added to each side.

        Parameters
        ----------
        variant_distance : int
            New variant distance threshold

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.variant_distance = variant_distance
        return self

    @property
    def low_memory(self) -> int:
        """
        Get the low memory mode distance setting.

        Returns
        -------
        int
            The region size at which low_memory mode is enabled
        """
        return self.thisptr.opts.low_memory

    def set_low_memory(self, low_memory: int) -> 'Gw':
        """
        Set the distance threshold - regions larger than this threshold will be drawn using
        low_memory mode, and no reads will be held in memory.

        Parameters
        ----------
        low_memory : int
            Region size to enable low_memory mode

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.low_memory = low_memory
        return self

    def set_image_number(self, x: int, y: int) -> 'Gw':
        """
        Set the grid dimensions for image view.

        Parameters
        ----------
        x : int
            Number of columns in the grid
        y : int
            Number of rows in the grid

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.opts.number.x = x
        self.thisptr.opts.number.y = y
        return self

    def set_paint_ARBG(self, paint_enum: int, a: int, r: int, g: int, b: int) -> 'Gw':
        """
        Set the ARGB color for a specific paint type.

        Parameters
        ----------
        paint_enum : int
            Paint type enumeration value from GwPalette enum or Paint class
            (e.g., GwPalette.NORMAL_READ, GwPalette.DELETION)
        a : int
            Alpha channel value (0-255)
        r : int
            Red channel value (0-255)
        g : int
            Green channel value (0-255)
        b : int
            Blue channel value (0-255)

        Returns
        -------
        Gw
            Self for method chaining

        Example
        -------
        >>> # Set normal read color to dark blue
        >>> gw.set_paint_ARBG(GwPalette.NORMAL_READ, 255, 0, 0, 128)
        """
        self.thisptr.opts.theme.setPaintARGB(paint_enum, a, r, g, b)
        return self

    def set_active_region_index(self, index: int) -> 'Gw':
        """
        Set the currently active region for visualisation.

        Parameters
        ----------
        index : int
            Index of the region to activate

        Returns
        -------
        Gw
            Self for method chaining
        """
        if index < <int>self.thisptr.regions.size():
            self.regionSelection = index
        return self

    def clear_alignments(self) -> None:
        """
        Remove all loaded alignment data.
        """
        self.thisptr.clearCollections()
        self.force_buffered_reads = <bint>False

    def clear_regions(self) -> None:
        """
        Remove all defined genomic regions.
        """
        cdef size_t i
        for i in range(self.thisptr.regions.size()):
            self.remove_region(i)

    def clear(self) -> None:  #todo this is incomplete: tracks, variant files
        """
        Remove all data.
        """
        self.clear_alignments()
        self.clear_regions()

    def add_bam(self, path: str) -> 'Gw':
        """
        Add a BAM file to the visualisation.

        Parameters
        ----------
        path : str
            Path to the BAM file

        Returns
        -------
        Gw
            Self for method chaining
        """
        cdef string b
        b = path.encode("utf-8")
        self.thisptr.addBam(b)
        return self

    def add_pysam_alignments(self, pysam_alignments: List['AlignedSegment'],
                            region_index: int = -1,
                            bam_index: int = -1) -> 'Gw':
        """
        Adds alignments from a pysam list to a region. Creates a raster surface if needed. Calls clear_alignments
        if non-pysam collections in use

        Parameters
        ----------
        pysam_alignment_list : list
            List of pysam AlignedSegments
        region_index: int, optional
            The region index to draw to for multi-region support. If -1, the last added region will be used
        bam_index: int, optional
            The bam index to draw to for multi-region support. If -1, the last added bam will be used

        Returns
        -------
        Gw
            Self for method chaining

        Raises
        ------
        IndexError
            If the region_index or bam_index are out of range
        UserWarning
            If any normal collections are already present in the Gw object
        """

        if not self.raster_surface_created:
            self.make_raster_surface()
        cdef bint needs_clearing = <bint>False
        for i in range(self.thisptr.collections.size()):
            if not self.thisptr.collections[i].ownsBamPtrs:
                needs_clearing = <bint>True
                break
        if needs_clearing:
            self.clear_alignments()
            raise UserWarning("Can not mix pysam collections with normal collections. Current collections have been cleared")

        if self.thisptr.sizeOfBams() == 0:
            raise IndexError("Add a bam/cram file first")
        if self.thisptr.sizeOfRegions() == 0:
            raise IndexError("Add a region first")

        self.force_buffered_reads = <bint>True

        cdef int regionIdx
        cdef int bamIdx
        if region_index < 0:
            regionIdx = self.thisptr.sizeOfRegions() - 1
        else:
            regionIdx = region_index
            assert regionIdx < <int>self.thisptr.sizeOfRegions()
        if bam_index < 0:
            bamIdx = self.thisptr.sizeOfBams() - 1
        else:
            bamIdx = bam_index
            assert bamIdx < <int>self.thisptr.sizeOfBams()

        cdef uint32_t start = <uint32_t> self.thisptr.regions[regionIdx].start
        cdef uint32_t end = <uint32_t> self.thisptr.regions[regionIdx].end

        self.thisptr.collections.push_back(ReadCollection())
        self.thisptr.collections.back().region = &self.thisptr.regions[regionIdx]
        self.thisptr.collections.back().ownsBamPtrs = <bint>False
        if self.thisptr.opts.max_coverage > 0:
            self.thisptr.collections.back().covArr.resize(end - start + 1)
        if self.thisptr.opts.snp_threshold > <int>(end - start):
            self.thisptr.collections.back().makeEmptyMMArray()

        self.thisptr.collections.back().regionIdx = regionIdx
        self.thisptr.collections.back().bamIdx = bamIdx

        cdef bam1_t* bam_ptr
        cdef AlignedSegment read
        cdef vector[Align]* readQueue = &self.thisptr.collections.back().readQueue

        for read in pysam_alignments:
            bam_ptr = <bam1_t* >read._delegate
            if bam_ptr[0].core.flag & 4 or bam_ptr[0].core.n_cigar == 0:
                continue
            readQueue[0].push_back(Align(bam_ptr))
            align_init(&readQueue[0].back(), <bint>True)  # todo set parse_mods
            if self.thisptr.opts.max_coverage > 0:
                addToCovArray(self.thisptr.collections.back().covArr, readQueue[0].back(), start, end)

        # todo sortReadsBy
        cdef int maxY = findY(self.thisptr.collections.back(), readQueue[0], self.thisptr.opts.link_op,
                              self.thisptr.opts, <bint>False, 0)

        self.thisptr.samMaxY = max(maxY, self.thisptr.samMaxY)
        self.thisptr.processed = <bint>True

        return self

    def remove_bam(self, index: int) -> 'Gw':
        """
        Remove a BAM file from the visualisation.

        Parameters
        ----------
        index : int
            Index of the BAM file to remove

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.removeBam(index)
        return self

    def add_track(self, path: str, vcf_as_track: bool = True,
                 bed_as_track: bool = True) -> 'Gw':
        """
        Add a genomic data track to the visualisation.

        Parameters
        ----------
        path : str
            Path to the track file (VCF, BED, etc.)
        vcf_as_track : bool, optional
            Whether to display VCF files as tracks
        bed_as_track : bool, optional
            Whether to display BED files as tracks

        Returns
        -------
        Gw
            Self for method chaining
        """
        cdef string b
        b = path.encode("utf-8")
        self.thisptr.addTrack(b, <bint>False, vcf_as_track, bed_as_track)
        return self

    def remove_track(self, index: int) -> 'Gw':
        """
        Remove a data track from the visualisation.

        Parameters
        ----------
        index : int
            Index of the track to remove

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.removeTrack(index)
        return self

    def add_region(self, chrom: str, start: int, end: int,
                  marker_start: int = -1,
                  marker_end: int = -1) -> 'Gw':
        """
        Add a genomic region for visualisation.

        Parameters
        ----------
        chrom : str
            Chromosome name
        start : int
            Start position
        end : int
            End position
        marker_start : int, optional
            Start position for a marker, -1 for no marker
        marker_end : int, optional
            End position for a marker, -1 for no marker

        Returns
        -------
        Gw
            Self for method chaining
        """
        cdef string c = chrom.encode("utf-8")
        self.thisptr.regions.push_back(Region())
        self.thisptr.regions.back().chrom = c
        self.thisptr.regions.back().start = start
        self.thisptr.regions.back().end = end
        self.thisptr.regions.back().markerPos = marker_start
        self.thisptr.regions.back().markerPosEnd = marker_end
        self.thisptr.fetchRefSeq(self.thisptr.regions.back())
        self.thisptr.regionSelection = <int>self.thisptr.regions.size() - 1
        self.thisptr.resetCollectionRegionPtrs()
        return self

    def remove_region(self, index: int) -> 'Gw':
        """
        Remove a genomic region from the visualisation.

        Parameters
        ----------
        index : int
            Index of the region to remove

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.thisptr.removeRegion(index)
        return self

    def apply_command(self, command: str) -> None:
        """
        Apply a GW command string.

        Parameters
        ----------
        command : str
            GW command to execute (e.g., "filter", "count", etc.)

        """
        cdef string c = command.encode("utf-8")
        self.thisptr.inputText = c
        self.thisptr.commandProcessed()

    def key_press(self, key: int, scancode: int, action: int, mods: int) -> None:
        """
        Process a key press event.

        Parameters
        ----------
        key : int
            Key code
        scancode : int
            Scan code
        action : int
            Key action code
        mods : int
            Modifier keys
        """
        self.thisptr.keyPress(key, scancode, action, mods)
    #todo
    # scroll_left, scroll_right, zoom_out, zoom_in
    # click screen
    def make_raster_surface(self, width: int = -1, height: int = -1) -> 'Gw':
        """
        Create a raster surface for rendering.

        Parameters
        ----------
        width : int, optional
            Width of the raster surface
        height : int, optional
            Height of the raster surface

        Returns
        -------
        Gw
            Self for method chaining

        Raises
        ------
        RuntimeError
            If the raster surface could not be created
        """
        if width > 0:
            self.thisptr.opts.dimensions.x = width
        if height > 0:
            self.thisptr.opts.dimensions.y = height
        self.thisptr.setImageSize(self.thisptr.opts.dimensions.x, self.thisptr.opts.dimensions.y)
        size = self.thisptr.makeRasterSurface()
        if size == 0:
            raise RuntimeError("Could not create raster image. Size was 0")
        self.raster_surface_created = True
        return self

    def save_png(self, path: str) -> 'Gw':
        """
        Draws and saves the raster canvas to a PNG file.

        Parameters
        ----------
        path : str
            Path to save the PNG file

        Returns
        -------
        Gw
            Self for method chaining
        """
        if self.redraw:
            self.draw()
        cdef size_t i
        for i in range(self.thisptr.collections.size()):
            self.thisptr.collections[i].resetDrawState()
        cdef string c = path.encode("utf-8")
        self.thisptr.rasterToPng(c.c_str())
        self.thisptr.redraw = <bint>True  # Don't block further interactions
        return self

    def save_pdf(self, path: str) -> 'Gw':
        """
        Draws and saves a PDF file using the current configuration.

        Parameters
        ----------
        path : str
            Path to save the PDF file

        Returns
        -------
        Gw
            Self for method chaining
        """
        cdef string c = path.encode("utf-8")
        self.thisptr.saveToPdf(c.c_str(), self.force_buffered_reads)
        self.thisptr.redraw = <bint> True  # Don't block further interactions
        return self

    def save_svg(self, path: str) -> 'Gw':
        """
        Saves an SVG file using the current configuration.

        Parameters
        ----------
        path : str
            Path to save the SVG file

        Returns
        -------
        Gw
            Self for method chaining
        """
        cdef string c = path.encode("utf-8")
        self.thisptr.saveToSvg(c.c_str(), self.force_buffered_reads)
        self.thisptr.redraw = <bint> True  # Don't block further interactions
        return self

    def draw(self, clear_buffer: bool = False) -> 'Gw':
        """
        Draw the visualisation to the raster surface. Caches state for using with interactive functions.

        Creates the raster surface if it doesn't exist yet.

        Parameters
        ----------
        clear_buffer : bool
            Clears any buffered reads before re-drawing

        Returns
        -------
        Gw
            Self for method chaining
        """
        if not self.raster_surface_created:
            self.make_raster_surface()
        if clear_buffer:
            self.thisptr.processed = False
        self.thisptr.syncImageCacheQueue()
        self.thisptr.drawScreen(self.force_buffered_reads)
        return self

    def draw_image(self) -> Image.Image:
        """
        Draw the visualisation and return it as a PIL Image.

        Returns
        -------
        PIL.Image
            The visualisation as a PIL Image
        """
        if not HAVE_PILLOW:
            raise ImportError("Pillow could not be imported")
        if not self.raster_surface_created:
            self.make_raster_surface()
        self.draw()
        return Image.fromarray(self.array())

    def show(self) -> None:
        """
        Convineience method for showing the image on screen. Equivalent to gw.draw_image().show()
        """
        if not HAVE_PILLOW:
            raise ImportError("Pillow could not be imported")
        self.draw_image().show()

    def view_region(self, chrom: str, start: int, end: int) -> 'Gw':
        """
        Clear existing regions and view a specific genomic region.

        Parameters
        ----------
        chrom : str
            Chromosome
        start : int
            Region start
        end : int
            Region end

        Returns
        -------
        Gw
            Self for method chaining
        """
        self.clear_regions()
        self.add_region(chrom, start, end)
        return self

    def encode_as_png(self, compression_level: int = 6) -> Optional[bytes]:
        """
        Encode the current canvas as PNG and return the binary data.

        Returns:
            bytes: PNG encoded image data
            or None if the raster surface hasn't been created
        """
        if not self.raster_surface_created:
            return None
        cdef vector[uint8_t]* png_vector = self.thisptr.encodeToPngVector(compression_level)
        if not png_vector[0].empty():
            return PyBytes_FromStringAndSize(<char *> png_vector[0].data(), png_vector[0].size())
        return None

    def encode_as_jpeg(self, quality: int = 80) -> Optional[bytes]:
        """
        Encode the current canvas as JPEG and return the binary data.

        Returns:
            bytes: PNG encoded image data
            or None if the raster surface hasn't been created

        Raises
        ------
        RuntimeError
            If image encoding failed
        """
        if not self.raster_surface_created:
            return None
        cdef vector[uint8_t]* jpeg_vector = self.thisptr.encodeToJpegVector(quality)
        if not jpeg_vector[0].empty():
            return PyBytes_FromStringAndSize(<char *> jpeg_vector[0].data(), jpeg_vector[0].size())
        raise RuntimeError("Encoding image failed, size was 0 bytes")

    @property
    def __array_interface__(self) -> Optional[Dict[str, Any]]:
        """
        Implement the array interface protocol for direct access by Numpy.

        Returns:
            dict: Describes the underlying image buffer
            or None if the raster surface hasn't been created
        """
        if not self.raster_surface_created:
            return None
        cdef char* data_ptr = self.thisptr.pixelMemory.data()
        return {
            'shape': (self.canvas_height, self.canvas_width, 4),
            'typestr': '|u1',  # unsigned char
            'data': (<size_t>data_ptr, False),
            'strides': (self.canvas_width * 4, 4, 1),
            'version': 3
        }

    # def __getbuffer__(self, Py_buffer *buffer, int flags):
    #     """
    #     Implement the buffer protocol for access to pixel data.
    #
    #     This enables using the object with numpy.array().
    #
    #     Parameters
    #     ----------
    #     buffer : Py_buffer*
    #         Buffer to fill
    #     flags : int
    #         Buffer flags
    #     """
    #     print("Called __getbuffer__")
    #     cdef Py_ssize_t itemsize = sizeof(self.thisptr.pixelMemory[0])
    #     self.shape[0] = self.thisptr.pixelMemory.size()
    #     self.strides[0] = sizeof(char)
    #     buffer.buf = &(self.thisptr.pixelMemory[0])  # char *
    #     buffer.format = 'B'
    #     buffer.internal = NULL
    #     buffer.itemsize = itemsize
    #     buffer.len = self.shape[0] * itemsize
    #     buffer.ndim = 1
    #     buffer.obj = self
    #     buffer.readonly = 0
    #     buffer.shape = self.shape
    #     buffer.strides = self.strides
    #     buffer.suboffsets = NULL

    def array(self) -> Optional[np.ndarray]:
        """
        Convert the pixel data to a numpy array using zero-copy interface

        Returns
        -------
        numpy.ndarray or None
            RGBA image data as a 3D numpy array (height × width × 4)
            or None if the raster surface hasn't been created
        """
        if not self.raster_surface_created:
            return None
        #return np.array(self).reshape(self.canvas_height, self.canvas_width, 4)
        return np.asarray(self)

    def __dealloc__(self):
        """ Freeing of Gw is left to the c++ layer"""
        pass