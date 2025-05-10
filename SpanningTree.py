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
        self.cost = 0
        self.root_id = 0
        self.sum_cost = 0

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
        # Check if node exists already
        if self.get_index(name) != -1:
            return self.node_count
        
        new_node = Node(name, node_id)
        
        # Initialize links for existing nodes (column)
        for node in self.nodes:
            node.add_link()
        # Initialize links for new node (row)
        for _ in range(self.node_count):
             new_node.add_link()
        
        # Add the nodes link to itself
        new_node.add_link()
        
        self.nodes.append(new_node)
        self.node_count += 1
        return self.node_count
    
    def add_link(self, from_name: str, to_name: str, cost: int) -> bool:
        from_idx = self.get_index(from_name)
        to_idx = self.get_index(to_name)
        
        # Ensure link lists are long enough (should be handled by append_node)
        if to_idx >= len(self.nodes[from_idx].links) or from_idx >= len(self.nodes[to_idx].links):
             print(f"Error: Link index out of bounds for {from_name}-{to_name}.")
             return False

        self.nodes[from_idx].links[to_idx].cost = cost
        self.nodes[to_idx].links[from_idx].cost = cost
        return True
    
    def print_topology(self):
        print(f"Graph {self.name} {{")
        print("  // Node-IDs")
        for node in self.nodes:
            print(f"  {node.name} = {node.node_id};")
        print("\n  // Links and costs")
        printed_links = set()
        for i in range(self.node_count):
            for j in range(self.node_count):
                if self.nodes[i].links[j].cost > 0 and i != j:
                    link_key = tuple(sorted((self.nodes[i].name, self.nodes[j].name)))
                    if link_key not in printed_links:
                        print(f"  {self.nodes[i].name} - {self.nodes[j].name} : {self.nodes[i].links[j].cost};")
                        printed_links.add(link_key)
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
                        node_id_str = parts[1].strip().rstrip(";")
                        try:
                            node_id = int(node_id_str)
                        except ValueError:
                            print(f"Invalid node ID format: {node_id_str}")
                            continue

                        if not node_name or not node_name[0].isalpha() or len(node_name) > MAX_IDENT:
                            print(f"Invalid node name: {node_name}")
                            continue
                        
                        if node_id <= 0 or node_id > MAX_NODE_ID:
                            print(f"Invalid node ID value: {node_id}")
                            continue
                        
                        graph.append_node(node_name, node_id)
                    
                    # Store Link definitions temporarily
                    elif "-" in line and ":" in line and ";" in line:
                        parts = line.split("-")
                        node1_name = parts[0].strip()
                        
                        rest = parts[1].split(":")
                        node2_name = rest[0].strip()
                        cost_str = rest[1].strip().rstrip(";")
                        try:
                             cost = int(cost_str)
                        except ValueError:
                             print(f"Invalid link cost format: {cost_str}")
                             continue

                        if cost <= 0 or cost > MAX_KOSTEN:
                            print(f"Invalid link cost value: {cost}")
                            continue

                        graph.add_link(node1_name, node2_name, cost)

            return graph
        
        except FileNotFoundError:
             print(f"Error: File not found at {filename}")
             return None
        except Exception as e:
            print(f"Error parsing graph file '{filename}': {e}")
            return None

