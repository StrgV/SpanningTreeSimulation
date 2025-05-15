import random
import time
from typing import Dict, List, Tuple, Optional
from util.graph_parser import GraphParser
from models.graph import Graph
from tests.graph_tests import test_graph


class Simulation:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.expected_root_id = None
    
    def initialize_switches_to_be_root(self):
        if self.graph.switch_count == 0:
            return
            
        self.expected_root_id = min(switch.switch_id for switch in self.graph.switches)
            
        for i in range(self.graph.switch_count):
            switch = self.graph.switches[i]
            switch.next_hop = i 
            switch.msg_cnt = 0
            
            # Initialize the information received by switch i from switch k
            for k in range(self.graph.switch_count):
                if k < len(switch.links):
                    switch.links[k].root_id = self.graph.switches[k].switch_id
                    switch.links[k].sum_cost = 2

    def _find_best_path(self, switch_idx: int) -> Tuple[int, int, int]:
        switch = self.graph.switches[switch_idx]
        best_path_tuple = (switch.switch_id, 0, switch.switch_id)
        best_hop_idx = switch_idx  # Default to self

        for neighbor_idx in range(self.graph.switch_count):
            link_to_neighbor = switch.links[neighbor_idx]
            # Skip non-neighbors and self
            if neighbor_idx == switch_idx or link_to_neighbor.cost == 0:
                continue

            neighbor_switch = self.graph.switches[neighbor_idx]
            received_info = switch.links[neighbor_idx]

            total_cost_via_neighbor = received_info.sum_cost + link_to_neighbor.cost
            current_path_tuple = (received_info.root_id, total_cost_via_neighbor, neighbor_switch.switch_id)

            if current_path_tuple < best_path_tuple:
                best_path_tuple = current_path_tuple
                best_hop_idx = neighbor_idx

        # Extract results from the best tuple found
        best_root_id = best_path_tuple[0]
        best_path_cost = best_path_tuple[1]

        return best_root_id, best_path_cost, best_hop_idx

    def sptree_iteration(self, switch_idx: int):
        if not (0 <= switch_idx < self.graph.switch_count):
            return

        switch = self.graph.switches[switch_idx]
        switch.msg_cnt += 1

        # Find the best path for switch
        my_advertised_root_id, my_advertised_cost, best_hop_idx = self._find_best_path(switch_idx)

        # Update the switches chosen next hop index
        switch.next_hop = best_hop_idx

        # Broadcast this switches information to its neighbors
        for neighbor_idx in range(self.graph.switch_count):
            # Check if neighbor_idx is actually a neighbor
            if neighbor_idx != switch_idx and switch.links[neighbor_idx].cost > 0:
                # Update the information that neighbor_idx *receives from* switch_idx
                neighbor_switch = self.graph.switches[neighbor_idx]
                if switch_idx < len(neighbor_switch.links):
                    neighbor_switch.links[switch_idx].root_id = my_advertised_root_id
                    neighbor_switch.links[switch_idx].sum_cost = my_advertised_cost
            
    def simulate(self, iterations: int, debug_interval: Optional[int] = None) -> bool:
        self.initialize_switches_to_be_root()
        
        if self.graph.switch_count == 0:
            print("Graph is empty, nothing to simulate.")
            return True

        # Seed for random switch selection
        random.seed(time.time())
        
        # Run algorithm iterations
        for i in range(iterations):
            switch_idx = random.randint(0, self.graph.switch_count - 1)
            self.sptree_iteration(switch_idx)

            # Check for convergence early
            if i > self.graph.switch_count and self._is_converged():
                print(f"Converged early after {i+1} iterations.")
                return True

        # Final convergence check after all iterations
        return self._is_converged()

    def _is_converged(self) -> bool:
        if self.graph.switch_count == 0:
            return True

        if self.expected_root_id is None:
            self.expected_root_id = min(switch.switch_id for switch in self.graph.switches)

        for i in range(self.graph.switch_count):
            switch = self.graph.switches[i]

            calculated_root_id, _, calculated_best_hop_idx = self._find_best_path(i)
            
            # Check if switches root is the global root
            if calculated_root_id != self.expected_root_id:
                return False
                
            # Check if stored next_hop matches calculated best hop
            if switch.next_hop != calculated_best_hop_idx:
                return False
                
            # Root must point to itself
            if switch.switch_id == self.expected_root_id and switch.next_hop != i:
                return False

        return True

    def print_spanning_tree(self):
        root_idx = -1
        for i, switch in enumerate(self.graph.switches):
            if switch.next_hop == i:
                root_idx = i
                break
        
        if root_idx == -1:
            print("Error: No root switch found (no switch points to itself)! STP did not converge correctly.")
            return
        
        root_switch = self.graph.switches[root_idx]
        print(f"\nSpanning-Tree of {self.graph.name} {{")
        print(f"  Root: {root_switch.name};")
        
        print("  Edges:")
        for i in range(self.graph.switch_count):
            if i != root_idx: 
                switch = self.graph.switches[i]
                next_hop_switch = self.graph.switches[switch.next_hop]
                print(f"  {switch.name} - {next_hop_switch.name};")

        print("}")

def main():
    filename = "input.txt" 
    graph = GraphParser.parse_file(filename)
    
    if not graph:
        print("Failed to load graph.")
        return
    
    print(f"Loaded graph '{graph.name}' with {graph.switch_count} switches.")

    # Run tests with assertions
    try:
        test_graph(graph)
    except AssertionError as e:
        print(f"Graph test failed: {e}")
        # Decide whether to continue anyway
        if input("Continue anyway? (y/n): ").lower() != 'y':
            return

    # Run simulation
    simulator = Simulation(graph)
    iterations = graph.switch_count * 10

    print(f"\nStarting simulation for {iterations} iterations...")
    
    if simulator.simulate(iterations):
        print("\nSpanning tree algorithm converged!")
        simulator.print_spanning_tree()
    else:
        print(f"\nSpanning tree algorithm did NOT converge after {iterations} iterations.")

if __name__ == "__main__":
    main()
