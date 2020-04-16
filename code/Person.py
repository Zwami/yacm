from mesa import Agent
from enum import Enum

# Enhanced SIR epidemic model states
class State(Enum):
    S = 1 # Susceptible
    A = 2 # Infected, Asymptomatic
    I = 3 # Infected, Symptomatic
    R = 4 # Recovered
    # D = 5 # Deceased TODO - Add this. May need separate location?

class PopType(Enum):
    C = 1 # Control
    D = 2 # Doctor
    E = 3 # Essential

# Agent class
class Person(Agent):

    def __init__(self, unique_id, model, home_node, pop_type: PopType, init_state: State, well_trans, sick_trans):
        super().__init__(unique_id, model)
        self.home_node = home_node
        self.pop_type = pop_type
        self.state = init_state
        self.well_trans = well_trans
        self.sick_trans = sick_trans
        print("Agent ", self.unique_id, " home node ", self.home_node)
        print(self.state)
        print(self.pop_type)
        # I believe Mesa keeps track of current location, so should not need to define as a member

    def step(self):
        # 1. Get all other infected people on current node
        # 2. Calculate if infected
        # 3. Move
        # 4. Update infected state
        pass
