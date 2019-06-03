"""
Workflow specifically for use in the mock OR.
Calls more generic functions from functions.py
"""
import os.path
import platform
from subprocess import Popen, PIPE, STDOUT

from sksurgerybk.interface import bk5000
import slicer

from ..config import Config
import functions


def start_dependencies():
    """Launch services on which the Slicelet depends."""
    # pyIGTLink server
    pyigtlink = bk5000.BKpyIGTLink(Config.PYIGTLINK_TCP_IP,
                                   Config.PYIGTLINK_TCP_PORT,
                                   Config.PYIGTLINK_TIMEOUT,
                                   Config.PYIGTLINK_FPS)
    pyigtlink.start()
    # PLUS Server (command will depend on the operating system)
    # NB: This assumes that the PlusServer executable is on the path,
    # and that we are in the root of the repository when running this!
    os_name = platform.system()
    plus_exec = "PlusServer.exe" if os_name == "Windows" else "PlusServer"
    plus_config = os.path.join(Config.PATH_TO_PLUS_SETTINGS,
                               Config.PLUS_CONFIG_FILE)
    plus_args = [plus_exec, "--config-file=" + plus_config]
    plus = Popen(plus_args, stdout=PIPE, stderr=STDOUT)
    # We may want to keep track of these connections/processes,
    # e.g. so we can stop them when the slicelet shuts down or crashes
    return pyigtlink, plus


def connect():
    """Connect to PLUS Server to receive OpenIGTLink data.

    :return: The resulting vtkMRMLIGTLConnectorNode.
    """
    igt_connector = functions.connect_to_OpenIGTLink(
        Config.IGTLINK_CONNECTOR_NAME, Config.PLUS_HOST, Config.PLUS_PORT)
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

    transforms = [Config.STYLUSTOREFERENCE_TF, Config.SURETRACK2TORAS_TF]

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
    for volume_name in [Config.SCOUTSCAN_VOL, Config.LIVERECONSTRUCTION_VOL]:
        functions.create_volume_node(volume_name)
    # Setup the module to use the correct connector.
    # This should enable the reconstruction buttons.
    combo_box = functions.get_plus_remote_connector_selector()
    combo_box.setCurrentNode(connector)


def create_models():
    """
    Create 3D models to visualise stylus and probe locations.
    """
    functions.create_needle_model(Config.STYLUS_MOD, 100, 1, 0.1)
    functions.create_needle_model(Config.PROBE_MOD, 100, 0.5, 0.2)
    functions.load_probe_image()


def prepare_pivot_cal():
    """ Set some default values for pivot calibration """
    tf_tip2suretrack = functions.create_linear_transform_node(
                                        Config.SURETRACK2TIPTOSURETRACK2_TF)
    tf_suretrack2ras = slicer.mrmlScene.GetFirstNodeByName(
                                        Config.SURETRACK2TORAS_TF)

    functions.set_pivot_transforms(tf_suretrack2ras, tf_tip2suretrack)

    functions.remove_unused_widgets_from_pivot_calibration()


def set_transform_hierarchy():
    """ Set the tranform hierarchy for the stylus and probe """
    scene = slicer.mrmlScene

    tf_tip2suretrack = scene.GetFirstNodeByName(
                             Config.SURETRACK2TIPTOSURETRACK2_TF)
    tf_suretrack2ras = scene.GetFirstNodeByName(
                             Config.SURETRACK2TORAS_TF)
    tf_stylus2reference = scene.GetFirstNodeByName(
                                Config.STYLUSTOREFERENCE_TF)
    img = scene.GetFirstNodeByName(Config.US_NAME)
    ref = scene.GetFirstNodeByName(Config.REFERENCETORAS_TF)

    stylus = scene.GetFirstNodeByName(Config.STYLUS_MOD)
    probe = scene.GetFirstNodeByName(Config.PROBE_MOD)
    probe_img = scene.GetFirstNodeByName(Config.PROBE_IMG)
    scout = scene.GetFirstNodeByName(Config.SCOUTSCAN_VOL)
    reconstruction = scene.GetFirstNodeByName(Config.LIVERECONSTRUCTION_VOL)

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
