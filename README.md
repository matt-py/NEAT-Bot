# NEAT-Bot

NEAT-Bot is an implementation of Neuroevolution of Augmenting Topologies (NEAT) for a machine-learning bot written in Python.

This bot learns to play Rocket League by integrating with the RLBot framework.


## How It Works

A population of genomes is created, with each genome containing a network of nodes and node connections. Each genome has a lifespan in which it uses its network to decide what to do in the game, and when its lifespan is reached, its success is measured. When the entire population of genomes have all reached their lifespan, the best genomes become the parents of generation 2 by sharing and adjusting the nodes and connections in their networks. This cycle is then repeatedly indefinitely, generation after generation, with the hope of improving the measurable success.

#### Current Success

* 17/03/19 - Bot can successfully hit the ball and score using a basic implementation of NEAT


### TODO

- [x] Add all files for a working implementation of NEAT
- [x] Define simple inputs. Define simple outputs of throttle and steer
- [x] Adjustments to get the bot learning correctly

- [x] Add saving neural networks using pickle
- [ ] Add loading neural networks using pickle
- [ ] Try adding parallelism/running multiple bots at once (may be possible with subprocess communication)
- [ ] Modify inputs to be relative to the bot
- [ ] Compare relative inputs to non-relative inputs
- [ ] Add advanced outputs (the rest of the controller states)
- [ ] Add advanced (calculated) inputs
- [ ] Add more rewards
- [ ] Improve rewards system
- [ ] Improve fitness function
- [ ] Add mechanics like double jump, dodge, half-flip as outputs
