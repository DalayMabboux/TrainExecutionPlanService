from dataclasses import dataclass
from enum import Enum
from random import randint
from random import choice

import numpy as np

track_switch_block_count = 6

def update_track_switches(action: int, track_switch_states: np.array) -> np.array:
    match action:
        case 4:
            track_switch_states[0] = 0
            return track_switch_states
        case 5:
            track_switch_states[0] = 1
            return track_switch_states
        case 6:
            track_switch_states[1] = 0
            return track_switch_states
        case 7:
            track_switch_states[1] = 1
            return track_switch_states
        case 8:
            track_switch_states[2] = 0
            return track_switch_states
        case 9:
            track_switch_states[2] = 1
            return track_switch_states
        case 10:
            track_switch_states[3] = 0
            return track_switch_states
        case 11:
            track_switch_states[3] = 1
            return track_switch_states
        case _:
            return track_switch_states

class LocomotiveAction(Enum):
    FORWARD = 1  # clockwise
    BACKWARD = 2  # anti clockwise
    STAY = 3
    ERROR = 4

class TrackSwitchAction(Enum):
    STRAIGHT = 1
    DIVERGING = 2
    STAY = 3
    ERROR = 4


class TrackSwitchState(Enum):
    STRAIGHT = 1
    DIVERGING = 2


@dataclass
class Action:
    locomotive_1: LocomotiveAction
    locomotive_2: LocomotiveAction
    track_switch_1: TrackSwitchAction
    track_switch_2: TrackSwitchAction
    track_switch_3: TrackSwitchAction
    track_switch_4: TrackSwitchAction


track_model = {
    0: {
        0: {
            'trackSwitch': 1,
            0: 2,
            1: -1
        },
        1: {
            'trackSwitch': 0,
            0: 5,
            1: -1
        }
    },
    1: {
        0: {
            'trackSwitch': 1,
            0: -1,
            1: 2
        },
        1: {
            'trackSwitch': 0,
            0: -1,
            1: 5
        }
    },
    2: {
        0: {
            'trackSwitch': 2,
            0: 5,
            1: {
              'trackSwitch': 3,
                0: 4,
                1: 3,
            }
        },
        1: {
            'trackSwitch': 1,
            0: 0,
            1: 1
        }
    },
    3: {
        1: {
            'trackSwitch': 3,
            0: -1,
            1: {
              'trackSwitch': 2,
                0: -1,
                1: 2
            }
        }
    },
    4: {
        1: {
            'trackSwitch': 3,
            0: {
              'trackSwitch': 2,
                0: -1,
                1: 2
            },
            1: -1
        }
    },
    5: {
        0: {
            'trackSwitch': 0,
            0: 0,
            1: 1
        },
        1: {
            'trackSwitch': 2,
            0: 2,
            1: -1
        }
    }
}


def apply_action_to_track_switch(track_switch_action: TrackSwitchAction, track_switch_state: TrackSwitchState) -> TrackSwitchState:
  match track_switch_action:
    case TrackSwitchAction.STAY:
      return track_switch_state
    case TrackSwitchAction.STRAIGHT:
      return TrackSwitchState.STRAIGHT
    case TrackSwitchAction.DIVERGING:
      return TrackSwitchState.DIVERGING



def get_new_block(current_block: int, move_direction: int, track_switch_states: np.array) -> int:
    sub_model = track_model[current_block].get(move_direction)
    if sub_model is None:
        return -1
    track_switch = sub_model['trackSwitch']
    track_state = track_switch_states[track_switch]
    new_block = sub_model[track_state]
    if not isinstance(new_block, (int)):
        sub_sub_model = new_block
        sub_switch = new_block['trackSwitch']
        sub_switch_state = track_switch_states[sub_switch]
        return sub_sub_model[sub_switch_state]
    return new_block


def decode_action(action: int) -> Action:
    lok1_action = action & 3
    lok2_action = (action & (3 << 2)) >> 2
    w1 = (action & (3 << 4)) >> 4
    w2 = (action & (3 << 6)) >> 6
    w3 = (action & (3 << 8)) >> 8
    w4 = (action & (3 << 10)) >> 10
    return Action(_decode_locomotive_action(lok1_action),
                  _decode_locomotive_action(lok2_action),
                  _decode_track_switch_action(w1),
                  _decode_track_switch_action(w2),
                  _decode_track_switch_action(w3),
                  _decode_track_switch_action(w4),
                  )


def _decode_locomotive_action(action_code: int) -> LocomotiveAction:
    match action_code:
        case 0:
            return LocomotiveAction.STAY
        case 1:
            return LocomotiveAction.FORWARD
        case 2:
            return LocomotiveAction.BACKWARD
        case 3:
            return LocomotiveAction.ERROR


def _decode_track_switch_action(action_code: int) -> TrackSwitchAction:
    match action_code:
        case 0:
            return TrackSwitchAction.STAY
        case 1:
            return TrackSwitchAction.STRAIGHT
        case 2:
            return TrackSwitchAction.DIVERGING
        case 3:
            return TrackSwitchAction.ERROR


def random_states() -> [int, int, int, int]:
    locomotive_1_initial = randint(0, track_switch_block_count)
    locomotive_2_initial = choice([i for i in range(0, track_switch_block_count) if i != locomotive_1_initial])
    locomotive_1_target = randint(0, track_switch_block_count)
    locomotive_2_target = choice([i for i in range(0, track_switch_block_count) if i != locomotive_1_target])
    return [locomotive_1_initial, locomotive_2_initial, locomotive_1_target, locomotive_2_target]


def is_action_invalid(action: Action) -> bool:
    return (
            action.locomotive_1 == LocomotiveAction.ERROR
            or action.locomotive_2 == LocomotiveAction.ERROR
            or action.track_switch_1 == LocomotiveAction.ERROR
            or action.track_switch_2 == LocomotiveAction.ERROR
            or action.track_switch_3 == LocomotiveAction.ERROR
            or action.track_switch_4 == LocomotiveAction.ERROR
    )

