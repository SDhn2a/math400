import sys
import math
import networkx as nx
from numpy.core.fromnumeric import transpose
from numpy.lib.function_base import place
import pyvis.network
import numpy as np


SOLUTIONS_LIST = []
EQUIVALENCE_DUMP = set()


def create_all_equiv(transposition_list):
    equiv_list = [transposition_list]
    current_transposition = sort_and_make(transposition_list)
    while(not current_transposition == transposition_list):
        equiv_list.append(current_transposition)
        current_transposition = sort_and_make(current_transposition)
        if len(current_transposition) < len(transposition_list):
            print(transposition_list, "got turned into", current_transposition)
            break
    # print("all done!")
    return equiv_list


def standard_order(transposition_list):
    new_t_list = transposition_list
    for t in range(len(new_t_list)-1):
        transposition = new_t_list[t]
        next_transposition = new_t_list[t+1]
        if transposition+1 < next_transposition:
            new_t_list[t] = next_transposition
            new_t_list[t+1] = transposition
            return standard_order(new_t_list)
    return new_t_list


def sort_and_make(transposition_list):
    final_transposition_list = []
    pools = create_pools(transposition_list)
    # for pool in pools:
    #     print(pool)
    even_list = []
    for i in range(math.ceil(len(pools)/2)):
        even_list.append(find_endpoint(pools[i*2]))
    # for _ in range(15):
    while(True):
        protected = np.zeros(len(even_list))
        for i in range(math.floor(len(pools)/2)):
            pool = pools[i*2+1]
            items_to_remove = []
            for item in pool:
                marked = [None, None]
                for e in range(len(even_list)):
                    even = even_list[e]
                    if item[0] == even:
                        marked[0] = e
                    elif item[1] == even:
                        marked[1] = e
                if marked[0] is not None and marked[1] is not None:
                    final_transposition_list.append(
                        len(pools)-1-(marked[0]+marked[1]))
                    # print("b", len(pools)-1-(marked[0]+marked[1]))
                    items_to_remove.append(item)
                elif marked[0] is not None:
                    protected[marked[0]] = 1
                elif marked[1] is not None:
                    protected[marked[1]] = 1
            for item in items_to_remove:
                pool.remove(item)
        even_list, pools, to_append = increment_vertices(
            even_list, pools, protected)
        for transposition in to_append:
            final_transposition_list.append(transposition)
        if sum([len(pool) for pool in pools]) == max(transposition_list) % 2:
            break
    return standard_order(final_transposition_list)


def find_endpoint(pool):
    if pool[0][1] is None:
        return pool[0][0]
    full_list = []
    for entry in pool:
        for i in range(2):
            if entry[i] in full_list:
                full_list.remove(entry[i])
            else:
                full_list.append(entry[i])
    return full_list[[entry[0] for entry in full_list].index(min([entry[0] for entry in full_list]))]


def increment_vertices(currents, pools, protected):
    newPool = pools
    new_current = currents
    transpositions = []
    for i in range(len(currents)):
        item = currents[i]
        if protected[i] == 0 and len(newPool[i*2]) > 0 and newPool[i*2][0][1] is not None:
            new_current[i], newPool[i *
                                    2] = get_next_from_pool(item, newPool[i*2])
            transpositions.append(len(pools)-1-i*2)
            # print("a", len(pools)-1-i*2)
            break
    return new_current, newPool, transpositions


def get_next_from_pool(current, list):
    newList = list
    for item in list:
        if item[0] == current:
            newList.remove(item)
            current = item[1]
            return(current, newList)
        elif item[1] == current:
            newList.remove(item)
            current = item[0]
            return(current, newList)
    return(current, newList)


def create_pools(transposition_list):
    bitmasks = all_bitmasks(transposition_list)
    pools = []
    if max(transposition_list) % 2 == 1:
        pools.append([((max(transposition_list)-1, 0), (None))])
    for b in range(len(bitmasks)):
        pools.append([])
    vx = vertex_form(transposition_list)
    for i in range(max(transposition_list)+1):
        for n in range(len(transposition_list)):
            if transposition_list[n] == i:
                for b in range(len(bitmasks)):
                    if bitmasks[b][n] == 1:
                        pools[b+max(transposition_list) % 2].append(vx[n])
                        break
    # for pool in pools:
    #     print(pool)
    return pools


