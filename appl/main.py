from enum import Enum

from fastapi import FastAPI
from typing import List
from starlette.staticfiles import StaticFiles

from appl.ppo_eval import get_best_actions

# NICHT ENTFERNEN
# from appl.traintrack_env.envs.model import LocomotiveAction, TrackSwitchAction

import appl.traintrack_env
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
    SWITCH_2_DIVERGING = "switch_2_diverging"
    SWITCH_3_STRAIGHT = "switch_3_straight"
    SWITCH_3_DIVERGING = "switch_3_diverging"

def action_to_enum(action_as_int: int) -> Action:
    return Action(list(Action._member_map_.items())[action_as_int][1])

api_app = FastAPI(title="api app")
@api_app.post("/evaluate-execution-plan")
async def evaluate_execution_plan(state_vector: list[int]) -> List[Action]:
    bla = get_best_actions(state_vector, 50)
    return list(map(action_to_enum, bla))

app = FastAPI(title="main app")
app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="./appl/html", html = True), name="site")




