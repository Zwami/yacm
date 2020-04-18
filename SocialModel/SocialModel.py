from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from SocialModel.Person import Person, PopType, State
from SocialModel.Location import NodeType, Location
import random
import math
import numpy as np
from collections import deque
import array as arr

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
def compute_home_pop(model):
    agent_loc = [agent.current_loc for agent in model.schedule.agents]
    return agent_loc.count(NodeType.H) / len(model.schedule.agents)
def compute_clinic_pop(model):
    agent_loc = [agent.current_loc for agent in model.schedule.agents]
    return agent_loc.count(NodeType.C) / len(model.schedule.agents)
def compute_service_pop(model):
    agent_loc = [agent.current_loc for agent in model.schedule.agents]
    return agent_loc.count(NodeType.S) / len(model.schedule.agents)
def known_cases_past_day(model):
    sum_cases = 0
    for i in (model.known_cases_in_last_day):
        sum_cases += i
    return sum_cases
def true_cases_past_day(model):
    sum_cases = 0
    for i in (model.unknown_cases_in_last_day):
        sum_cases += i
    for i in (model.known_cases_in_last_day):
        sum_cases += i
    return sum_cases

def known_total_cases(model):
    return model.known_cumulative_cases

def true_total_cases(model):
    return model.unknown_cumulative_cases # all cases start as unknown so this is best running tally
def patients_at_clinic(model):
    num_patients = 0
    for c in model.clinics:
        clinic_pop = model.grid.get_cell_list_contents([c])
        for p in clinic_pop:
            if (p.state == State.I or p.pop_type != PopType.D): num_patients += 1
    return num_patients

#MultiGrid maybe not the MOST efficient way to do this, but adds some convenient Mesa hooks
class SocialModel(Model):

    def __setup_locations(self,locations,homes,clinics,services,grid_dim):
        for i in range(len(locations)):
            x = i % grid_dim
            y = int(i/grid_dim)
            if (locations[i].node_type == NodeType.H):
                h = (x,y)
                homes.append(h)
            elif (locations[i].node_type == NodeType.C):
                c = (x,y)
                clinics.append(c)
            else :
                s = (x,y)
                services.append(s)

    def __init__(self,\
                 population_size,\
                 n_doc,\
                 n_essential,\
                 initial_sick,\
                 n_homes,\
                 n_services,\
                 n_clinics,\
                 trans_sick,\
                 R0,
                 t_contagious,
                 trans_infection,
                 hospital_modifier,
                 service_modifier,
                 p_time_home_control,
                 p_time_service_control,
                 p_time_clinic_control,
                 p_time_home_doc,
                 p_time_service_doc,
                 p_time_clinic_doc,
                 p_time_home_essential,
                 p_time_service_essential,
                 p_time_clinic_essential,
                 max_steps):
        # TODO clean this up
        locations = []
        for i in range(n_homes):
            locations.append(Location(len(locations),NodeType.H))
        for i in range(n_clinics):
            locations.append(Location(len(locations),NodeType.C))
        for i in range(n_services):
            locations.append(Location(len(locations),NodeType.S))
        # Simplifying the state transitions by assuming only one ergodic, recurrent class and
        # setting the eigenvalues to 1, 0, 0
        control_p = np.array([p_time_home_control, p_time_service_control, p_time_clinic_control])
        trans_control = np.matrix(np.stack((control_p,control_p,control_p)))
        doc_p = np.array([p_time_home_doc, p_time_service_doc, p_time_clinic_doc])
        trans_doctor = np.matrix(np.stack((doc_p,doc_p,doc_p)))
        essential_p = np.array([p_time_home_essential, p_time_service_essential, p_time_clinic_essential])
        trans_essential = np.matrix(np.stack((essential_p,essential_p,essential_p)))

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
        R0_ScaleFactor = 0.1 # Test
        self.p_infect = R0 * R0_ScaleFactor / (t_contagious * 24.)

        self.__setup_locations(locations,self.homes,self.clinics,self.services,grid_dim)
        self.max_steps = max_steps

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

            a = Person(i,self,home_node,p_type,sick_state,well_trans,sick_trans)
            if (sick_agent_ids.count(i) > 0):
                a.state = State.A # start sick and asymptomatic...
                a.infectability = self.p_infect
            self.schedule.add(a)
            self.grid.place_agent(a, a.home_node) # everyone starts at home
        self.service_transmission_modifier= 1.-service_modifier# Effect of masks & distancing at services
        self.hospital_transmission_modifier = 1.-hospital_modifier# Effect of PPE at hospitals

        self.datacollector = DataCollector(model_reporters = \
            {"Num Susceptible":compute_num_susceptible, \
             "Num Asymptomatic":compute_num_asymptomatic, \
             "Num Symptomatic":compute_num_symptomatic, \
             "Num Recovered":compute_num_recovered})

        self.loc_datacollector = DataCollector(model_reporters = \
            {"Home Pop":compute_home_pop, \
             "Clinic Pop":compute_clinic_pop, \
             "Service Pop":compute_service_pop})

        self.known_cases_in_last_day = deque(maxlen = 24)
        self.unknown_cases_in_last_day = deque(maxlen = 24)
        for i in range(24):
            self.known_cases_in_last_day.append(0)
            self.unknown_cases_in_last_day.append(0)
        self.known_cases_this_step = 0
        self.unknown_cases_this_step = 0
        rows,cols = (grid_dim,grid_dim)
        self.inf_counter_cell = [[0 for i in range(cols)] for j in range(rows)]
        self.unknown_cumulative_cases = initial_sick
        self.known_cumulative_cases = 0

        self.cases_per_day = DataCollector(model_reporters =
                                           {"Known New Cases Per Day" : known_cases_past_day,
                                            "True New Cases Per Day" : true_cases_past_day})

        self.cumulative_cases = DataCollector(model_reporters =
                                             {"Known Number Cases" : known_total_cases,
                                             "True Number Cases" : true_total_cases,
                                             "True Number Recovered" : compute_num_recovered})
        self.num_patients = DataCollector(model_reporters =
                                         {"Number of Patients at Hospitals" : patients_at_clinic})

        self.running = True# Must be set for server to work


    def grid_location_type(self,pos):
        xy = {"x":pos[0],"y":pos[1]}
        if (self.clinics.count(xy) > 0) : return NodeType.C
        elif (self.services.count(xy) > 0) : return NodeType.S
        elif (self.homes.count(xy) > 0) : return NodeType.H
        else: print("node not found? ", xy)

    # expect that state value has already been converted to appropriate row index
    def state_transition(self,trans_matrix,row_value):
        draw = random.random()
        curr_sum = 0.0
        for i in range(trans_matrix[row_value][:].size):
            curr_sum += trans_matrix.item(row_value,i)
            if (draw <= curr_sum):
                return i

    def step(self):
        self.known_cases_this_step = 0
        self.unknown_cases_this_step = 0
        self.datacollector.collect(self)
        self.cases_per_day.collect(self)
        self.loc_datacollector.collect(self)
        self.schedule.step()
        self.known_cases_in_last_day.append(self.known_cases_this_step)
        self.unknown_cases_in_last_day.append(self.unknown_cases_this_step)
        self.known_cumulative_cases += self.known_cases_this_step
        self.unknown_cumulative_cases += self.unknown_cases_this_step
        self.cumulative_cases.collect(self)
        self.num_patients.collect(self)
        # stop running once no more contagious
        if (compute_num_contagious(self) == 0 or self.schedule.steps >= self.max_steps):
            self.running = False
