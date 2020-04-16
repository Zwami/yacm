from mesa import Model
from mesa.time import RandomActivation
from Person import Person

class SocialModel(Model):

    def __init__(self,N):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        for i in range(self.num_agents):
            a = Person(i,self)
            print("Created agent ", a.unique_id)
            self.schedule.add(a)

    def step(self):
        self.schedule.step()
