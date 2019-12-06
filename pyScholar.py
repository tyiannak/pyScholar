#!/usr/bin/env python
"""
Description:
Command line google scholar metadata analysis and visualisation

Usage Example:


Theodoros Giannakopoulos
tyiannak@gmail.cm
"""

import argparse
import sys
import os


def parse_arguments():
    """!
    @brief Parse Arguments for calmod testing.
    """
    parser = argparse.ArgumentParser(description="Test calmod")
    parser.add_argument("-a", "--authors", required=True, nargs="+",
                        help="list of authors to analyse")
    parser.add_argument("-o", "--output_dir", required=True, nargs=None,
                        help="Output dir")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    authors = args.authors
    print(authors)