class SpanningTreeSimulator:
    def __init__(self, graph: Graph):
        self.graph = graph
    
    def initialize_nodes_to_be_root(self):
        if self.graph.node_count == 0:
             return
        for i in range(self.graph.node_count):
            node = self.graph.nodes[i]
            node.next_hop = i  
            node.msg_cnt = 0
            # Initialize the information received by node 'i' *from* node 'k'
            for k in range(self.graph.node_count):
                 if k < len(node.links) and self.graph.nodes[k].node_id is not None:
                      node.links[k].root_id = self.graph.nodes[k].node_id
                      node.links[k].sum_cost = 2

    def _find_best_path(self, node_idx: int) -> Tuple[int, int, int]:
        node = self.graph.nodes[node_idx]

        best_path_tuple = (node.node_id, 0, node.node_id)
        best_hop_idx = node_idx # Default to self

        for neighbor_idx in range(self.graph.node_count):
            # Skip non-neighbors and self
            link_to_neighbor = node.links[neighbor_idx]
            if neighbor_idx == node_idx or link_to_neighbor.cost == 0:
                continue

            neighbor_node = self.graph.nodes[neighbor_idx]
            # Info received *from* neighbor_idx
            received_info = node.links[neighbor_idx]

            # Calculate path info if using this neighbor
            total_cost_via_neighbor = received_info.sum_cost + link_to_neighbor.cost
            # Create the tuple representing the path offered by this neighbor
            current_path_tuple = (received_info.root_id, total_cost_via_neighbor, neighbor_node.node_id)

            # Python's tuple comparison does exactly what STP needs
            if current_path_tuple < best_path_tuple:
                best_path_tuple = current_path_tuple
                best_hop_idx = neighbor_idx

        # Extract results from the best tuple found
        best_root_id = best_path_tuple[0]
        best_path_cost = best_path_tuple[1] # This is the cost *from this node*

        return best_root_id, best_path_cost, best_hop_idx

    # Spanning tree iteration for one node
    def sptree(self, node_idx: int):
        """Performs one STP step for the given node."""
        if not (0 <= node_idx < self.graph.node_count):
            return

        node = self.graph.nodes[node_idx]
        node.msg_cnt += 1

        # 1. Find the best path using the helper method
        my_advertised_root_id, my_advertised_cost, best_hop_idx = self._find_best_path(node_idx)

        # 2. Update the node's chosen next hop index
        node.next_hop = best_hop_idx

        # 3. Broadcast this node's *new* understanding to its neighbors
        for neighbor_idx in range(self.graph.node_count):
            # Check if neighbor_idx is actually a neighbor
            if neighbor_idx != node_idx and node.links[neighbor_idx].cost > 0:
                # Update the information that neighbor_idx *receives from* node_idx
                neighbor_node = self.graph.nodes[neighbor_idx]
                if node_idx < len(neighbor_node.links):
                    neighbor_node.links[node_idx].root_id = my_advertised_root_id
                    neighbor_node.links[node_idx].sum_cost = my_advertised_cost
            
    # Spanning tree simulation
    def simulate(self, iterations: int, debug_interval: Optional[int] = None) -> bool:
        self.initialize_nodes_to_be_root()
        
        if self.graph.node_count == 0:
            print("Graph is empty, nothing to simulate.")
            return True

        random.seed(time.time())
        
        # Run algorithm iterations
        for i in range(iterations):
            node_idx = random.randint(0, self.graph.node_count - 1)
            self.sptree(node_idx)

            # Check for convergence early
            if i > self.graph.node_count * 2 and self._is_converged(): # Check after some initial churn
                print(f"Converged early after {i+1} iterations.")
                return True

        # Final convergence check after all iterations
        converged = self._is_converged()
        return converged

    def _is_converged(self) -> bool:
        if self.graph.node_count == 0:
            return True

        try:
            # Find the expected root (node with the lowest ID)
            expected_root_node = min(self.graph.nodes, key=lambda n: n.node_id)
            expected_root_id = expected_root_node.node_id
        except ValueError: # Handle empty graph case if min() fails
            return True

        for i in range(self.graph.node_count):
            node = self.graph.nodes[i]

            # Calculate what the node *should* decide based on current info
            calculated_root_id, _, calculated_best_hop_idx = self._find_best_path(i)
            # 1. Does the node's calculation agree on the global root?
            if calculated_root_id != expected_root_id:
                return False
            # 2. Does the node's current stored next_hop match the calculated best hop?
            if node.next_hop != calculated_best_hop_idx:
                return False
            # 3. Explicit check: Root must point to itself
            if node.node_id == expected_root_id and node.next_hop != i:
                return False

        # If all nodes pass the checks
        return True

    # Print the finished spanning tree 
    def print_spanning_tree(self):
        root_idx = -1
        for i, node in enumerate(self.graph.nodes):
            if node.next_hop == i:
                root_idx = i
        
        if root_idx == -1:
            print("Error: No root node found (no node points to itself)! STP did not converge correctly.")
            return
        
        root_node = self.graph.nodes[root_idx]
        print(f"\nSpanning-Tree of {self.graph.name} {{")
        print(f"  Root: {root_node.name};")
        
        print("  Edges:")
        for i in range(self.graph.node_count):
            if i != root_idx: 
                node = self.graph.nodes[i]
                next_hop_node = self.graph.nodes[node.next_hop]
                print(f"  {node.name} - {next_hop_node.name};")

        print("}")

def main():
    filename = "input.txt" 
    graph = GraphParser.parse_file(filename)
    
    print(f"Loaded graph '{graph.name}' with {graph.node_count} nodes.")
    graph.print_topology()
    
    # Run simulation
    simulator = SpanningTreeSimulator(graph)
    iterations = graph.node_count * 10

    print(f"\nStarting simulation for {iterations} iterations...")
    
    if simulator.simulate(iterations):
        print("\nSpanning tree algorithm converged!")
        simulator.print_spanning_tree()
    else:
        print("\nSpanning tree algorithm did NOT converge after {iterations} iterations.")

if __name__ == "__main__":
    main()
