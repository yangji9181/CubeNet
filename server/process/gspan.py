#!/usr/bin/env python
import copy
import server.process.graph as graph
import server.process.graph_reader as graph_reader
import os.path
import numpy as np


__author__ = 'Jamie Fujimoto (gSpan, https://github.com/hayntopdawg/gSpan) William Wang (closeGraph)'


num_call = 1


def build_graph(C):
    """ Builds a graph using code C. """

    g = graph.Graph(1)
    for t in C:
        g.add_ext(t)
    return g


def sub_graph_isomorphisms(C, G):
    """ Returns all of the possible isomorphisms for code C in graph G. """

    phi = [[x] for x in G.get_vertex_by_label(C[0][2])]
    for t in C:
        u, v, u_label, v_label, edge_label = t
        phi_prime = []
        for p in phi:
            if v > u:
                # forward edge
                for x in G.get_neighbors(p[u]):
                    if (x not in p) and \
                       (G.get_vertex_label(x) == v_label) and \
                       (G.get_edge_label(p[u], x) == edge_label):
                        p_prime = p + [x]
                        phi_prime.append(p_prime)
            else:
                # backward edge
                if p[v] in G.get_neighbors(p[u]):
                    phi_prime.append(p)
        phi = copy.copy(phi_prime)
    return copy.copy(phi)


def right_most_path_extensions(C, D):
    """ Returns all possible extensions for the right most path with their respective supports. """

    Gc = build_graph(C)
    R = [v.id for v in Gc]  # nodes on the rightmost path in C
    if R:
        u_r = R[-1]  # rightmost child in C (DFS number)
    else:
        u_r = 0
    E = {}  # set of extensions from C

    for G in D:
        E[G.id] = []
        if not C:
            # add distinct label tuples in Gi as forward extensions
            for dist_tuple in G.get_distinct_label_tuples():
                E[G.id].append((0, 1) + dist_tuple)
        else:
            phi = sub_graph_isomorphisms(C, G)
            for p in phi:  # for each isomorphism in phi
                # backward extensions from rightmost child
                for x in G.get_neighbors(p[u_r]):
                    vs = Gc.get_vertex_by_label(G.get_vertex_label(x))
                    valid_v = [v for v in vs if (p[v] == x) and (v in R) and ((u_r, v) not in Gc.connections)]
                    for v in valid_v:
                        b = (u_r, v, Gc.get_vertex_label(u_r), Gc.get_vertex_label(v), G.get_edge_label(p[u_r], p[v]))
                        E[G.id].append(b)

                # forward extension from nodes on rightmost path
                for u in R:
                    neigbors = [n for n in G.get_neighbors(p[u]) if n not in p]
                    for x in neigbors:
                        E[G.id].append((u, u_r + 1,
                                        Gc.get_vertex_label(u),
                                        G.get_vertex_label(x),
                                        G.get_edge_label(p[u], x)))

    # compute the support of each extension
    sup = {}
    for G in E:
        distinct_exts = list(set(E[G]))  # make each list of tuples distinct
        for ext in distinct_exts:
            if ext not in sup:
                sup[ext] = 1
            else:
                sup[ext] += 1
    sorted_tuples = sort_tuples(list(sup.items()))
    return sorted_tuples

def sort_tuples2(E):
    """
        Sort a list of tuples using the get_minimum_DFS function.
    """
    sorted_tuples = []
    tuples = [[t] for t in E]
    for i in range(0, len(tuples)):
        min_G, min_idx = get_minimum_DFS(tuples)
        sorted_tuples.append(tuples[min_idx][0])
        del tuples[min_idx]
    return sorted_tuples

def tuple_is_smaller(t1,t2):
    """
        Checks whether the tuple t1 is smaller than t2
    """
    t1_forward = t1[1] > t1[0]
    t2_forward = t2[1] > t2[0]
    i,j,x,y = str(t1[0]), str(t1[1]), str(t2[0]), str(t2[1])
    # Edge comparison
    if t1_forward and t2_forward:
        if j < y or (j == y and i > x):
            return True
        elif j > y or (j == y and i < x):
            return False
    elif (not t1_forward) and (not t2_forward):
        if i < x or (i == x and j < y):
            return True
        elif i > x or (i == x and j > y):
            return False
    elif t1_forward and (not t2_forward):
        if j <= x:
            return True
        else:
            return False
    elif (not t1_forward) and t2_forward:
        if i < y:
            return True
        elif i > y: # Maybe something missing here
            return False
    # Lexicographic order comparison
    a1,b1,c1 = t1[2], t1[3], t1[4]
    a2,b2,c2 = t2[2], t2[3], t2[4]

    if not a1.isdigit():
        a1,b1,c1 = ord(a1),ord(b1),ord(c1)
        a2,b2,c2 = ord(a2),ord(b2),ord(c2)
    else:
        a1,b1,c1 = int(a1),int(b1),int(c1)
        a2,b2,c2 = int(a2),int(b2),int(c2)

    if a1 < a2:
        return True
    elif a1 == a2:
        if b1 < b2:
            return True
        elif b1 == b2:
            if c1 < c2:
                return True

    return False

