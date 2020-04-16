from enum import Enum

class NodeType(Enum):
    H = 1 # Home
    S = 2 # Service (essential)
    C = 3 # Clinic (Hospital)

class Location:

    def __init__(self, loc_id, node_type: NodeType):
        self.loc_id = loc_id
        self.node_type = node_type
