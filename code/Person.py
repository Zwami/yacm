from mesa import Agent
from enum import Enum
import random

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
        self.next_state = self.state
        print("Agent ", self.unique_id, " home node ", self.home_node)
        print(self.state)
        print(self.pop_type)
        # I believe Mesa keeps track of current location, so should not need to define as a member

    def step(self):
        # 1. Determine disease progression
        # 1a. Get all other infected people on current node (if susceptible)
        if (self.state == State.S):
            p_avoids_infection = 1.0
            others = self.model.grid.get_cell_list_contents([self.pos])
            for i in others:
                if (i.state == State.A or i.state == State.I):
                    p_avoids_infection *= (1.0 - self.model.p_infect)
            if (random.random() > p_avoids_infection):
                self.next_state = State.A
                print("Agent : ", self.unique_id, " infected!")
        # 1b. Calculate updated disease state otherwise
        else: # Part of infection chain (TODO, make sure this is appropriately represented)
            next_state_val = self.model.state_transition(self.model.inf_trans,self.state.value - 2)
            self.next_state = State(next_state_val+2)
            print("Agent : ", self.unique_id, " next state ", self.next_state)
        # 2. Move
        curr_loc = self.model.grid_location_type(self.pos).value
        if (self.state != State.I):
            next_loc = self.model.state_transition(self.well_trans,curr_loc-1)
        else:
            next_loc = self.model.state_transition(self.sick_trans,curr_loc-1)
        if (next_loc == 0): # home
            self.model.grid.move_agent(self,(self.home_node["x"],self.home_node["y"]))
        elif (next_loc == 1): # service, pick at random 
            s = random.choice(self.model.services)
            self.model.grid.move_agent(self,(s["x"],s["y"]))
        else:
            s = random.choice(self.model.clinics)
            self.model.grid.move_agent(self,(s["x"],s["y"]))

        # 3. Update infected state
        self.state = self.next_state
