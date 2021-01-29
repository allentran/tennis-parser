
from enum import Enum
from typing import List

import pandas as pd


class ErrorType(Enum):
    net = 'n'
    wide = 'w'
    deep = 'd'
    wide_and_deep = 'x'
    foot_fault = 'g'


class Terminal(Enum):
    winner = '*'
    error = '@'
    forced_error = '#'


class StrokeType(Enum):
    forehand = 'f'
    backhand = 'b'
    forehand_slice = 'r'
    backhand_slice = 's'
    forehand_volley = 'v'
    backhand_volley = 'z'
    backhand_lob = 'm'
    lob = 'l'
    smash = 'o'
    backhand_smash = 'p'
    forehand_drop = 'u'
    backhand_drop = 'y'
    forehand_half_volley = 'h'
    backhand_half_volley = 'i'
    forehand_swinging_volley = 'j'
    backhand_swinging_volley = 'k'
    trickshot = 't'
    unknown = 'q'


class ServeDirection(Enum):
    down_t = 6
    body = 5
    wide = 4
    unknown = 0


class ShotDirection(Enum):
    middle = 2
    bh = 3
    fh = 1
    unknown = 0


class ReturnDepth(Enum):
    shallow = 7
    middle = 8
    deep = 9


class CourtPosition(Enum):
    approach = '+'
    net = '-'
    baseline = '='


class Shot(object):

    def __init__(self, court_position: CourtPosition, terminal: Terminal = None, error: ErrorType = None, raw_string=None):
        self.court_position = court_position
        self.terminal = terminal
        self.error_type = error
        self.raw_string = raw_string
        self.serve_direction = None
        self.stroke_type = None
        self.return_depth = None
        self.is_return = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            self_dict = {k: v for k, v in self.__dict__.items() if k != 'raw_string'}
            other_dict = {k: v for k, v in other.__dict__.items() if k != 'raw_string'}
            return self_dict == other_dict
        else:
            return False

    @staticmethod
    def explode_df(df: pd.DataFrame) -> pd.DataFrame:
        df['has_second'] = False
        df.loc[df['2nd'].notnull(), 'has_second'] = True
        shot_dicts = []
        for row in df.itertuples():
            match_details = {
                'match_id': row.match_id,
                'pt_nbr': row.Pt,
                'first_pt': True
            }
            shots = Shot.parse_shots_string(row._15)
            for shot_sequence_nbr, shot in enumerate(shots):
                shot_dict = shot.to_dict()
                shot_dict.update(match_details)
                shot_dict['shot_sequence_nbr'] = shot_sequence_nbr
                shot_dicts.append(shot_dict)

            if row.has_second:

                shots = Shot.parse_shots_string(row._16)
                for shot_sequence_nbr, shot in enumerate(shots):
                    shot_dict = shot.to_dict()
                    shot_dict.update(match_details)
                    shot_dict['shot_sequence_nbr'] = shot_sequence_nbr
                    shot_dict['first_pt'] = False
                    shot_dicts.append(shot_dict)
        return pd.DataFrame(shot_dicts)

    def to_dict(self):
        return {
            'court_position': None if self.court_position is None else self.court_position.name,
            'terminal': None if self.terminal is None else self.terminal.name,
            'error_type': None if self.error_type is None else self.error_type.name,
            'serve_direction': None if self.serve_direction is None else self.serve_direction.name,
            'stroke_type': None if self.stroke_type is None else self.stroke_type.name,
            'return_depth': None if self.return_depth is None else self.return_depth.name,
            'is_return': False if not self.is_return else True,
            'raw_string': self.raw_string
        }

    @staticmethod
    def parse_shots_string(s: str) -> List['Shot']:
        segmented_strs = Shot.segment_string(s)
        shots = []
        for position, sub_str in enumerate(segmented_strs):
            shots.append(Shot.parse_shot_string(sub_str, position == 1))

        return shots

    @staticmethod
    def parse_shot_string(s: str, is_return=False) -> 'Shot':
        assert len(s) > 0

        terminal = None
        for c in [t.value for t in Terminal]:
            if str(c) in s:
                terminal = Terminal(c)

        stroke_type = None
        for c in [st.value for st in StrokeType]:
            if str(c) in s:
                stroke_type = StrokeType(c)

        return_depth = None
        for c in [rt.value for rt in ReturnDepth]:
            if str(c) in s:
                return_depth = ReturnDepth(int(c))

        court_position = None
        for c in [cp.value for cp in CourtPosition]:
            if str(c) in s:
                court_position = CourtPosition(c)

        shot_direction = None
        for c in [sd.value for sd in ShotDirection]:
            if str(c) in s:
                shot_direction = ShotDirection(int(c))

        serve_direction = None
        for c in [sd.value for sd in ServeDirection]:
            if str(c) in s:
                serve_direction = ServeDirection(int(c))

        error = None
        for c in [e.value for e in ErrorType]:
            if str(c) in s:
                error = ErrorType(c)

        if is_return or return_depth is not None:
            return Return(
                return_depth=return_depth,
                stroke_type=stroke_type,
                shot_direction=shot_direction,
                court_position=court_position,
                terminal=terminal,
                error=error,
                raw_string=s
            )
        if serve_direction is not None:
            return Serve(
                court_position=court_position,
                terminal=terminal,
                serve_direction=serve_direction,
                error=error,
                raw_string=s
            )
        else:
            return GroundStroke(
                stroke_type=stroke_type,
                shot_direction=shot_direction,
                court_position=court_position,
                terminal=terminal,
                error=error,
                raw_string=s
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
                if c in set([str(serve_direction.value) for serve_direction in ServeDirection]):
                    curr_shot_str = c
                elif c in set([str(terminal.value) for terminal in Terminal]):
                    curr_shot_str += c
                elif c in set([str(stroke_type.value) for stroke_type in StrokeType]):
                    shot_strs.append(s[start_pos: curr_pos])
                    start_pos = curr_pos
                    curr_shot_str = c
                elif c in set([str(sd.value) for sd in ShotDirection]):
                    curr_shot_str += c
                elif c in set([str(e.value) for e in ErrorType]):
                    curr_shot_str += c
                elif c in set([str(r.value) for r in ReturnDepth]):
                    curr_shot_str += c
                elif c in set([str(cp.value) for cp in CourtPosition]):
                    curr_shot_str += c
        else:
            shot_strs.append(s[start_pos:])

        return shot_strs


class Serve(Shot):

    def __init__(self,serve_direction: ServeDirection,  court_position: CourtPosition = None, terminal=None, error=None, raw_string=None):
        super().__init__(court_position, terminal, error, raw_string=raw_string)
        self.serve_direction = serve_direction


class GroundStroke(Shot):

    def __init__(self, stroke_type: StrokeType, shot_direction: ShotDirection = None, court_position: CourtPosition = None, terminal=None, error=None, raw_string=None):
        super().__init__(court_position, terminal, error, raw_string=raw_string)
        self.stroke_type = stroke_type
        self.shot_direction = shot_direction


class Return(GroundStroke):

    def __init__(self, return_depth: ReturnDepth = None, stroke_type: StrokeType = None, shot_direction: ShotDirection = None, court_position: CourtPosition = None, terminal=None, error=None, raw_string=None):
        super().__init__(stroke_type, shot_direction, court_position, terminal, error, raw_string=raw_string)
        self.return_depth = return_depth
        self.is_return = True