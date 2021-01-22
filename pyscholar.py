#!/usr/bin/env python
"""
Description:
Command line google scholar metadata analysis and visualisation

Usage Example:


Theodoros Giannakopoulos
tyiannak@gmail.cm
"""

from scholarly import scholarly
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
             "year": pub['bib']['pub_year'] if "pub_year" in pub['bib'] else -1,
             "citedby": pub['num_citations'] if "num_citations" in pub else 0,
             "link": pub["id_citations"] if "id_citations" in pub else ""
             }
            for pub in author["publications"]]
    }
    return a_data


def read_pub_data(publication_title):
    search_query = scholarly.search_pubs(publication_title)
    try:
        p = next(search_query)
    except:
        p = {'num_citations': 0}
    return p


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