def tuples_are_smaller(DFScodes_1, DFScodes_2):
    """
        Checks if tuples in DFScodes_1 are less than tuples in DFScodes_2
    """
    if len(DFScodes_1) != len(DFScodes_2):
        raise Exception('Size of the two graphs are not equal')
    for i in range(0, len(DFScodes_1)):
        if tuple_is_smaller(DFScodes_1[i],DFScodes_2[i]):
            return True
    return False

def get_minimum_DFS(G_list):
    """
        Finds the graph with smallest DFS code i.e. the canonical graph
    """
    # Initialize first one as minimum
    min_G = G_list[0]
    min_idx = 0
    counts = np.zeros(len(G_list))
    for i in range(0, len(G_list)):
        for j in range(0, len(G_list)):
            if i == j:
                continue
            smaller = tuples_are_smaller(G_list[i], G_list[j])
            if not smaller:
                counts[i] += 1
    min_idx = np.argmin(counts)
    assert counts[min_idx] == 0
    min_G = G_list[min_idx]
    return min_G, min_idx

def sort_tuples(E):
    sorted_E = []
    while len(E) > 0:
        min_tuple = find_min_edge(E)
        sorted_E.append(min_tuple)
        E.remove(min_tuple)
    return copy.copy(sorted_E)


def find_min_edge(E):
    min_edge, min_edge_sup = [], 0
    for (edge, sup) in E:
        if not min_edge:
            min_edge, min_edge_sup = edge, sup
        else:
            # if edge is smaller than min_edge
            if is_smaller(edge, min_edge):
                min_edge, min_edge_sup = edge, sup
    return min_edge, min_edge_sup


def is_smaller(s, t):
    # (i, j) = (x, y)
    if s[0] == t[0] and s[1] == t[1]:
        if s < t:
            return True
        else:
            return False
    else:
        # Condition 1 (Both forward edges)
        if s[0] < s[1] and t[0] < t[1]:
            # (a) j < y
            if s[1] < t[1]:
                return True
            # (b) j = y and i > x
            elif s[1] == t[1] and s[0] > t[0]:
                return True
            else:
                return False
        # Condition 2 (Both backward edges)
        elif s[0] > s[1] and t[0] > t[1]:
            # (a) i < x
            if s[0] < t[0]:
                return True
            # (b) i = x and j < y
            elif s[0] == t[0] and s[1] < t[1]:
                return True
            else:
                return False
        # Condition 3 (e_ij is forward edge and e_xy is backward edge)
        elif s[0] < s[1] and t[0] > t[1]:
            # j <= x
            if s[1] <= t[0]:
                return True
            else:
                return False
        # Condition 4 (e_ij is backward edge and e_xy is forward edge)
        elif s[0] > s[1] and t[0] < t[1]:
            # i < y
            if s[0] < t[1]:
                return True
            else:
                return False


def is_canonical(C):
    """ Checks if code C is canonical """

    Gc = build_graph(C)
    Dc = [Gc]  # graph corresponding to code C
    C_star = []
    for t in C:
        E = right_most_path_extensions(C_star, Dc)
        s, sup = find_min_edge(E)
        if is_smaller(s, t):
            return False
        C_star.append(s)
    return True


def output(C, sup=None):
    global num_call

    if os.path.isfile("output.txt") and num_call > 1:
        mode = "a"
    else:
        mode = "w"

    with open("output.txt", mode) as f:
        print("pattern {}".format(num_call))
        f.write("pattern {}\n".format(num_call))

        num_call += 1

        if not C:
            print("()")
            f.write("()\n")
        for t in C:
            print(t)
            f.write("{}\n".format(t))
        if sup is not None:
            print("support: %d" % sup)
        print("")
        f.write("\n")

