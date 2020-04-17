from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from SocialModel.Person import Person, PopType, State
from SocialModel.Location import NodeType, Location
import random
import math
import numpy as np

def compute_num_susceptible(model):
    agent_states = [agent.state for agent in model.schedule.agents]
    return agent_states.count(State.S)
def compute_num_asymptomatic(model):
    agent_states = [agent.state for agent in model.schedule.agents]
    return agent_states.count(State.A)
def compute_num_symptomatic(model):
    agent_states = [agent.state for agent in model.schedule.agents]
    return agent_states.count(State.I)
def compute_num_recovered(model):
    agent_states = [agent.state for agent in model.schedule.agents]
    return agent_states.count(State.R)
def compute_num_contagious(model):
    agent_states = [agent.state for agent in model.schedule.agents]
    return agent_states.count(State.I) + agent_states.count(State.A)


#MultiGrid maybe not the MOST efficient way to do this, but adds some convenient Mesa hooks
class SocialModel(Model):

    def __setup_locations(self,locations,homes,clinics,services,grid_dim):
        for i in range(len(locations)):
            x = i % grid_dim
            y = int(i/grid_dim)
            if (locations[i].node_type == NodeType.H):
                h = { "x" : x, "y" : y }
                homes.append(h)
            elif (locations[i].node_type == NodeType.C):
                c = { "x" : x, "y" : y }
                clinics.append(c)
            else :
                s = { "x" : x, "y" : y }
                services.append(s)

    def __init__(self,\
                 population_size,\
                 n_doc,\
                 n_essential,\
                 initial_sick,\
                 n_homes,\
                 n_services,\
                 n_clinics,\
                 trans_doctor,\
                 trans_essential,\
                 trans_control,\
                 trans_sick,\
                 p_infect,\
                 trans_infection):
        # TODO clean this up
        locations = []
        for i in range(n_homes):
            locations.append(Location(len(locations),NodeType.H))
        for i in range(n_clinics):
            locations.append(Location(len(locations),NodeType.C))
        for i in range(n_services):
            locations.append(Location(len(locations),NodeType.S))

        self.num_agents = population_size
        self.schedule = RandomActivation(self)
        # determine initially sick agents (a bit yucky)
        sick_agent_ids = []
        while len(sick_agent_ids) < initial_sick:
            s_id = random.randint(1,self.num_agents+1)
            if s_id not in sick_agent_ids: sick_agent_ids.append(s_id)

        # setup locations in model
        grid_dim = math.ceil(math.sqrt(len(locations))) # smallest possible square grid to contain all nodes
        self.grid = MultiGrid(grid_dim,grid_dim,True)
        # Note : grid indices are 0 base (which is great considering mesa in general seems to be base 1...)
        self.homes = []
        self.clinics = []
        self.services = []
        self.inf_trans = trans_infection
        self.p_infect = p_infect
        self.running = True# Must be set for server to work

        self.__setup_locations(locations,self.homes,self.clinics,self.services,grid_dim)

        for i in range(self.num_agents):
            home_node = random.choice(self.homes)
            sick_state = State.S
            sick_trans = trans_sick# eventually may want to modify this
            if (i < n_doc) :
                p_type = PopType.D
                well_trans = trans_doctor
            elif (i >= n_doc and i < n_doc + n_essential) :
                p_type = PopType.E
                well_trans = trans_essential
            else:
                p_type = PopType.C
                well_trans = trans_control

            if (sick_agent_ids.count(i) > 0): sick_state = State.A # start sick and asymptomatic...
            a = Person(i,self,home_node,p_type,sick_state,well_trans,sick_trans)
            self.schedule.add(a)
            self.grid.place_agent(a, (a.home_node["x"],a.home_node["y"])) # everyone starts at home

        self.datacollector = DataCollector(model_reporters = \
            {"Num Susceptible":compute_num_susceptible, \
             "Num Asymptomatic":compute_num_asymptomatic, \
             "Num Symptomatic":compute_num_symptomatic, \
             "Num Contagious":compute_num_contagious, \
             "Num Recovered":compute_num_recovered})

    def grid_location_type(self,pos):
        xy = {"x":pos[0],"y":pos[1]}
        if (self.clinics.count(xy) > 0) : return NodeType.C
        elif (self.services.count(xy) > 0) : return NodeType.S
        elif (self.homes.count(xy) > 0) : return NodeType.H
        else: print("node not found? ", xy)

    # expect that state value has already been converted to appropriate row index
    def state_transition(self,trans_matrix,row_value):
        row = trans_matrix[row_value]
        draw = random.random()
        curr_sum = 0.0
        for i in range(np.size(row)):
            curr_sum += row.item(0,i)
            if (draw <= curr_sum):
                return i

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()