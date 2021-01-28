import unittest

from parser import Shot


class ParserTests(unittest.TestCase):

    def test_shots(self):
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


