#!/usr/bin/env python

import server.process.graph as graph


__author__ = 'Jamie Fujimoto'


# referenced code from https://github.com/clemej/pygspan


def graph_reader(filename):
    D = []
    count = 0

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("t"):
                if count > 0:
                    D.append(g)
                _, g_id = [e for e in line.split()[1:]]
                g = graph.Graph(int(g_id))
                count += 1

            elif line.startswith("v"):  # assumes v will always come after a t
                v_id, v_label = [e for e in line.split()[1:]]
                g.add_vertex(int(v_id), v_label)

            elif line.startswith("e"):
                v1_id, v2_id, e_label = [e for e in line.split()[1:]]
                g.add_connection(int(v1_id), int(v2_id), e_label)
        D.append(g)
    return D


if __name__ == "__main__":
    D = graph_reader("testG.txt")
    for g in D:
        print("id: {}".format(g.id))
        for v in g:
            print("{} {} {}".format(v.id, v.label, v.edges))
        # print g.get_distinct_label_tuples()
