from typing import Optional
from models.graph import Graph

# Constants
MAX_IDENT = 20
MAX_ITEMS = 100
MAX_COST = 1000
MAX_SWITCH_ID = 10000

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
                
                # graph start
                if line.startswith("Graph ") and "{" in line:
                    in_graph = True
                    graph_name = line[6:line.find("{")].strip()
                    graph = Graph(graph_name)
                    continue
                
                # graph end
                if line == "}" and in_graph:
                    in_graph = False
                    continue
                
                if in_graph and graph is not None:
                    # Switches hinzufügen
                    if "=" in line and ";" in line and "-" not in line:
                        parts = line.split("=")
                        switch_name = parts[0].strip()
                        switch_id_str = parts[1].strip().rstrip(";")
                        try:
                            switch_id = int(switch_id_str)
                        except ValueError:
                            print(f"Invalid switch ID format: {switch_id_str}")
                            continue

                        if not switch_name or not switch_name[0].isalpha() or len(switch_name) > MAX_IDENT:
                            print(f"Invalid switch name: {switch_name}")
                            continue
                        
                        if switch_id <= 0 or switch_id > MAX_SWITCH_ID:
                            print(f"Invalid switch ID value: {switch_id}")
                            continue
                        
                        graph.append_switch(switch_name, switch_id)


                    elif "-" in line and ":" in line and ";" in line:
                        # Links hinzugügen
                        parts = line.split("-")
                        switch1_name = parts[0].strip()
                        
                        rest = parts[1].split(":")
                        switch2_name = rest[0].strip()
                        cost_str = rest[1].strip().rstrip(";")
                        try:
                            cost = int(cost_str)
                        except ValueError:
                            print(f"Invalid link cost format: {cost_str}")
                            continue

                        if cost <= 0 or cost > MAX_COST:
                            print(f"Invalid link cost value: {cost}")
                            continue

                        graph.add_link(switch1_name, switch2_name, cost)

            return graph
        
        except FileNotFoundError:
            print(f"Error: File not found at {filename}")
            return None
        except Exception as e:
            print(f"Error parsing graph file '{filename}': {e}")
            return None