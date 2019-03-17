import random

class Species:
    def __init__(self, p=None):
        self.players = []
        self.best_fitness = 0
        self.champ = None
        self.average_fitness = 0
        self.staleness = 0
        self.rep = None

        self.excess_coeff = 1
        self.weight_diff_coeff = 0.5
        self.compatibility_threshold = 3
        if p is not None:
            self.players.append(p)
            self.best_fitness = p.fitness
            self.rep = p.brain.clone()
            self.champ = p.clone()

    def same_species(self, g):
        excess_and_disjoint = self.get_excess_disjoint(g, self.rep)
        average_weight_diff = self.average_weight_diff(g, self.rep)
        large_genome_normaliser = len(g.genes) - 20
        if large_genome_normaliser < 1:
            large_genome_normaliser = 1

        compatibility = ((self.excess_coeff * excess_and_disjoint / large_genome_normaliser) +
                            (self.weight_diff_coeff * average_weight_diff))
        return (self.compatibility_threshold > compatibility)

    def add_to_species(self, p):
        self.players.append(p)

    def get_excess_disjoint(self, brain1, brain2):
        matching = 0
        for i in range(len(brain1.genes)):
            for j in range(len(brain2.genes)):
                if brain1.genes[i].innovation_num == brain2.genes[j].innovation_num:
                    matching += 1
                    break
        return ((len(brain1.genes)+len(brain2.genes)) - (2 * matching))

    def average_weight_diff(self, brain1, brain2):
        if len(brain1.genes) == 0 or len(brain2.genes) == 0:
            return 0
        matching = 0
        total_diff = 0
        for i in range(len(brain1.genes)):
            for j in range(len(brain2.genes)):
                if brain1.genes[i].innovation_num == brain2.genes[j].innovation_num:
                    matching += 1
                    total_diff += abs(brain1.genes[i].weight - brain2.genes[j].weight)
                    break
        if matching == 0:
            return 100
        return total_diff/matching

    def sort_species(self):
        temp = sorted(self.players, key=lambda x: x.fitness, reverse=True)
        self.players = []
        self.players = list(temp)
        if len(self.players) == 0:
            self.staleness = 200
            return
        if self.players[0].fitness > self.best_fitness:
            self.staleness = 0
            self.best_fitness = self.players[0].fitness
            self.rep = self.players[0].brain.clone()
            self.champ = self.players[0].clone()
        else:
            self.staleness += 1

    def set_average(self):
        total_sum = 0
        for player in self.players:
            total_sum += player.fitness
        self.average_fitness = total_sum/len(self.players)

    def give_me_baby(self, innovation_history):
        baby = None
        if random.random() < 0.25:
            baby = self.select_player().clone()
        else:
            parent1 = self.select_player()
            parent2 = self.select_player()
            if parent1.fitness < parent2.fitness:
                baby = parent2.crossover(parent1)
            else:
                baby = parent1.crossover(parent2)
        baby.brain.mutate(innovation_history)
        return baby

    def select_player(self):
        fitness_sum = 0
        for player in self.players:
            fitness_sum += player.fitness
        rand = random.uniform(0, fitness_sum)
        running_sum = 0
        for player in self.players:
            running_sum += player.fitness
            if running_sum > rand:
                return player
        return self.players[0]

    def cull(self):
        if len(self.players) > 2:
            i = len(self.players)/2
            while i < len(self.players):
                del self.players[i]

    def fitness_sharing(self):
        for player in self.players:
            player.fitness /= len(self.players)