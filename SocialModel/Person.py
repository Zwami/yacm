from mesa import Agent
from enum import Enum
from SocialModel.Location import NodeType
import random

# Enhanced SIR epidemic model states
class State(Enum):
    S = 1 # Susceptible
    A = 2 # Infected, Asymptomatic
    I = 3 # Infected, Symptomatic
    R = 4 # Recovered

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
        self.current_loc = NodeType.H
        self.infectability = 0.
        #print("Agent ", self.unique_id, " home node ", self.home_node)
        #print(self.state)
        #print(self.pop_type)
        # I believe Mesa keeps track of current location, so should not need to define as a member

    def step(self):
        # 1. Determine disease progression
        # 1a. Get all other infected people on current node (if susceptible)
        self.__calculate_next_state()
        # 2. Move
        self.__calculate_movement()
        # 3. Update infected state
        if (self.state != State.I and self.next_state == State.I): #known infected
            self.model.known_cases_this_step += 1
        if (self.state != State.A and self.next_state == State.A): #unknown infected
            self.model.unknown_cases_this_step += 1

        self.state = self.next_state

    def __calculate_next_state(self):
        if (self.state == State.S):
            p_avoids_infection = 1.0
#            others = self.model.grid.get_cell_list_contents([self.pos])
            n_infected = self.model.inf_counter_cell[self.pos[0]][self.pos[1]]
            inf_modifier = 1.0
            if self.current_loc == NodeType.C: inf_modifier = self.model.hospital_transmission_modifier
            elif self.current_loc == NodeType.S: inf_modifier = self.model.service_transmission_modifier
            p_avoids_infection = (1.0 - (self.model.p_infect * inf_modifier))**n_infected
            draw = random.random()
            #print ("p(infected) ", 1 -p_avoids_infection)
            #print ("draw value ", draw)
            if (draw > p_avoids_infection):
                self.next_state = State.A
                self.infectability = self.model.p_infect
            else:
                self.next_state = self.state
                if self.next_state == State.R: self.infectability = 0.
                #print("Agent : ", self.unique_id, " infected!")
        # 1b. Calculate updated disease state otherwise
        else: 
            next_state_val = self.model.state_transition(self.model.inf_trans,self.state.value - 2)
            self.next_state = State(next_state_val+2)

    def __calculate_movement(self):
        if (self.state != State.I):
            next_loc = self.model.state_transition(self.well_trans,self.current_loc.value-1)
        else:
            next_loc = self.model.state_transition(self.sick_trans,self.current_loc.value-1)

        next_pos = self.pos
        if (next_loc == 0 and self.current_loc != NodeType.H): # home
            next_pos = self.home_node
            self.current_loc = NodeType.H
        elif (next_loc == 1 and self.current_loc != NodeType.S): # service, pick at random 
            next_pos = random.choice(self.model.services)
            self.current_loc = NodeType.S
        elif (next_loc == 2 and self.current_loc != NodeType.C):
            next_pos = random.choice(self.model.clinics)
            self.current_loc = NodeType.C

        if (self.state == State.I or self.state == State.A):
            self.model.inf_counter_cell[self.pos[0]][self.pos[1]] -= 1
            self.model.inf_counter_cell[next_pos[0]][next_pos[1]] += 1

        if (next_pos != self.pos):
            self.model.grid.move_agent(self,next_pos)
