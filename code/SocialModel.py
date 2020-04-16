from mesa import Model
from mesa.time import RandomActivation
from Person import Person
import networkx as nx

# Must define :
# How many home nodes
# How many "essential" work nodes
# How many "hospital" Nodes
class SocialModel(Model):

    def __init__(self,N,Homes,Services,Hospitals):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        for i in range(self.num_agents):
            a = Person(i,self)
            print("Created agent ", a.unique_id)
            self.schedule.add(a)

    def step(self):
        self.schedule.step()
