
import networkx as nx
import matplotlib.pyplot as plt

G=nx.Graph()

with open("/Users/snehabhadbhade/Downloads/datav4.0/Data/1. Network Data/Adjacency Matrices/adj_allVillageRelationships_vilno_1.csv") as f:
    relat_data = f.readlines()
f.close()
    
with open("/Users/snehabhadbhade/Downloads/indiv.csv") as f:
    ind_data = f.readlines()
f.close()

count_nodes = len(relat_data)
count_nodes+=1
G.add_nodes_from(range(1,count_nodes))

node_attrib = {}
for i in range(1,count_nodes):
    node_attrib[i] = 0

count_row = 0
for row in ind_data:
    if count_row == 0:
        count_row+=1
        continue    
    data = row.split(",")
    if data[1] == '1':
        node = int(data[2])
        if data[6] == '1':
            node_attrib[node] = 1
        if data[6] == '2':
            node_attrib[node] = 2
    else:
        break

nx.set_node_attributes(G,"Gender",node_attrib)

# color map  0 
val_map = {0: 'w',   # no information
           1: 'r',   # female 
           2: 'b'   # male
           }  


count_row = 0
for row in relat_data:
    count_row+= 1
    data = row.split(",")
    count_col = 0
    for col in data:
        count_col+=1
        if col == '1':
            if not G.has_edge(count_row,count_col):
                G.add_edge(count_row,count_col)
               

print G.number_of_edges()

# draw it
colors = [val_map[G.node[n]['Gender']] for n in G.nodes()]
nx.draw(G,node_color = colors,edge_color ='k', with_labels=True)
plt.show() 
