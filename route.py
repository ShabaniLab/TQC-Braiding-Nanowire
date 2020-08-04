import sys
import numpy as np

# ########################################################################
# Adjacency matrix
def adjacency_matrix(file):
    data = []
    c=0
    try:
        file = open(file,'r')
        line = file.readline()
        row = line.split(',')
        row_int = [int(i) for i in row]
        data.append(row_int)
        while line:
            line = file.readline()
            if not line:
                continue;
            row = line.split(',')
            row_int = [int(i) for i in row]
            data.append(row_int)
        file.close()
        return data
    except IOError:
        raise

def validate_matrix(matrix):
    m = np.array(matrix)
    mT = m.transpose()
    if (m == mT).all() and (all (len(row) == len(m) for row in m)):
        return True
    else:
        raise SyntaxError('Invalid adjacency matrix')

def transform_matrix(matrix):
    N = len(matrix)
    for row in matrix:
        for i in range(len(row)):
            if row[i]==0:
                row[i]=float("Inf")
    return matrix

# ########################################################################
# Dijkstra
def min_distance(dist, blackened):
    min = float("Inf")
    for v in range(len(dist)):
        if not blackened[v] and dist[v]<min:
            min = dist[v]
            min_index = v
    return float("Inf") if min == float("Inf") else min_index

def get_path(matrix, parent, _d, path):
    if parent[_d]==-1:
        path.append(_d)
        return
    get_path(matrix, parent, parent[_d], path)
    path.append(_d)

def dijkstra(graph, _s, _d):
    row = len(graph)
    col = len(graph[0])
    dist = [float("Inf")] * row
    blackened =[0] * row
    pathlength =[0] * row
    parent = [-1] * row
    dist[_s]= 0
    for count in range(row-1):
        u = min_distance(dist, blackened)
        if u == float("Inf"):
            break
        else:
            blackened[u]= 1
        for v in range(row):
            if blackened[v]== 0 and graph[u][v] and dist[u]+graph[u][v]<dist[v]:
                parent[v]= u
                pathlength[v]= pathlength[parent[v]]+1
                dist[v]= dist[u]+graph[u][v]
            elif blackened[v]== 0 and graph[u][v] and dist[u]+graph[u][v]== dist[v] and pathlength[u]+1<pathlength[v]:
                parent[v]= u
                pathlength[v] = pathlength[u] + 1

    if dist[_d]!= float("Inf"):
        return parent
    else:
        raise StopIteration("No known path between {} and {}".format(_s,_d))

def start(matrix,start,end):
    try:
        validate_matrix(matrix)
        matrix = transform_matrix(matrix)

        path = []
        parent = dijkstra(matrix, start, end)
        get_path(matrix,parent,end,path)

        return path
    except SyntaxError as err:
        print(err)
    except StopIteration as err:
        print(err)
