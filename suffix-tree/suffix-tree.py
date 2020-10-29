#!./pypy3.7-v7.3.2-linux64/bin/pypy3
import argparse

nodes = []
last_visited_node = None
index = 0

def increment(n):
    n = n + 1
    return n

class Node(object):
    
    def __init__(self, root=None, node_label=None, index=(increment(index))):
        self.label = node_label
        self.children = []
        self.index = index
        self.root = root
        self.ocurrences = []

    def search(self, node_label, node):
        global last_visited_node
        last_visited_node = node
        if (node.label == node_label):
            return node
        else:
            for child_node in node.children:
                aux_node = self.search(node_label, child_node)
                if (aux_node is not None):
                    return aux_node
            return None
        
    def insert(self, node_label):
        global last_visited_node
        aux_node = self.search(node_label, root)
        if (aux_node):
            aux_node.add(node_label)
        else:
            last_visited_node.children + [Node(node_label)]

    def print_compression(self, node):
        if node is not None:
            print (node.label)
        else:
            for child_node in node.children:
                self.print_compression(child_node)
      

root = Node()


parser = argparse.ArgumentParser(description='Create suffix-tree from lines in file.')
parser.add_argument('file')
args = parser.parse_args()

with open(args.file, 'r') as fp:
    vertice = fp.readline()
    while vertice:
        root.insert(vertice)
        vertice = fp.readline()

root.print_compression(root)

# substring = []
# ocurrences = []

# with open(args.file, 'r') as fp:
#     vertice = fp.readline()
#     while vertice:
#         root.insert(vertice)
#         vertice = fp.readline()
