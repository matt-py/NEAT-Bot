
class ConnectionHistory:
    def __init__(self, from_node, to_node, innovation_num, innovation_nums_list):
        self.from_node = from_node
        self.to_node = to_node
        self.innovation_num = innovation_num
        self.innovation_nums_list = list(innovation_nums_list)

    def matches(self, genome, from_node, to_node):
        if len(genome.genes) == len(self.innovation_nums_list):
            if (from_node.num == self.from_node and to_node.num == self.to_node):
                for gene in genome.genes:
                    if gene.innovation_num not in self.innovation_nums_list:
                        return False
                return True
        return False