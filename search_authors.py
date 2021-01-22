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
import pickle
import os
import plotly
import plotly.graph_objs as go


def parse_arguments():
    """!
    @brief Parse Arguments for calmod testing.
    """
    parser = argparse.ArgumentParser(description="Test calmod")
    parser.add_argument("-a", "--authors", required=True, nargs="+",
                        help="list of authors to analyse")
    parser.add_argument("-o", "--output", required=True, nargs=None,
                        help="Output HTML path")
    parser.add_argument("-t", "--word_cloud_threshold", required=True,
                        nargs=None, type=int, default=5,
                        help="percentage of the less frequent word in "
                             "tag cloud")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    authors = args.authors
    out_file = args.output

    if os.path.isfile('temp.pkl'):
        with open('temp.pkl', 'rb') as f:
            data = pickle.load(f)
    else:
        data = {a: pyscholar.read_author_data(a) for a in authors}
#        UNCOMMENT THIS FOR CACHING:
#        with open('temp.pkl', 'wb') as f:
#            pickle.dump(data, f)

    str_titles, specs = [], []
    for a in data:
        str_titles.append("Info")
        str_titles.append("Tag cloud")
        str_titles.append("Paper List")
        str_titles.append("Citations Per Year")
        str_titles.append("")
        str_titles.append("")

        specs.append([{"type": "table"}, {"type": "scatter", "rowspan": 2},
                      {"type": "table", "rowspan": 2}])
        specs.append([{"type": "scatter"},{},{}]),
    figs = plotly.tools.make_subplots(rows=len(data)*2, cols=3,
                                      subplot_titles=str_titles,
                                      specs=specs)

    for ia, a in enumerate(data):
        # plot generic info
        figs.append_trace(go.Table(columnwidth=[20, 100],
                                   header=dict(values=["name<br>aff",
                                                       data[a]["name"] +
                                                      "<br>" +
                                                       data[a]["affiliation"]],
                                               line_color='rgb(220, 235, 240)',
                                               fill_color='rgb(220, 235, 240)',
                                               font=dict(size=10),
                                               height=40, align='left'),
                                   cells=dict(values=pyscholar.generic_info_table(data[a]),
                                              line_color='rgb(200, 215, 220)',
                                              fill_color='rgb(200, 215, 220)',
                                              font=dict(size=10), height=20,
                                              align='left')),
                          2*ia+1, 1)
        # plot citations per year
        figs.append_trace(go.Scatter(x=list(data[a]["cites_per_year"].keys()),
                                     y=list(data[a]["cites_per_year"].values()),
                                     marker=dict(size=1,
                                                 color='rgb(100, 115, 250)',),
                                     showlegend=False), 2*ia+2, 1)
        # plot tag cloud
        f = pyscholar.wordcloud(data[a], int(args.word_cloud_threshold))
        figs.append_trace(f, 2*ia+1, 2)

        # plot list of papers
        figs.append_trace(go.Table(columnwidth=[20, 100, 20, 20],
                                   header=dict(values=["citedby", "title",
                                                       "year", "link"],
                                               line_color='rgb(220, 235, 240)',
                                               fill_color='rgb(220, 235, 240)',
                                               font=dict(size=10),
                                               height=40,
                                               align='left'),
                                   cells=dict(values=pyscholar.pubs_table(data[a]),
                                              line_color='rgb(200, 215, 220)',
                                              fill_color='rgb(200, 215, 220)',
                                              font=dict(size=10), height=40,
                                              align='left')
                                   ),
                          2*ia+1, 3)
    figs['layout'].update(height=(len(authors) * 500))
    plotly.offline.plot(figs, filename=out_file, auto_open=True)