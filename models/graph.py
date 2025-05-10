from typing import List
from .switch import Switch

class Graph:
    def __init__(self, name: str = ""):
        self.name = name
        self.switches = []  
        self.switch_count = 0
        self.name_to_index = {}
    
    def get_index(self, name: str) -> int:
        return self.name_to_index.get(name, -1)
    
    def append_switch(self, name: str, switch_id: int) -> int:
        # Check if switch exists already
        if name in self.name_to_index:
            return self.switch_count
        
        new_switch = Switch(name, switch_id)
        
        # Initialize links for existing switches (column)
        for switch in self.switches:
            switch.add_link()
        
        # Initialize links for new switch (row)
        for _ in range(self.switch_count + 1):
            new_switch.add_link()
        
        self.switches.append(new_switch)
        self.name_to_index[name] = self.switch_count
        self.switch_count += 1
        return self.switch_count
    
    def add_link(self, from_name: str, to_name: str, cost: int) -> bool:
        from_idx = self.get_index(from_name)
        to_idx = self.get_index(to_name)
        
        if from_idx == -1 or to_idx == -1:
            print(f"Error: Switch not found for link {from_name}-{to_name}.")
            return False

        self.switches[from_idx].links[to_idx].cost = cost
        self.switches[to_idx].links[from_idx].cost = cost
        return True
    
    def print_topology(self):
        print(f"Graph {self.name} {{")
        print("  // Switch-IDs")
        for switch in self.switches:
            print(f"  {switch.name} = {switch.switch_id};")
        
        print("\n  // Links and costs")
        printed_links = set()
        for i in range(self.switch_count):
            for j in range(self.switch_count):
                if self.switches[i].links[j].cost > 0 and i != j:
                    link_key = tuple(sorted((self.switches[i].name, self.switches[j].name)))
                    if link_key not in printed_links:
                        print(f"  {self.switches[i].name} - {self.switches[j].name} : {self.switches[i].links[j].cost};")
                        printed_links.add(link_key)
        print("}")