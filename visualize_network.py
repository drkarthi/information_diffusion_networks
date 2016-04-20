"""
Visualize the network by religion to investigate for homophily in terms of religion
"""
no_muslim_village_count = 0
all_hindu_villages = []

import csv
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy import stats
import random
from random import choice

def construct_graph_with_attribute(vilno):
    f = open("datav4.0/datav4.0/Data/1. Network Data\Adjacency Matrices/adj_allVillageRelationships_vilno_" + str(vilno) + ".csv", 'r')
    fk = open("datav4.0/datav4.0/Data/1. Network Data/Adjacency Matrix Keys/key_vilno_" + str(vilno) + ".csv", 'r')
    fi = open("indiv.csv", 'r')
    csv_reader = csv.reader(f)
    # adjacency matrix of village 1
    list_adj_matrix = list(csv_reader)
    # list of individual keys
    csv_reader_keys = csv.reader(fk)
    list_keys = list(csv_reader_keys)
    # list of individual characteristics
    csv_indiv = csv.reader(fi)
    list_indiv = list(csv_indiv)
    num_nodes = len(list_adj_matrix)
    # create dictionary mapping each individual to a key 
    keys = [(x,y[0])  for x,y in zip( range(num_nodes), list_keys )]    # y[0] because the keys are stored as one-element lists 
    nodes_to_keys = dict(keys)
    # create dictionary mapping each key to a religion
    keys_to_religion = {}
    for row in list_indiv:
        key = row[3]
        religion = row[9]
        keys_to_religion[key] = religion
    
    i = 0
    edge_count = 0
    edge_list = []
    node_list = []
    g = nx.Graph()
    # for each node, get the key and find the religion if the key is present in the indiv file
    for row in list_adj_matrix:
        node = i
        key = nodes_to_keys[node]
        # print("Key: ",key)
        # if the key is present in the sample of 200 in the indiv.csv file
        if key in keys_to_religion:
            religion = keys_to_religion[key]
            # print("Religion: ", religion)
            # add node and corresponding religion
            g.add_node(node, religion=religion)
            
            for j in range(i+1, len(row)):
                # if the node is part of the sample in the indiv file, add edge
                if nodes_to_keys[j] in keys_to_religion:
                    if(row[j]=='1'):
                        edge_count += 1
                        edge_list.append((i,j))
        i += 1
        
    # print("Number of edges: ", edge_count)
    g.add_edges_from(edge_list)
    hindus = [node for node in g.nodes() if g.node[node]['religion']=='HINDUISM']
    muslims = [node for node in g.nodes() if g.node[node]['religion']=='ISLAM']
    christians = [node for node in g.nodes() if g.node[node]['religion']=='CHRISTIANITY']
    nx.draw(g, nodelist=hindus, node_color='r', node_size=300)
    nx.draw(g, nodelist=muslims, node_color='b', node_size=300)
    nx.draw(g, nodelist=christians, node_color='g', node_size=300)
    plt.show()
    return g, hindus, muslims, christians


