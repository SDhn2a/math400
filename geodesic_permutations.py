import sys
import math
import networkx as nx
import pyvis.network


SOLUTIONS_LIST = []


def create_transpositions_list_alt(current_list, current_length, target_length):
    if current_length == target_length:
        SOLUTIONS_LIST.append(current_list)
        return None
    for pos in range(len(current_list)+1):
        new_list = []
        for i in range(pos):
            new_list.append(current_list[i]+1)
        for i in range(current_length):
            new_list.append(i)
        for i in range(len(current_list)-pos):
            new_list.append(current_list[i+pos])
        create_transpositions_list_alt(
            new_list, current_length+1, target_length)


def create_transpositions_list(current_list, current_result):
    length = len(current_result.keys())
    for i in range(length-1):
        # if i > len(current_list):
        #     break
        if len(current_list) > 0 and i > current_list[-1]+1:
            break
        if len(current_list) > length-1 and current_list[-1] == length-2 and current_list[1-length] == 0 and current_list[-length] < i:
            break
        temp_low = current_result.get(i)
        temp_high = current_result.get(i+1)
        if temp_low < temp_high:
            new_list = current_list.copy()
            new_list.append(i)
            current_result.update({i+1: temp_low})
            current_result.update({i: temp_high})
            create_transpositions_list(new_list, current_result)
            current_result.update({i+1: temp_high})
            current_result.update({i: temp_low})
    if(len(current_list) == (((length-1)**2+length-1)/2)):
        SOLUTIONS_LIST.append(current_list)


def graph_transposition_list(transposition_list):
    net = pyvis.network.Network(notebook=True)
    graph = nx.Graph()
    active_vertex_list = []
    next_vertex = 0
    slots = math.ceil((len(transposition_list)/2)**(1/2))
    for i in range(slots):
        active_vertex_list.append(next_vertex)
        graph.add_node(next_vertex)
        next_vertex += 1
    for element in transposition_list:
        if element % 2 == 0:
            previous_vertex = active_vertex_list[int(element/2)]
            active_vertex_list[int(element/2)] = next_vertex
            graph.add_edge(previous_vertex, next_vertex)
            next_vertex += 1
        else:
            graph.add_edge(
                active_vertex_list[int((element-1)/2)], active_vertex_list[int((element+1)/2)])
    print(graph.nodes())
    print(graph.edges())
    net.from_nx(graph)
    file_name = 'output/graph'+str(transposition_list)+'.html'
    net.show(file_name)
    # nx.draw(graph, with_labels=True, font_weight='bold')


if __name__ == '__main__':
    # starting_arrangement = {}
    # for i in range(int(sys.argv[1])):
    #     starting_arrangement.update({i: i})
    # create_transpositions_list([], starting_arrangement)
    create_transpositions_list_alt([], 1, int(sys.argv[1]))
    # print(SOLUTIONS_LIST)
    if(len(sys.argv) > 2):
        for transposition_list in SOLUTIONS_LIST:
            graph_transposition_list(transposition_list)
    print(len(SOLUTIONS_LIST))
    # graph_transposition_list(SOLUTIONS_LIST[0])
