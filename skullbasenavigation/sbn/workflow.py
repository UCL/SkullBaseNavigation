"""
Workflow specifically for use in the mock OR.
Calls more generic functions from functions.py
"""
import os.path
import platform
from subprocess import Popen, PIPE, STDOUT

# from sksurgerybk.interface import bk5000
import slicer

import functions
from .config import Config

def start_dependencies():
    """Launch services on which the Slicelet depends."""
    # pyIGTLink server
    # pyigtlink = bk5000.BKpyIGTLink(Config.BK_TCP_IP,
    #                                Config.BK_TCP_PORT,
    #                                Config.BK_TIMEOUT,
    #                                Config.BK_FPS)
    # pyigtlink.start()
    # PLUS Server (command will depend on the operating system)
    # NB: This assumes that the PlusServer executable is on the path,
    # and that we are in the root of the repository when running this!

    os.environ["PATH"] += r";C:\Users\SBN\PlusApp-2.6.0.20190221-StealthLink-Win32\bin;"
    os_name = platform.system()
    plus_exec = "PlusServer.exe" if os_name == "Windows" else "PlusServer"
    plus_exec_path = os.path.join(Config.PLUS_EXEC_PATH,
                                  plus_exec)
    plus_config = os.path.join(Config.PATH_TO_PLUS_SETTINGS,
                               Config.PLUS_CONFIG_FILE)
    plus_args = [plus_exec_path, "--config-file=" + plus_config]
    plus = Popen(plus_args, stdout=PIPE, stderr=STDOUT)
    # We may want to keep track of these connections/processes,
    # e.g. so we can stop them when the slicelet shuts down or crashes
    return plus


def connect():
    """Connect to PLUS Server to receive OpenIGTLink data.

    :return: The resulting vtkMRMLIGTLConnectorNode.
    """
    igt_connector = functions.connect_to_OpenIGTLink(
        Config.IGTLINK_CONNECTOR_NAME, Config.PLUS_HOST, Config.PLUS_PORT)
    return igt_connector


def set_visible(node):
    """ Set the US and CT data to visible """
    functions.set_node_visible(node)


def wait_for_transforms():
    """ Check if the transforms that correspond to the tools being
    placed in the StealthStation field of view have been created.
    """

    # USE BELOW FOR CUSA
    #transforms = [Config.STYLUS_TO_REFERENCE_TF, Config.US_TO_RAS_TF,
    #              Config.CUSA_TO_RAS_TF, Config.NEUROSTIM_TO_RAS_TF]

    transforms = [Config.STYLUS_TO_REFERENCE_TF, Config.US_TO_RAS_TF,
                  Config.NEUROSTIM_TO_RAS_TF]

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
    #functions.create_needle_model(Config.CUSA_MOD, 100, 2, 0.1)
    functions.create_needle_model(Config.NEUROSTIM_MOD, 100, 3, 0.1)
    functions.load_probe_image()


def prepare_probe_pivot_cal():
    """ Set some default values for pivot calibration """
    functions.create_linear_transform_node(
        Config.US_TO_US_TIP_TF)
    functions.create_linear_transform_node(
        Config.NEUROSTIM_TIP_TO_NEUROSTIM_TF)
    set_calibration_mode("us")
    functions.remove_unused_widgets_from_pivot_calibration()


def set_calibration_mode(mode="us"):
    """Choose which instrument to calibrate.

    Current choices are: "us" (ultrasound), "neuro" (neurostimulator).
    """
    if mode == "us":
        output_transform = slicer.mrmlScene.GetFirstNodeByName(
            Config.US_TO_US_TIP_TF)
        input_transform = slicer.mrmlScene.GetFirstNodeByName(
            Config.US_TO_RAS_TF)
    elif mode == "neuro":
        output_transform = slicer.mrmlScene.GetFirstNodeByName(
            Config.NEUROSTIM_TIP_TO_NEUROSTIM_TF)
        input_transform = slicer.mrmlScene.GetFirstNodeByName(
            Config.NEUROSTIM_TO_RAS_TF)
    else:
        raise ValueError("Unrecognised instrument to calibrate: " + mode)
    functions.set_pivot_transforms(input_transform, output_transform)


