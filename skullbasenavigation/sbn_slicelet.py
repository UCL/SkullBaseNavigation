""" Slicelet for SBN Project """

import logging  #pylint: disable=unused-import

import ctk
import qt
import slicer
from slicer.ScriptedLoadableModule import *

from sbn import workflow, functions

#pylint: disable=useless-object-inheritance
# Pylint thinks that passing 'object' as an argument is
# unnecessary, but that is incorrect.

class Slicelet(object):
    """
    SBN Slicelet
    """

    def __init__(self):

        # GUI has a right panel for displaying models/images
        # and a left panel for controls/buttons etc.
        # Use a QSplitter to separate the two.
        self.parent = qt.QSplitter()
        self.parent.orientation = qt.Qt.Horizontal

        # Left side of splitter
        self.control_panel = qt.QSplitter(self.parent)
        self.control_panel.orientation = qt.Qt.Vertical

        # Create a widget to contain all buttons
        button_widget_index = 0

        self.buttons = qt.QFrame(self.control_panel)
        self.control_panel.setCollapsible(button_widget_index, False)

        self.buttons.setLayout(qt.QVBoxLayout())

        # Button to connect to OpenIGTLink
        self.connect_btn = qt.QPushButton("Connect to OpenIGTLink")
        self.buttons.layout().addWidget(self.connect_btn)
        self.connect_btn.clicked.connect(self.try_connection)

        # Collapsible button to hold OpenIGTLink Remote Module
        self.ctk_model_box = ctk.ctkCollapsibleButton()
        self.ctk_model_box.setText("OpenIGTLink Remote")
        self.ctk_model_box.setChecked(False)

        self.remote_layout = qt.QVBoxLayout()
        self.remote_scroll_area = qt.QScrollArea()
        self.remote = slicer.modules.openigtlinkremote.widgetRepresentation()

        self.remote_scroll_area.setWidget(self.remote)
        self.remote_scroll_area.setWidgetResizable(True)
        self.remote_layout.addWidget(self.remote_scroll_area)
        self.ctk_model_box.setLayout(self.remote_layout)

        self.buttons.layout().addWidget(self.ctk_model_box)

        # Collapsible button to hole Pivot calibration module
        # Won't be active until the tools have been seen
        # by the StealthStation - i.e. the Stylus and SureTrack
        # transforms have been sent to Slicer
        self.ctk_pivot_box = ctk.ctkCollapsibleButton()
        self.ctk_pivot_box.setText("Pivot Calibration")
        self.ctk_pivot_box.setChecked(False)

        self.pivot_layout = qt.QVBoxLayout()
        self.pivot_scroll_area = qt.QScrollArea()
        self.pivot = slicer.modules.pivotcalibration.widgetRepresentation()

        self.pivot_scroll_area.setWidget(self.pivot)
        self.pivot_scroll_area.setWidgetResizable(True)
        self.pivot_layout.addWidget(self.pivot_scroll_area)

        self.ctk_pivot_box.setLayout(self.pivot_layout)
        self.buttons.layout().addWidget(self.ctk_pivot_box)

        # Disable the button (enabled if wait_for_transforms returns
        # true)
        self.ctk_pivot_box.setEnabled(False)

        # Ultrasound reconstruction buttons from PlusRemote module
        plus_wid = slicer.modules.plusremote.widgetRepresentation().children()
        # In recent versions of the module, the collapsible button we want can
        # be identified by name. In older versions, the names are empty, so we
        # have to hardcode the position we expect (and hope it is right!)
        btn = [widget for widget in plus_wid
               if widget.name == "VolumeReconstructionCollapsibleButton"]
        if len(btn) == 1:
            self.ctk_recon_box = btn[0]
        else:  # e.g. if no buttons found because their names are empty
            self.ctk_recon_box = plus_wid[6]
        self.buttons.layout().addWidget(self.ctk_recon_box)
        # Disable until transforms are available
        self.ctk_recon_box.setEnabled(False)

        self.advanced_options_checkbox = qt.QCheckBox("Show Advanced Settings")
        self.buttons.layout().addWidget(self.advanced_options_checkbox)
        self.advanced_options_checkbox.stateChanged.connect(
            self.toggle_tab_panel)

        # Timer to check if CT model and ultrasound are available
        self.checkModelsTimer = qt.QTimer()
        self.checkModelsTimer.setInterval(1000)
        self.checkModelsTimer.timeout.connect(self.check_if_models_exist)
        self.checkModelsTimer.start()

        # Timer to check if needed transforms are active
        self.checkTranformsTimer = qt.QTimer()
        self.checkTranformsTimer.setInterval(1000)
        self.checkTranformsTimer.timeout.connect(
            self.check_if_transforms_active)
        self.checkTranformsTimer.start()

        # Tabbed modules - hide by default
        tab_widget_index = 2
        self.tabWidget = qt.QTabWidget()
        self.tabWidget.hide()
        self.add_tab_widgets()

        self.control_panel.insertWidget(tab_widget_index, self.tabWidget)

        # Button to start/stop ultrasound volume reconstruction
        self.us_recon_btn = USReconstructionButton(self)
        self.buttons.layout().addWidget(self.us_recon_btn)

        # Button to save all transforms to file
        # Used for syncing with neuromonitoring data
        self.transform_save_btn = qt.QPushButton('Save Transforms')
        self.transform_save_btn.clicked.connect(functions.save_transforms)
        self.buttons.layout().addWidget(self.transform_save_btn)

        # Right side of splitter - 3D/Slice Viewer
        self.layoutManager = slicer.qMRMLLayoutWidget()
        self.layoutManager.setMRMLScene(slicer.mrmlScene)
        self.layoutManager.setLayout(
            slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
        self.parent.addWidget(self.layoutManager)

        # On startup, there are some 'hidden' identity transforms, named
        # 'LinearTransform_*', that don't show up in the hierarchy.
        # Want to delete these, so that they aren't saved when we use
        # transform_save_btn
        functions.remove_all_transforms()

        # Non-visual members:
        self.connector = None  # the OpenIGTLink connector to be used

        self.parent.show()



    def check_if_models_exist(self):
        """ Check if the CT and ultrasound models have been
        loaded.
        """

        # The ultrasound name is defined in the PLUS xml config file.
        # The CT doesn't have a name (not sure why) when it is sent from
        # the StealthStation
        # TODO - tidy up - shouldn't hard code the variable names here,
        # better to read in from a file or something.

        ultrasound_name = 'Image_SureTrack2Tip'
        # CT_name = 'CT_scan'

        ultrasound_id = functions.get_item_id_by_name(ultrasound_name)
        # ct_id = functions.get_item_id_by_name(CT_name)

        ultrasound_exists = functions.check_if_item_exists(ultrasound_id)
        # ct_exists = functions.check_if_item_exists(ct_id)


        # if (ultrasound_exists and ct_exists):
        #     # Get the nodes
        #     ultrasound_node = slicer.mrmlScene.GetNodeByID(str(ultrasound_id))
        #     ct_node = slicer.mrmlScene.GetNodeByID(str(ct_id))
        #     print(ultrasound_node, ct_node)
        #     # workflow.set_visible(ultrasound_node, ct_node)
        #     workflow.set_visible()
        #     self.checkModelsTimer.stop()
        if ultrasound_exists:
            # Get the node
            ultrasound_node = slicer.mrmlScene.GetFirstNodeByName(
                ultrasound_name)
            workflow.set_visible(ultrasound_node)
            self.checkModelsTimer.stop()


    def check_if_transforms_active(self):
        """ Check if the transform is active"""
        all_active = workflow.wait_for_transforms()

        if all_active:
            workflow.setup_plus_remote(self.connector)
            workflow.create_models()
            workflow.prepare_pivot_cal()
            workflow.set_transform_hierarchy()

            self.ctk_pivot_box.setEnabled(True)
            self.ctk_recon_box.setEnabled(True)
            self.checkTranformsTimer.stop()

    def add_tab_widgets(self):
        """
        Add tab widgets for each of the Slicer modules we want access
        to in the 'advanced' mode.
        """

        module_names = [
            "data",
            "volumerendering",
            "openigtlinkif",
            "createmodels",
            "transforms",
            "plusremote",
            "volumereslicedriver"]

        # Need to have a text label for each module tab
        module_labels = ["Data", "Volumes", "IGTLink", "Models", "Transforms", \
                         "PLUS Remote", "Volume Reslice"]

        # Create a tab widget for each module
        for name, label in zip(module_names, module_labels):
            self.scrollArea = qt.QScrollArea()
            widget = getattr(slicer.modules, name).widgetRepresentation()
            self.scrollArea.setWidget(widget)
            self.scrollArea.setWidgetResizable(True)
            self.tabWidget.addTab(self.scrollArea, label)

    def toggle_tab_panel(self):
        """ Set the advanced panel visible/invisible. """
        if self.advanced_options_checkbox.isChecked():
            self.tabWidget.show()
        else:
            self.tabWidget.hide()

    def try_connection(self):
        """Try to set up an OpenIGTLink connection.

        :return: True if the connection was successful, else False.
        """
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Connecting...")
        self.connector = workflow.connect()
        success = functions.is_connected(self.connector)
        if success:
            self.show_message("OpenIGTLink connection successful.")
            self.connect_btn.setText("Connected")
        else:
            self.show_message("Could not connect via OpenIGTLink.")
            self.connect_btn.setText("Connect to OpenIGTLink")
            self.connect_btn.setEnabled("True")
        return success

    def show_message(self, text):
        """Display the given text to the user.

        Current implementation shows a message box.
        """
        msg = qt.QMessageBox()
        msg.setText(text)
        # Note that the Qt method is properly called exec, but as this clashes
        # with the reserved keyword in Python 2, the Python version is exec_.
        # A method called exec also exists for backwards compatibility.
        msg.exec_()


class TractographySlicelet(Slicelet):
    """ Creates the interface when module is run as a stand alone gui app.
    """
    #pylint: disable=useless-super-delegation
    def __init__(self):
        super(TractographySlicelet, self).__init__()


class USReconstructionButton(qt.QPushButton):
    """A button that starts or stops ultrasound reconstruction when clicked."""
    START_TEXT = "Start acquisition"
    STOP_TEXT = "Stop acquisition & reconstruct"
    VOLUME_NAME = "ReconVolReference"

    def __init__(self, parent_slicelet):
        """Create a new button belonging to the given slicelet."""
        super(USReconstructionButton, self).__init__(self.START_TEXT)
        self.working = False  # are we currently doing a reconstruction?
        self.slicelet = parent_slicelet  # the parent slicelet
        self.clicked.connect(self.react)  # call the react method when clicked
        self.logic = slicer.modules.openigtlinkremote.logic()
        # It seems we need to connect to this signal to avoid a segmentation
        # fault when the slicelet is closed
        self.destroyed.connect(lambda: 0)

    def react(self):
        """React to being clicked, depending on the current state."""
        try:
            node_id = self.slicelet.connector.GetID()
        except AttributeError:  # something (connector) is None or missing
            self.slicelet.show_message(
                "Cannot find OpenIGT connection! You must first connect.")
            return
        if self.working:  # Send command to stop reconstruction
            cmd = slicer.vtkSlicerOpenIGTLinkCommand()
            cmd.SetCommandName("StopVolumeReconstruction")
            # Specify the name of the output volume and a filename to store it
            cmd.SetCommandAttribute("OutputVolDeviceName", self.VOLUME_NAME)
            cmd.SetCommandAttribute("OutputVolFilename",
                                    "output_reconstruction.mha")
        else:  # Send command to start reconstruction
            cmd = slicer.vtkSlicerOpenIGTLinkCommand()
            cmd.SetCommandName("StartVolumeReconstruction")
        # Sending the command returns True on success, False on failure
        response = self.logic.SendCommand(cmd, node_id)
        # TODO Maybe we should use an observer for the command completing
        # instead of examining the response value.
        if response:
            # Toggle state and text
            self.working = not self.working
            self.setText(self.STOP_TEXT if self.working else self.START_TEXT)
            # Change reslice settings after US reconstruction complete
            self.change_reslice_settings()

    def change_reslice_settings(self):
        """After US reconstruction, the slice views are set
        to show projections."""
        # Get the necessary nodes
        CT_name = 'SLD-*'
        CT_node = slicer.util.getNode(CT_name)
        SureTrack2TipToSureT_name = 'SureTrack2TipToSureTrack2'
        SureTrack2TipToSureT_node = slicer.mrmlScene.GetFirstNodeByName(SureTrack2TipToSureT_name)
        SureTrack2TipToSureT_node_id = SureTrack2TipToSureT_node.GetID()
        liveReconstruction_name = 'liveReconstruction'
        liveReconstruction_node = slicer.mrmlScene.GetFirstNodeByName(liveReconstruction_name)
        # Get the slice view nodes and the logic
        red_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
        yellow_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
        green_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')
        reslice_logic = slicer.modules.volumereslicedriver.logic()
        # Set the drivers
        reslice_logic.SetDriverForSlice(SureTrack2TipToSureT_node_id, red_slice_node)
        reslice_logic.SetDriverForSlice(SureTrack2TipToSureT_node_id, yellow_slice_node)
        reslice_logic.SetDriverForSlice(SureTrack2TipToSureT_node_id, green_slice_node)
        # Set the modes
        reslice_logic.SetModeForSlice(reslice_logic.MODE_AXIAL, red_slice_node)
        reslice_logic.SetModeForSlice(reslice_logic.MODE_SAGITTAL, yellow_slice_node)
        reslice_logic.SetModeForSlice(reslice_logic.MODE_CORONAL, green_slice_node)
        # Set the backgrounds
        slicer.util.setSliceViewerLayers(background=CT_node)
        # Set the foregrounds
        slicer.util.setSliceViewerLayers(foreground=liveReconstruction_node)
        # Set the red slice view foreground value to 0.5
        slicer.util.setSliceViewerLayers(foregroundOpacity=0.5)



if __name__ == "__main__":

    import sys
    print(sys.argv)

    # Set the transverse mode for the red slice view before
    # running the slicelet as it seems not to work otherwise
    red_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
    reslice_logic = slicer.modules.volumereslicedriver.logic()
    reslice_logic.SetModeForSlice(reslice_logic.MODE_TRANSVERSE, red_slice_node)

    slicelet = TractographySlicelet()
