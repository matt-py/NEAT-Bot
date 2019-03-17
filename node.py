import math

class Node:
    def __init__(self, num):
        self.num = num
        self.input_sum = 0
        self.output_value = 0
        self.output_connections = []
        self.layer = 0

    def engage(self):
        # print(self.num)
        if self.layer != 0:
            self.output_value = self.sigmoid(self.input_sum)
            # print(self.input_sum, self.output_value)
        
        for out_connect in self.output_connections:
            # print(self.output_value)
            if out_connect.enabled:
                out_connect.to_node.input_sum += out_connect.weight*self.output_value
                # print(self.num, out_connect.to_node.num)
                # print(out_connect.weight, self.output_value, out_connect.to_node.input_sum)

    def step_function(self, x):
        return 0 if x <= 0 else 1

    def sigmoid(self, x):
        # print(x, self.num, self.layer, self.output_value)
        if x < -2:
            x = -2
        return 1.0 / (1.0 + math.exp(-4.9*x))   # maybe should be -4.9*x

    def is_connected_to(self, node):
        if node.layer == self.layer:
            return False
        if node.layer < self.layer:
            for out_connect in node.output_connections:
                if out_connect.to_node == self:
                    return True
        else:
            for out_connect in self.output_connections:
                if out_connect.to_node == node:
                    return True
        return False

    def clone(self):
        clone = Node(self.num)
        clone.layer = self.layer
        return clone