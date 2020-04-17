#/bin/python3
from SocialModel import SocialModel
from Location import Location, NodeType
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import pandas
import math
from Person import State
#import yacm_server

# TODO - Description

# TODO - Implement Graph library? Not sure how useful except for visualization...

# Step size is effectively "1 hour" 
n_steps = 100

#### CONFIGURATION #### (TODO, make GUI/file input?) 
# 1. Define Population
# TODO - Consider doing this by sampling?
population_size = 5000
n_doc = 200
n_essential = 1000
# Remaining are implicitly the "normal" type (social distancing)
# TODO - Make sure sum is <= 1.0
initial_sick = 5 # randomly assign TODO - consider sampling and doing a proportion?

# 2. Define Environment
number_households = 4000 # each person is assigned one "household" that may be shared with others
# TODO - First draft likely won't handle multiple hospitals/services, should add soon
number_hospitals = 1 # Doctors work here, sick population goes here with higher probability
number_services = 1 # Essential population works here. Non-sick population goes here with higher probability

# 3. Define Movement Transition Rates (TODO simplify interface)
# Stochastic Matrices to define how population types move. 
# TODO - Add verification that matrix is stochastic
# State 1 is Home, 2 is Essential, 3 is Hospital
# 4. Define Infection & state transition rates
# Infected person can only infect others in their same node, but can infect anyone in that node.
# Infection rates are modified by number of infected people in the node
# This is used to calculate transition of healthy population -> infected asymptomatic, however it is 
# not constant as it is based on number of other people in the same node
p_infect = 0.02
# State 1 is Infected Asymptomatic, 2 is Infected Symptomatic, 3 is Recovered [TODO - 4, Deceased?]
# for simplicity, right now
model_params = { "population_size":population_size,
                "n_doc":n_doc,
                "n_essential":n_essential,
                "initial_sick":initial_sick,
                "locations":locations,
                "trans_doctor":trans_doctor,
                "trans_essential":trans_essential,
                "trans_control":trans_control,
                "trans_sick":trans_sick,
                "p_infect":p_infect,
                "trans_infection":trans_infection}

# TODO - Clean this up...(dict?)
#sm = SocialModel(population_size,\
#                 n_doc,\
#                 n_essential,\
#                 initial_sick,\
#                 locations,\
#                 trans_doctor,\
#                 trans_essential,\
#                 trans_control,\
#                 trans_sick,\
#                 p_infect,\
#                 trans_infection)

#grid_dim = math.ceil(math.sqrt(len(locations))) # smallest possible square grid to contain all nodes
#server.launch()

#for i in range(n_steps):
#    sm.step()
#    print("Step ", i, " complete!")
#
#pop_stats = sm.datacollector.get_model_vars_dataframe()
#print (pop_stats)
#fig = pop_stats.plot()
#plt.show(fig)
#plt.show()