def encode_tuple(t):
    s = ''
    for i, e in enumerate(t):
        if i < len(t) - 1:
            s += str(e) + ';'
        else:
            s += str(e)
    return s

def decode_tuple(s):
    l = s.split(';')
    l[0] = int(l[0])
    l[1] = int(l[1])
    return tuple(l)

# def transform_vertex(u, s, phi):
#     """
#         Given a vertex id u and a set of partial isomorphisms phi.
#         Returns the transformed vertex id
#     """
#     for i, _phi in enumerate(phi):
#         if s[i] == u:
#             return _phi
#     raise Exception('u couldn\' be found in the isomorphisms')

def check_inv_exists(v, phi):
    """
        Given a vertex id u and a set of partial isomorphisms phi.
        Returns True if an inverse transformation exists for v
    """
    for i, _phi in enumerate(phi):
        if _phi == v:
            return True
    return False

def inv_transform_vertex(x, phi):
    """
        Given a vertex id x and a set of partial isomorphisms phi.
        Returns the inverse transformed vertex id
    """
    for i, _phi in enumerate(phi):
        if _phi == x:
            return i
    raise Exception('Could not find inverse transformation')

def id_pair_exists_in_tuples(t, u, v, debug=False):
    for i, e in enumerate(t):
        if (e[0] == u or e[1] == u) and (e[0] == v or e[1]==v):
            # if debug:
            #     print('found at:', (u, v), i)
            return True
    return False

def equivalent_occurrences(C, D):
    """
        Returns the set of all equivalent occurences of C in D
    """
    equiv_occrs = []
    extension_set = None
    for j, G in enumerate(D):
        tmp = set([encode_tuple((G.vertices[edge[0]].label, G.vertices[edge[1]].label, G.get_edge_label(edge[0], edge[1]))) for edge in G.connections])
        # print([encode_tuple((edge.from_vertex.label, edge.to_vertex.label, edge.label)) for edge in G.edges])
        if j == 0:
            extension_set = tmp
        else:
            extension_set &= tmp
    # print(extension_set)
    vertex_set = set()
    for t in C:
        u, v, L_u, L_v, L_uv = t
        vertex_set.add(u)
        vertex_set.add(v)
    u_r = len(vertex_set)
    E_final = None
    for j, G in enumerate(D):
        isoms = sub_graph_isomorphisms(C, G) 
        E2 = None
        for i, isom in enumerate(isoms):
            # print(isom)
            E = set()
            for u in vertex_set:
                phi_u = isom[u]
                vertex = G.vertices[phi_u]
                neighbors = G.get_neighbors(phi_u)
                for x in neighbors:
                    inv_exists = check_inv_exists(x, isom)
                    e = vertex.edges[x]
                    if not inv_exists:
                        # Forward edge
                        f = (u, u_r, vertex.label, G.vertices[x].label, e[0])
                        E.add(encode_tuple(f))
                    elif inv_exists:
                        # Backward edge
                        c_code = inv_transform_vertex(x, isom)
                        # Eliminate repeats
                        if id_pair_exists_in_tuples(C, u, c_code) or encode_tuple((c_code, u, vertex.label, G.vertices[x].label, e[0])) in E:
                            continue # Not really an extension
                        f = (u, c_code, vertex.label, G.vertices[x].label, e[0])
                        E.add(encode_tuple(f))
            if i == 0:
                E2 = E
            else:
                E2 &= E  
            # print(E2)    
        if j == 0:
            E_final = E
        else:
            E_final &= E
        # print(E_final)
    return [decode_tuple(t) for t in E_final]

