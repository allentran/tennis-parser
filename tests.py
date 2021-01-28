import unittest

import pandas as pd

from parser import Shot, GroundStroke, Serve, ServeDirection, StrokeType, Terminal, ErrorType, ShotDirection, Return, ReturnDepth, CourtPosition


class ParserTests(unittest.TestCase):

    def test_real_data(self):
        df = pd.read_csv('test_data/points.csv', encoding='latin1')
        for s in df['1st']:
            shots = Shot.parse_shots_string(s)
            self.assertGreaterEqual(len(shots), 1)
        for s in df[df['2nd'].notnull()]['2nd']:
            shots = Shot.parse_shots_string(s)
            self.assertGreaterEqual(len(shots), 1)

    def test_shots(self):
        self.assertEqual(
            Shot.parse_shot_string('4'),
            Serve(serve_direction=ServeDirection.wide)
        )
        self.assertEqual(
            Shot.parse_shot_string('f'),
            GroundStroke(StrokeType.forehand)
        )
        self.assertEqual(
            Shot.parse_shot_string('b'),
            GroundStroke(StrokeType.backhand)
        )
        self.assertEqual(
            Shot.parse_shot_string('m'),
            GroundStroke(StrokeType.backhand_lob)
        )
        self.assertEqual(
            Shot.parse_shot_string('f*'),
            GroundStroke(StrokeType.forehand, terminal=Terminal.winner)
        )
        self.assertEqual(
            Shot.parse_shot_string('on@'),
            GroundStroke(StrokeType.smash, error=ErrorType.net, terminal=Terminal.error)
        )
        self.assertEqual(
            Shot.parse_shot_string('s28'),
            Return(
                return_depth=ReturnDepth.middle,
                stroke_type=StrokeType.backhand_slice,
                shot_direction=ShotDirection.middle
            )
        )
        self.assertEqual(
            Shot.parse_shot_string('v1'),
            GroundStroke(stroke_type=StrokeType.volley, shot_direction=ShotDirection.fh)
        )
        self.assertEqual(
            Shot.parse_shot_string('f-3*'),
            GroundStroke(
                stroke_type=StrokeType.forehand,
                shot_direction=ShotDirection.bh,
                court_position=CourtPosition.net,
                terminal=Terminal.winner
            )
        )
        self.assertEqual(
            Shot.parse_shot_string('b1w#'),
            GroundStroke(
                stroke_type=StrokeType.backhand,
                shot_direction=ShotDirection.fh,
                error=ErrorType.wide,
                terminal=Terminal.forced_error
            )
        )
        self.assertEqual(
            Shot.parse_shot_string('o=1'),
            GroundStroke(
                stroke_type=StrokeType.smash,
                court_position=CourtPosition.baseline,
                shot_direction=ShotDirection.fh,
            )
        )

    def test_shots_strs(self):
        s = '4ffbbf*'
        shot_strs = Shot.segment_string(s)
        self.assertEqual(len(shot_strs), 6)
        self.assertEqual(shot_strs[0], '4')
        self.assertEqual(shot_strs[1], 'f')
        self.assertEqual(shot_strs[2], 'f')
        self.assertEqual(shot_strs[3], 'b')
        self.assertEqual(shot_strs[4], 'b')
        self.assertEqual(shot_strs[5], 'f*')

        s = '6svlon@'
        shot_strs = Shot.segment_string(s)
        self.assertEqual(len(shot_strs), 5)
        self.assertEqual(shot_strs[0], '6')
        self.assertEqual(shot_strs[1], 's')
        self.assertEqual(shot_strs[2], 'v')
        self.assertEqual(shot_strs[3], 'l')
        self.assertEqual(shot_strs[4], 'on@')

        s = '4+s28v1f-3*'
        shot_strs = Shot.segment_string(s)
        self.assertEqual(len(shot_strs), 4)
        self.assertEqual(shot_strs[0], '4+')
        self.assertEqual(shot_strs[1], 's28')
        self.assertEqual(shot_strs[2], 'v1')
        self.assertEqual(shot_strs[3], 'f-3*')

        s = '5f2f3b3b1w#'
        shot_strs = Shot.segment_string(s)
        self.assertEqual(len(shot_strs), 5)
        self.assertEqual(shot_strs[0], '5')
        self.assertEqual(shot_strs[1], 'f2')
        self.assertEqual(shot_strs[2], 'f3')
        self.assertEqual(shot_strs[3], 'b3')
        self.assertEqual(shot_strs[4], 'b1w#')

        s = '6s17f1*'
        shot_strs = Shot.segment_string(s)
        self.assertEqual(len(shot_strs), 3)
        self.assertEqual(shot_strs[0], '6')
        self.assertEqual(shot_strs[1], 's17')
        self.assertEqual(shot_strs[2], 'f1*')

        s = '4+s28v1f-3*'
        shot_strs = Shot.segment_string(s)
        self.assertEqual(len(shot_strs), 4)
        self.assertEqual(shot_strs[0], '4+')
        self.assertEqual(shot_strs[1], 's28')
        self.assertEqual(shot_strs[2], 'v1')
        self.assertEqual(shot_strs[3], 'f-3*')

        s = '5r37b+3m2l1o=1r#'
        shot_strs = Shot.segment_string(s)
        self.assertEqual(len(shot_strs), 7)
        self.assertEqual(shot_strs[0], '5')
        self.assertEqual(shot_strs[1], 'r37')
        self.assertEqual(shot_strs[2], 'b+3')
        self.assertEqual(shot_strs[3], 'm2')
        self.assertEqual(shot_strs[4], 'l1')
        self.assertEqual(shot_strs[5], 'o=1')
        self.assertEqual(shot_strs[6], 'r#')


