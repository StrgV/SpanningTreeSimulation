import random
import time
from typing import Dict, List, Tuple, Optional

# Constants
MAX_IDENT = 20
MAX_ITEMS = 100
MAX_KOSTEN = 1000
MAX_NODE_ID = 10000

class Link:
    def __init__(self):
        self.kosten = 0
        
        self.root_id = 0
        self.summe_kosten = 0

class Node:
    def __init__(self, name: str, node_id: int):
        self.name = name
        self.node_id = node_id
        self.links = []
        self.next_hop = 0
        self.msg_cnt = 0 

    def add_link(self):
        self.links.append(Link())

class Graph:
    def __init__(self, name: str = ""):
        self.name = name
        self.nodes = []  
        self.node_count = 0
    
    def get_index(self, name: str) -> int:
        for i, node in enumerate(self.nodes):
            if node.name == name:
                return i
        return -1
    
    def append_node(self, name: str, node_id: int) -> int:
        if self.get_index(name) != -1:
            # Node already exists
            return self.node_count
        
        # Create new node
        new_node = Node(name, node_id)
        
        # Initialize links for existing nodes
        for node in self.nodes:
            node.add_link()
            new_node.add_link()
        
        # Add the node's link to itself (diagonal in matrix)
        new_node.add_link()
        
        self.nodes.append(new_node)
        self.node_count += 1
        return self.node_count
    
    def add_link(self, from_name: str, to_name: str, cost: int) -> bool:
        from_idx = self.get_index(from_name)
        to_idx = self.get_index(to_name)
        
        if from_idx == -1 or to_idx == -1 or from_idx == to_idx:
            return False
        
        self.nodes[from_idx].links[to_idx].kosten = cost
        self.nodes[to_idx].links[from_idx].kosten = cost
        return True
    
    def print_topology(self):
        print(f"Graph {self.name} {{")
        
        # Print node IDs
        print("  // Node-IDs")
        for node in self.nodes:
            print(f"  {node.name} = {node.node_id};")
        
        # Print links
        print("\n  // Links and costs")
        for i in range(self.node_count):
            for j in range(i + 1, self.node_count):
                if self.nodes[i].links[j].kosten > 0:
                    print(f"  {self.nodes[i].name} - {self.nodes[j].name} : {self.nodes[i].links[j].kosten};")
        
        print("}")

class GraphParser:
    @staticmethod
    def parse_file(filename: str) -> Optional[Graph]:
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            in_graph = False
            graph = None
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines, comments, and lines with just whitespace
                if not line or line.startswith("//") or line.isspace():
                    continue
                
                # Check for graph start
                if line.startswith("Graph ") and "{" in line:
                    in_graph = True
                    graph_name = line[6:line.find("{")].strip()
                    graph = Graph(graph_name)
                    continue
                
                # Check for graph end
                if line == "}" and in_graph:
                    in_graph = False
                    continue
                
                if in_graph and graph is not None:
                    # Add nodes
                    if "=" in line and ";" in line and "-" not in line:
                        parts = line.split("=")
                        node_name = parts[0].strip()
                        node_id = int(parts[1].strip().rstrip(";"))
                        
                        if not node_name[0].isalpha():
                            print(f"Invalid node name: {node_name}")
                            continue
                        
                        if node_id <= 0 or node_id > MAX_NODE_ID:
                            print(f"Invalid node ID: {node_id}")
                            continue
                        
                        graph.append_node(node_name, node_id)
                    
                    # Add Links
                    elif "-" in line and ":" in line and ";" in line:
                        parts = line.split("-")
                        node1_name = parts[0].strip()
                        
                        rest = parts[1].split(":")
                        node2_name = rest[0].strip()
                        cost = int(rest[1].strip().rstrip(";"))
                        
                        if cost <= 0 or cost > MAX_KOSTEN:
                            print(f"Invalid link cost: {cost}")
                            continue
                        
                        node1_idx = graph.get_index(node1_name)
                        node2_idx = graph.get_index(node2_name)
                        
                        if node1_idx == -1:
                            graph.append_node(node1_name, MAX_NODE_ID)
                        
                        if node2_idx == -1:
                            graph.append_node(node2_name, MAX_NODE_ID)
                        
                        # Add bidirectional link
                        graph.add_link(node1_name, node2_name, cost)
            
            return graph
        
        except Exception as e:
            print(f"Error parsing graph file: {e}")
            return None

