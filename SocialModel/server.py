from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from SocialModel.SocialModel import *
from SocialModel.Person import State
import math

def agent_portrayal(agent):

    portrayal = {"Shape": "rectangle",
                 "Filled": "true",
                 "r": 0.9}
 #                "text": "H"}
    if (agent.state == State.S):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
    elif (agent.state == State.A):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.7
    elif (agent.state == State.I):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 2
        portrayal["r"] = 0.5
    else:
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
        portrayal["r"] = 0.9

    #if (agent.current_loc == NodeType.C):
    #    portrayal["text"] = "C"
    #elif (agent.current_loc == NodeType.S):
    #    portrayal["text"] = "S"

    return portrayal

# TODO - User interface?
trans_doctor = np.matrix('0.9 0.02 0.08; 0.5 0.5 0.0; 0.05 0.0 0.95')
trans_essential = np.matrix('0.8 0.18 0.02; 0.95 0.05 0.0; 0.25 0.0 0.75')
trans_control = np.matrix('0.90 0.09 0.01; 0.5 0.5 0.0;  0.25 0.0 0.75')
# For simplicity, behavior of all (symptomatic) sick patients is the same
trans_sick = np.matrix('0.9 0.0 0.1; 0.9 0.0 0.1; 0.01 0.0 0.99')

trans_infection = np.matrix('0.95 0.04 0.01; 0.0 0.98 0.02; 0.0 0.0 1.0')

model_params = {
    "population_size": UserSettableParameter('number', 'Population Size', value=100),
    "n_doc": UserSettableParameter('number' , 'Number Doctors', value=5),
    "n_essential": UserSettableParameter('number', 'Number Essential Workers', value=50),
    "initial_sick": UserSettableParameter('number', 'Number Initially Sick', value=5),
    "n_homes": UserSettableParameter('number', 'Number of Households', value=75),
    "n_clinics": UserSettableParameter('number', 'Number of Hospitals', value=1),
    "n_services": UserSettableParameter('number', 'Number of Essential Services', value=5),
    "p_infect": UserSettableParameter('slider', 'Pr(single sick person infects healthy person)', value=0.01, min_value =0., max_value =1.0, step = 0.005),
    "trans_doctor": trans_doctor,
    "trans_essential":trans_essential,
    "trans_control":trans_control,
    "trans_sick":trans_sick,
    "trans_infection":trans_infection}

grid_dim = math.ceil(math.sqrt(model_params["n_homes"].value + \
                               model_params["n_clinics"].value +\
                               model_params["n_services"].value)) # smallest possible square grid to contain all nodes
grid = CanvasGrid(agent_portrayal, grid_dim, grid_dim, 500, 500)

chart = ChartModule([{"Label": "Num Susceptible",
                      "Color": "Blue"},
                     {"Label": "Num Asymptomatic",
                      "Color": "Red"},
                     {"Label": "Num Symptomatic",
                      "Color": "Grey"},
                     {"Label": "Num Recovered",
                      "Color": "Green"},
                     {"Label": "Num Contagious",
                      "Color": "Black"},
                    ],
                    data_collector_name='datacollector')

server = ModularServer(SocialModel,
                       [grid, chart],
                       "Social Model",
                       model_params)

server.port = 8521 # The default
