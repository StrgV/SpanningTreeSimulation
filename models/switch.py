from .link import Link

class Switch:
    def __init__(self, name: str, switch_id: int):
        self.name = name
        self.switch_id = switch_id
        self.links = []  
        self.next_hop = 0 
        self.msg_cnt = 0 

    def add_link(self, cost=0):
        self.links.append(Link(cost))

