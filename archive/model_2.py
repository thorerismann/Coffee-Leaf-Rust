# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


from dataclasses import dataclass
import pandas as pd
import numpy as np
import scipy
import random
from itertools import chain
import seaborn as sns


# what is the size of a typical smallholder coffee plantation? (how many plants)

# set parameters for number of plants, branches, leaves
plants_per_cell_min = 10
plants_per_cell_max = 14


branches_per_plant_min = 12
branches_per_plant_max = 16

leaves_per_branch_min = 20
leaves_per_branch_max = 25

age_min = 0
age_max = 350

prod_factor = 1
berry_cost = 70

leaf_cost = 80

# virus growth benchmarks (days)

benchmark_1 = 20
benchmark_2 = 35
benchmark_3 = 50
benchmark_4 = 100
benchmark_5 = 150

# virus spread
clr_b = 0.1
clr_p = 0.05
clr_g = 0.01

# chance of germination
germ_chance = 0.5



# plant cut-off ages
age_1 = 50
age_2 = 200
age_3 = 250
age_4 = 300
age_5 = 350

# make grid
grid_size = 2
x = np.arange(0,grid_size)
y = np.arange(0,grid_size)
tuples = []
for i in x:
    for j in y:
        tuples.append((i,j))
grid = tuples


@dataclass
class Leaf:
    """
    The leaf class is the basic element of infection, leaf and berry production
    """
    grid: tuple = (0,0)
    plant: int = 0
    branch: int = 0
    leaf: int = 0
    age: int = 0
    status: int = 0
    hstatus: int = 10
    idays: int = 0
    infectivity: int = 0
    clr_germs: int = 0 
    
    def aging(self):
        """
        Each turn the leaf ages by one day. Its base productivity is determined by its age.
        """
        if self.status < 2:
            self.age+=1
            if self.age > 350:
                self.status = 2
            if self.age >300:
                self.hstatus = 4
            elif self.age > 250:
                self.hastatus = 6
            elif self.age > 200:
                self.hstatus = 9
            elif self.age > 50:
                self.hstatus = 10
            elif self.age < 50:
                self.hstatus = 8
        
    
    def clr_progression(self):
        """
        Each turn the coffee leaf rust infection in the leaf advances by one day
        """
        if self.status == 1:
            self.idays += 1
            if self.idays < benchmark_1:
                self.health = max(self.hstatus-1,0)
            elif self.idays < benchmark_2:
                self.health = max(self.hstatus-2,0)
            elif self.idays < benchmark_3:
                self.heatlh = max(self.hstatus-5,0)
            elif self.idays < benchmark_4:
                self.health = max(self.hstatus-8,0)
            elif self.idays < benchmark_5:
                self.health = 0
            else:
                self.status = 2
    
    def germ_rust(self):
        """
        Each turn the rust spores can germinate on the leaf"""
        if self.status == 0:
            if self.clr_germs > 0:
                if np.random.binomial(self.clr_germs,germ_chance) > 0:
                    self.status = 1
                    self.idays = 1
            
    def leaf_death(self):
        """
        Each turn leaves that age past 350 years old or are infected for more than 150 days die.
        """
        if (self.idays >=150):
            self.status = 2
        elif (self.age >= 350):
            self.status = 2
        
            
# initiate leaves
mylist =[]
for i in grid:
    plants = random.randint(plants_per_cell_min,plants_per_cell_max)
    for j in range(plants):
        branches = random.randint(branches_per_plant_min,branches_per_plant_max)
        for k in range(branches):
            leaves = random.randint(leaves_per_branch_min,leaves_per_branch_max)
            for l in range(leaves):
                mylist.append(Leaf(grid=i,plant=j,branch=k,leaf=l,age=random.randint(age_min,age_max),status=0,hstatus=10,idays=0,infectivity=0,clr_germs=0))              
al = mylist       


