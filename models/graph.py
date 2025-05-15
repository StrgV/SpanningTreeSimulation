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
    
    def append_switch(self, name: str, switch_id: int):
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
        return
    
    def add_link(self, from_name: str, to_name: str, cost: int):
        from_idx = self.get_index(from_name)
        to_idx = self.get_index(to_name)
        
        if from_idx == -1 or to_idx == -1:
            print(f"Error: Switch not found for link {from_name}-{to_name}.")
            return

        self.switches[from_idx].links[to_idx] = cost  # Jetzt direkt Kosten speichern
        self.switches[to_idx].links[from_idx] = cost
        return 