def vertex_form(transposition_list):
    current_count = np.zeros(1+math.ceil(max(transposition_list)/2))
    vx_list = []
    for i in transposition_list:
        vx = np.zeros((2, 2))
        if i % 2 == 0:
            vx = ((i, int(current_count[int(i/2)])),
                  (i, int(current_count[int(i/2)]+1)))
            current_count[int(i/2)] += 1
        else:
            vx = ((i-1, int(current_count[int((i-1)/2)])),
                  (i+1, int(current_count[int((i+1)/2)])))
        vx_list.append(vx)
    return vx_list


def all_bitmasks(transposition_list, raw=True):
    bitmask_list = []
    current_bitmask = np.zeros(len(transposition_list))
    mx = max(transposition_list)
    layers = math.ceil(mx/2)
    if mx % 2 == 0:
        short_line = short_line_bitmask(
            transposition_list, np.zeros(len(transposition_list)))
        if raw:
            bitmask_list.append(short_line)
        else:
            bitmask_list.append(("short", short_line))
        current_bitmask += short_line
        short_pad = short_pad_bitmask(transposition_list, current_bitmask)
        if raw:
            bitmask_list.append(short_pad)
        else:
            bitmask_list.append(("padding", short_pad))
        current_bitmask += short_pad
    else:
        point = point_bitmask(transposition_list)
        if raw:
            bitmask_list.append(point)
        else:
            bitmask_list.append(("point", point))
        current_bitmask += point
    for layer in range(layers):
        if layer == layers - 1:
            short_line = short_line_bitmask(
                transposition_list, current_bitmask)
            if raw:
                bitmask_list.append(short_line)
            else:
                bitmask_list.append(("short", short_line))
            current_bitmask += short_line
        else:
            line = line_bitmask(transposition_list, current_bitmask)
            if raw:
                bitmask_list.append(line)
            else:
                bitmask_list.append(("line", line))
            current_bitmask += line
            pad = pad_bitmask(transposition_list, current_bitmask)
            if raw:
                bitmask_list.append(pad)
            else:
                bitmask_list.append(("padding", pad))
            current_bitmask += pad
    return bitmask_list


def point_bitmask(transposition_list):
    mx = max(transposition_list)
    bitmask = np.zeros(len(transposition_list))
    for t in range(len(transposition_list)):
        if transposition_list[t]+3 > mx:
            bitmask[t] = 1
        if transposition_list[t]+1 == mx:
            break
    return bitmask


def short_pad_bitmask(transposition_list, ignore_list):
    mod_list = transposition_list*(1-ignore_list)
    mx = max(mod_list)
    bitmask = np.zeros(len(mod_list))
    target_numbers_found = [0, 0]
    for t in range(len(mod_list)):
        if mod_list[t] == mx and target_numbers_found[0] == 0:
            bitmask[t] = 1
            target_numbers_found[0] = 1
        elif transposition_list[t]+1 == mx and ignore_list[t] == 0 and sum(target_numbers_found) < 2:
            bitmask[t] = 1
        elif transposition_list[t]+2 == mx and ignore_list[t] == 0 and target_numbers_found[1] == 0:
            bitmask[t] = 1
            target_numbers_found[1] = 1
        elif transposition_list[t]+3 == mx and ignore_list[t] == 0 and target_numbers_found[1] == 0:
            bitmask[t] = 1
    return bitmask


def pad_bitmask(transposition_list, ignore_list):
    mod_list = transposition_list*(1-ignore_list)
    mx = max(mod_list)
    if mx % 2 == 0:
        mx += 1
    bitmask = np.zeros(len(mod_list))
    target_numbers_found = [0, 0]
    for t in range(len(mod_list)):
        if mod_list[t] == mx:
            bitmask[t] = 1
        elif transposition_list[t]+1 == mx and ignore_list[t] == 0 and target_numbers_found[0] == 0:
            bitmask[t] = 1
            target_numbers_found[0] = 1
        elif transposition_list[t]+2 == mx and ignore_list[t] == 0 and sum(target_numbers_found) < 2:
            bitmask[t] = 1
        elif transposition_list[t]+3 == mx and ignore_list[t] == 0 and target_numbers_found[1] == 0:
            bitmask[t] = 1
            target_numbers_found[1] = 1
        elif transposition_list[t]+4 == mx and ignore_list[t] == 0 and target_numbers_found[1] == 0:
            bitmask[t] = 1
    return bitmask


