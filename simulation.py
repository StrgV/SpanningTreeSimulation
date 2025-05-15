import random
import time
from typing import Tuple, Optional
from util.graph_parser import GraphParser
from models.graph import Graph
from tests.graph_tests import test_graph

MAX_MSG_PER_SWITCH = 10

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
            switch.next_hop = i  # Jeder Switch zeigt initial auf sich selbst
            switch.msg_cnt = 0
            
            # Initialisiere Switch mit seinen eigenen STP-Informationen
            switch.root_id = switch.switch_id
            switch.distance_to_root = 0
            switch.best_neighbor_id = None
            switch.received_bpdus = {}
            
            # Initialisiere BPDUs von Nachbarn
            for k in range(self.graph.switch_count):
                if k != i and switch.links[k] > 0:  # Wenn es einen Link gibt
                    neighbor = self.graph.switches[k]
                    # Initialisiere mit Default-Werten (jeder Switch denkt, er ist Root)
                    switch.receive_bpdu(k, neighbor.switch_id, 0)

    def _find_best_path(self, switch_idx: int) -> Tuple[int, int, int]:
        switch = self.graph.switches[switch_idx]
        
        # Beginne mit sich selbst als beste Option
        best_root_id = switch.switch_id
        best_path_cost = 0
        best_hop_idx = switch_idx
        
        # Prüfe alle BPDUs von allen Nachbarn
        for neighbor_idx, bpdu_info in switch.received_bpdus.items():
            received_root_id, received_distance = bpdu_info
            
            # Berechne Gesamtkosten über diesen Nachbarn
            link_cost = switch.links[neighbor_idx]
            total_cost = received_distance + link_cost
            
            # Vergleiche mit der besten bekannten Route
            if (received_root_id < best_root_id or 
                (received_root_id == best_root_id and total_cost < best_path_cost)):
                best_root_id = received_root_id
                best_path_cost = total_cost
                best_hop_idx = neighbor_idx

        return best_root_id, best_path_cost, best_hop_idx

    def sptree_iteration(self, switch_idx: int):

        switch = self.graph.switches[switch_idx]
        switch.msg_cnt += 1

        # Finde den besten Pfad für den Switch
        best_root_id, best_path_cost, best_hop_idx = self._find_best_path(switch_idx)

        # Aktualisiere die STP-Informationen des Switches
        old_root_id = switch.root_id
        old_distance = switch.distance_to_root
        
        switch.root_id = best_root_id
        switch.distance_to_root = best_path_cost
        switch.next_hop = best_hop_idx
        
        # Nur senden, wenn sich die Informationen geändert haben oder periodisch
        if old_root_id != best_root_id or old_distance != best_path_cost:
            # Sende BPDU an alle Nachbarn (außer über den Pfad zum Root)
            for neighbor_idx in range(self.graph.switch_count):
                # Überprüfe, ob neighbor_idx tatsächlich ein Nachbar ist
                if neighbor_idx != switch_idx and switch.links[neighbor_idx] > 0:
                    neighbor_switch = self.graph.switches[neighbor_idx]
                    # Aktualisiere die BPDU-Informationen, die neighbor_idx von switch_idx erhält
                    neighbor_switch.receive_bpdu(switch_idx, best_root_id, best_path_cost)
            
    def simulate(self):
        self.initialize_switches_to_be_root()
        # Seed für zufällige Switch-Auswahl
        random.seed(time.time())
        
        # Führe Algorithmus-Iterationen durch
        while not self.all_switches_sent_enough_messages(MAX_MSG_PER_SWITCH):
            switch_idx = random.randint(0, self.graph.switch_count - 1)
            self.sptree_iteration(switch_idx)

        return True
    
    def all_switches_sent_enough_messages(self, min_messages: int) -> bool:
        for switch in self.graph.switches:
            if switch.msg_cnt < min_messages:
                return False
        return True

    def print_spanning_tree(self):
        root_idx = -1
        for i, switch in enumerate(self.graph.switches):
            if switch.next_hop == i:
                root_idx = i
                break
        
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

    try:
        test_graph(graph)
    except AssertionError as e:
        print(f"Graph test failed: {e}")
        if input("Continue anyway? (y/n): ").lower() != 'y':
            return

    # Führe Simulation durch
    simulator = Simulation(graph)

    print(f"Simulating until every switch sent {MAX_MSG_PER_SWITCH} messages...")
    
    simulator.simulate()
    simulator.print_spanning_tree()
    
if __name__ == "__main__":
    main()
