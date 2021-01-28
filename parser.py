
from __future__ import annotations
from enum import Enum
from typing import List


class ErrorType(Enum):
    net = 'n'
    wide = 'w'
    deep = 'd'
    wide_and_deep = 'x'


class Terminal(Enum):
    winner = '*'
    error = '@'
    forced_error = '#'


class StrokeType(Enum):
    forehand = 'f'
    backhand = 'b'
    forehand_slice = 'r'
    backhand_slice = 's'
    volley = 'v'
    backhand_lob = 'm'
    lob = 'l'
    smash = 'o'


class ServeDirection(Enum):
    down_t = 6
    body = 5
    wide = 4


class ShotDirection(Enum):
    middle = 2
    bh = 3
    fh = 1


class ReturnDepth(Enum):
    shallow = 7
    middle = 8
    deep = 9


class CourtPosition(Enum):
    approach = '+'
    net = '-'
    baseline = '='


class Shot(object):

    def __init__(self, court_position: CourtPosition, terminal: Terminal = None, error: ErrorType = None):
        self.court_position = court_position
        self.terminal = terminal
        self.error_type = error
        self.serve_direction = None
        self.stroke_type = None
        self.return_depth = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    @staticmethod
    def parse_shots_string(s: str) -> List[Shot]:
        segmented_strs = Shot.segment_string(s)
        shots = []
        for position, sub_str in enumerate(segmented_strs):
            shots.append(Shot.parse_shot_string(sub_str, position == 1))

        return shots

    @staticmethod
    def parse_shot_string(s: str, is_return=False) -> Shot:
        assert len(s) > 0

        terminal = None
        for c in ['@', '#', '*']:
            if c in s:
                terminal = Terminal(c)

        stroke_type = None
        for c in ['f', 'b', 'r', 's', 'v', 'm', 'l', 'o']:
            if c in s:
                stroke_type = StrokeType(c)

        return_depth = None
        for c in ['7', '8', '9']:
            if c in s:
                return_depth = ReturnDepth(int(c))

        court_position = None
        for c in ['+', '-', '=']:
            if c in s:
                court_position = CourtPosition(c)

        shot_direction = None
        for c in ['1', '2', '3']:
            if c in s:
                shot_direction = ShotDirection(int(c))

        serve_direction = None
        for c in ['4', '5', '6']:
            if c in s:
                serve_direction = ServeDirection(int(c))

        error = None
        for c in ['n', 'w', 'd', 'x']:
            if c in s:
                error = ErrorType(c)

        if is_return or return_depth is not None:
            return Return(
                return_depth=return_depth,
                stroke_type=stroke_type,
                shot_direction=shot_direction,
                court_position=court_position,
                terminal=terminal,
                error=error
            )
        if serve_direction is not None:
            return Serve(
                court_position=court_position,
                terminal=terminal,
                serve_direction=serve_direction,
                error=error
            )
        else:
            return GroundStroke(
                stroke_type=stroke_type,
                shot_direction=shot_direction,
                court_position=court_position,
                terminal=terminal,
                error=error
            )

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

    def __init__(self,serve_direction: ServeDirection,  court_position: CourtPosition = None, terminal=None, error=None):
        super().__init__(court_position, terminal, error)
        self.serve_direction = serve_direction


class GroundStroke(Shot):

    def __init__(self, stroke_type: StrokeType, shot_direction: ShotDirection = None, court_position: CourtPosition = None, terminal=None, error=None):
        super().__init__(court_position, terminal, error)
        self.stroke_type = stroke_type
        self.shot_direction = shot_direction


class Return(GroundStroke):

    def __init__(self, return_depth: ReturnDepth = None, stroke_type: StrokeType = None, shot_direction: ShotDirection = None, court_position: CourtPosition = None, terminal=None, error=None):
        super().__init__(stroke_type, shot_direction, court_position, terminal, error)
        self.return_depth = return_depth