def short_line_bitmask(transposition_list, ignore_list):
    if not sum(ignore_list) == 0:
        return 1 - ignore_list
    mod_list = transposition_list*(1-ignore_list)
    mx = max(mod_list)
    if mx % 2 == 1:
        mx += 1
    bitmask = np.zeros(len(mod_list))
    target_numbers_found = 0
    for t in range(len(mod_list)):
        if transposition_list[t]+3 > mx and ignore_list[t] == 0 and target_numbers_found == 0:
            bitmask[t] = 1
        if transposition_list[t]+1 == mx and ignore_list[t] == 0:
            target_numbers_found = 1
    return bitmask


def line_bitmask(transposition_list, ignore_list):
    mod_list = transposition_list*(1-ignore_list)
    mx = max(mod_list)
    if mx % 2 == 1:
        mx += 1
    bitmask = np.zeros(len(mod_list))
    target_numbers_found = [0, 0]
    for t in range(len(mod_list)):
        if mod_list[t] == mx:
            bitmask[t] = 1
        elif transposition_list[t]+1 == mx and ignore_list[t] == 0 and target_numbers_found[0] == 0:
            bitmask[t] = 1
            target_numbers_found[0] = 1
        elif transposition_list[t]+2 == mx and ignore_list[t] == 0 and sum(target_numbers_found) < 2:
            bitmask[t] = 1
        elif transposition_list[t]+3 == mx and ignore_list[t] == 0 and target_numbers_found[1] == 0:
            bitmask[t] = 1
            target_numbers_found[1] = 1
        elif transposition_list[t]+4 == mx and ignore_list[t] == 0 and target_numbers_found[1] == 0:
            bitmask[t] = 1
    return bitmask


def create_transpositions_list(current_list, current_length, target_length):
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
        create_transpositions_list(
            new_list, current_length+1, target_length)


def create_full_transpositions_list(current_list, current_result):
    length = len(current_result.keys())
    for i in range(length-1):
        # if i > len(current_list):
        #     break
        if len(current_list) > 0 and i > current_list[-1]+1:
            break
        # if len(current_list) > length-1 and current_list[-1] == length-2 and current_list[1-length] == 0 and current_list[-length] < i:
        #     break
        temp_low = current_result.get(i)
        temp_high = current_result.get(i+1)
        if temp_low < temp_high:
            new_list = current_list.copy()
            new_list.append(i)
            current_result.update({i+1: temp_low})
            current_result.update({i: temp_high})
            create_full_transpositions_list(new_list, current_result)
            current_result.update({i+1: temp_high})
            current_result.update({i: temp_low})
    flatten = tuple(current_list)
    if(len(current_list) == (((length-1)**2+length-1)/2)):
        if not flatten in EQUIVALENCE_DUMP:
            for equiv_list in create_all_equiv(current_list):
                EQUIVALENCE_DUMP.add(tuple(equiv_list))
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
    # print([i for i in create_all_equiv([int(i)
    #       for i in sys.argv[1].split(",")])])
    # SOLUTIONS_LIST.append([int(i) for i in sys.argv[1].split(",")])

    starting_arrangement = {}
    for i in range(int(sys.argv[1])):
        starting_arrangement.update({i: i})
    create_full_transpositions_list([], starting_arrangement)
    # create_transpositions_list([], 1, int(sys.argv[1]))
    # print(SOLUTIONS_LIST)
    if(len(sys.argv) > 2):
        for transposition_list in SOLUTIONS_LIST:
            graph_transposition_list(transposition_list)
    print(len(SOLUTIONS_LIST))

    # print("\n        ", SOLUTIONS_LIST[0])
    # print("vx form = ", vertex_form(SOLUTIONS_LIST[0]))
    # create_pools(SOLUTIONS_LIST[0])
    # a = sort_and_make(SOLUTIONS_LIST[0])
    # print(a)
    # bitmasks = all_bitmasks(SOLUTIONS_LIST[0], False)
    # for bitmask in bitmasks:
    #     print(f'{bitmask[0]:<8}', bitmask[1])
    # graph_transposition_list(SOLUTIONS_LIST[0])