class SpanningTreeSimulator:
    def __init__(self, graph: Graph):
        self.graph = graph
    
    def initialize_nodes_to_be_root(self):
        for i in range(self.graph.node_count):
            self.graph.nodes[i].next_hop = i  
            for k in range(self.graph.node_count):
                if self.graph.nodes[i].links[k].kosten > 0:
                    self.graph.nodes[i].links[k].root_id = self.graph.nodes[i].node_id
                    self.graph.nodes[i].links[k].summe_kosten = 0
    
    def sptree(self, node_idx: int):
        if node_idx < 0 or node_idx >= self.graph.node_count:
            return
        
        node = self.graph.nodes[node_idx]
        node.msg_cnt += 1
        
        # Find best path to root from all link offers
        best_root_id = node.node_id
        best_path_cost = 0
        best_next_hop = node_idx  # Default to self
        
        for i in range(self.graph.node_count):
            if node.links[i].kosten == 0:
                continue
            
            link = node.links[i]
            total_cost = link.summe_kosten + node.links[i].kosten
            
            # Better root ID
            if link.root_id < best_root_id:
                best_root_id = link.root_id
                best_path_cost = total_cost
                best_next_hop = i
            # Same root ID but better path
            elif link.root_id == best_root_id and total_cost < best_path_cost:
                best_path_cost = total_cost
                best_next_hop = i
        
        # Update next hop
        node.next_hop = best_next_hop
        
        # Broadcast new information to neighbors
        for i in range(self.graph.node_count):
            if node.links[i].kosten > 0:
                self.graph.nodes[i].links[node_idx].root_id = best_root_id
                self.graph.nodes[i].links[node_idx].summe_kosten = best_path_cost
    
    def simulate(self, iterations: int) -> bool:
        self.initialize_nodes_to_be_root()
        
        # Seed random number with system time
        random.seed(time.time())
        
        # Run algorithm iterations
        for _ in range(iterations):
            node_idx = random.randint(0, self.graph.node_count - 1)
            self.sptree(node_idx)
        
        # Check convergence
        root_id = None
        for node in self.graph.nodes:
            if root_id is None:
                root_id = node.links[node.next_hop].root_id
            elif root_id != node.links[node.next_hop].root_id:
                return False  # Not converged
        
        return True  # Converged
    
    def print_spanning_tree(self):
        # Find root
        root_idx = -1
        for i, node in enumerate(self.graph.nodes):
            if node.next_hop == i and node.node_id == node.links[i].root_id:
                root_idx = i
                break
        
        if root_idx == -1:
            print("No root found!")
            return
        
        print(f"Spanning-Tree of {self.graph.name} {{")
        print(f"  Root: {self.graph.nodes[root_idx].name};")
        
        # Print all edges 
        for i in range(self.graph.node_count):
            if i != root_idx and self.graph.nodes[i].next_hop != i:
                next_hop = self.graph.nodes[i].next_hop
                print(f"  {self.graph.nodes[i].name} - {self.graph.nodes[next_hop].name};")
        
        print("}")

def main():
    filename = "input.txt"
    graph = GraphParser.parse_file(filename)
    
    if graph is None:
        print(f"Failed to load graph from {filename}")
        return
    
    print(f"Loaded graph '{graph.name}' with {graph.node_count} nodes")
    graph.print_topology()
    
    # Run simulation
    simulator = SpanningTreeSimulator(graph)
    iterations = graph.node_count * 10  # Heuristic for convergence
    
    if simulator.simulate(iterations):
        print("\nSpanning tree algorithm converged!")
        simulator.print_spanning_tree()
    else:
        print("\nSpanning tree algorithm did not converge.")

if __name__ == "__main__":
    main()
