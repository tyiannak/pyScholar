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
import pickle
import os
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


def create_generic_info_table(author_data):
    for a in author_data:
        print(a, author_data[a])


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

    if os.path.isfile('temp.pkl'):
        with open('temp.pkl', 'rb') as f:
            data = pickle.load(f)
    else:
        data = {a: read_author_data(a) for a in authors}
        with open('temp.pkl', 'wb') as f:
            pickle.dump(data, f)
    print(data)

    str_titles, specs = [], []
    for a in data:
        str_titles.append(a + " - Info")
        str_titles.append(a + " - Citations Per Year")
        str_titles.append(a + " - Tag cloud")
        specs.append([{"type": "table"},
             {"type": "scatter"},
             {"type": "scatter"}])

    print(specs)
    figs = plotly.tools.make_subplots(rows=len(data), cols=3,
                                      subplot_titles=str_titles,
                                      specs=specs)

    for ia, a in enumerate(data):
        figs.append_trace(go.Table(header=dict(values=['A Scores', 'B Scores'],
                        line_color='darkslategray',
                        fill_color='lightskyblue',
                        align='left'),
            cells=dict(values=[[100, 90, 80, 90],  # 1st column
                               [95, 85, 75, 95]],  # 2nd column
                       line_color='darkslategray',
                       fill_color='lightcyan',
                       align='left')), ia+1, 1)
        figs.append_trace(go.Scatter(x=list(data[a]["cites_per_year"].keys()),
                                     y=list(data[a]["cites_per_year"].values()),
                                     showlegend=False), ia+1, 2)
    plotly.offline.plot(figs, filename="temp.html", auto_open=True)