@dataclass
class Branch:
    """
    Branches are where production of berries and leaves are defined.
    """
    leaves: list
    grid: tuple = (0,0)
    plant: int = 0
    branch: int = 0
    berries: int = 0
    leaf_prod: int = 0
    berry_prod: int = 0
    prod_factor: int = 0
    branch_status: int = 0
    inf_leaves: int = 0
    
    def production_l(self):
        """
        leaf production function
        """
        for i in self.leaves:
            if i.status<2:
                self.leaf_prod = self.leaf_prod + 0.1*getattr(i,'hstatus')
        a = int(np.floor(self.leaf_prod/leaf_cost))
        leaf_count = len(self.leaves)
        if a>0:
            for i in range(a):
                self.leaves.append(Leaf(grid = self.grid,plant = self.plant, branch = self.branch,status = 0,leaf = leaf_count+a,age=0,hstatus=8,idays=0,infectivity=0,clr_germs=0))
                self.leaf_prod = self.leaf_prod - a*leaf_cost
                
    def production_b(self):
        """
        berry production function
        """
        for i in self.leaves:
            if i.status <2:
                self.berry_prod = self.berry_prod + 0.1*getattr(i,'hstatus')
        a = int(np.floor(self.berry_prod/berry_cost))
        self.berries = self.berries + a
        self.berry_prod = self.berry_prod - a*berry_cost
    
    def branch_status(self):
        """
        update branch status (healthy infected dead)
        """
        a = [x.status for x in self.leaves if x.status < 2]
        if len(a) <3:
            self.branch_status = 2
    
    def get_inf_leaves(self):
        infected = [x for x in self.leaves if x.status == 1]
        self.inf_leaves = len(infected)
        return(len(infected))
    
    def infection(self):
        """
        Each turn the healthy leaves on the branch can get infected by leaves from same branch, same plant or same grid cell.
        """
        # first infected leaves on the branch
        infected_branch = [x for x in self.leaves if x.status == 1]
        infected = len(infected_branch)
        healthy = [x for x in self.leaves if x.status == 0]
        if infected > 0:
            for i in healthy:
                i.clr_germs = i.clr_germs + np.random.binomial(infected,clr_b)
        
        # infected leaves on same plant different branch
        my_infected_plant = [x for x in ap if (x.grid == self.grid) & (x.plant ==self.plant)]
        infected_leaves_plant = my_infected_plant[0].infected
        infected = infected_leaves_plant - len(infected_branch)
        if infected > 0:
            for i in healthy:
                i.clr_germs = i.clr_germs + np.random.binomial(infected,clr_p) 
        infected_grid = [x for x in ag if (x.grid == self.grid)]
        infected_leaves_grid = infected_grid[0].infected
        infected = infected_leaves_grid - infected_leaves_plant
        if infected > 0:
            for i in healthy:
                i.clr_germs = i.clr_germs + np.random.binomial(infected,clr_g) 
            
            
            
        

# create branch objects            
mylist = []
for i in grid:
    grid_ = [x for x in al if getattr(x,'grid')== i]
    a = set([x.plant for x in grid_])
    for j in a:
        plant_ = [x for x in grid_ if getattr(x,'plant')== j]
        b = set([x.branch for x in plant_])
        for k in b:
            branch_ = [x for x in plant_ if getattr(x,'branch')== k]
            mylist.append(Branch(leaves=branch_,grid=i,plant=j,branch=k,berries=0,leaf_prod=0,berry_prod=0,prod_factor=1,branch_status=0,inf_leaves=0))
ab = mylist    

@dataclass
class Plant:
    branches: list
    grid: tuple
    plant: int
    infected: int    
    
    def get_inf_leaves(self):
        inf_leaves = 0
        for i in self.branches:
            inf_leaves += i.inf_leaves
        self.infected = inf_leaves
    
@dataclass
class Grid:
    plants: list
    grid: tuple
    infected: int
    
    def get_inf_leaves(self):
        inf_leaves = 0
        for i in self.plants:
            inf_leaves += i.infected
        self.infected = inf_leaves

mylist = []
for i in grid:
    grid_ = [x for x in ab if getattr(x,'grid')== i]
    plants_ = set([x.plant for x in grid_])
    for j in plants_:
        branches_ = [x for x in grid_ if getattr(x,'plant')== j]
        mylist.append(Plant(branches=branches_,grid=i,plant=j,infected = 0))
ap = mylist

mylist = []
for i in grid:
    plants_ = [x for x in ap if getattr(x,'grid')==i]
    mylist.append(Grid(plants = plants_,grid = i,infected = 0))
ag = mylist


def make_frame_branches(branches,time):
    list_dict = []
    for i in branches:
        dead =  len([x for x in i.leaves if x.status == 2])
        infected = len([x for x in i.leaves if x.status == 1])
        healthy = len([x for x in i.leaves if x.status == 0])
        list_dict.append({'dead':dead,'healthy':healthy,'infected':infected,'plant':i.plant,'branch' : i.branch,'grid':i.grid,'berries' : i.berries,'time' : time})
    return list_dict
    
# run code with aging, leaf death, berry production and leaf production
# need to construct a dataframe 
toinfect = [x for x in al if (x.plant == 2) & (x.branch == 3) & ((x.leaf == 2) | (x.leaf == 3))&((x.grid == (0,0)) | (x.grid == (0,1)) | (x.grid == (1,1)))]
for i in toinfect:
    i.status = 1
    i.idays =1


my_dict_list = []
time = 0
while time<100:
    [x.aging() for x in al]
    [x.get_inf_leaves() for x in ab]
    [x.get_inf_leaves() for x in ap]
    [x.get_inf_leaves() for x in ag]
    [x.leaf_death() for x in al]
    [x.production_l() for x in ab]
    [x.production_b() for x in ab]
    [x.clr_progression() for x in al]
    [x.germ_rust() for x in al]
    [x.infection() for x in ab]
    my_dict_list.append(make_frame_branches(ab,time))
    time+=1


df = pd.DataFrame(list(chain.from_iterable(my_dict_list)))
df.plant = df.plant.astype(str)
mylist = ["".join(str(x)) for x in df.grid]
mylist = [x[1]+x[4] for x in mylist]
df.grid = mylist
df['id_no'] = df.grid + df.plant
df.set_index('id_no',inplace=True,drop=True)
grouped_tg = df.groupby(['time','grid']).agg({'healthy':'mean','dead':'mean','infected':'mean','berries':'mean'})
grouped_tg.reset_index(inplace=True,drop=False)



