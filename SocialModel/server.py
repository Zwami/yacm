from mesa.visualization.modules import CanvasGrid, ChartModule, PieChartModule, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.TextVisualization import *
from SocialModel.SocialModel import *
from SocialModel.Person import State
import math

def agent_portrayal(agent):
    portrayal = {"Shape": "rectangle",
                 "Filled": "False",
                 "Layer": 0,
                 "w": 1,
                 "r":1,
                 "text_color": "Black"}
    portrayal["text"] = str(len(agent.model.grid.get_cell_list_contents([agent.pos])))
#    if (agent.state == State.S):
#        portrayal["Color"] = "blue"
#        portrayal["Layer"] = 0
#    elif (agent.state == State.A):
#        portrayal["Color"] = "red"
#        portrayal["Layer"] = 1
#        portrayal["r"] = 0.7
#    elif (agent.state == State.I):
#        portrayal["Color"] = "grey"
#        portrayal["Layer"] = 2
#        portrayal["r"] = 0.5
#    else:
#        portrayal["Color"] = "blue"
#        portrayal["Layer"] = 0
#        portrayal["r"] = 0.9

    #if (agent.current_loc == NodeType.C):
    #    portrayal["text"] = "C"
    #elif (agent.current_loc == NodeType.S):
    #    portrayal["text"] = "S"
    return portrayal

#trans_doctor = np.matrix('0.73 0.02 0.25; 0.5 0.5 0.0; 0.1 0.0 0.9')
#trans_essential = np.matrix('0.75 0.25 0.0; 0.2 0.8 0.0; 0.25 0.0 0.75')
#trans_control = np.matrix('0.99 0.01 0.0; 0.5 0.5 0.0;  0.1 0.0 0.9')
# For simplicity, behavior of all (symptomatic) sick patients is the same
# Unsure yet how to make these configurable in the same way as the state transitions of movement
#trans_sick = np.matrix('0.9998 0.0 0.0002; 0.9998 0.0 0.0002; 0.00 0.0 1.0')
trans_sick = np.matrix('0.99 0.0 0.01; 0.9998 0.0 0.0002; 0.00 0.0 1.0')

# 75% of infected show symptoms within 14 days 
# https://www.npr.org/sections/health-shots/2020/03/31/824155179/cdc-director-on-models-for-the-months-to-come-this-virus-is-going-to-be-with-us
# https://annals.org/aim/fullarticle/2762808/incubation-period-coronavirus-disease-2019-covid-19-from-publicly-reported
# median incubation period 5.1 days
# mean incubation period 6.4 days
#trans_infection = np.matrix('0.9963 0.003 0.0007; 0.0 0.998 0.002; 0.0 0.0 1.0')
trans_infection = np.matrix('0.998 0.00175 0.00025; 0.0 0.998 0.002; 0.0 0.0 1.0')
# Notable test case, Columbia MD
# Pop 99615
# Hospitals 1
# Households: ~40,000 (datausa.io)
# Employed in Healtcare ~7670  (1800 at HOCO general https://www.hopkinsmedicine.org/howard_county_general_hospital/about/)
# Essential : Retail + Food Prep & Service (
# 4300 + 2900
# Assume ~7000 people employed at 200 essential businesses

# Treating R0 as E[People infected while contagious]
# Given bernoulli style trials, this can be approximated as
# p_infect = R0 / (time_contagious in hours)
# approximating time contagious in hours as on average 18 days (need source)
# we can then use a R0 of 2.4 to get a p_infect of ~ 0.0056

# TODO - Probability of immunity?
model_params = {
    "population_size": UserSettableParameter('number', 'Population Size', value=9961),
    "n_doc": UserSettableParameter('number' , 'Number Doctors', value=180),
    "n_essential": UserSettableParameter('number', 'Number Essential Workers', value=700),
    "initial_sick": UserSettableParameter('number', 'Number Initially Sick', value=3),
    "n_homes": UserSettableParameter('number', 'Number of Households', value=4100),
    "n_clinics": UserSettableParameter('number', 'Number of Hospitals', value=1),
    "n_services": UserSettableParameter('number', 'Number of Essential Services', value=20),
    "R0": UserSettableParameter('number', 'Average number of people infected by single person', value=2.4),
    "t_contagious": UserSettableParameter('number', 'Average time someone is contagious (days)', value=14.),
    "hospital_modifier": UserSettableParameter('number', 'Transmission reduction at clinics', value=0.95),
    "service_modifier": UserSettableParameter('number', 'Transmission reduction at services', value=0.85),
    "p_time_home_control": UserSettableParameter('number', 'Control: Percent of time spent at home', value=0.98),
    "p_time_service_control": UserSettableParameter('number', 'Control: Percent of time spent at service', value=0.02),
    "p_time_clinic_control": UserSettableParameter('number', 'Control: Percent of time spent at hospital', value=0.0),
    "p_time_home_doc": UserSettableParameter('number', 'Doctor: Percent of time spent at home', value=0.48),
    "p_time_service_doc": UserSettableParameter('number', 'Doctor: Percent of time spent at service', value=0.02),
    "p_time_clinic_doc": UserSettableParameter('number', 'Doctor: Percent of time spent at hospital', value=0.4),
    "p_time_home_essential": UserSettableParameter('number', 'Essential Worker: Percent of time spent at home', value=0.7),
    "p_time_service_essential": UserSettableParameter('number', 'Essential Worker: Percent of time spent at service', value=0.3),
    "p_time_clinic_essential": UserSettableParameter('number', 'Essential Worker: Percent of time spent at hospital', value=0.0),
    "max_steps": UserSettableParameter('number', 'Maximum number of steps', value=10000),#1008
    "trans_sick":trans_sick,
    "trans_infection":trans_infection}

#grid_dim = math.ceil(math.sqrt(model_params["n_homes"].value + \
#                               model_params["n_clinics"].value +\
#                               model_params["n_services"].value)) # smallest possible square grid to contain all nodes
#grid = CanvasGrid(agent_portrayal, grid_dim, grid_dim, 500, 500)

#chart = ChartModule([{"Label": "Num Susceptible",
#                      "Color": "Blue"},
chart = ChartModule([{"Label": "Num Asymptomatic",
                      "Color": "Red"},
                     {"Label": "Num Symptomatic",
                      "Color": "Grey"},
                     {"Label": "Num Recovered",
                      "Color": "Green"},
                    ],
                    data_collector_name='datacollector')

cpd = ChartModule([{"Label": "Known New Cases Per Day",
                    "Color": "Red"},
                    {"Label": "True New Cases Per Day",
                    "Color": "Black"}
                    ],
                    data_collector_name='cases_per_day')

total_cases = ChartModule([{"Label": "Known Number Cases",
                    "Color": "Red"},
                    {"Label": "True Number Cases",
                    "Color": "Black"},
                    {"Label": "True Number Recovered",
                    "Color": "Green"}
                    ],
                    data_collector_name='cumulative_cases')

popchart = ChartModule([{"Label": "Home Pop",
                      "Color": "Blue"},
                     {"Label": "Clinic Pop",
                      "Color": "Red"},
                     {"Label": "Service Pop",
                      "Color": "Black"},
                    ],
                    data_collector_name='loc_datacollector')

patchart = ChartModule([{"Label": "Number of Patients at Hospitals",
                      "Color": "Red"}
                    ],
                    data_collector_name='num_patients')
server = ModularServer(SocialModel,
                       [total_cases,cpd,chart,popchart,patchart],
                       "Social Model",
                       model_params)

server.port = 8521 # The default
