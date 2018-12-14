"""
Basic set of unit tests for the methods in functions.py using Slicer
and the Python unittest framework.
"""

import unittest

import slicer

import sbn.functions as fns


class TestOpenIGTLinkConnection(unittest.TestCase):

    def setUp(self):
        self.message = "Creating and testing an OpenIGTLink connection"
        self.name = "test_OpenIGTLink_connection"
        self.host = 'localhost'
        self.port = 18904
        self.cnode = fns.connect_to_OpenIGTLink(self.name,
                                                self.host,
                                                self.port)

    def test_connect_to_OpenIGTLink(self):
        print(self.message)
        self.assertEqual(self.cnode.GetServerHostname(), self.host)


class TestNeedle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.message = "Creating and testing a Needle model"
        cls.needle_name = "test_needle"
        cls.length = 100
        cls.radius = 10
        cls.tip = 2
        cls.needle = fns.create_needle_model(cls.needle_name,
                                             cls.length,
                                             cls.radius,
                                             cls.tip)


class TestCreateNeedleModel(TestNeedle):

    def runTest(self):
        print(self.message)
        self.assertEqual(self.needle.GetName(), self.needle_name)


class TestNodeVisibilitySettings(TestNeedle):

    def test_visible_setting(self):
        self.message = "Testing node visible setting"
        print(self.message)
        fns.set_node_visible(self.needle)
        self.assertEqual(self.needle.GetDisplayVisibility(), 1)

    def test_invisible_setting(self):
        self.message = "Testing node invisible setting"
        print(self.message)
        fns.set_node_invisible(self.needle)
        self.assertEqual(self.needle.GetDisplayVisibility(), 0)


class TestGetItemId(TestNeedle):

    def test_get_item_id_NSinput(self):
        self.message = "Testing getting the item id with \
                        invalid (non-string) input"
        print(self.message)
        non_string_input = 1001
        item_id = fns.get_item_id_by_name(non_string_input)
        self.assertEqual(item_id, -1)

    def test_get_item_id_valid_input(self):
        self.message = "Testing if item exists from node with valid input"
        print(self.message)
        item_id = fns.get_item_id_by_name(self.needle.GetName())
        self.assertEqual(fns.check_if_item_exists(item_id), True)

    def test_get_item_id_NEinput(self):
        self.message = "Testing if item exists from node with invalid \
                        (non-existent) input"
        print(self.message)
        invalid_input = "fake_item"
        item_ID = fns.get_item_id_by_name(invalid_input)
        self.assertEqual(fns.check_if_item_exists(item_ID), False)


class TestTransform(TestNeedle):
    @classmethod
    def setUpClass(cls):
        super(TestTransform, cls).setUpClass()
        cls.tf_name = "test_create_transform"
        cls.transform = fns.create_linear_transform_node(cls.tf_name)
        cls.transform_name = cls.transform.GetName()
        cls.transform_id = fns.get_item_id_by_name(cls.transform_name)

    def test_creating_transform(self):
        self.message = "Testing Transform Creation"
        print(self.message)
        self.assertEqual(self.transform.GetName(), self.tf_name)
        self.assertEqual(type(self.transform),
                         type(slicer.vtkMRMLLinearTransformNode()))

    def test_actual_transform(self):
        self.message = "Test if actual transform"
        print(self.message)
        self.assertEqual(fns.check_if_item_is_transform(self.transform_id),
                         True)

    def test_is_node_transform_wrapper(self):
        self.message = "Testing Transform Checker Wrapper Function"
        print(self.message)
        self.assertEqual(fns.does_node_exist_as_a_transform(
                         self.transform_name), True)

    def test_not_transform(self):
        self.message = "Test not a transform"
        print(self.message)
        item_id = fns.get_item_id_by_name(self.needle.GetName())
        self.assertEqual(fns.check_if_item_is_transform(item_id), False)


class TestTransformFiliation(unittest.TestCase):

    def setUp(self):
        self.message = "Testing node hierachy"
        self.tf_child = fns.create_linear_transform_node('child')
        self.tf_parent = fns.create_linear_transform_node('parent')

    def test_node_hierarchy(self):
        print(self.message)
        fns.set_parent_of_transform_hierarchy_node(self.tf_child,
                                                   self.tf_parent)
        parent_id_from_child = self.tf_child.GetParentTransformNode().GetID()
        parent_id = self.tf_parent.GetID()
        self.assertEqual(parent_id_from_child, parent_id)


if __name__ == "__main__":
    unittest.main()
