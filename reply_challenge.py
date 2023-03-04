from copy import deepcopy
import random
import sys
from collections import namedtuple, OrderedDict
import pandas as pd

N = 100
POPULATION_SIZE = N         
OFFSPRING_SIZE = N*2        
NUM_GENERATIONS = N   
MAX_STEADY=5
MAX_EXTINCTIONS=5   
Individual = namedtuple("Individual", ["genome", "fitness"])
TOURNAMENT_SIZE =int(N/2)
GENETIC_OPERATOR_RANDOMNESS = 0.3
MUTATION_THRESHOLD = 0.1
CROSSOVER_THRESHOLD = 0.5

#PROBLEM PARAMETERS
INITIAL_STAMINA=None
MAX_STAMINA=None
N_TURNS=None
N_DEMONS=None
RIGHE_FILE=None
#DATA
best_fit = sys.float_info.min
best_individual=None
list_of_lists=[]

#FABIO
def take_data(nome_file):
    global list_of_lists
    global INITIAL_STAMINA
    global MAX_STAMINA
    global N_TURNS
    global N_DEMONS
    f = open(nome_file, "r")
    intestazione = f.readline().split()
    INITIAL_STAMINA= int(intestazione[0])
    MAX_STAMINA= int(intestazione[1])
    N_TURNS= int(intestazione[2])
    N_DEMONS = int(intestazione[3])
    for line in f:
        line=line.split()
        line=[int(i) for i in line]
        list_of_lists.append(line)
    f.close()

def print_data_output(result):
    s= pd.Series(result)
    s.to_csv("output",index=False)
    
#LEO

def compute_fitness(genome):
    global list_of_lists
    global INITIAL_STAMINA
    global MAX_STAMINA
    global N_TURNS
    global N_DEMONS
    fitness=0
    gene_index=0
    staminas=[0]*N_TURNS
    fragments=[0]*N_TURNS
    stamina=INITIAL_STAMINA
    for turn in range(N_TURNS):
        stamina+=staminas[turn]
        if stamina>MAX_STAMINA:
            stamina=MAX_STAMINA
        demon=list_of_lists[genome[gene_index]]
        if turn==0 and demon[0]>stamina:
            print("INITIAL STAMINA NOT ENOUGH TO START")
            return fitness
        if demon[0]<=stamina:
            stamina-=demon[0]
            gene_index+=1
            if turn+demon[1]<N_TURNS:
                staminas[turn+demon[1]]+=demon[2]
            for i in range(0,demon[3]):
                if turn+i>=N_TURNS:
                    break
                fragments[turn+i]+=demon[4+i]
        fitness+=fragments[turn]
    return fitness
        
        
        
###########FLAVIO##################

"""parent selection"""
def tournament(population, tournament_size=TOURNAMENT_SIZE):
    global TOURNAMENT_SIZE          
    return max(random.choices(population, k=TOURNAMENT_SIZE), key=lambda i: i.fitness) 
    
"""generate our initial population"""

def init_population():
    global INITIAL_STAMINA
    global MAX_STAMINA
    global N_TURNS
    global N_DEMONS
    global POPULATION_SIZE
    population = []
    for _ in range(POPULATION_SIZE):
        genome = []
        for i in range(N_DEMONS):
            genome.append(i)
        random.shuffle(genome)
        population.append(Individual(genome, compute_fitness(genome)))

    return population

"""mutation"""

def mutation(genome):
    global INITIAL_STAMINA
    global MAX_STAMINA
    global N_TURNS
    global N_DEMONS 
    new_genome = deepcopy(genome)
    
    pos_1 = random.randint(0,N_DEMONS-1)
    pos_2=None 
    while pos_2!=pos_1:
        pos_2 = random.randint(0,N_DEMONS-1) 

    val_1 = genome[pos_1]
    val_2 = genome[pos_2]

    new_genome[pos_1] = val_1
    new_genome[pos_2] = val_2
        
    return new_genome

"""crossover"""
def cross_over(genome_1, genome_2):
    global INITIAL_STAMINA
    global MAX_STAMINA
    global N_TURNS
    global N_DEMONS
    global CROSSOVER_THRESHOLD
    new_genome = []
    set_tot_val = {i for i in range(N_DEMONS)}
    for i in range(0, N_DEMONS):
        if (random.random() > CROSSOVER_THRESHOLD):
            new_genome.append(genome_1[i])
        else:
            new_genome.append(genome_2[i])

    new_genome_plus=list(OrderedDict.fromkeys(new_genome))
    residual = set_tot_val - set(new_genome_plus)

    for ele in residual:
        new_genome_plus.append(ele)

    return new_genome_plus


"""evolution"""
def evolution(population):
    global list_of_lists
    global best_fit
    global best_individual
    global INITIAL_STAMINA
    global MAX_STAMINA
    global N_TURNS
    global N_DEMONS
    global MAX_EXTINCTIONS
    global NUM_GENERATIONS
    global MAX_STEADY
    global OFFSPRING_SIZE
    global POPULATION_SIZE
    global GENETIC_OPERATOR_RANDOMNESS
    check_steady = 0
    check_extinctions=0
    generation=0

    while(check_extinctions<=MAX_EXTINCTIONS and generation<NUM_GENERATIONS):
        generation+=1
        offspring = list()
        for i in range(OFFSPRING_SIZE):
            if random.random() < GENETIC_OPERATOR_RANDOMNESS:                         
                p = tournament(population)                  
                o = mutation(p.genome)                    
            else:                                          
                p1 = tournament(population)                 
                p2 = tournament(population)
                o = cross_over(p1.genome, p2.genome)            
            f = compute_fitness(o)                                                          
            offspring.append(Individual(o, f))                 
        population += offspring      

        #unique population
        unique_population = []
        unique_genomes = []
        for individual in population:
            if individual.genome not in unique_genomes:
                unique_genomes.append(individual.genome)
                unique_population.append(individual)

        population = sorted(unique_population, key=lambda i: i[1], reverse=True)[:POPULATION_SIZE]

        #check actual best individual
        actual_best_individual=Individual(population[0][0],population[0][1])
        actual_best_fit = population[0][1]

        if actual_best_fit <= best_fit:
            check_steady = check_steady + 1

        if check_steady == MAX_STEADY:
            check_extinctions+=1
            check_steady = 0
            new_population = init_population()
            final_population = []
            for i in range(N_DEMONS):
                if random.random() > 0.3: #70% new population
                    final_population.append(new_population[i])
                else:
                    final_population.append(population[i]) #30% old population
            
                
        if actual_best_fit > best_fit:
            best_fit = actual_best_fit
            best_individual=actual_best_individual
            check_steady = 0


if __name__ == '__main__':
    take_data("00-example.txt")
    print(list_of_lists)
    population=init_population()
    evolution(population)
    print(best_fit)
    print_data_output(best_individual[0])
           



    
    

    