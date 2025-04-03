from typing import Callable

import gymnasium as gym
import torch
import torch.nn as nn
import numpy as np
import os
import appl.traintrack_env

from torch.distributions.categorical import Categorical

from functools import reduce
import operator

# NICHT ENTFERNEN
# from appl.traintrack_env.envs.model import LocomotiveAction, TrackSwitchAction

checks = [
    [[4, 2, 2, 1, 0, 1, 1, 1], [1, 3, 1]],
    [[1, 3, 6, 3, 0, 0, 0, 0], [7, 0, 0]], # geht auch kürzer: S0 auf diverging dann Lok1 1 x rückwärts
    [[4, 0, 1, 2, 1, 1, 1, 0], [11, 1, 1, 1, 6, 2]],
    [[4, 0, 1, 4, 0, 0, 1, 0], [11, 1, 1, 5, 10, 8, 0, 11, 2, 0, 9, 2, 2]] # korrekt, aber nicht optimal
]

def evaluate(
    initial_state: np.ndarray,
    model_path: str,
    make_env: Callable,
    env_id: str,
    eval_episodes: int,
    Model: torch.nn.Module,
    device: torch.device = torch.device("cpu"),
):
    envs = gym.vector.SyncVectorEnv([make_env(env_id)])
    agent = Model(envs).to(device)
    agent.load_state_dict(torch.load(model_path, map_location=device))
    agent.eval()

    obs, _ = envs.reset(options={'a': initial_state})
    episodic_returns = []
    done_actions = []
    while len(episodic_returns) < eval_episodes:
        actions, _, _, _ = agent.get_action_and_value(torch.Tensor(obs).to(device))
        next_obs, _, _, _, infos = envs.step(actions.cpu().numpy())
        done_actions += [actions.cpu().numpy()]
        if "final_info" in infos:
            for info in infos["final_info"]:
                if "episode" not in info:
                    continue
                episodic_returns += [info["episode"]["r"]]
        obs = next_obs
        if len(episodic_returns) == 1 and episodic_returns[0] < 0:
            episodic_returns = []
            obs, _ = envs.reset(options={'a': initial_state})

    return done_actions

def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer

class Agent(nn.Module):
    def __init__(self, envs):
        super().__init__()
        self.critic = nn.Sequential(
            layer_init(nn.Linear(np.array(envs.single_observation_space.shape).prod(), 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 1), std=1.0),
        )
        self.actor = nn.Sequential(
            layer_init(nn.Linear(np.array(envs.single_observation_space.shape).prod(), 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, envs.single_action_space.n), std=0.01),
        )

    def get_value(self, x):
        return self.critic(x)

    def get_action_and_value(self, x, action=None):
        logits = self.actor(x)
        probs = Categorical(logits=logits)
        if action is None:
            action = probs.sample()
        return action, probs.log_prob(action), probs.entropy(), self.critic(x)

def make_env(env_id):
    def thunk():
        env = gym.make(env_id)
        env = gym.wrappers.RecordEpisodeStatistics(env)
        return env
    return thunk

def flatten(xss):
    return [x for xs in xss for x in xs]

def run_ppo(input_vector: [int]):
    my_path = os.path.abspath(os.path.dirname(__file__))
    model_path = os.path.join(my_path, "ppo.cleanrl_model")
    torch.load(model_path)

    ret = evaluate(
        np.array([input_vector], dtype=np.int16),
        model_path,
        make_env,
        "traintrack_env/Railway-v0",
        eval_episodes=1,
        Model=Agent,
        device="cpu",
    )
    return flatten(ret)

def get_best_actions(input_vector: [int], number: int):
    res_list = []
    for _ in range(number):
        res_list.append(run_ppo(input_vector))
    return reduce(lambda a, v: a if len(a) < len(v) else v, res_list)

if __name__ == "__main__":
    print(get_best_actions([1, 2, 3, 5, 1, 1, 0, 1], 50))

# [4,3,3,4,0,0,0,0] => 9, 1, 1, 11, 3, 10, 2, 0, 11, 0 (korrekt)
# darstellungsproblem

# [0,2,1,5,1,1,0,1] => [10, 9, 2, 11, 4, 1, 5, 0, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, .....
#                      [2, 6, 0, 7, 1]
# [1,2,3,5,1,1,0,1] => [9, 10, 2, 11, 0, 10, 11, 10, 11, 11, 1, 9, 0, 10, 11, 10, 11, 10, 11, 0, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 9, 11, 10, 11, 10, 1]
#                      [2, 0, 9, 0]
# [1,2,5,3,1,1,0,1] => [1, 9, 2] korrekt
# [5,3,4,3,1,1,0,1] => [10, 9, 3]
#                      [1, 9, 10, 0]
# [2,5,4,3,1,1,0,1] => darstellungsfehler "ERROR: malformed path: #p3-1"
#                      [2, 0, 1, 9, 10, 0, 2, 11, 2]
# [1,5,4,3,1,1,0,1] => [3, 9, 2, 10, 0, 0]

# 0,1,1,0,0,0,0,0 works
# [5, 9, 1, 1, 11, 3, 10, 2, 0, 11, 0]

# [1,3,4,2,1,0,1,0] funktioniert nur manchmal
# [1, 8, 1, 9, 0, 11, 3] korrekt?
#  1, 7, 3, 7, 1, 8, 1, 9, 0, 11, 3
#  1, 11, 3, 8, 3, 1, 9, 10, 0, 2