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
        self.population = Population(20)
        self.bot_score = 0
        self.bot_dist_to_ball = 1000
        self.started = False



    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        if not self.started:
            self.bot_score = packet.game_cars[self.index].score_info.score
            car_to_ball_vec = Vector2(packet.game_ball.physics.location.x,
                        packet.game_ball.physics.location.y) - Vector2(packet.game_cars[self.index].physics.location.x,
                                                                        packet.game_cars[self.index].physics.location.y)
            car_to_ball_dist = car_to_ball_vec.mag()
            self.bot_dist_to_ball = car_to_ball_dist
            self.started = True
        reward = 0
        reward += (packet.game_cars[self.index].score_info.score - self.bot_score)*10
        self.bot_score = packet.game_cars[self.index].score_info.score
        car_to_ball_vec = Vector2(packet.game_ball.physics.location.x,
                        packet.game_ball.physics.location.y) - Vector2(packet.game_cars[self.index].physics.location.x,
                                                                        packet.game_cars[self.index].physics.location.y)
        car_to_ball_dist = car_to_ball_vec.mag()
        reward += ((50000/car_to_ball_dist) - (50000/self.bot_dist_to_ball))
        self.bot_dist_to_ball = car_to_ball_dist
            
        self.reset_controller_state()

        inputs = self.get_inputs(packet)

        if self.population.done():
            self.population.natural_selection()

        choice = self.population.update_alive(inputs, reward)
        self.action_text = ""
        self.set_controller_state(choice)

        self.render_nn()

        self.stop_bot_climbing_wall(packet)


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
        self.controller_state.throttle = choice[0]
        self.controller_state.steer = (choice[1]-0.5)*2
        # if choice == 0:
        #     self.controller_state.throttle = 1
        #     self.action_text = "throttle"
        # elif choice == 1:
        #     self.controller_state.throttle = 1
        #     self.controller_state.steer = 1
        #     self.action_text = "right"
        # elif choice == 2:
        #     self.controller_state.throttle = 1
        #     self.controller_state.steer = -1
        #     self.action_text = "left"
        # else:
        #     print("UNEXPECTED: unknown choice")

    def get_inputs(self, packet):
        ball = Vector2(packet.game_ball.physics.location.x,
                        packet.game_ball.physics.location.y)
        ballz = packet.game_ball.physics.location.z
        ball_speed = Vector2(packet.game_ball.physics.velocity.x,
                        packet.game_ball.physics.velocity.y).mag()
        my_car = packet.game_cars[self.index]
        bot = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        bot_speed = Vector2(my_car.physics.velocity.x, my_car.physics.velocity.y).mag()
        bot_dir = get_car_facing_vector(my_car)
        car_to_ball = ball - bot
        angle_to_ball = bot_dir.correction_to(car_to_ball)

        # bot.x = self.normalise_input(bot.x, -4096, 4096)
        # bot.y = self.normalise_input(bot.y, -6020, 6020)
        # bot_speed = self.normalise_input(bot_speed, 0, 1500)
        # ball.x = self.normalise_input(ball.x, -4096, 4096)
        # ball.y = self.normalise_input(ball.y, -6020, 6020)
        # ball_speed = self.normalise_input(ball_speed, 0, 2850)
        # bot.x = bot.x/100
        # bot.y = bot.y/100
        # ball.x = ball.x/100
        # ball.y = ball.y/100
        # bot_speed = bot_speed/50
        # ball_speed = ball_speed/50
        # angle_to_ball = self.normalise_input(angle_to_ball, (-2 * math.pi), (2 * math.pi))
        input_array = [bot.x, bot.y, bot_speed, ball.x, ball.y, ballz, ball_speed, angle_to_ball]  # bot_dir
        return input_array

    def normalise_input(self, input_i, min_i, max_i):
        return (input_i - min_i)/(max_i - min_i)

    def render_nn(self):
        # self.population.current_player.brain.print_genome()
        # print()
        self.renderer.begin_rendering()
        # nodes = self.population.current_player.brain.nodes
        # for node in nodes:
        #     self.renderer.draw_string_2d(5+(50*node.layer), (node.num*25)-(node.layer*175), 2, 2, str(node.num), self.renderer.white())
        p = self.population
        text_to_render = ("INFO \n"
                            "gen: " + str(p.gen) + "\n"
                            "player: " + str(p.current_player_index+1) + "/"
                            "" + str(len(p.players)) + "\n"
                            "num of genes: " + str(len(p.current_player.brain.genes)) + "\n"
                            "num of nodes: " + str(len(p.current_player.brain.nodes)) + "\n"
                            "lifespan: " + str(p.current_player.lifespan) + "\n"
                            "max lifespan: " + str(p.current_player.max_lifespan) + "\n"
                            "current score: " + str(p.current_player.score) + "\n"
                            "action: " + str(p.current_player.decision) + "\n"
                            )
        self.renderer.draw_string_2d(5, 5, 1, 1, text_to_render, self.renderer.white())

        self.renderer.end_rendering()

    def stop_bot_climbing_wall(self, packet):
        car = packet.game_cars[self.index].physics
        if car.rotation.pitch > 0.06 or car.location.z > 20:
            if self.controller_state.steer < 0.01:
                self.controller_state.steer = -1
        # self.controller_state.jump = 1
        # pitch = packet.game_cars[self.index].physics.rotation.pitch
        # roll = packet.game_cars[self.index].physics.rotation.roll
        # self.controller_state
        



        

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

