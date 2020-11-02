"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Graph

Objectives:
    1. Extracts the Adjacency matrix
    2. Calculates the shortest path using Dijkstra's algorithm

Class: Nanowire

Functions:
    1. adjacency_matrix
    2. validate_matrix
    3. transform_matrix
    4. min_distance
    5. get_path
    6. dijkstra
    7. route
"""

import numpy as np

################################################################################
def adjacency_matrix(file):
    """
    Extracts the Adjacency matrix from the given file
    """
    data = []
    try:
        file = open(file, 'r')
        line = file.readline()
        row = line.split(',')
        row_int = [int(i) for i in row]
        data.append(row_int)
        while line:
            line = file.readline()
            if not line:
                continue
            row = line.split(',')
            row_int = [int(i) for i in row]
            data.append(row_int)
        file.close()
        return data
    except IOError:
        raise

def validate_matrix(matrix):
    """
    Validates the given Adjacency matrix
    """
    m = np.array(matrix)
    mT = m.transpose()
    if (m == mT).all() and (all (len(row) == len(m) for row in m)):
        return True
    raise SyntaxError('Invalid adjacency matrix')

def transform_matrix(matrix):
    """
    Transforms the given matrix
    """
    for row in matrix:
        for i in range(len(row)):
            if row[i] == 0:
                row[i]=float("Inf")
    return matrix

################################################################################
def min_distance(dist, blackened):
    """
    Checks if dist is min distance
    """
    min = float("Inf")
    for v in range(len(dist)):
        if not blackened[v] and dist[v] < min:
            min = dist[v]
            min_index = v
    return float("Inf") if min == float("Inf") else min_index

def get_path(matrix, parent, _d, path):
    """
    Get path from parent
    """
    if parent[_d] == -1:
        path.append(_d)
        return
    get_path(matrix, parent, parent[_d], path)
    path.append(_d)

def dijkstra(graph, _s, _d):
    """
    Dijkstra's algorithm to extract shortest path
    """
    row = len(graph)
    dist = [float("Inf")] * row
    blackened =[0] * row
    pathlength =[0] * row
    parent = [-1] * row
    dist[_s]= 0
    for _ in range(row-1):
        u = min_distance(dist, blackened)
        if u == float("Inf"):
            break
        blackened[u]= 1
        for v in range(row):
            if blackened[v] == 0 and graph[u][v] and dist[u]+graph[u][v]<dist[v]:
                parent[v]= u
                pathlength[v]= pathlength[parent[v]]+1
                dist[v]= dist[u]+graph[u][v]
            elif blackened[v] == 0 and graph[u][v] and\
                dist[u]+graph[u][v] == dist[v] and pathlength[u] + 1 < pathlength[v]:
                parent[v]= u
                pathlength[v] = pathlength[u] + 1

    if dist[_d]!= float("Inf"):
        return parent
    raise StopIteration("No known path between {} and {}".format(_s, _d))

def route(matrix, start, end):
    """
    Validates matrix, and returns shortest path from start to end
    """
    try:
        validate_matrix(matrix)
        matrix = transform_matrix(matrix)

        path = []
        parent = dijkstra(matrix, start, end)
        get_path(matrix, parent, end, path)

        return path
    except SyntaxError as err:
        print(err)
    except StopIteration as err:
        print(err)
