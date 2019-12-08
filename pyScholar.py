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
             "citedby": pub.citedby if hasattr(pub, "citedby") else 0,
             "link": pub.id_citations if hasattr(pub, "id_citations") else ""
             }
            for pub in author.publications]
    }
    return a_data


def generic_info_table(author_data):
    data_list = [[], []]
    data_to_show = ["citedby", "hindex", "i10index"]
    for d in data_to_show:
        if d in author_data:
            data_list[0].append(d)
            data_list[1].append(author_data[d])
    data_list[0].append("#pubs")
    data_list[1].append(len(author_data["pubs"]))

    return data_list


def pubs_table(author_data):
    data_list = [[], [], [], []]
    data_to_show = ["citedby", "title", "year", "link"]
    for d in author_data["pubs"]:
        print(d)
        for ds in data_to_show:
            if ds in d:
                if ds =="link":
                    link_str = "<a href=\"https://scholar.google.com/" \
                               "citations?view_op=view_citation&" \
                               "citation_for_view={0:s}\">link</a>".format(d[ds])
                    data_list[data_to_show.index(ds)].append(link_str)
                else:
                    data_list[data_to_show.index(ds)].append(d[ds])
    print(data_list)
    return data_list


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
        str_titles.append("Info")
        str_titles.append("Citations Per Year")
        str_titles.append("Tag cloud")
        str_titles.append("Paper List")
        specs.append([{"type": "table"},
                      {"type": "scatter"},
                      {"type": "scatter"},
                      {"type": "table"}])

    print(specs)
    figs = plotly.tools.make_subplots(rows=len(data), cols=4,
                                      subplot_titles=str_titles,
                                      specs=specs)

    for ia, a in enumerate(data):
        # plot generic info
        figs.append_trace(go.Table(columnwidth=[20, 100],
                                   header=dict(values=["name<br>aff", data[a]["name"] +
                                                      "<br>" + data[a]["affiliation"]],
                                               line_color='rgb(220, 235, 240)',
                                               fill_color='rgb(220, 235, 240)',
                                               font=dict(size=10),
                                               height=40,
                                               align='left'),
                                   cells=dict(values=generic_info_table(data[a]),
                                              line_color='rgb(200, 215, 220)',
                                              fill_color='rgb(200, 215, 220)',
                                              font=dict(size=10), height=40,
                                              align='left')
                                   ),
                          ia+1, 1)
        # plot citations per year
        figs.append_trace(go.Scatter(x=list(data[a]["cites_per_year"].keys()),
                                     y=list(data[a]["cites_per_year"].values()),
                                     marker=dict(size=10,
                                                 color='rgba(100, 115, '
                                                       '250, 0.9)',),
                                     showlegend=False), ia+1, 2)
        # plot tag cloud
        # TODO

        # plot list of papers
        figs.append_trace(go.Table(columnwidth=[20, 100, 20, 20],
                                   header=dict(values=["citedby", "title",
                                                       "year", "link"],
                                               line_color='rgb(220, 235, 240)',
                                               fill_color='rgb(220, 235, 240)',
                                               font=dict(size=10),
                                               height=40,
                                               align='left'),
                                   cells=dict(values=pubs_table(data[a]),
                                              line_color='rgb(200, 215, 220)',
                                              fill_color='rgb(200, 215, 220)',
                                              font=dict(size=10), height=40,
                                              align='left')
                                   ),
                          ia+1, 4)

    plotly.offline.plot(figs, filename="temp.html", auto_open=True)