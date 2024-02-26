# cython: c_string_type=unicode, c_string_encoding=utf8

from libcpp.string cimport string
from libcpp.vector cimport vector

cdef class GWplot:
    """Interface to GW"""
    def __init__(self, str reference):
        cdef string ref = reference.encode("utf-8")
        self.opts = IniOptions()
        self.thisptr = new GwPlot(ref, self.__bampaths, self.opts, self.__regions, self.__track_paths)
        print("Constructed!")

    def print_message(self):
        print("Message type: ", self.opts.scroll_left)

    @property
    def scroll_left(self):
        return self.opts.scroll_left