def calculate_densities(g, hindus, muslims, vilno, rows, within_hindus_count=0, within_muslims_count=0, cross_edges_count=0):
    num_hindus = len(hindus)
    print("Number of hindus: ", num_hindus)
    max_edges_hindus = num_hindus * (num_hindus-1) / 2
    num_muslims = len(muslims)
    print("Number of muslims: ", num_muslims)
    max_edges_muslims = num_muslims * (num_muslims-1) / 2
    max_cross_edges = num_hindus * num_muslims
    num_nodes = g.number_of_nodes()
    num_edges = g.number_of_edges()
    avg_degree = g.number_of_edges()/g.number_of_nodes()
    max_edges_all = num_nodes*(num_nodes-1)/2

    global no_muslim_village_count
    global all_hindu_villages
    if num_muslims == 0:
        all_hindu_villages.append(vilno)
        no_muslim_village_count += 1

    # print("Number of edges: ", g.number_of_edges())
    for edge in g.edges():
        node1 = edge[0]
        node2 = edge[1]
        if (g.node[node1]['religion'], g.node[node2]['religion']) == ('HINDUISM', 'HINDUISM'):
            within_hindus_count += 1
        elif (g.node[node1]['religion'], g.node[node2]['religion']) == ('ISLAM', 'ISLAM'):
            within_muslims_count += 1
        elif (g.node[node1]['religion'], g.node[node2]['religion']) == ('HINDUISM', 'ISLAM') or (g.node[node1]['religion'], g.node[node2]['religion']) == ('ISLAM', 'HINDUISM'):
            cross_edges_count += 1

    p_within_hindus = within_hindus_count / max_edges_hindus
    p_within_muslims = within_muslims_count / max_edges_muslims if num_muslims>1 else 0
    p_cross_edges = cross_edges_count / max_cross_edges if num_muslims>0 else 0
    p_all = num_edges/ max_edges_all

    std_within_hindus = math.sqrt( p_within_hindus * (1-p_within_hindus) / max_edges_hindus )
    std_within_muslims = math.sqrt( p_within_muslims * (1-p_within_muslims) / max_edges_muslims ) if num_muslims>1 else 0
    std_cross_edges = math.sqrt( p_cross_edges * (1-p_cross_edges) / max_cross_edges ) if num_muslims>0 else 0
    std_all = math.sqrt( p_all * (1-p_all) / max_edges_all )

    row = [vilno, num_nodes, p_all, num_hindus, p_within_hindus, num_muslims, p_within_muslims, p_cross_edges, avg_degree]
    rows.append(row)

    conf_int_density_hindus = (p_within_hindus - 1.96*std_within_hindus, p_within_hindus + 1.96*std_within_hindus)
    print("Density within the Hindu community: ", conf_int_density_hindus)
    conf_int_density_muslims = (p_within_muslims - 1.96*std_within_muslims, p_within_muslims + 1.96*std_within_muslims)
    print("Density within the Muslim community", conf_int_density_muslims)
    conf_int_density_cross= (p_cross_edges - 1.96*std_cross_edges, p_cross_edges + 1.96*std_cross_edges)
    print("Density of cross edges: ", conf_int_density_cross)
    conf_int_density_all= (p_all - 1.96*std_all, p_all + 1.96*std_all)

    return {'hindu': (p_within_hindus, conf_int_density_hindus), 'muslim': (p_within_muslims, conf_int_density_muslims), 
    'cross': (p_cross_edges, conf_int_density_cross), 'all': (p_all, conf_int_density_all)}


def calculate_homophily_unnormalized(g, hindus, muslims):
    homophily_edge_count = 0
    homophily_hindu_edges = 0
    homophily_muslim_edges = 0
    N = g.number_of_nodes()
    E = g.number_of_edges()
    total_hindu_edges = 0
    total_muslim_edges = 0
    # print("Number of nodes in village: ", g.number_of_nodes())
    # print("Number of edges in village: ", g.number_of_edges())
    for edge in g.edges():
        if g.node[edge[0]]['religion'] == "HINDUISM" or g.node[edge[1]]['religion'] == "HINDUISM":
            total_hindu_edges += 1
        if g.node[edge[0]]['religion'] == "ISLAM" or g.node[edge[1]]['religion'] == "ISLAM":
            total_muslim_edges += 1    
        if g.node[edge[0]]['religion'] == g.node[edge[1]]['religion']:
            homophily_edge_count += 1
            if g.node[edge[0]]['religion'] == 'HINDUISM':
                homophily_hindu_edges += 1
            if g.node[edge[0]]['religion'] == 'ISLAM':
                homophily_muslim_edges += 1    
    # print("Number of same religion edges: ", homo_edge_count)
    homophily_unnormalized = homophily_edge_count/E
    homophily_hindus = homophily_hindu_edges/total_hindu_edges
    homophily_muslims = homophily_muslim_edges/total_muslim_edges

    return homophily_unnormalized, homophily_hindus, homophily_muslims


def calculate_homophily_normalized(g, hindus, muslims):
    N = g.number_of_nodes()
    E = g.number_of_edges()
    homophily_all, homophily_hindus, homophily_muslims = calculate_homophily_unnormalized(g, hindus, muslims)
    # print("Homophily of g: ", homophily_unnormalized)
    # create a random graph with the same number of nodes and edges as the graph g
    iter_count = 0
    h_all_sum = 0
    h_hindus_sum = 0
    h_muslims_sum = 0
    p = E / (N*(N-1)/2)
    for x in range(100):
        iter_count += 1
        print("Iteration number: ", iter_count)
        rg = nx.Graph()
        # copy the nodes from the village graph
        rg.add_nodes_from(g.nodes(data=True))
        # generate E random edges
        for x in range(E):
            existing_edges = rg.edges()
            # making sure that there are no self-edges
            while True:
                n1 = choice(g.nodes())
                n2 = choice(g.nodes())
                if n1!=n2 and (n1,n2) not in existing_edges and (n2,n1) not in existing_edges:
                    break
            rg.add_edge(n1,n2)
        # print("Number of nodes in random graph: ", rg.number_of_nodes())
        # print("Number of edges in random graph: ", rg.number_of_edges())
        homophily_all_random, homophily_hindus_random, homophily_muslims_random = calculate_homophily_unnormalized(rg, hindus, muslims)
        h_all_sum += homophily_all_random
        h_hindus_sum += homophily_hindus_random
        h_muslims_sum += homophily_muslims_random
        # print("Homophily of random graph: ", homophily_random)
    avg_homophily_all_random = h_all_sum/100
    avg_homophily_hindus_random = h_hindus_sum/100
    avg_homophily_muslims_random = h_muslims_sum/100

    # calculate the normalized homophily
    homophily_all_norm = homophily_all - avg_homophily_all_random
    print("Homophily overall: ", homophily_all_norm)
    homophily_hindus_norm = homophily_hindus - avg_homophily_hindus_random
    print("Homophily hindus: ", homophily_hindus_norm)
    homophily_muslims_norm = homophily_muslims - avg_homophily_muslims_random
    print("Homophily muslims: ", homophily_muslims_norm)
    return homophily_all_norm, homophily_hindus_norm, homophily_muslims_norm


