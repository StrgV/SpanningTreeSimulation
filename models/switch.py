class Switch:
    def __init__(self, name: str, switch_id: int):
        self.name = name
        self.switch_id = switch_id
        self.links = []  
        self.next_hop = switch_id 
        self.msg_cnt = 0
        
        # STP-spezifische Eigenschaften (statt in Links)
        self.root_id = switch_id  # Jeder Switch denkt initial, er ist der Root
        self.distance_to_root = 0  # Anfangs ist die Distanz zum Root (sich selbst) 0
        self.best_neighbor_id = None
        self.received_bpdus = {}  # Speichert BPDUs von Nachbarn: {neighbor_idx: (root_id, distance)}

    def add_link(self, cost=0):
        self.links.append(cost)  # Links speichern nur noch den Kostenwert
        
    def receive_bpdu(self, neighbor_idx: int, root_id: int, distance_to_root: int):
        """Empfängt BPDU-Informationen von einem Nachbarn"""
        self.received_bpdus[neighbor_idx] = (root_id, distance_to_root)
