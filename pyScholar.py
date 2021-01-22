#!/usr/bin/env python
"""
Description:
Command line google scholar metadata analysis and visualisation

Usage Example:


Theodoros Giannakopoulos
tyiannak@gmail.cm
"""

import argparse
from scholarly import scholarly
import pickle
import os
import plotly
import plotly.graph_objs as go
from nltk.corpus import stopwords
from collections import Counter

extra_stop_words = ["using", "approach", "method", "based", "case",
                    "within", "use", "via", "towards", "methods"]

def read_author_data(author_name):
    print("reading data for {0:s}".format(author_name))
    search_query = scholarly.search_author(author_name)
    author = scholarly.fill(next(search_query))

    print(author)
    a_data = {
        "name": author["name"],
        "affiliation": author["affiliation"],
        "cites_per_year": author["cites_per_year"],
        "citedby": author["citedby"],
        "hindex": author["hindex"],
        "i10index": author["i10index"],
        "url_picture": author["url_picture"],
        "pubs": [
            {"title": pub['bib']['title'],
             "year": pub['bib']['pub_year'] if "pub_year" in pub['bib']  else -1,
             "citedby": pub['num_citations'] if "num_citations" in pub else 0,
             "link": pub["id_citations"] if "id_citations" in pub else ""
             }
            for pub in author["publications"]]
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
        for ds in data_to_show:
            if ds in d:
                if ds =="link":
                    link_str = "<a href=\"https://scholar.google.com/" \
                               "citations?view_op=view_citation&" \
                               "citation_for_view=" \
                               "{0:s}\">link</a>".format(d[ds])
                    data_list[data_to_show.index(ds)].append(link_str)
                else:
                    data_list[data_to_show.index(ds)].append(d[ds])
    return data_list


def wordcloud(author_data, per_threshold=3):
    text = ""
    for a in author_data["pubs"]:
        text += (a["title"].lower() + " ")
    word_list = text.split()
    word_list = [word for word in word_list if
                 word not in stopwords.words('english') + extra_stop_words]
    word_counts = (Counter(word_list).most_common())
    word_list, freq_list, position_list, color_list = [], [], [], []
    n_cols = 3
    count_used = 0
    for (w, f) in word_counts:
        per_centage = 100 * f / float(len(author_data["pubs"]))
        if per_centage >= per_threshold:
            word_list.append(w)
            freq_list.append(per_centage)
            position_list.append((count_used % n_cols,
                                  int(count_used / n_cols)))
            count_used += 1
            color_list.append('rgb(20, 10, 50)')
    word_list.append('')
    freq_list.append(0)
    position_list.append((-0.5, 0))
    color_list.append('rgb(20, 10, 50)')
    word_list.append('')
    freq_list.append(0)
    position_list.append((n_cols-0.5, 0))
    color_list.append('rgb(20, 10, 50)')

    x = [p[0] for p in position_list]
    y = [p[1] for p in position_list]
    font_sizes = [f+1 for f in freq_list]
    trace = go.Scatter(x=x, y=y, textfont=dict(size=font_sizes,
                                               color=color_list),
                       hoverinfo='text',
                       hovertext=['{0:s} {1:.1f}%'.format(w, f)
                                  for w, f in zip(word_list, freq_list)],
                       mode='text', text=word_list, showlegend=False)
    return trace


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
        data = {a: read_author_data(a) for a in authors}
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
                                   cells=dict(values=generic_info_table(data[a]),
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
        f = wordcloud(data[a], int(args.word_cloud_threshold))
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
                                   cells=dict(values=pubs_table(data[a]),
                                              line_color='rgb(200, 215, 220)',
                                              fill_color='rgb(200, 215, 220)',
                                              font=dict(size=10), height=40,
                                              align='left')
                                   ),
                          2*ia+1, 3)
    figs['layout'].update(height=(len(authors) * 500))
    plotly.offline.plot(figs, filename=out_file, auto_open=True)