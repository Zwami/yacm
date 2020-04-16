#/bin/python3
from SocialModel import SocialModel

print("Yet Another Covid Model")

# TODO - Description

# Step size is effectively "1 hour" 
n_steps = 1000

#### CONFIGURATION #### (TODO, make GUI/file input?) 
# 1. Define Population
# TODO - Consider doing this by sampling?
population_size = 100
prop_doc = 0.05
prop_essential = 0.25
# Remaining are implicitly the "normal" type (social distancing)
# TODO - Make sure sum is <= 1.0
initial_sick = 5 # randomly assign TODO - consider sampling and doing a proportion?

# 2. Define Environment
number_households = 8 # each person is assigned one "household" 
number_hospitals = 1 # Doctors work here, sick population goes here with higher probability
number_services = 1 # Essential population works here. Non-sick population goes here with higher probability

# 3. Define Movement Transition Rates (TODO simplify interface)
# Stochastic Matrices to define how population types move. 
# TODO - Add verification that matrix is stochastic
# State 1 is Home, 2 is Essential, 3 is Hospital
trans_doctor = np.matrix('0.9 0.02 0.08; 0.5 0.5 0.0; 0.05 0.0 0.95')
trans_essential = np.matrix('0.8 0.18 0.02; 0.95 0.05 0.0; 0.25 0.0 0.75')
trans_control = np.matrix('0.90 0.09 0.01; 0.5 0.5 0.0;  0.25 0.0 0.75')
# For simplicity, behavior of all (symptomatic) sick patients is the same
trans_doctor = np.matrix('0.9 0.01 0.09; 0.5 0.5 0.0; 0.01 0.0 0.99')

# 4. Define Infection & state transition rates
# Infected person can only infect others in their same node, but can infect anyone in that node.
# Infection rates are modified by number of infected people in the node
# TODO (soon!) Add negation effects (like PPE) dependent on location (eg hospital should have lower)
# This is used to calculate transition of healthy population -> infected asymptomatic, however it is 
# not constant as it is based on number of other people in the same node
p_infect = 0.1
# State 1 is Infected Asymptomatic, 2 is Infected Symptomatic, 3 is Recovered [TODO - 4, Deceased?]
trans_infection = np.matrix('0.9 0.08 0.02; 0.0 0.98 0.02; 0.0 0.0 1.0')

sm = SocialModel(10)
sm.step()
