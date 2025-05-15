class Switch:
    def __init__(self, name: str, switch_id: int):
        self.name = name
        self.switch_id = switch_id 
        self.links = [] # Liste von Links zu anderen Switches
        self.next_hop = switch_id  # Jeder Switch denkt initial, er ist der Root
        self.msg_cnt = 0 # Anzahl der gesendeten BPDUs
        
        self.root_id = switch_id  # Jeder Switch denkt initial, er ist der Root
        self.distance_to_root = 0  # Anfangs ist die Distanz zum Root (sich selbst) 0
        self.best_neighbor_id = None # ID des besten Nachbarn
        self.received_bpdus = {}  # Speichert BPDUs von Nachbarn: {neighbor_idx: (root_id, distance)}

    def add_link(self, cost=0):
        self.links.append(cost)
        
    def receive_bpdu(self, neighbor_idx: int, root_id: int, distance_to_root: int):
        self.received_bpdus[neighbor_idx] = (root_id, distance_to_root) # Empfängt BPDU-Informationen von einem Nachbarn
