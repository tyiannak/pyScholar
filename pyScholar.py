#!/usr/bin/env python
"""
Description:
Command line google scholar metadata analysis and visualisation

Usage Example:


Theodoros Giannakopoulos
tyiannak@gmail.cm
"""

import argparse
import scholarly
import plotly
import plotly.graph_objs as go


def read_author_data(author_name):
    print("reading data for {0:s}".format(author_name))
    author = next(scholarly.search_author(author_name)).fill()
    a_data = {
        "name": author.name,
        "affiliation": author.affiliation,
        "cites_per_year": author.cites_per_year,
        "citedby": author.citedby,
        "hindex": author.hindex,
        "i10index": author.i10index,
        "url_picture": author.url_picture,
        "pubs": [
            {"title": pub.bib['title'],
             "year": pub.bib['year'] if "year" in pub.bib  else -1,
             "citedby": pub.citedby if hasattr(pub, "citedby") else 0
             }
            for pub in author.publications]
    }
    return a_data


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

    data = {a: read_author_data(a) for a in authors}
    print(data)

    figs = plotly.tools.make_subplots(rows=len(data), cols=3,
                                      subplot_titles=authors)
    for ia, a in enumerate(data):
        figs.append_trace(go.Scatter(x=list(data[a]["cites_per_year"].keys()),
                                     y=list(data[a]["cites_per_year"].values()),
                                     showlegend=False), ia+1, 1)
    plotly.offline.plot(figs, filename="temp.html", auto_open=True)