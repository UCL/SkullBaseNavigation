"""
Workflow specifically for use in the mock OR.
Calls more generic functions from functions.py
"""

import slicer

import functions

def connect():
    """Connect to PLUS Server to receive OpenIGTLink data.

    :return: The resulting vtkMRMLIGTLConnectorNode.
    """
    igt_connector = functions.connect_to_OpenIGTLink(
        'OpenIGT', 'localhost', 18944)
    return igt_connector


# def set_visible(ultrasound_node, ct_node):
def set_visible(node):
    """ Set the US and CT data to visible """
    # scene = slicer.mrmlScene
    #
    # ultrasound_volume_name = 'Image_Reference'
    # ct_volume_name = ''
    #
    # ultrasound_node = scene.GetFirstNodeByName(ultrasound_volume_name)
    # ct_node = scene.GetFirstNodeByName(ct_volume_name)

    functions.set_node_visible(node)
    # functions.set_node_visible(ct_node)


def wait_for_transforms():
    """ Check if the transforms that correspond to the tools being
    placed in the StealthStation field of view have been created.
    """

    transforms = ['StylusToReference', 'SureTrack2ToRas']

    for transform in transforms:
        if not functions.does_node_exist_as_a_transform(transform):
            return False

    return True


def create_models():
    """
    Create 3D models to visualise stylus and probe locations.
    """
    functions.create_needle_model("StylusModel", 100, 1, 0.1)
    functions.create_needle_model("ProbeModel", 100, 0.5, 0.2)
    functions.load_probe_image()


def prepare_pivot_cal():
    """ Set some default values for pivot calibration """
    tf_tip2suretrack = functions.create_linear_transform_node(
        "SureTrack2TipToSureTrack2")
    tf_suretrack2ras = slicer.mrmlScene.GetFirstNodeByName("SureTrack2ToRas")

    functions.set_pivot_transforms(tf_suretrack2ras, tf_tip2suretrack)

    functions.remove_unused_widgets_from_pivot_calibration()


def set_transform_hierarchy():
    """ Set the tranform hierarchy for the stylus and probe """
    scene = slicer.mrmlScene

    tf_tip2suretrack = scene.GetFirstNodeByName("SureTrack2TipToSureTrack2")
    tf_suretrack2ras = scene.GetFirstNodeByName("SureTrack2ToRas")
    tf_stylus2reference = scene.GetFirstNodeByName("StylusToReference")
    img = scene.GetFirstNodeByName("Image_SureTrack2Tip")

    stylus = scene.GetFirstNodeByName("StylusModel")
    probe = scene.GetFirstNodeByName("ProbeModel")
    probe_img = scene.GetFirstNodeByName("BK_Probe")

    functions.set_parent_of_transform_hierarchy_node(
        stylus, tf_stylus2reference)
    functions.set_parent_of_transform_hierarchy_node(probe, tf_tip2suretrack)
    functions.set_parent_of_transform_hierarchy_node(
        probe_img, tf_tip2suretrack)
    functions.set_parent_of_transform_hierarchy_node(
        tf_tip2suretrack, tf_suretrack2ras)
    functions.set_parent_of_transform_hierarchy_node(img, tf_tip2suretrack)

    # TODO Once we have the STL model of the probe loaded, we should set that
    # under SureTrack2Tip2SureTrack2.
