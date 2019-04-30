import unittest

from AdDetectorModel.utils.evaluation import *


class TestEvaluationMethod(unittest.TestCase):
    def test_fscore(self):
        self.assertEqual(0, f_score(0, 0))
        self.assertEqual(0, f_score(0, 1))
        self.assertEqual(0, f_score(1, 0))
        self.assertEqual(0.5, f_score(0.5, 0.5))
        self.assertEqual(1, f_score(1, 1))

    def test_precision(self):
        self.assertEqual(0, calc_precision({'1': []}, {'1': []}))

    def test_recall(self):
        self.assertEqual(0, calc_recall({'1': []}, {'1': []}))

    def test_intersection(self):
        self.assertEqual(0, calc_intersection([], []))
        self.assertEqual(0, calc_intersection([(1, 2)], []))
        self.assertEqual(0, calc_intersection([], [(1, 2)]))
        self.assertEqual(1.5, calc_intersection([(1, 2), (3, 5)], [(1.5, 3.5), (4.5, 6)]))

    def test_union(self):
        self.assertEqual(0, calc_union([], []))
        self.assertEqual(1, calc_union([(1, 2)], []))
        self.assertEqual(1, calc_union([], [(1, 2)]))
        self.assertEqual(5, calc_union([(1, 2), (3, 5)], [(1.5, 3.5), (4.5, 6)]))

    def test_IoU(self):
        self.assertEqual(0, calc_IoU({'1': []}, {'1': [(1, 2)]}))
        self.assertEqual(1, calc_IoU({'1': [(1, 2)]}, {'1': [(1, 2)]}))
        self.assertEqual(1, calc_IoU({'1': []}, {'1': []}))
        self.assertEqual(0.25, calc_IoU({'1': [(1, 2)]}, {'1': [(1, 3), (4, 6)]}))

    def test_diff(self):
        self.assertEqual(0, calc_diff([], []))
        self.assertEqual(0, calc_diff([], [(1, 2)]))
        self.assertEqual(0, calc_diff([(1, 2)], [(1, 2)]))
        self.assertEqual(1, calc_diff([(1, 2)], []))
        self.assertEqual(1.5, calc_diff([(1, 2), (3, 5)], [(1.5, 3.5), (4.5, 6)]))


if __name__ == '__main__':
    unittest.main()