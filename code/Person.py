from mesa import Agent
from enum import Enum

# Enhanced SIR epidemic model states
class State(Enum):
    S = 1 # Susceptible
    A = 2 # Infected, Asymptomatic
    I = 3 # Infected, Symptomatic
    R = 4 # Recovered
    D = 5 # Deceased

# TODO Configurable transition probabilities for States

# Base class for agents in model
class Person(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = State['S'] # by default everyone is Susceptible
        self.home_node = 0 # TODO - Need to get nodes setup

    def get_state(self):
        return self.state

    # public method?
    def update_state(self, new_state: State):
        self.state = new_state

    def step(self):
        # TODO Move
        # TODO state transition
        pass

