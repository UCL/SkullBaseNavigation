"""
Workflow specifically for use in the mock OR.
Calls more generic functions from functions.py
"""
import os.path
import platform
from subprocess import Popen, PIPE, STDOUT

#from sksurgerybk.interface import bk5000
import slicer

import functions


def start_dependencies():
    """Launch services on which the Slicelet depends."""
    # pyIGTLink server
    # pyigtlink = bk5000.BKpyIGTLink()
    # pyigtlink.start()
    # # PLUS Server (command will depend on the operating system)
    # NB: This assumes that the PlusServer executable is on the path,
    # and that we are in the root of the repository when running this!
    
    os.environ["PATH"] += r";C:\Users\SBN\PlusApp-2.6.0.20190221-StealthLink-Win32\bin;"
    os_name = platform.system()
    plus_exec = "PlusServer.exe" if os_name == "Windows" else "PlusServer"
    plus_config = os.path.join(
        "PLUS_settings",
        "PlusDeviceSet_Server_StealthLinkTracker_pyIGTLink.xml")
    plus_args = [plus_exec, "--config-file=" + plus_config]
    plus = Popen(plus_args, stdout=PIPE, stderr=STDOUT)
    # We may want to keep track of these connections/processes,
    # e.g. so we can stop them when the slicelet shuts down or crashes
    return plus


def connect():
    """Connect to PLUS Server to receive OpenIGTLink data.

    :return: The resulting vtkMRMLIGTLConnectorNode.
    """
    igt_connector = functions.connect_to_OpenIGTLink(
        'OpenIGT', 'localhost', 18944)
    return igt_connector


def set_visible(node):
    """ Set the US and CT data to visible """
    functions.set_node_visible(node)


def wait_for_transforms():
    """ Check if the transforms that correspond to the tools being
    placed in the StealthStation field of view have been created.
    """

    transforms = ['StylusToReference', 'SureTrack2ToRas']

    for transform in transforms:
        if not functions.does_node_exist_as_a_transform(transform):
            return False

    return True


def setup_plus_remote(connector):
    """
    Set up the nodes and widgets that the PlusRemote module requires.

    :param connector: A vtkMRMLIGTConnectorNode to select.
    """
    # Create two volume nodes to hold the CT and reconstructed ultrasound.
    # This is required because the PlusRemote module expects nodes with
    # particular names and, if they are not present, it will use meaningless
    # names such as _1, _2 etc.
    for volume_name in ["ScoutScan", "liveReconstruction"]:
        functions.create_volume_node(volume_name)
    # Setup the module to use the correct connector.
    # This should enable the reconstruction buttons.
    combo_box = functions.get_plus_remote_connector_selector()
    combo_box.setCurrentNode(connector)


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
    ref = scene.GetFirstNodeByName("ReferenceToRas")

    stylus = scene.GetFirstNodeByName("StylusModel")
    probe = scene.GetFirstNodeByName("ProbeModel")
    probe_img = scene.GetFirstNodeByName("BK_Probe")
    scout = scene.GetFirstNodeByName("ScoutScan")
    reconstruction = scene.GetFirstNodeByName("liveReconstruction")

    functions.set_parent_of_transform_hierarchy_node(
        stylus, tf_stylus2reference)
    functions.set_parent_of_transform_hierarchy_node(probe, tf_tip2suretrack)
    functions.set_parent_of_transform_hierarchy_node(
        probe_img, tf_tip2suretrack)
    functions.set_parent_of_transform_hierarchy_node(
        tf_tip2suretrack, tf_suretrack2ras)
    functions.set_parent_of_transform_hierarchy_node(img, tf_tip2suretrack)

    functions.set_parent_of_transform_hierarchy_node(scout, ref)
    functions.set_parent_of_transform_hierarchy_node(reconstruction, ref)

    # TODO Once we have the STL model of the probe loaded, we should set that
    # under SureTrack2Tip2SureTrack2.
