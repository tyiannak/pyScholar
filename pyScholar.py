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
from nltk.corpus import stopwords
from collections import Counter

extra_stop_words = ["using", "approach", "method", "based", "case",
                    "within", "use"]

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
        for ds in data_to_show:
            if ds in d:
                if ds =="link":
                    link_str = "<a href=\"https://scholar.google.com/" \
                               "citations?view_op=view_citation&" \
                               "citation_for_view={0:s}\">link</a>".format(d[ds])
                    data_list[data_to_show.index(ds)].append(link_str)
                else:
                    data_list[data_to_show.index(ds)].append(d[ds])
    return data_list


def wordcloud(author_data):
    text = ""
    for a in author_data["pubs"]:
        text += (a["title"].lower() + " ")
    word_list = text.split()
    word_list = [word for word in word_list if
                 word not in stopwords.words('english') + extra_stop_words]
    word_counts = (Counter(word_list).most_common())
    word_list, freq_list, position_list, color_list = [], [], [], []
    threshold = 5
    n_cols = 3
    count_used = 0
    for (w, f) in word_counts:
        per_centage = 100 * f / float(len(author_data["pubs"]))
        if per_centage >= threshold:
            word_list.append(w)
            freq_list.append(per_centage)
            position_list.append((count_used % n_cols,
                                  int(count_used / n_cols)))
            count_used += 1
            color_list.append('rgb(20, 10, 50)')
    word_list.append('')
    freq_list.append(1)
    position_list.append((-0.5, 0))
    color_list.append('rgb(20, 10, 50)')
    word_list.append('')
    freq_list.append(1)
    position_list.append((n_cols-0.5, 0))
    color_list.append('rgb(20, 10, 50)')

    # create the positions and freqs
    x, y = [], []
    for i in position_list:
        x.append(i[0])
        y.append(i[1])
    freqs = []
    for i in freq_list:
        freqs.append(i + 1)

    trace = go.Scatter(x=x, y=y, textfont=dict(size=freqs, color=color_list),
                       hoverinfo='text',
                       hovertext=['{0}{1}'.format(w, f) for w, f in
                                  zip(word_list, freq_list)],
                       mode='text', text=word_list, showlegend=False)
    return trace


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

    str_titles, specs = [], []
    for a in data:
        str_titles.append("Info")
        str_titles.append("Citations Per Year")
        str_titles.append("Tag cloud")
        str_titles.append("Paper List")
        specs.append([{"type": "table"}, {"type": "scatter"},
                      {"type": "scatter"}, {"type": "table"}])

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
                                               height=40, align='left'),
                                   cells=dict(values=generic_info_table(data[a]),
                                              line_color='rgb(200, 215, 220)',
                                              fill_color='rgb(200, 215, 220)',
                                              font=dict(size=10), height=40,
                                              align='left')),
                          ia+1, 1)
        # plot citations per year
        figs.append_trace(go.Scatter(x=list(data[a]["cites_per_year"].keys()),
                                     y=list(data[a]["cites_per_year"].values()),
                                     marker=dict(size=10,
                                                 color='rgb(100, 115, 250)',),
                                     showlegend=False), ia+1, 2)
        # plot tag cloud
        # TODO
        f = wordcloud(data[a])
        figs.append_trace(f, ia+1,3)

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
#        figs['layout'].update(xaxis4=dict(range=[-5, 10]))

    plotly.offline.plot(figs, filename="temp.html", auto_open=True)