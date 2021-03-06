"""
Basic set of tests for slicer functions in functions.py
"""
import slicer
from sbn import functions

#pylint: disable=missing-docstring
def check_equal(a, b):
    if a == b:
        print("Passed")
        return True

    print("FAILED!!!")
    return False


def run_all_tests():

    test_connect_to_OpenIGTLink()
    model_node = test_create_needle_model()
    test_visiblity_settings(model_node)
    test_find_item_id(model_node)

    tf = test_create_transform()
    test_check_if_transform(tf, model_node)

    test_set_transform_parent()


def test_connect_to_OpenIGTLink():
    print("Creating OpenIGTLink Connection")

    name = "test_IGT"
    host = 'localhost'
    port = 18904

    cnode = functions.connect_to_OpenIGTLink(name, host, port)

    check_equal(cnode.GetServerHostname(), host)


def test_create_needle_model():
    print("Creating Needle Model")

    name = "test_needle"
    length = 100
    radius = 10
    tip = 2

    needle = functions.create_needle_model(name, length, radius, tip)

    check_equal(needle.GetName(), name)

    return needle


def test_visiblity_settings(node):
    print("Testing setting node visible/invisible")
    functions.set_node_visible(node)
    check_equal(node.GetDisplayVisibility(), 1)

    functions.set_node_invisible(node)
    check_equal(node.GetDisplayVisibility(), 0)


def test_find_item_id(node):

    print("Testing Find Item ID")
    print("Testing invalid (non-string) input")
    non_string_input = 1001
    node_id = functions.get_item_id_by_name(non_string_input)
    check_equal(node_id, -1)

    print("Testing valid input")
    item_ID = functions.get_item_id_by_name(node.GetName())
    check_equal(functions.check_if_item_exists(item_ID), True)

    print("Testing invalid (non-existent) input")
    item_doesnt_exist = "fake_item"
    item_ID = functions.get_item_id_by_name(item_doesnt_exist)
    check_equal(functions.check_if_item_exists(item_ID), False)


def test_create_transform():

    print("Testing Transform Creation")
    name = "test_transform"
    tf = functions.create_linear_transform_node(name)
    check_equal(tf.GetName(), name)
    check_equal(type(tf), type(slicer.vtkMRMLLinearTransformNode()))

    return tf


def test_check_if_transform(tf, model):

    tf_name = tf.GetName()
    model_name = model.GetName()
    print("Testing Transform Checker")
    tf_ID = functions.get_item_id_by_name(tf_name)
    model_ID = functions.get_item_id_by_name(model_name)

    print("Actual Transform")
    check_equal(functions.check_if_item_is_transform(tf_ID), True)
    print("Not a transform")
    check_equal(functions.check_if_item_is_transform(model_ID), False)

    print("Testing Transform Checker Wrapper Function")
    check_equal(functions.does_node_exist_as_a_transform(tf_name), True)


def test_set_transform_parent():

    print("Testing Setting of Transform Parent Node")
    tf_child = functions.create_linear_transform_node('child')
    tf_parent = functions.create_linear_transform_node('parent')

    functions.set_parent_of_transform_hierarchy_node(tf_child, tf_parent)

    child_nodes_parent_id = tf_child.GetParentTransformNode().GetID()
    parent_id = tf_parent.GetID()
    check_equal(child_nodes_parent_id, parent_id)


if __name__ == "__main__":
    run_all_tests()
