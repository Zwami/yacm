from mesa import Agent
from enum import Enum

# Enhanced SIR epidemic model states
class State(Enum):
    S = 1 # Susceptible
    A = 2 # Infected, Asymptomatic
    I = 3 # Infected, Symptomatic
    R = 4 # Recovered
    # D = 5 # Deceased TODO - Add this. May need separate location?

# TODO Configurable transition probabilities for States

# Base class for agents in model
class Person(Agent):

    def __init__(self, unique_id, model, home_node):
        super().__init__(unique_id, model)
        self.state = State['S'] # by default everyone is Susceptible
        self.home_node = home_node # TODO - Need to get nodes setup

    def step(self):
        # 1. Get all other infected people on current node
        # 2. Calculate if infected
        # 3. Move
        # 4. Update infected state
        print("stepped person ", self.unique_id)

