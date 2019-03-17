import math
import random
from connection_gene import ConnectionGene
from connection_history import ConnectionHistory
from node import Node

class Genome:

    next_connection_num = 1000

    def __init__(self, inputs, outputs, crossover=False):
        self.genes = []
        self.nodes = []
        self.inputs = inputs
        self.outputs = outputs
        self.layers = 2
        self.next_node = 0
        # self.bias_node
        self.network = []

        if crossover:
            return
        
        for i in range(self.inputs):
            self.nodes.append(Node(i))
            self.next_node += 1
            self.nodes[i].layer = 0

        for i in range(self.outputs):
            self.nodes.append(Node(i + self.inputs))
            self.nodes[i + self.inputs].layer = 1
            self.next_node += 1

        self.nodes.append(Node(self.next_node))
        self.bias_node = self.next_node
        self.next_node += 1
        self.nodes[self.bias_node].layer = 0

    def fully_connect(self, innovation_history):
        for i in range(self.inputs):
            for j in range(self.outputs):
                connection_innovation_num = self.get_innovation_num(innovation_history,
                    self.nodes[i], self.nodes[len(self.nodes)-j-2])
                self.genes.append(ConnectionGene(self.nodes[i], self.nodes[len(self.nodes)-j-2],
                    random.uniform(-1, 1), connection_innovation_num))

        connection_innovation_num = self.get_innovation_num(innovation_history,
            self.nodes[self.bias_node], self.nodes[len(self.nodes)-2])
        self.genes.append(ConnectionGene(self.nodes[self.bias_node], self.nodes[len(self.nodes)-2],
            random.uniform(-1, 1), connection_innovation_num))

        self.connect_nodes()

    def get_node(self, node_num):
        for i in range(len(self.nodes)):
            if self.nodes[i].num == node_num:
                return self.nodes[i]
        return None

    def connect_nodes(self):
        for node in self.nodes:
            node.output_connections = []
        for gene in self.genes:
            gene.from_node.output_connections.append(gene)

    def feed_forward(self, input_values):
        for i in range(self.inputs):
            self.nodes[i].output_value = input_values[i]
        self.nodes[self.bias_node].output_value = 1
        for network_node in self.network:
            network_node.engage()
        outs = [self.nodes[self.inputs + i].output_value for i in range(self.outputs)]
        for node in self.nodes:
            node.input_sum = 0
        return outs

    def generate_network(self):
        self.connect_nodes()
        self.network = []
        for l in range(self.layers):
            for i in range(len(self.nodes)):
                if self.nodes[i].layer == l:
                    self.network.append(self.nodes[i])

    def add_node(self, innovation_history):
        if len(self.genes) == 0:
            self.add_connection(innovation_history)
            return
        random_connection = math.floor(random.uniform(0, len(self.genes)))
        while (self.genes[random_connection].from_node == self.nodes[self.bias_node] and
                len(self.genes) != 1):
            random_connection = math.floor(random.uniform(0, len(self.genes)))
        self.genes[random_connection].enabled = False

        new_node_num = self.next_node
        self.nodes.append(Node(new_node_num))
        self.next_node += 1
        connection_innovation_num = self.get_innovation_num(innovation_history,
            self.genes[random_connection].from_node, self.get_node(new_node_num))
        self.genes.append(ConnectionGene(self.genes[random_connection].from_node,
            self.get_node(new_node_num), 1, connection_innovation_num))
        connection_innovation_num = self.get_innovation_num(innovation_history,
            self.get_node(new_node_num), self.genes[random_connection].to_node)
        self.genes.append(ConnectionGene(self.get_node(new_node_num),
            self.genes[random_connection].to_node, self.genes[random_connection].weight,
            connection_innovation_num))
        self.get_node(new_node_num).layer = self.genes[random_connection].from_node.layer + 1

        connection_innovation_num = self.get_innovation_num(innovation_history,
            self.nodes[self.bias_node], self.get_node(new_node_num))
        self.genes.append(ConnectionGene(self.nodes[self.bias_node], self.get_node(new_node_num),
            0, connection_innovation_num))
        if self.get_node(new_node_num).layer == self.genes[random_connection].to_node.layer:
            for i in range(len(self.nodes)-1):
                if self.nodes[i].layer >= self.get_node(new_node_num).layer:
                    self.nodes[i].layer += 1
            self.layers += 1
        self.connect_nodes()

    def add_connection(self, innovation_history):
        if self.fully_connected():
            print("connection failed")
            return
        
        random_node1 = math.floor(random.uniform(0, len(self.nodes)))
        random_node2 = math.floor(random.uniform(0, len(self.nodes)))
        while self.bad_random_connection_nodes(random_node1, random_node2):
            random_node1 = math.floor(random.uniform(0, len(self.nodes)))
            random_node2 = math.floor(random.uniform(0, len(self.nodes)))
        
        temp = random_node2
        if self.nodes[random_node1].layer > self.nodes[random_node2].layer:
            random_node2 = random_node1
            random_node1 = temp
        
        connection_innovation_num = self.get_innovation_num(innovation_history,
            self.nodes[random_node1], self.nodes[random_node2])
        self.genes.append(ConnectionGene(self.nodes[random_node1], self.nodes[random_node2],
            random.uniform(-1, 1), connection_innovation_num))
        self.connect_nodes()

    def bad_random_connection_nodes(self, random1, random2):
        if self.nodes[random1].layer == self.nodes[random2].layer:
            return True
        elif self.nodes[random1].is_connected_to(self.nodes[random2]):
            return True
        return False

    def get_innovation_num(self, innovation_history, from_node, to_node):
        is_new = True
        connection_innovation_num = Genome.next_connection_num
        for i in range(len(innovation_history)):
            if innovation_history[i].matches(self, from_node, to_node):
                is_new = False
                connection_innovation_num = innovation_history[i].innovation_num
                break
        if is_new:
            inno_nums = []
            for i in range(len(self.genes)):
                inno_nums.append(self.genes[i].innovation_num)
            innovation_history.append(ConnectionHistory(from_node.num, to_node.num,
                connection_innovation_num, inno_nums))
            Genome.next_connection_num += 1
        return connection_innovation_num

    def fully_connected(self):
        max_connections = 0
        nodes_in_layers = [0] * self.layers
        
        for i in range(len(self.nodes)):
            nodes_in_layers[self.nodes[i].layer] += 1
        
        for i in range(self.layers - 1):
            nodes_in_front = 0
            for j in range(i+1, self.layers):
                nodes_in_front += nodes_in_layers[j]
            max_connections += nodes_in_layers[i]*nodes_in_front

        if max_connections <= len(self.genes):
            return True
        return False

    def mutate(self, innovation_history):
        if len(self.genes) == 0:
            self.add_connection(innovation_history)
        
        if random.random() < 0.9:
            for gene in self.genes:
                gene.mutate_weight()
        
        if random.random() < 0.8:
            self.add_connection(innovation_history)
        
        if random.random() < 0.9:
            self.add_node(innovation_history)

    def crossover(self, parent2):
        child = Genome(self.inputs, self.outputs, True)
        child.genes = []
        child.nodes = []
        child.layers = self.layers
        child.next_node = self.next_node
        child.bias_node = self.bias_node
        child_genes = []
        is_enabled = []

        for i in range(len(self.genes)):
            set_enabled = True
            parent2_gene = self.matching_gene(parent2, self.genes[i].innovation_num)
            if parent2_gene != -1:
                if not (self.genes[i].enabled and parent2.genes[parent2_gene].enabled):
                    if random.random() < 0.75:
                        set_enabled = False
                if random.random() < 0.5:
                    child_genes.append(self.genes[i])
                else:
                    child_genes.append(parent2.genes[parent2_gene])
            else:
                child_genes.append(self.genes[i])
                set_enabled = self.genes[i].enabled
            is_enabled.append(set_enabled)

        for node in self.nodes:
            child.nodes.append(node.clone())
        
        for i in range(len(child_genes)):
            child.genes.append(child_genes[i].clone(child.get_node(child_genes[i].from_node.num),
                child.get_node(child_genes[i].to_node.num)))
            child.genes[i].enabled = is_enabled[i]
        
        child.connect_nodes()
        return child

    def matching_gene(self, parent2, innovation_num):
        for i in range(len(parent2.genes)):
            if parent2.genes[i].innovation_num == innovation_num:
                return i
        return -1

    def print_genome(self):
        print("Print genome layers: " + str(self.layers))
        print("bias node: " + str(self.bias_node))
        print("self.nodes")
        for node in self.nodes:
            print(str(node.num) + ",")
        print("Genes")
        for gene in self.genes:
            print(("gene " + str(gene.innovation_num) +
                    " From node " + str(gene.from_node.num) +
                    " To node " + str(gene.to_node.num) +
                    " is enabled " + str(gene.enabled) +
                    " from layer " + str(gene.from_node.layer) +
                    " to layer " + str(gene.to_node.layer) +
                    " weight: " + str(gene.weight)))
        print()

    def clone(self):
        clone = Genome(self.inputs, self.outputs, True)
        for node in self.nodes:
            clone.nodes.append(node.clone())
        
        for gene in self.genes:
            clone.genes.append(gene.clone(clone.get_node(gene.from_node.num),
                                        clone.get_node(gene.to_node.num)))
        
        clone.layers = self.layers
        clone.next_node = self.next_node
        clone.bias_node = self.bias_node
        clone.connect_nodes()

        return clone