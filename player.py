from genome import Genome

class Player:

    max_lifespan = 500

    def __init__(self):
        self.fitness = 0
        self.vision = []
        self.decision = []
        self.lifespan = 0
        self.best_score = 0
        self.dead = False
        self.score = 0
        self.gen = 0
        self.genome_inputs = 8
        self.genome_outputs = 3
        self.brain = Genome(self.genome_inputs, self.genome_outputs)

    def reward(self, reward):
        self.score += reward

    def update(self):
        self.lifespan += 1
        if self.lifespan > Player.max_lifespan:
            self.dead = True

    def look(self, inputs):
        self.vision = []
        self.vision = inputs

    def think(self):
        choice_max = 0
        max_index = 0
        self.decision = self.brain.feed_forward(self.vision)
        for i in range(len(self.decision)):
            if self.decision[i] > choice_max:
                choice_max = self.decision[i]
                max_index = i
        return max_index

    def clone(self):
        clone = Player()
        clone.brain = self.brain.clone()
        clone.fitness = self.fitness
        clone.brain.generate_network()
        clone.gen = self.gen
        clone.best_score = self.score
        return clone

    def calculate_fitness(self):
        self.fitness = self.score * self.score

    def crossover(self, parent2):
        child = Player()
        child.brain = self.brain.crossover(parent2.brain)
        child.brain.generate_network()
        return child