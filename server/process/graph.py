#!/usr/bin/env python

__author__ = 'Jamie Fujimoto'


# referenced code from http://www.bogotobogo.com/python/python_graph_data_structures.php


class Vertex(object):
    def __init__(self, id, label):
        self.id = id
        self.label = label
        self.neighbors = set()
        self.edges = {}


    def add_edge(self, neighbor, neighbor_label, edge_label):
        self.neighbors.add(neighbor)
        edge = (self.label, neighbor_label, edge_label)
        self.edges[neighbor] = edge


class Graph(object):
    def __init__(self, id):
        self.id = id
        self.vertices = {}
        self.connections = []


    def __iter__(self):
        return iter(list(self.vertices.values()))


    def add_vertex(self, v_id, label=''):
        new_vertex = Vertex(v_id, label)
        self.vertices[v_id] = new_vertex


    def add_connection(self, node1, node2, label=''):
        if node1 not in self.vertices:
            self.add_vertex(node1)
        if node2 not in self.vertices:
            self.add_vertex(node2)
        self.vertices[node1].add_edge(node2, self.vertices[node2].label, label)
        self.connections.append((node1, node2))
        self.vertices[node2].add_edge(node1, self.vertices[node1].label, label)
        self.connections.append((node2, node1))


    def add_ext(self, t):
        node1, node2, node1_label, node2_label, edge_label = t
        if node1 not in self.vertices:
            self.add_vertex(node1, node1_label)
        if node2 not in self.vertices:
            self.add_vertex(node2, node2_label)
        self.add_connection(node1, node2, edge_label)

    def remove_vertices_by_label(self, labels):
        keys_to_remove = set([v.id for v in self.vertices.values() if v.label in labels])
        for key in keys_to_remove:
            v = self.vertices[key]
            # print(len(v.neighbors))
            for neighbor in v.neighbors:
                # print(v.neighbors)
                neighbor = self.vertices[neighbor]
                # print(neighbor)
                # print(v.id)
                # if v.id in neighbor.edges:
                del neighbor.edges[v.id]
                neighbor.neighbors.remove(v.id)
            del self.vertices[key]
        new_edges = []
        for edge in self.connections:
            if edge[0] in keys_to_remove or edge[1] in keys_to_remove:
                continue
            new_edges.append(edge)
        self.connections = new_edges

    # def remove_edges_by_label(self, labels):
    #     new_edges = []
    #     for edge in self.connections:
    #         if edge[2] in labels:
    #             v1 = self.vertices[edge[0]]
    #             v2 = self.vertices[edge[1]]
    #             del v1.edges[v2]
    #             del v2.edges[v1]
    #             v1.neighbors.remove(v2)
    #             v2.neighbors.remove(v1)
    #             continue
    #         new_edges.append(edge)
    #     self.connections = new_edges

    def get_distinct_label_tuples(self):
        tuples = []
        for v in list(self.vertices.values()):
            tuples.extend(list(v.edges.values()))
        distinct = list(set(tuples))
        distinct.sort()
        return distinct


    def get_vertex_by_label(self, label):
        return [v.id for v in list(self.vertices.values()) if v.label == label]


    def get_vertex_label(self, v_id):
        return self.vertices[v_id].label


    def get_edge_label(self, node1, node2):
        return self.vertices[node1].edges[node2][2]


    def get_neighbors(self, v_id):
        return self.vertices[v_id].neighbors