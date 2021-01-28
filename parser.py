
from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ErrorType:
    winner: bool = False
    error: bool = False
    forced_error: bool = False


@dataclass(frozen=True)
class Terminal:
    winner: bool = False
    error: bool = False
    forced_error: bool = False


@dataclass(frozen=True)
class StrokeType:
    forehand: bool = False
    backhand: bool = False
    forehand_slice: bool = False
    backhand_slice: bool = False
    volley: bool = False
    lob: bool = False
    smash: bool = False


@dataclass(frozen=True)
class ServeDirection:
    down_t: bool = False
    body: bool = False
    wide: bool = False


@dataclass(frozen=True)
class ShotDirection:
    middle: bool = False
    bh: bool = False
    fh: bool = False


@dataclass(frozen=True)
class ReturnDepth:
    shallow: bool = False
    middle: bool = False
    deep: bool = False


@dataclass(frozen=True)
class CourtPosition:
    approach: bool = False
    net: bool = False
    baseline: bool = False


class Shot(object):

    def __init__(self, terminal=None, error=None):
        self.terminal = terminal
        self.error_type = error
        self.serve_direction = None
        self.stroke_type = None
        self.return_depth = None

    @staticmethod
    def segment_string(s: str) -> List[str]:
        shot_strs = []  # List[str]
        start_pos = 0
        curr_shot_str = ''
        for curr_pos in range(len(s)):
            c = s[curr_pos]
            if curr_pos == 0:
                continue
            else:
                if c in {4, 5, 6}:  # serve
                    curr_shot_str = c
                elif c in {'@', '#', '*'}:  # current point is terminal
                    curr_shot_str += c
                elif c in {'f', 'b', 's', 'r', 'v', 'l', 'o', 'm'}:  #
                    shot_strs.append(s[start_pos: curr_pos])
                    start_pos = curr_pos
                    curr_shot_str = c
                elif c in {'1', '2', '3'}:  # direction annotation
                    curr_shot_str += c
                elif c in {'n', 'w', 'd', 'x'}:  # error annotation
                    curr_shot_str += c
                elif c in {'7', '8', '9'}:  # return depth annotation
                    curr_shot_str += c
                elif c in {'+', '-', '='}:  # court position annotation
                    curr_shot_str += c
        else:
            shot_strs.append(s[start_pos:])

        return shot_strs


class Serve(Shot):

    def __init__(self, serve_direction: ServeDirection, terminal=None, error=None):
        super().__init__(terminal, error)
        self.serve_direction = serve_direction


class GroundStroke(Shot):

    def __init__(self, stroke_type: StrokeType, shot_direction: ShotDirection, terminal=None, error=None):
        super().__init__(terminal, error)
        self.stroke_type = stroke_type
        self.shot_direction = shot_direction


class Return(GroundStroke):

    def __init__(self, return_depth: ReturnDepth, stroke_type: StrokeType, shot_direction: ShotDirection, terminal=None, error=None):
        super().__init__(stroke_type, shot_direction, terminal, error)
        self.return_depth = return_depth