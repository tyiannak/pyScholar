#!/usr/bin/env python
"""
Description:
Command line google scholar metadata analysis and visualisation

Usage Example:


Theodoros Giannakopoulos
tyiannak@gmail.cm
"""

import argparse
import pyscholar


def parse_arguments():
    """!
    @brief Parse Arguments for calmod testing.
    """
    parser = argparse.ArgumentParser(description="search publications")
    parser.add_argument("-c", "--csv", required=True, nargs=None,
                        help="csv file containing the list of publication "
                             "titles")
    parser.add_argument("-o", "--output", required=True, nargs=None,
                        help="output csv file containing number of citations")

    return parser.parse_args()

import time
if __name__ == "__main__":
    args = parse_arguments()
    input_path = args.csv
    output_path = args.output

    with open(input_path) as f:
        lines = f.readlines()

    for pub in lines:
        a = (pyscholar.read_pub_data(pub))
        if 'num_citations' in a:
            print(a['num_citations'])
        else:
            print(0)
        time.sleep(5)