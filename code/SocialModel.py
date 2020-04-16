from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from Person import Person
from Location import NodeType
import random
import math

#MultiGrid maybe not the MOST efficient way to do this, but adds some convenient Mesa hooks

class SocialModel(Model):

    def __setup_locations(self,locations,homes,clinics,services,grid_dim):
        for i in range(len(locations)):
            x = i % grid_dim
            y = int(i/grid_dim)
            if (locations[i].node_type == NodeType.H):
                h = { "x" : x, "y" : y }
                homes.append(h)
                print("added home to x: ", x, " y: ", y)
            elif (locations[i].node_type == NodeType.C):
                c = { "x" : x, "y" : y }
                clinics.append(c)
                print("added clinic to x: ", x, " y: ", y)
            else :
                s = { "x" : x, "y" : y }
                services.append(s)
                print("added service to x: ", x, " y: ", y)

    def __init__(self,\
                 population_size,\
                 n_doc,\
                 n_essential,\
                 initial_sick,\
                 locations,\
                 trans_doctor,\
                 trans_essential,\
                 trans_control,\
                 p_infect,\
                 trans_infection):
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
        homes = []
        clinics = []
        services = []

        self.__setup_locations(locations,homes,clinics,services,grid_dim)

        for i in range(self.num_agents):
            home_node = random.choice(homes)
            a = Person(i,self,home_node)
            print("Created agent ", a.unique_id)
            self.schedule.add(a)

    def step(self):
        self.schedule.step()
