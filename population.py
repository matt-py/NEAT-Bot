import math
from player import Player
from species import Species

class Population:

    super_speed = 1

    def __init__(self, size):
        self.players = []
        self.best_player = None
        self.current_player = None
        self.current_player_index = 0
        self.best_score = 0
        self.global_best_score = 0
        self.gen = 1
        self.innovation_history = []
        self.gen_players = []
        self.species = []

        self.mass_extinction_event = False
        self.new_stage = False

        self.gens_since_new_world = 0

        for _ in range(size):
            self.players.append(Player())
            # self.players[len(self.players)-1].brain.fully_connect(self.innovation_history)
            self.players[len(self.players)-1].brain.mutate(self.innovation_history)
            self.players[len(self.players)-1].brain.generate_network()
        
        self.get_next_player(True)

    def get_current_best(self):
        for player in self.players:
            if not player.dead:
                return player
        return self.players[0]

    def get_next_player(self, reset=False):
        if reset:
            self.current_player_index = 0
            self.current_player = self.players[0]
        else:
            self.current_player_index += 1
            self.current_player = self.players[self.current_player_index]

    def update_alive(self, inputs, reward):
        output = None
        self.current_player.reward(reward)
        if self.current_player is None:
            print("UNEXPECTED: current_player is None")
        elif self.current_player.dead:
            self.get_next_player(False)
        self.current_player.look(inputs)
        output = self.current_player.think()
        self.current_player.update()
        if self.current_player.score > self.global_best_score:
            self.global_best_score = self.current_player.score
        return output

    def done(self):
        for player in self.players:
            if not player.dead:
                return False
        return True

    def set_best_player(self):
        temp_best = self.species[0].players[0]
        temp_best.gen = self.gen

        if temp_best.score >= self.best_score:
            self.gen_players.append(temp_best.clone())
            print("old best: " + self.best_score)
            print("new best: " + temp_best.score)
            self.best_score = temp_best.score
            self.best_player = temp_best.clone()

    def natural_selection(self):
        previous_best = self.players[0]
        self.speciate()
        self.calculate_fitness()
        self.sort_species()
        if (self.mass_extinction_event):
            self.mass_extinction()
            self.mass_extinction_event = False
        self.cull_species()
        self.set_best_player()
        self.kill_stale_species()
        self.kill_bad_species()

        print(("generation: " + self.gen
                " Num of mutations: " + len(self.innovation_history)
                " species: " + len(self.species)
                " <<<<<<<<<<<<<<<<<"))
        
        average_sum = self.get_avg_fitness_sum()
        children = []
        for specie in self.species:
            children.append(specie.champ.clone())
            num_of_children = math.floor(specie.average_fitness / average_sum * len(self.players)) - 1
            for _ in range(num_of_children):
                children.append(specie.give_me_baby(self.innovation_history))
            
        if len(children) < len(self.players):
            children.append(previous_best.clone())
        while len(children) < len(self.players):
            children.append(self.species[0].give_me_baby(self.innovation_history))

        self.players = list(children)
        self.gen += 1
        for player in self.players:
            player.brain.generate_network()
        self.get_next_player(True)

    def speciate(self):
        for s in self.species:
            s.players = []
        for player in self.players:
            species_found = False
            for s in self.species:
                if s.same_species(player.brain):
                    s.add_to_species(player)
                    species_found = True
                    break
            if not species_found:
                self.species.append(Species(player))

    def calculate_fitness(self):
        for player in self.players[1:]:
            player.calculate_fitness()

    def sort_species(self):
        for s in self.species:
            s.sort_species()
        temp = sorted(self.species, key=lambda x: x.best_fitness, reverse=True)
        self.species = []
        self.species = list(temp)

    def kill_stale_species(self):
        i = 2
        while i < len(self.species):
            if self.species[i].staleness >= 15:
                del self.species[i]
                i -= 1
            i += 1

    def kill_bad_species(self):
        average_sum = self.get_avg_fitness_sum()
        i = 1
        while i < len(self.species):
            if (self.species[i].average_fitness / average_sum * len(self.players)) < 1:
                del self.species[i]
                i -= 1
            i += 1
    
    def get_avg_fitness_sum(self):
        average_sum = 0
        for s in self.species:
            average_sum += s.average_fitness
        return average_sum

    def cull_species(self):
        for s in self.species:
            s.cull()
            s.fitness_sharing()
            s.set_average()

    def mass_extinction(self):
        i = 5
        while i < len(self.species):
            del self.species[i]