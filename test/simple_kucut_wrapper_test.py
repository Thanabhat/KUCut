# -*- coding: utf8 -*-
import unittest
from kucut import SimpleKucutWrapper as KUCut

class TestSimpleKucutWrapper(unittest.TestCase):
    def setUp(self):
        self.kucut = KUCut()
        
    def test_simple(self):
        input = [u"กากากา"]
        expected_output = [[[u"กา", u"กา", u"กา"]]]
        result = self.kucut.tokenize(input)
        print result
        print expected_output
        print
        self.assertEqual(expected_output, result, "Incorrect word break")