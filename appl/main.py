from enum import Enum

from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from appl.ppo_eval import run_ppo

# NICHT ENTFERNEN
# from appl.traintrack_env.envs.model import LocomotiveAction, TrackSwitchAction

import appl.traintrack_env

app = FastAPI()

class State(BaseModel):
    train1_initial_position: int
    train1_target_position: int
    train2_initial_position: int
    train2_target_position: int
    switch_state: List[int]

class Action(Enum):
    TRAIN_1_FORWARD = "train_1_forward"
    TRAIN_1_BACKWARD = "train_1_backward"
    TRAIN_2_FORWARD = "train_2_forward"
    TRAIN_2_BACKWARD = "train_2_backward"
    SWITCH_0_STRAIGHT = "switch_0_straight"
    SWITCH_0_DIVERGING = "switch_0_diverging"
    SWITCH_1_STRAIGHT = "switch_1_straight"
    SWITCH_1_DIVERGING = "switch_1_diverging"
    SWITCH_2_STRAIGHT = "switch_2_straight"
    SWITCH_2_DIVERGING = "switch_3_diverging"
    SWITCH_3_STRAIGHT = "switch_3_straight"
    SWITCH_3_DIVERGING = "switch_3_diverging"


def action_to_enum(action_as_int: int) -> Action:
    return Action(list(Action._member_map_.items())[action_as_int][1])

@app.post("/evaluate-execution-plan")
async def evaluate_execution_plan(state: State) -> List[Action]:
    bla = run_ppo(state_to_vec(state))
    return list(map(action_to_enum, bla))

def state_to_vec(state: State) -> [int]:
    return [state.train1_initial_position, state.train2_initial_position, state.train1_target_position, state.train2_target_position, *state.switch_state]