def set_transform_hierarchy():
    """ Set the tranform hierarchy for the stylus and probe """
    scene = slicer.mrmlScene

    # US
    tf_us_to_us_tip = scene.GetFirstNodeByName(Config.US_TO_US_TIP_TF)
    tf_us_to_ras = scene.GetFirstNodeByName(Config.US_TO_RAS_TF)

    # Neurostim
    tf_neurostim_to_neurostim_tip = scene.GetFirstNodeByName(
        Config.NEUROSTIM_TIP_TO_NEUROSTIM_TF)
    tf_neurostim_to_ras = scene.GetFirstNodeByName(Config.NEUROSTIM_TO_RAS_TF)

    # CUSA
    #tf_cusa_to_ras = scene.GetFirstNodeByName(Config.CUSA_TO_RAS_TF)

    # Stylus
    tf_stylus_to_reference = scene.GetFirstNodeByName(
        Config.STYLUS_TO_REFERENCE_TF)

    img = scene.GetFirstNodeByName(Config.US_IMG)
    ref = scene.GetFirstNodeByName(Config.REFERENCETORAS_TF)

    stylus = scene.GetFirstNodeByName(Config.STYLUS_MOD)
    probe = scene.GetFirstNodeByName(Config.PROBE_MOD)
    #cusa = scene.GetFirstNodeByName(Config.CUSA_MOD)
    neurostim = scene.GetFirstNodeByName(Config.NEUROSTIM_MOD)
    probe_img = scene.GetFirstNodeByName(Config.PROBE_IMG)

    scout = scene.GetFirstNodeByName(Config.SCOUTSCAN_VOL)
    reconstruction = scene.GetFirstNodeByName(Config.LIVERECONSTRUCTION_VOL)

    # Stylus
    functions.set_parent_of_transform_hierarchy_node(
        stylus, tf_stylus_to_reference)

    # US
    functions.set_parent_of_transform_hierarchy_node(probe, tf_us_to_us_tip)
    functions.set_parent_of_transform_hierarchy_node(
        probe_img, tf_us_to_us_tip)
    functions.set_parent_of_transform_hierarchy_node(
        tf_us_to_us_tip, tf_us_to_ras)

    # Neurostim
    functions.set_parent_of_transform_hierarchy_node(
        neurostim, tf_neurostim_to_neurostim_tip)
    functions.set_parent_of_transform_hierarchy_node(
        tf_neurostim_to_neurostim_tip, tf_neurostim_to_ras)

    # CUSA
    #functions.set_parent_of_transform_hierarchy_node(
    #    cusa, tf_cusa_to_ras)

    functions.set_parent_of_transform_hierarchy_node(img, tf_us_to_us_tip)

    functions.set_parent_of_transform_hierarchy_node(scout, ref)
    functions.set_parent_of_transform_hierarchy_node(reconstruction, ref)


def align_volumes_to_model(volumes):
    """Align a list of volumes to the model that was loaded from the Stealth.

    :param volumes: an iterable of vtkMRMLVolumeNode
    :returns: True if all available volumes were aligned, else False
    """
    transform = functions.load_registration_tf()
    if not transform:
        return False
    for volume in volumes:
        if volume is not None:
            functions.set_parent_of_transform_hierarchy_node(volume, transform)
    return True


def track_probe_in_slice_viewers(probe_type):
    """
    Change the slice viewer settings to track the US or neurostimulation probe.

    :param probe_type: "us" or "neuro", to specify which probe to track.
    """
    if probe_type not in ["us", "neuro"]:
        raise ValueError("Unrecognised instrument to track: " + probe_type)
    # Find the ID of the transform corresponding to the probe tip
    tf_name = (Config.US_TO_US_TIP_TF if probe_type == "us"
               else Config.NEUROSTIM_TIP_TO_NEUROSTIM_TF)
    node_id = slicer.mrmlScene.GetFirstNodeByName(tf_name).GetID()
    # Get the slice view nodes and the logic
    red_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
    yellow_slice_node = slicer.mrmlScene.GetNodeByID(
        'vtkMRMLSliceNodeYellow')
    green_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')
    reslice_logic = slicer.modules.volumereslicedriver.logic()
    # Set the drivers
    for node in [red_slice_node, yellow_slice_node, green_slice_node]:
        reslice_logic.SetDriverForSlice(node_id, node)
    # Set the modes
    reslice_logic.SetModeForSlice(reslice_logic.MODE_AXIAL, red_slice_node)
    reslice_logic.SetModeForSlice(reslice_logic.MODE_SAGITTAL,
                                  yellow_slice_node)
    reslice_logic.SetModeForSlice(reslice_logic.MODE_CORONAL,
                                  green_slice_node)


def setup_ultrasound_view(to_show=[], to_hide=[]):
    """Change settings to prepare for showing the ultrasound."""
    # TODO: Show the reconstruction in the 3D viewer and hide current contents
    for node in to_show:
        node.SetDisplayVisibility(True)
    for node in to_hide:
        node.SetDisplayVisibility(False)
    # Track the probe in the slice viewers
    track_probe_in_slice_viewers("us")

    # Update the layers: Show the reconstruction in the foreground,
    # and the CT (as received from the Stealth) in the background.
    # Get the necessary nodes
    CT_name = 'SLD-*'
    CT_node = slicer.util.getNode(CT_name)
    recon_node = slicer.mrmlScene.GetFirstNodeByName(
        Config.LIVERECONSTRUCTION_VOL)

    # Change the volume lookup table color settings
    CT_node.GetDisplayNode().SetAndObserveColorNodeID(
        'vtkMRMLColorTableNodeGrey')
    recon_node.GetDisplayNode().SetAndObserveColorNodeID(
        'vtkMRMLColorTableNodeRed')

    # Set the foregrounds
    slicer.util.setSliceViewerLayers(foreground=recon_node)
    # Set the backgrounds
    slicer.util.setSliceViewerLayers(background=CT_node)
    # Set the red slice view foreground value to 0.5
    slicer.util.setSliceViewerLayers(foregroundOpacity=0.5)


def setup_neurostim_view(to_show=[], to_hide=[]):
    """Change settings to prepare for showing the neurostimulation points."""
    # TODO: Hide the reconstruction if shown in 3D viewer
    for node in to_show:
        node.SetDisplayVisibility(True)
    for node in to_hide:
        node.SetDisplayVisibility(False)
    # Track the neurostimulation probe
    track_probe_in_slice_viewers("neuro")
    # TODO: Set background according to selected options
