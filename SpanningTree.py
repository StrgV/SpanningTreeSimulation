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
        
        # Initialize links for existing nodes (add column)
        for node in self.nodes:
            node.add_link()
        # Initialize links for new node (add row)
        for _ in range(self.node_count):
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
            print(f"Warning: Could not add link {from_name}-{to_name}. Indices: {from_idx}, {to_idx}")
            return False
        
        # Ensure link lists are long enough (should be handled by append_node)
        if to_idx >= len(self.nodes[from_idx].links) or from_idx >= len(self.nodes[to_idx].links):
             print(f"Error: Link index out of bounds for {from_name}-{to_name}.")
             return False

        self.nodes[from_idx].links[to_idx].kosten = cost
        self.nodes[to_idx].links[from_idx].kosten = cost
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
                if self.nodes[i].links[j].kosten > 0 and i != j:
                    link_key = tuple(sorted((self.nodes[i].name, self.nodes[j].name)))
                    if link_key not in printed_links:
                        print(f"  {self.nodes[i].name} - {self.nodes[j].name} : {self.nodes[i].links[j].kosten};")
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
            link_definitions = [] 

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

                        if not node_name or not node_name[0].isalpha():
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
                        
                        link_definitions.append((node1_name, node2_name, cost))

            # After parsing all nodes, add the links
            if graph:
                for node1, node2, cost in link_definitions:
                    if not graph.add_link(node1, node2, cost):
                         print(f"Failed to add link {node1}-{node2} after parsing.")

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
            node.next_hop = i  # Initially, each node thinks it's the root
            node.msg_cnt = 0
            # Initialize the information *received* by node 'i' *from* node 'k'
            for k in range(self.graph.node_count):
                 # Check if link exists (cost > 0) before initializing received info
                 # Need to check both directions as add_link sets both
                 if k < len(node.links) and self.graph.nodes[k].node_id is not None:
                      # Simulate initial broadcast: k advertises itself as root with cost 0
                      node.links[k].root_id = self.graph.nodes[k].node_id
                      node.links[k].summe_kosten = 0
                 elif k < len(node.links):
                      # Handle cases where a node might have been created but ID not set?
                      # Or link list size mismatch - should not happen with corrected append_node
                      node.links[k].root_id = MAX_NODE_ID + 1 # Invalid ID
                      node.links[k].summe_kosten = MAX_KOSTEN + 1 # Invalid cost


    def sptree(self, node_idx: int):
        """Performs one STP step for the given node."""
        if not (0 <= node_idx < self.graph.node_count):
            return
        
        node = self.graph.nodes[node_idx]
        node.msg_cnt += 1
        
        # Find best path to root based on information *received* from neighbors
        # Start by assuming the current node itself is the best root option
        best_root_id = node.node_id
        best_path_cost = 0 # Cost to reach the root (0 if self is root)
        best_next_hop = node_idx  # Default to self

        for neighbor_idx in range(self.graph.node_count):
            # Skip non-neighbors and self
            if neighbor_idx == node_idx or self.graph.nodes[node_idx].links[neighbor_idx].kosten == 0:
                continue
            
            # Info received *from* neighbor_idx
            received_link_info = node.links[neighbor_idx]
            # Cost of the direct link *to* neighbor_idx
            link_cost = self.graph.nodes[node_idx].links[neighbor_idx].kosten

            # Total cost to reach the root advertised by the neighbor
            total_cost_via_neighbor = received_link_info.summe_kosten + link_cost
            
            # Decision Logic:
            # 1. Is the neighbor advertising a root with a lower ID?
            if received_link_info.root_id < best_root_id:
                best_root_id = received_link_info.root_id
                best_path_cost = total_cost_via_neighbor
                best_next_hop = neighbor_idx
            # 2. Same root ID, but is the path through this neighbor shorter?
            elif received_link_info.root_id == best_root_id and total_cost_via_neighbor < best_path_cost:
                # best_root_id remains the same
                best_path_cost = total_cost_via_neighbor
                best_next_hop = neighbor_idx
            # 3. Tie-breaking (optional but good practice): If root ID and cost are equal,
            #    prefer the neighbor with the lower Node ID.
            elif received_link_info.root_id == best_root_id and \
                 total_cost_via_neighbor == best_path_cost and \
                 self.graph.nodes[neighbor_idx].node_id < self.graph.nodes[best_next_hop].node_id:
                 best_next_hop = neighbor_idx


        # Update the node's chosen next hop
        node.next_hop = best_next_hop
        
        # Broadcast this node's *new* understanding of the path to the root to its neighbors
        # The info sent is: ("My chosen root is best_root_id, and my cost to reach it is best_path_cost")
        my_advertised_root_id = best_root_id
        my_advertised_cost = best_path_cost

        for neighbor_idx in range(self.graph.node_count):
             # Check if neighbor_idx is actually a neighbor
            if neighbor_idx != node_idx and self.graph.nodes[node_idx].links[neighbor_idx].kosten > 0:
                # Update the information that neighbor_idx *receives from* node_idx
                neighbor_node = self.graph.nodes[neighbor_idx]
                neighbor_node.links[node_idx].root_id = my_advertised_root_id
                neighbor_node.links[node_idx].summe_kosten = my_advertised_cost
    
    def simulate(self, iterations: int, debug_interval: Optional[int] = None) -> bool:
        """Runs the STP simulation."""
        self.initialize_nodes_to_be_root()
        
        if self.graph.node_count == 0:
             print("Graph is empty, nothing to simulate.")
             return True # Empty graph is trivially converged

        # Seed random number with system time
        random.seed(time.time())
        
        # Run algorithm iterations
        for i in range(iterations):
            node_idx = random.randint(0, self.graph.node_count - 1)
            self.sptree(node_idx)

            if debug_interval and (i + 1) % debug_interval == 0:
                 print(f"\n--- Iteration {i+1} ---")
                 self.print_current_state()

            # Optional: Check for convergence early (can slow down simulation)
            # if i > self.graph.node_count * 2 and self._is_converged(): # Check after some initial churn
            #     print(f"Converged early after {i+1} iterations.")
            #     return True

        # Final convergence check after all iterations
        converged = self._is_converged()
        if debug_interval:
             print("\n--- Final State ---")
             self.print_current_state()
        return converged

    def _is_converged(self) -> bool:
        """Checks if the STP algorithm has reached a stable state."""
        if self.graph.node_count == 0:
            return True

        # Find the expected root (node with the lowest ID)
        expected_root_node = min(self.graph.nodes, key=lambda n: n.node_id)
        expected_root_id = expected_root_node.node_id

        for i, node in enumerate(self.graph.nodes):
            # 1. Check if the root node points to itself
            if node.node_id == expected_root_id:
                if node.next_hop != i:
                    # print(f"Debug: Root node {node.name} does not point to self (next_hop={node.next_hop})")
                    return False
            # 2. Check if non-root nodes point somewhere else
            elif node.next_hop == i:
                 # print(f"Debug: Non-root node {node.name} points to self.")
                 return False

            # 3. Check if all nodes agree on the root ID based on their next hop's advertisement
            #    This part is tricky because the 'received' info might lag slightly.
            #    A better check focuses on the stability of next_hop pointers,
            #    but for simplicity after enough iterations, we check advertised root.
            #    Get the root ID this node *thinks* is the best based on its state
            current_best_root_id = node.node_id # Assume self initially
            current_best_cost = 0
            if node.next_hop != i: # If not pointing to self, use next hop's info
                 # Info received *from* the next hop
                 received_info = node.links[node.next_hop]
                 current_best_root_id = received_info.root_id
                 # current_best_cost = received_info.summe_kosten + node.links[node.next_hop].kosten

            if current_best_root_id != expected_root_id:
                 # print(f"Debug: Node {node.name} believes root is {current_best_root_id}, expected {expected_root_id}")
                 return False

        return True

    def print_current_state(self):
         """Prints the current next_hop and perceived root for each node."""
         print("Node States:")
         for i, node in enumerate(self.graph.nodes):
              next_hop_node = self.graph.nodes[node.next_hop]
              # Determine perceived root ID based on current state
              perceived_root_id = node.node_id
              perceived_cost = 0
              if node.next_hop != i:
                   received_info = node.links[node.next_hop]
                   perceived_root_id = received_info.root_id
                   perceived_cost = received_info.summe_kosten + node.links[node.next_hop].kosten

              print(f"  {node.name}({node.node_id}): next_hop -> {next_hop_node.name}({next_hop_node.node_id}), believes root={perceived_root_id} (cost={perceived_cost}), msg_cnt={node.msg_cnt}")


    def print_spanning_tree(self):
        """Prints the calculated spanning tree."""
        # Find root - the node pointing to itself
        root_idx = -1
        for i, node in enumerate(self.graph.nodes):
            if node.next_hop == i: # The root node points to itself after convergence
                root_idx = i
                # Optional: Verify it's the lowest ID node
                min_id_node = min(self.graph.nodes, key=lambda n: n.node_id)
                if node.node_id != min_id_node.node_id:
                     print(f"Warning: Node {node.name} points to self but isn't lowest ID node ({min_id_node.name}). STP might not be fully converged or graph issue.")
                break # Found the node pointing to itself
        
        if root_idx == -1:
            print("Error: No root node found (no node points to itself)! STP did not converge correctly.")
            return
        
        root_node = self.graph.nodes[root_idx]
        print(f"\nSpanning-Tree of {self.graph.name} {{")
        print(f"  Root: {root_node.name};")
        
        # Print all edges in the spanning tree (non-root nodes pointing to their next hop)
        print("  Edges:")
        for i in range(self.graph.node_count):
            if i != root_idx: # Exclude the root node itself
                node = self.graph.nodes[i]
                # Ensure next_hop is valid before accessing
                if 0 <= node.next_hop < self.graph.node_count:
                     next_hop_node = self.graph.nodes[node.next_hop]
                     print(f"  {node.name} - {next_hop_node.name};")
                else:
                     print(f"  Warning: Node {node.name} has invalid next_hop index {node.next_hop}")

        print("}")

def main():
    filename = "input.txt" 
    graph = GraphParser.parse_file(filename)
    
    print(f"Loaded graph '{graph.name}' with {graph.node_count} nodes.")
    graph.print_topology()
    
    # Run simulation
    simulator = SpanningTreeSimulator(graph)
    # Increase iterations significantly for robustness, especially with random selection
    iterations = graph.node_count * 50
    debug_interval = iterations // 10 # Print state 10 times during simulation

    print(f"\nStarting simulation for {iterations} iterations...")
    
    if simulator.simulate(iterations, debug_interval=debug_interval):
        print("\nSpanning tree algorithm converged!")
        simulator.print_spanning_tree()
    else:
        print("\nSpanning tree algorithm did NOT converge after {iterations} iterations.")
        print("Check the final state above. Possible issues: insufficient iterations, graph partitioning, or subtle bug.")
        # Still try to print the tree, it might be partially correct
        simulator.print_spanning_tree()


if __name__ == "__main__":
    main()
