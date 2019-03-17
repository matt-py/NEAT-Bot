import random

class ConnectionGene:
    def __init__(self, from_node, to_node, weight, innovation_num):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
        self.innovation_num = innovation_num
        self.enabled = True

    def mutate_weight(self):
        rand_float = random.random()
        if rand_float < 0.1:
            self.weight = random.uniform(-1, 1)
        else:
            self.weight += (random.gauss(0, 1)/50)
            self.weight = self.clip_value(self.weight, -1, 1)

    def clone_gene(self, from_node, to_node):
        clone = ConnectionGene(from_node, to_node, self.weight, self.innovation_num)
        clone.enabled = self.enabled
        return clone

    def clip_value(self, value, lower, upper):
        if value < lower:
            value = lower
        elif value > higher:
            value = higher
        return value