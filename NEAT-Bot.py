import math
import random

# from connection_gene import ConnectionGene
# from connection_history import ConnectionHistory
# from genome import Genome
# from node import Node
# from player import Player
from population import Population
# from species import Species

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class NEATBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()

        # NEAT stuff
        self.population = Population(10)
        self.bot_score = 0



    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        if packet.game_cars[self.index].score_info.score > self.bot_score:
            reward = packet.game_cars[self.index].score_info.score - self.bot_score
            self.bot_score = packet.game_cars[self.index].score_info.score
            
        self.reset_controller_state()

        inputs = self.get_inputs(packet)

        if self.population.done():
            self.population.natural_selection()

        choice = self.population.update_alive(inputs, reward)
        self.set_controller_state(choice)

        return self.controller_state
    
    def reset_controller_state(self):
        self.controller_state.throttle = 0
        self.controller_state.steer = 0
        self.controller_state.pitch = 0
        self.controller_state.yaw = 0
        self.controller_state.roll = 0
        self.controller_state.jump = 0
        self.controller_state.boost = 0
        self.controller_state.handbrake = 0

    def set_controller_state(self, choice):
        if choice == 0:
            self.controller_state.throttle = 1
        elif choice == 1:
            self.controller_state.throttle = 1
            self.controller_state.steer = 1
        elif choice == 2:
            self.controller_state.throttle = 1
            self.controller_state.steer = -1
        else:
            print("UNEXPECTED: unknown choice")


    def get_inputs(self, packet):
        ball = Vector2(packet.game_ball.physics.location.x,
                        packet.game_ball.physics.location.y)
        ball_speed = Vector2(packet.game_ball.physics.velocity.x,
                        packet.game_ball.physics.velocity.y).mag()
        my_car = packet.game_cars[self.index]
        bot = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        bot_speed = Vector2(my_car.physics.velocity.x, my_car.physics.velocity.y).mag()
        bot_dir = get_car_facing_vector(my_car)
        car_to_ball = ball - bot
        angle_to_ball = bot_dir.correction_to(car_to_ball)

        input_array = [bot.x, bot.y, bot_speed, ball.x, ball.y, ball_speed, bot_dir, angle_to_ball]
        return input_array
        

class Vector2:
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2(self.x + val.x, self.y + val.y)

    def __sub__(self, val):
        return Vector2(self.x - val.x, self.y - val.y)

    def mag(self):
        return math.sqrt((self.x**2) + (self.y**2))

    def correction_to(self, ideal):
        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)
        correction = ideal_in_radians - current_in_radians
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi
        return correction


def get_car_facing_vector(car):
    pitch = float(car.physics.rotation.pitch)
    yaw = float(car.physics.rotation.yaw)

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vector2(facing_x, facing_y)

