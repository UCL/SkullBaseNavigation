""" Slicelet for SBN Project """

import logging  #pylint: disable=unused-import
import time
import datetime
import json
import os
import ctk
import qt
import slicer
from slicer.ScriptedLoadableModule import *

from sbn.config import Config
from sbn import functions, workflow

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

        self.get_model_btn = qt.QPushButton("Get Model From Remote")
        self.get_model_btn.clicked.connect(self.get_ct_model)
        self.buttons.layout().addWidget(self.get_model_btn)

        # Buttons to load and align volumes from file
        self.ctk_data_box = ctk.ctkCollapsibleButton()
        self.ctk_data_box.setText("Local Data Files")
        self.ctk_data_box.setChecked(False)
        self.data_layout = qt.QGridLayout()
        self.load_t1_btn = qt.QPushButton("Load T1")
        self.load_t1_btn.clicked.connect(self.load_t1_model)
        self.load_t2_btn = qt.QPushButton("Load T2")
        self.load_t2_btn.clicked.connect(self.load_t2_model)
        self.load_ct_btn = qt.QPushButton("Load CT")
        self.load_ct_btn.clicked.connect(self.load_ct_model)
        self.load_cm_btn = qt.QPushButton("Load Colourmap")
        self.load_cm_btn.clicked.connect(self.load_colourmap)
        self.load_tum_seg_btn = qt.QPushButton("Load Tumour Seg")
        self.load_tum_seg_btn.clicked.connect(self.load_tumour_segmentation)
        self.load_ner_seg_btn = qt.QPushButton("Load Nerve Seg")
        self.load_ner_seg_btn.clicked.connect(self.load_nerve_segmentation)
        self.align_btn = qt.QPushButton("Align Data")
        self.align_btn.clicked.connect(self.align_volumes)

        t1_file = 'C:/Users/SBN/Documents/sbn_005_SliceletData/sbn_005_SliceletData/T1stealth.nii.gz'
        t2_file = 'C:/Users/SBN/Documents/sbn_005_SliceletData/sbn_005_SliceletData/T2.nii.gz'
        ct_file = 'C:/Users/SBN/Documents/sbn_005_SliceletData/sbn_005_SliceletData/s007_t1_mpr_stealth_ns_tra_DIS3D.nii.gz'
        ts_file = 'C:/Users/SBN/Documents/sbn_005_SliceletData/sbn_005_SliceletData/abn_005_VS.seg.nrrd'
        ns_file = 'C:/Users/SBN/Documents/sbn_005_SliceletData/sbn_005_SliceletData/sbn_005_nerve.seg.nrrd'
        cm_file = 'C:/Users/SBN/Documents/sbn_005_SliceletData/sbn_005_SliceletData/colourmap_wm_gm_csf_2.nii.mgh'

        # Add volume buttons to one row
        self.data_layout.addWidget(self.load_t1_btn, 0, 0)
        self.data_layout.addWidget(self.load_t2_btn, 0, 1)
        self.data_layout.addWidget(self.load_ct_btn, 0, 2)
        # Add segmentation and colourmap buttons to the next row
        self.data_layout.addWidget(self.load_tum_seg_btn, 1, 0)
        self.data_layout.addWidget(self.load_ner_seg_btn, 1, 1)
        self.data_layout.addWidget(self.load_cm_btn, 1, 2)
        # Let the alignment button span the whole bottom row
        self.data_layout.addWidget(self.align_btn, 2, 0, 1, -1)
        self.ctk_data_box.setLayout(self.data_layout)
        self.buttons.layout().addWidget(self.ctk_data_box)

        # Neurostimulation button to save the neurostim points and save the
        # tracking location to a file
        self.neurostim_box = ctk.ctkCollapsibleButton()
        self.neurostim_box.setText("Neurostimulation")
        self.neurostim_box.setChecked(False)

        self.neurostim_layout = qt.QGridLayout()

        self.neurostim_voltage_label = qt.QLabel("Voltage in mA:")
        self.neurostim_voltage_text = qt.QLineEdit()
        self.neurostim_layout.addWidget(self.neurostim_voltage_label, 0, 0)
        self.neurostim_layout.addWidget(self.neurostim_voltage_text, 0, 1)

        self.neurostim_response_b1 = qt.QRadioButton("Neurostimulation response")
        self.neurostim_response_b2 = qt.QRadioButton("No neurostimulation response")
        self.neurostim_response_b2.setChecked(True)
        self.neurostim_layout.addWidget(self.neurostim_response_b1, 1, 0)
        self.neurostim_layout.addWidget(self.neurostim_response_b2, 1, 1)

        self.neurostim_save_and_display_btn = qt.QPushButton("Save and display neurostim point")
        self.neurostim_save_and_display_btn.clicked.connect(self.save_and_display_neurostim_pt)
        self.neurostim_layout.addWidget(self.neurostim_save_and_display_btn, 2, 0, 1, -1)

        self.neurostim_box.setLayout(self.neurostim_layout)
        self.buttons.layout().addWidget(self.neurostim_box)

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
            # this is originally in position 6, but we have already taken
            # something out, so the indices have changed
            self.ctk_recon_box = plus_wid[5]
        functions.check_add_timestamp_to_filename_box(self.ctk_recon_box)
        self.buttons.layout().addWidget(self.ctk_recon_box)

        self.ctk_recon_box.setChecked(False)
        # Disable until transforms are available
        self.ctk_recon_box.setEnabled(True)

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

        # Timer to check if live reconstruction has some data in it
        # The timer is started by the check_if_transforms_active function
        self.checkReconTimer = qt.QTimer()
        self.checkReconTimer.setInterval(1000)
        self.checkReconTimer.timeout.connect(
            self.check_if_recon_display_node_exists)

        # Tabbed modules - hide by default
        tab_widget_index = 2
        self.tabWidget = qt.QTabWidget()
        self.tabWidget.hide()
        self.add_tab_widgets()

        self.control_panel.insertWidget(tab_widget_index, self.tabWidget)

        # Radio button group to toggle between the different backgrounds
        # from the loaded files
        self.T1 = qt.QRadioButton('T1')
        self.T2 = qt.QRadioButton('T2')
        self.CT = qt.QRadioButton('CT')
        self.MR = qt.QRadioButton('MR')
        self.MR.setEnabled(False)
        self.background_group = qt.QButtonGroup()
        self.background_group.addButton(self.T1)
        self.background_group.addButton(self.T2)
        self.background_group.addButton(self.CT)
        self.background_group.addButton(self.MR)
        # Toggle the displayed image when any button in this group is clicked
        self.background_group.buttonClicked.connect(self.toggle_image)

        # Checkbox to apply the colourmap or not
        self.colormap_applied_btn = qt.QCheckBox("Colourmap")
        self.colormap_applied_btn.setChecked(False)
        # TODO: Specify behaviour when clicked. In neurostimulation view,
        # it should show/hide the colourmap in the foreground. In US view,
        # the foreground should switch between the colourmap and whatever
        # image type is selected from the radio button group.
        self.colormap_applied_btn.toggled.connect(self.toggle_colormap)

        # Checkbox to freeze tracking
        self.freeze_tracking_btn = qt.QCheckBox("Freeze tracking")
        self.freeze_tracking_btn.setChecked(False)  # By default, slice views
        # are in 'Reformat' mode, ie. images are changing along with moving
        # the probe/Neurostimulator
        self.freeze_tracking_btn.toggled.connect(self.freeze_tracking)

        # Radio buttons to choose between ultrasound or neurostimulation "view"
        self.view_group = qt.QButtonGroup()
        self.us_view_btn = qt.QRadioButton("Ultrasound view")
        self.us_view_btn.setEnabled(False)
        self.view_group.addButton(self.us_view_btn)
        self.us_live_view_btn = qt.QRadioButton("Ultrasound live")
        self.us_live_view_btn.setEnabled(False)
        self.view_group.addButton(self.us_live_view_btn)
        self.neuro_view_btn = qt.QRadioButton("Neurostimulation view")
        self.neuro_view_btn.setChecked(False)
        self.view_group.addButton(self.neuro_view_btn)
        self.view_group.buttonClicked.connect(self.toggle_view)

        # Visualise box containing the above buttons
        # Box is disabled until live recon has been updated with real data
        self.ctk_visualise_box = ctk.ctkCollapsibleButton()
        self.ctk_visualise_box.setText("Choose Image")
        self.ctk_visualise_box.setChecked(False)
        self.ctk_visualise_box.setEnabled(True) 
        self.visualise_layout = qt.QGridLayout()
        # First a row with the overall view choices
        for i, button in enumerate(self.view_group.buttons()):
            self.visualise_layout.addWidget(button, 0, i)
        self.visualise_layout.addWidget(self.freeze_tracking_btn, 0, 4)  # We
        # don't want the freeze_tracking button to be in the view_group
        # Then the buttons for selecting what images to show, shown in a group
        self.images_group_box = qt.QGroupBox("Displayed image")
        self.images_layout = qt.QHBoxLayout()
        for button in [self.T1, self.T2, self.CT, self.MR, self.colormap_applied_btn]:
            self.images_layout.addWidget(button)
        self.images_group_box.setLayout(self.images_layout)
        self.visualise_layout.addWidget(self.images_group_box, 1, 0, 1, -1)
        # Update and assign layout
        self.ctk_visualise_box.setLayout(self.visualise_layout)
        self.ctk_visualise_box.setChecked(True)
        self.buttons.layout().addWidget(self.ctk_visualise_box)

        # Button to save all transforms to file
        # Used for syncing with neuromonitoring data
        self.transform_save_btn = qt.QPushButton('Save Transforms')
        self.transform_save_btn.clicked.connect(self.save_transforms)
        self.buttons.layout().addWidget(self.transform_save_btn)

        # Button to save all (scene and transforms) to file
        self.save_all_btn = qt.QPushButton('Save All')
        self.save_all_btn.clicked.connect(self.save_all)
        self.buttons.layout().addWidget(self.save_all_btn)

        # Add QSlider to control opacity
        self.opacity_layout = qt.QHBoxLayout()
        self.opacity_label = qt.QLabel('Background Slice Opacity:')
        self.opacity_label.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        self.opacity_slider = qt.QSlider(qt.Qt.Horizontal)
        self.opacity_slider.setValue(50)
        self.opacity_slider.setTickInterval(50)
        self.opacity_slider.valueChanged.connect(functions.set_slice_opacity)
        self.opacity_layout.addWidget(self.opacity_label)
        self.opacity_layout.addWidget(self.opacity_slider)
        self.buttons.layout().addLayout(self.opacity_layout)
        # Spacer to occupy excess space
        self.vertical_spacer = qt.QSpacerItem(20, 40, qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.buttons.layout().addItem(self.vertical_spacer)

        # Advanced settings
        self.advanced_options_checkbox = qt.QCheckBox("Show Advanced Settings")
        self.buttons.layout().addWidget(self.advanced_options_checkbox)
        self.advanced_options_checkbox.stateChanged.connect(
            self.toggle_tab_panel)

        # Add status bar for info messages
        self.status_layout = qt.QVBoxLayout()
        self.status_label = qt.QLabel("Status Log:")
        self.status_text = qt.QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.status_text)
        self.buttons.layout().addLayout(self.status_layout)

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
        # Load data in for demo automatically
        _, self.t1_node = slicer.util.loadVolume(t1_file, {"show": False}, returnNode=True)
        _, self.t2_node = slicer.util.loadVolume(t2_file, {"show": False}, returnNode=True)
        _, self.ct_node = slicer.util.loadVolume(ct_file, {"show": True}, returnNode=True)
        _, self.tum_seg_node = slicer.util.loadSegmentation(ts_file, returnNode=True)
        _, self.ner_seg_node = slicer.util.loadSegmentation(ns_file, returnNode=True)
        _, self.cm_node = slicer.util.loadVolume(cm_file, {"show": False}, returnNode=True)

        # Show in 3D view
        functions.set_MR_model_visible(self.ct_node)
        self.neurostim_points = []  # list of nodes of neurostim locations

        # Launch dependencies
        #self.plus = workflow.start_dependencies()

        self.parent.show()

    def view(self):
        """Get the Slicelet's current view mode, as either "us" or "neuro"."""
        return "us" if self.us_view_btn.isChecked() else "neuro"

    def toggle_view(self, clicked_button=None):
        """
        Switch between the ultrasound and neurostimulation "views".

        Note: the argument to this is the button that was clicked, and is
        received by Qt.
        """
        # When switching views, first check whether the colourmap should be
        # displayed, and update accordingly. This is because the colourmap
        # is shown differently in the two views.
        self.toggle_colormap(self.colormap_applied_btn.isChecked())
        # See what is exclusive to a view and so needs to be shown or hidden
        neurostim_data = (
                self.neurostim_points
                + list(filter(None, [self.ner_seg_node, self.tum_seg_node]))
        )
        recon_node = slicer.util.getNode(Config.LIVERECONSTRUCTION_VOL)
        ultrasound_data = [recon_node] if recon_node else []

        # Set default view
        if clicked_button is None:
            workflow.setup_ultrasound_view(to_show=ultrasound_data,
                                           to_hide=neurostim_data)
            return
        
        # Respond to user selection
        if clicked_button.text.startswith("Ultrasound"):
            if clicked_button.text.endswith("live"):
                workflow.setup_ultrasound_live(to_show=ultrasound_data,
                                               to_hide=neurostim_data)
            else:
                workflow.setup_ultrasound_view(to_show=ultrasound_data,
                                               to_hide=neurostim_data)
        else:
            # If switching to neurostim view, we want to also hide the scout
            # scan volume (if it exists). However, we don't want to show that
            # when switching to the US view again, so we only try to retrieve
            # it in this case.
            scout_node = slicer.util.getNode(Config.SCOUTSCAN_VOL)
            if scout_node:
                ultrasound_data.append(scout_node)
            workflow.setup_neurostim_view(to_show=neurostim_data,
                                          to_hide=ultrasound_data)

    def toggle_image(self, clicked_button=None):
        """
        Toggle the slice view backgrounds between the loaded images from files.

        Note: the argument to this is the button that was clicked, and is
        received by Qt.
        """

        if clicked_button is not None:
            image_name = clicked_button.text
        
        else:
            image_name = "MR"
    
        selected_node = self._button_to_node(image_name)
        if not selected_node:
            self.status_text.append(image_name + " node is not found.")
        # Set the backgrounds accordingly (or remove them if node not found)
        slicer.util.setSliceViewerLayers(background=selected_node)

    def _button_to_node(self, image_name):
        """Map between image options and which node to choose."""
        return {
            "T1": self.t1_node,
            "T2": self.t2_node,
            "CT": self.ct_node,
            #"MR": self.mr_node,
            "Colourmap": self.cm_node,
        }[image_name]

    def toggle_colormap(self, checked):
        """Show or hide the colourmap, depending on what view is selected.

        Also ensures that the right base image is shown (this is necessary when
        switching views).
        """
        # if self.view() == "us":
        #     # In US view, selecting the colourmap means showing only that
        #     # in the foreground, regardless of what base layer is selected.
        #     # We also disable the other radio buttons to make that clear.
        #     # This is because we can only show two layers, and the ultrasound
        #     # reconstruction will take up the background.
        #     if checked:
        #         for button in self.background_group.buttons():
        #             button.setEnabled(True)
        #         self.toggle_image(self.colormap_applied_btn)
        #     else:
        #         # Re-enable buttons in case they were previously disabled...
        #         for button in self.background_group.buttons():
        #             button.setEnabled(True)
        #         # ...and show the appropriate image
        #         self.toggle_image(self.background_group.checkedButton())
        # else:
        #     # In neurostimulation view, the base image is in the background,
        #     # so we can just show or hide the colourmap in the foreground.
        #     # before updating the background image.
        fg_node = self.cm_node if checked else None
        slicer.util.setSliceViewerLayers(foreground=fg_node)
        self.toggle_image(self.background_group.checkedButton())

    def freeze_tracking(self, checked):
        """Change the slice view driver from any defined node (ie, tracking) to
        'None' (fixed) and back when unchecked."""
        if checked:
            # Get the slice nodes
            red_slice_node = slicer.mrmlScene.GetNodeByID(
                'vtkMRMLSliceNodeRed')
            yellow_slice_node = slicer.mrmlScene.GetNodeByID(
                'vtkMRMLSliceNodeYellow')
            green_slice_node = slicer.mrmlScene.GetNodeByID(
                'vtkMRMLSliceNodeGreen')
            # Get the logic
            reslice_logic = slicer.modules.volumereslicedriver.logic()
            # Set the drivers to 'None'
            for node in [red_slice_node, yellow_slice_node, green_slice_node]:
                reslice_logic.SetDriverForSlice(Config.EMPTY_NODE, node)
        else:
            # Back to the default view settings
            # WARNING: the node names used after are defined in the config.py
            # (Config.US_TO_US_TIP_TF and Config.NEUROSTIM_TIP_TO_NEUROSTIM_TF)
            # but the nodes are created after the tools being tracked by the
            # StealthStation.
            if self.us_view_btn.isChecked():
                workflow.track_probe_in_slice_viewers("us")
            else:
                workflow.track_probe_in_slice_viewers("neuro")


    def save_and_display_neurostim_pt(self):
        """Save the neurostim transform in a timestamped file and
        under the scene. Display the point in the 3D viewer if appropriate."""
        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        neurostim_response = self.neurostim_response_b1.isChecked()
        self.save_neurostim_transform(timestamp=current_time,
                                      response=neurostim_response)
        # If we are in ultrasound view, we don't want to show the point yet.
        show_point = self.neuro_view_btn.isChecked()
        try:
            point = functions.create_neurostim_point(
                response=neurostim_response,
                timestamp=current_time,
                show=show_point)
        except RuntimeError:
            self.status_text.append("Could not create neurostim point.")
        else:
            self.neurostim_points.append(point)

    def save_neurostim_transform(self, timestamp, response):
        """Write the current neurostim transforms in the current hierarchy
        to a file, where the filename contains a timestamp."""
        # NB: as opposed to the get_all_transforms which returns a
        # dictionary, this one only returns an array.
        neurostim_transform = functions.get_neurostim_transform()

        if not neurostim_transform:
            self.status_text.append("Could not find neurostim transform.")
            return

        directory = Config.TF_OUTPUT_DIR

        # Create dir if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Fill the Dictionary
        neurostim_data = {}
        neurostim_data['Voltage in mA'] = self.neurostim_voltage_text.text
        neurostim_data['Neurostim response'] = response
        neurostim_data['Neurostim transform'] = neurostim_transform

        path_to_file = os.path.join(directory, 'neurostim_transform_' + timestamp + '.json')
        with open(path_to_file, 'w') as f:
            json.dump(neurostim_data, f, indent=4)

        self.status_text.append("Saving neurostim transform to: " + path_to_file)

    def check_if_models_exist(self):
        """ Check if the CT and ultrasound models have been
        loaded.
        """

        # The ultrasound name is defined in the PLUS xml config file.
        # The CT node doesn't have a name in Slicer 4.8 when it is sent from
        # the StealthStation. We rename the node after fetching it by ID.
        # TODO - tidy up - shouldn't hard code the variable names here,
        # better to read in from a file or something.

        ultrasound_name = Config.US_IMG
        ultrasound_id = functions.get_item_id_by_name(ultrasound_name)
        ultrasound_exists = functions.check_if_item_exists(ultrasound_id)
        if ultrasound_exists:
            # Get the node
            ultrasound_node = slicer.mrmlScene.GetFirstNodeByName(
                ultrasound_name)
            workflow.set_visible(ultrasound_node)

        # Set the name
        MR_node_name = Config.MR_IMG
        MR_node_id = 'vtkMRMLScalarVolumeNode1' # Assuming the id remains always the same
        volume_nodes_list = list(slicer.mrmlScene.GetNodesByClassByName('vtkMRMLScalarVolumeNode', ''))
        if volume_nodes_list:

            self.mr_node = volume_nodes_list[0]
            self.mr_node.SetName(MR_node_name)
            # Make the node visible in the volume rendering module
            workflow.set_visible(self.mr_node)

        # Stop the timer
        if ultrasound_exists and volume_nodes_list:
            self.status_text.append("Found Ultrasound Node: " + ultrasound_name)
            self.status_text.append("Found MR_node: " + MR_node_name)
            self.status_text.append("Waiting for tools to be visible to StealthStation")
            self.checkModelsTimer.stop()

    def check_if_transforms_active(self):
        """ Check if the transform is active"""
        all_active = workflow.wait_for_transforms()

        if all_active:
            self.status_text.append("Found expected transforms")
            workflow.setup_plus_remote(self.connector)
            workflow.create_models()
            workflow.set_transform_hierarchy()

            self.ctk_recon_box.setEnabled(True)
            self.checkTranformsTimer.stop()
            self.checkReconTimer.start()

            self.toggle_image()
            workflow.track_probe_in_slice_viewers("us")
            self.status_text.append("Enabling pivot calibration")
    
    def check_if_recon_display_node_exists(self):
        recon_node = slicer.mrmlScene.GetFirstNodeByName(
            Config.LIVERECONSTRUCTION_VOL)
        
        if recon_node.GetDisplayNode():
            self.ctk_visualise_box.setEnabled(True)
            self.checkReconTimer.stop()

    def choose_us_pivot(self):
        """Prepare transforms to calibrate ultrasound probe."""
        workflow.set_calibration_mode("us")

    def choose_neuro_pivot(self):
        """Prepare transforms to calibrate neurostimulator probe."""
        workflow.set_calibration_mode("neuro")

    def add_tab_widgets(self):
        """
        Add tab widgets for each of the Slicer modules we want access
        to in the 'advanced' mode.
        """

        module_names = [
            "data",
            "volumerendering",
            "openigtlinkif",
            "openigtlinkremote",
            "createmodels",
            "transforms",
            "plusremote",
            "volumereslicedriver"]

        # Need to have a text label for each module tab
        module_labels = ["Data", "Volumes", "IGTLink", "IGTLinkRemote",
                         "Models", "Transforms",
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
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Connecting...")
        self.connector = workflow.connect()
        success = functions.is_connected(self.connector)
        if success:
            self.status_text.append("OpenIGTLink connection successful.")
            self.connect_btn.setText("Connected")
        else:
            self.status_text.append("Could not connect via OpenIGTLink.")
            self.connect_btn.setText("Connect to OpenIGTLink")
            self.connect_btn.setEnabled("True")
        return success

    def get_ct_model(self):
        """
        To load the CT model from the StealthStation, we use the
        OpenIGTLinkRemote module. The openIGTLink connection node needs
        to be set to the one we have already created.

        Then click/select the relevant widget functions to load the CT model from remote.
        Whenever a GUI element is clicked/selected, need to do a qApp.processEvents() call
        so that QT reacts to the change.
        """

        # Need to get the QT Event loop to respond to the button clicks
        # So call it manually - TODO: is there a better way to handle this?
        app = qt.QApplication.instance()

        self.status_text.append("Querying remote")
        igt_remote_widget = slicer.modules.openigtlinkremote.widgetRepresentation()

        connector_box = slicer.util.findChild(igt_remote_widget, 'connectorNodeSelector')
        update_btn = slicer.util.findChildren(igt_remote_widget, 'updateButton')[0]
        remote_data_table = slicer.util.findChildren(igt_remote_widget, 'remoteDataListTable')[0]
        get_item_btn = slicer.util.findChildren(igt_remote_widget, 'getSelectedItemButton')[0]

        # TODO Wrap the above in a try-catch in case node(s) don't exist
        # (in case it changes in future versions)

        # Set the connector node
        connector_box.setCurrentNode(self.connector)
        app.processEvents()

        # Click 'Update' button and wait for the results to be received
        update_btn.clicked()
        time.sleep(1)
        app.processEvents()
        self.status_text.append("Received data from remote")

        # Select the first item in results table
        first_item = remote_data_table.item(0, 0).text()
        if not first_item.startswith('SLD'):
            raise ValueError("Expecting first item in remote data query list to be SLD-*")
        remote_data_table.selectRow(0)
        app.processEvents()

        # click the 'Get selected items' button
        get_item_btn.clicked()
        app.processEvents()

        self.status_text.append("Loading model")

    def load_t1_model(self):
        """Load a T1 MRI model from a file."""
        self.t1_node = functions.load_data_from_file("T1 MRI")
        if self.t1_node:
            self.status_text.append("Loaded T1 MRI from file")

    def load_t2_model(self):
        """Load a T2 MRI model from a file."""
        self.t2_node = functions.load_data_from_file("T2 MRI")
        if self.t2_node:
            self.status_text.append("Loaded T2 MRI from file")

    def load_ct_model(self):
        """Load a CT model from a file."""
        self.ct_node = functions.load_data_from_file("CT")
        if self.ct_node:
            self.status_text.append("Loaded CT from file")

    def load_colourmap(self):
        """Load a colourmap from a file."""
        self.cm_node = functions.load_data_from_file("Colourmap")
        if self.cm_node:
            self.status_text.append("Loaded colourmap from file")

    def load_tumour_segmentation(self):
        """Load a tumour segmentation from a file."""
        self.tum_seg_node = self._load_segmentation("tumour")

    def load_nerve_segmentation(self):
        """Load a nerve segmentation from a file."""
        self.ner_seg_node = self._load_segmentation("nerve")

    def _load_segmentation(self, segmentation_type):
        loaded_node = functions.load_data_from_file(
            "{} Segmentation".format(segmentation_type.capitalize()),
            segmentation=True)
        if loaded_node:
            self.status_text.append(
                "Loaded {} segmentation from file".format(segmentation_type))
            # Make the segmentations partially transparent so that they don't
            # hide the neurostimulation points
            loaded_node.GetDisplayNode().SetOpacity3D(0.7)
            # Don't show segmentation if in US view
            if self.view() == "us":
                loaded_node.SetDisplayVisibility(False)
        return loaded_node

    def align_volumes(self):
        """Apply appropriate transforms to ensure all volumes are aligned."""
        to_align = [self.t1_node, self.ct_node, self.cm_node]
        aligned = workflow.align_volumes_to_model(to_align)
        if aligned:
            self.status_text.append("All available volumes aligned")
        else:
            self.status_text.append("Failed to align some volumes")

    def save_all(self):
        """Save the current scene and transforms in timestamped files"""
        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        directory = Config.SCENE_OUTPUT_DIR
        # Create dir if inexistent
        if not os.path.exists(directory):
            os.makedirs(directory)
        path_to_file = os.path.join(directory, 'scene_' + current_time + '.mrb')
        # Save the scene
        slicer.util.saveScene(path_to_file)
        self.status_text.append("Saving scene to: " + path_to_file)

    def save_transforms(self):
        """ Write all transforms in the current hierarchy to a file,
        where the filename contains a timestamp. """
        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        transforms = functions.get_all_transforms()

        if not transforms:
            return

        directory = Config.TF_OUTPUT_DIR

        # Create dir if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        path_to_file = os.path.join(directory, 'transforms_' + current_time + '.json')
        with open(path_to_file, 'w') as f:
            json.dump(transforms, f, indent=4)

        self.status_text.append("Saving transforms to: " + path_to_file)


class TractographySlicelet(Slicelet):
    """ Creates the interface when module is run as a stand alone gui app.
    """
    #pylint: disable=useless-super-delegation
    def __init__(self):
        super(TractographySlicelet, self).__init__()


if __name__ == "__main__":

    import sys
    print(sys.argv)

    # Set the transverse mode for the red slice view before
    # running the slicelet as it seems not to work otherwise
    red_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
    reslice_logic = slicer.modules.volumereslicedriver.logic()
    reslice_logic.SetModeForSlice(reslice_logic.MODE_TRANSVERSE, red_slice_node)

    slicelet = TractographySlicelet()
    #slicelet.parent.showFullScreen()
