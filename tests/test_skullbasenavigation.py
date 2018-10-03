# coding=utf-8

"""Skull Base Navigation tests"""

from unittest import TestCase

from skullbasenavigation.ui.skullbasenavigation_demo import run_demo


class TestSkullBaseNavigation(TestCase):
    def test_skullbasenavigation(self):
        run_demo(True, "Hello world")
