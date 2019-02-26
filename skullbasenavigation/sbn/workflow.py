"""
 Workflow specifically for use in the mock OR.
Calls more generic functions from functions.py
"""
import functions
import qt
import slicer

def connect(button):
    """ Connect to PLUS Server to receive OpenIGTLink data.

    :param button: the button that triggered this request."""
    button.setEnabled(False)
    button.setText("Connecting...")
    igt_connector = functions.connect_to_OpenIGTLink(
        'OpenIGT', 'localhost', 18905)
    if functions.is_connected(igt_connector):
        show_message("OpenIGTLink connection successful.")
        button.setText("Connected")
    else:
        show_message("Could not connect via OpenIGTLink.")
        button.setText("Connect to OpenIGTLink")
        button.setEnabled("True")
    return igt_connector


def set_visible():
    """ Set the US and CT data to visible """
    scene = slicer.mrmlScene

    ultrasound_volume_name = 'Image_Reference'
    ct_volume_name = ''

    ultrasound_node = scene.GetFirstNodeByName(ultrasound_volume_name)
    ct_node = scene.GetFirstNodeByName(ct_volume_name)

    functions.set_node_visible(ultrasound_node)
    functions.set_node_visible(ct_node)


def wait_for_transforms():
    """ Check if the transforms that correspond to the tools being
    placed in the StealthStation field of view have been created.
    """

    transforms = ['StylusToRas', 'StylusToReference', 'SureTrack2ToRas']

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


def prepare_pivot_cal():
    """ Set some default values for pivot calibration """
    tf_tip2suretrack = functions.create_linear_transform_node("Tip2SureTrack")
    tf_suretrack2ras = slicer.mrmlScene.GetFirstNodeByName("SureTrack2ToRas")

    functions.set_pivot_transforms(tf_suretrack2ras, tf_tip2suretrack)

    functions.remove_unused_widgets_from_pivot_calibration()


def set_transform_hierarchy():
    """ Set the tranform hierarchy for the stylus and probe """
    scene = slicer.mrmlScene

    tf_tip2suretrack = scene.GetFirstNodeByName("Tip2SureTrack")
    tf_suretrack2ras = scene.GetFirstNodeByName("SureTrack2ToRas")
    tf_stylus2ras = scene.GetFirstNodeByName("StylusToRas")

    stylus = scene.GetFirstNodeByName("StylusModel")
    probe = scene.GetFirstNodeByName("ProbeModel")

    functions.set_parent_of_transform_hierarchy_node(stylus, tf_stylus2ras)
    functions.set_parent_of_transform_hierarchy_node(probe, tf_tip2suretrack)

    functions.set_parent_of_transform_hierarchy_node(
        tf_tip2suretrack, tf_suretrack2ras)


def show_message(text):
    msg = qt.QMessageBox()
    msg.setText(text)
    # Note that the Qt method is properly called exec, but as this clashes
    # with the reserved keyword in Python 2, the Python version is exec_.
    # A method called exec also exists for backwards compatibility.
    msg.exec_()