def all_frequent_extensions(s, D, min_sup, debug=False):
    """
        Returns the set of all frequent extensions of s in D
    """
    vertex_set = set()
    for t in s:
        u, v, L_u, L_v, L_uv = t
        vertex_set.add(u)
        vertex_set.add(v)
    sup_dict = {}
    for i, G in enumerate(D):
        E = set()
        isoms = sub_graph_isomorphisms(s, G) 
        # if debug == True:
        #     print(i, isoms)
        for isom in isoms:
            # print(len(isom), len(s))
            # print(isom, s)
            for u in vertex_set:
                # phi_u = transform_vertex(u, s, isom)
                phi_u = isom[u]
                # Find neighbors of transformed vertex
                vertex = G.vertices[phi_u]
                neighbors = G.get_neighbors(phi_u)
                # if debug == True:
                #     print(u, neighbors)
                for x in neighbors:
                    inv_exists = check_inv_exists(x, isom)
                    e = vertex.edges[x]
                    if not inv_exists:
                        # Forward edge
                        f = (u, -1, vertex.label, G.vertices[x].label, e[0])
                        # if (debug==True):
                        #     print(i, f)
                        E.add(encode_tuple(f))
                    elif inv_exists:
                        # Backward edge
                        c_code = inv_transform_vertex(x, isom)
                        # Eliminate repeats
                        if id_pair_exists_in_tuples(s, u, c_code) or encode_tuple((c_code, u, vertex.label, G.vertices[x].label, e[0])) in E:
                            # if debug == True:
                            #     print('continued', (u, c_code), s, id_pair_exists_in_tuples(s, u, c_code, debug=True), encode_tuple((c_code, u, vertex.label, G.vertices[x].label, e[0])) in E)
                            continue # Not really an extension
                        f = (u, c_code, vertex.label, G.vertices[x].label, e[0])
                        # if (debug==True):
                        #     print(i, f)
                        E.add(encode_tuple(f))
        for e in E:
            if e in sup_dict:
                sup_dict[e] += 1
            else:
                sup_dict[e] = 1
    return [(decode_tuple(e), support) for e, support in sup_dict.items() if support >= min_sup]

def gSpan(C, D, minsup):
    """
    Recursively mines a database of graphs to determine all frequent subgraphs.

    Keyword arguments:
    C -- a canonical and frequent code (list of tuples)
    D -- a database of n graphs (list of graphs)
    minsup -- minimum support threshold (integer)
    """

    output(C)

    E = right_most_path_extensions(C, D)
    for (t, sup) in E:
        C_prime = C + [t]
        sup_C_prime = sup
        if sup_C_prime >= minsup and is_canonical(C_prime):
            gSpan(C_prime, D, minsup)

def close_graph(s, s_sup, p, D, min_sup, extensions, upper_limit):
    if (len(extensions) == upper_limit):
        return
    if not is_canonical(s):
        return
    # if p is not None:
        # equiv_occrs = equivalent_occurrences(p, D)
        # g_primes = [sort_tuples2(p+[e_prime]) for e_prime in equiv_occrs]
        # print(g_primes)
        # if np.any([is_smaller(g_prime, s) for g_prime in g_primes]):
        #     print('Early termination')
        #     return
        # if len(equiv_occrs):
        #     return
    extension_supports = all_frequent_extensions(s, D, min_sup)
    if np.all([s_sup != sup for ext, sup in extension_supports]):
        output(s, s_sup)
        extensions.append(s)
    E = right_most_path_extensions(s, D)
    for t, sup_t in E:
        C_prime = list(s) + [t]
        if (sup_t >= min_sup):
            close_graph(C_prime, sup_t, s, D, min_sup, extensions, upper_limit)

def remove_infrequent_occurences(D, min_sup):
    """
        Removes infrequent vertices and edges from D according to min_sup
    """
    vertex_sup = {}
    edge_sup = {}
    for G in D:
        for v in G.vertices.values():
            if v.label in vertex_sup:
                vertex_sup[v.label].add(G.id)
            else:
                vertex_sup[v.label] = set([G.id])
        # for e in G.connections:
        #     label = G.get_edge_label(e[0], e[1])
        #     if label in edge_sup:
        #         edge_sup[label].add(G.id)
        #     else:
        #         edge_sup[label] = set([G.id])
    rem_vertex_labels = set([label for label, sup in vertex_sup.items() if len(sup) < min_sup])
    # rem_edge_labels = set([label for label, sup in edge_sup.items() if len(sup) < min_sup])
    print('vertices pruned:%d' % (len(rem_vertex_labels)))
    for G in D:
        G.remove_vertices_by_label(rem_vertex_labels)
        # G.remove_edges_by_label(rem_edge_labels)

def close_mining(D, min_sup, upper_limit=100):
    # remove_infrequent_occurences(D, min_sup)
    E = right_most_path_extensions([], D)
    patterns = []
    for t, sup_t in E:
        C_prime = [t]
        if sup_t >= min_sup:
            close_graph(C_prime, sup_t, None, D, min_sup, patterns, upper_limit)
    return patterns


if __name__ == "__main__":
    D = graph_reader.graph_reader("testG.txt")
    remove_infrequent_occurences(D, 2)
    patterns = close_mining(D, 2)
