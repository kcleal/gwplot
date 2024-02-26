
import unittest
import os
import pysam
import time

from libgw import GWplot


root = os.path.abspath(os.path.dirname(__file__))


class TestConstruct(unittest.TestCase):
    """ Test construction and alignment"""

    def test_create(self):
        plot = GWplot("/Users/sbi8kc2/Documents/data/db/hg19/ucsc.hg19.fa")
        print(plot)
        print()
        print()
        print(plot.print_message())

        print("yo", plot.scroll_left)


def main():
    unittest.main()


if __name__ == "__main__":
    unittest.main()