if __name__=='__main__':
    hindu_densities = []
    muslim_densities = []
    cross_densities = []
    all_densities = []
    headings = ['VillageNumber', 'NumNodes', 'DensityAll', 'NumHindus', 'DensityHindus', 'NumMuslims', 'DensityMuslims', 'DensityCrossEdges', 'AvgDegree']
    rows = [headings]
    village_count = 0
    homophily_villages = []
    x = []
    y1 = []
    y2 = []
    y3 = []

    for vilno in [1]:
        if vilno in [13,22]:
            continue
        print("Village number: ", vilno)
        g, hindus, muslims, christians = construct_graph_with_attribute(vilno)
    
        return_value = calculate_densities(g, hindus, muslims, vilno, rows)
        if return_value!=None:
            village_count += 1
            edge_densities = return_value
            hindu_densities.append(edge_densities['hindu'][0])
            muslim_densities.append(edge_densities['muslim'][0])
            cross_densities.append(edge_densities['cross'][0])
            all_densities.append(edge_densities['all'][0])

        # # if it is an all-Hindu village, do not calculate homophily
        # if len(muslims)<3:
            # continue
        # homophily_all, homophily_hindus, homophily_muslims = calculate_homophily_normalized(g, hindus, muslims)
        # homophily_villages.append( (vilno, homophily_all, homophily_hindus, homophily_muslims) )
# 
    # print("Homophily normalized: ", homophily_villages)
    # f = open("homophily2.csv", 'w')
    # csv_writer = csv.writer(f, lineterminator='\n')
    # csv_writer.writerow(["Vilno", "HomophilyAll", "HomophilyHindus", "HomophilyMuslims"])
    # for item in homophily_villages:
        # csv_writer.writerow([ item[0], item[1], item[2], item[3] ])
        # x.append(item[0]) 
        # y1.append(item[1])
        # y2.append(item[2])
        # y3.append(item[3])
    # # plot distribution of overall homophily for villages
    # plt.hist(y1)
    # plt.xlim(-0.1,0.5)
    # plt.xlabel("Homophily")
    # plt.ylabel("Number of villages")
    # plt.title("Distribution of overall homophily across villages")
    # plt.show()

    # # plot distribution of hindus homophily for villages
    # plt.hist(y2)
    # plt.xlim(-0.1,1)
    # plt.xlabel("Homophily")
    # plt.ylabel("Number of villages")
    # plt.title("Distribution of hindu homophily across villages")
    # plt.show()

    # # plot distribution of muslims homophily for villages
    # plt.hist(y3)
    # plt.xlim(-0.1,1)
    # plt.xlabel("Homophily")
    # plt.ylabel("Number of villages")
    # plt.title("Distribution of muslim homophily across villages")
    # plt.show()
# 
    # print("Average overall homophily: ", sum(y1)/len(y1))
    # print("Average hindu homophily: ", sum(y2)/len(y2))
    # print("Average muslim homophily: ", sum(y3)/len(y3))
    
    # print("Hindu densities: ", hindu_densities)
    # plt.plot(hindu_densities, label="Hinduism")
    # print("Muslim densities: ", muslim_densities)
    # plt.plot(muslim_densities, label="Islam")
    # print("Cross densities: ", cross_densities)
    # plt.plot(cross_densities, label="Cross edges")
    # xticks_set = set(range(1,78)) - set([13,22])
    # plt.xticks(list(xticks_set))
    # plt.xlabel("Village numbers")
    # plt.ylabel("Edge density")
    # plt.legend()
    # plt.show()
    # print("Village count: ", village_count)
    # print("Num villages with no muslims: ", no_muslim_village_count)
    # print("All hindu villages: ", all_hindu_villages)
    # print(rows)
    # print(len(rows))
    # with open("density_by_religion.csv", 'w') as f:
        # csv_writer = csv.writer(f, lineterminator='\n')
        # csv_writer.writerows(rows)
