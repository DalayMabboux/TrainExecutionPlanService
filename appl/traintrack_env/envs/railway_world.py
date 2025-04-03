from random import choice
from random import randint

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.core import RenderFrame

# from traintrack_env.envs.action_decoder import decode_action
from appl.traintrack_env.envs.model import get_new_block, update_track_switches

# from traintrack_env.envs.utility import random_states, is_action_invalid

train_block_in_image = [
    (337, 62),
    (333, 134),
    (544, 402),
    (280, 398),
    (255, 306),
    (198, 317),
    (95, 332),
    (0, 0)
]

class RailwayEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 1}

    def __init__(self, render_mode="rgb_array"):
        self._switch_states_initial = None
        self._locomotive_1_initial = None
        self._locomotive_2_initial = None
        self._target_locomotive_2 = None
        self._target_locomotive_1 = None
        self.state = np.array([], dtype=np.int16)
        self.render_mode = render_mode

        # Pygame
        self.screen_width = 600
        self.screen_height = 400
        self.screen = None
        self.img = None
        self.clock = None

        # 2x current train location + 2x destination train location + 4x switch states
        self.low_state = np.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int16)
        self.high_state = np.array([5, 5, 5, 5, 1, 1, 1, 1], dtype=np.int16)
        self.observation_space = spaces.Box(low=self.low_state, high=self.high_state, dtype=np.int16)

        self.action_space = spaces.Discrete(12)


    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        if options and"a" in options:
            self.state = options['a'][0]
            self._target_locomotive_1 = self.state[2]
            self._target_locomotive_2 = self.state[3]
        else:
            # Random train target location
            self._target_locomotive_1 = randint(0, 5)
            self._target_locomotive_2 = choice([i for i in range(0, 5) if i != self._target_locomotive_1])

            # Random train initial location
            self._locomotive_1_initial: np.int16 = randint(0, 5)
            self._locomotive_2_initial = choice([i for i in range(0, 5) if i != self._locomotive_1_initial])
            self._switch_states_initial = np.array([randint(0, 1), randint(0, 1), randint(0, 1), randint(0, 1)], dtype=np.int16)

            self.state = np.concatenate(
                (np.array([
                    self._locomotive_1_initial,
                    self._locomotive_2_initial,
                    self._target_locomotive_1,
                    self._target_locomotive_2], dtype=np.int16),
                 self._switch_states_initial), axis=0, dtype=np.int16)

        return np.array(self.state, dtype=np.int16), {}

    def step(self, action: int):
      current_track_switch_states = self.state[-4:]
      current_train_state_1 = self.state[0]
      current_train_state_2 = self.state[1]
      updated_track_switches_states = update_track_switches(action, current_track_switch_states)
      locomotive_1_new_block = current_train_state_1
      locomotive_2_new_block = current_train_state_2

      match action:
        case 0 | 1:
          locomotive_1_new_block = get_new_block(current_train_state_1, action, updated_track_switches_states)
        case 2 | 3:
          locomotive_2_new_block = get_new_block(current_train_state_2, action - 2, updated_track_switches_states)

      reward = -1
      terminated = False
      info = {}
      if locomotive_1_new_block == locomotive_2_new_block or locomotive_1_new_block == -1 or locomotive_2_new_block == -1:
          info = {
              "locomotive_1_new_block": locomotive_1_new_block,
              "locomotive_2_new_block": locomotive_2_new_block,
              "action": action
          }
          terminated = True
      else:
          if locomotive_1_new_block == self._target_locomotive_1 and locomotive_2_new_block == self._target_locomotive_2:
              terminated = True
              reward = 100

      self.state = np.concatenate(
            (np.array([
                locomotive_1_new_block,
                locomotive_2_new_block,
                self._target_locomotive_1,
                self._target_locomotive_2], dtype=np.int16),
             updated_track_switches_states), axis=0, dtype=np.int16)

      return self.state, reward, terminated, False, info

    def render(self):
        pass