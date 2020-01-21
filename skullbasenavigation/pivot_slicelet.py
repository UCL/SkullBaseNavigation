""" Slicelet for SBN Project """

import logging  #pylint: disable=unused-import
import time
import datetime
import json
import re
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
        # Collapsible button to hole Pivot calibration module
        # Won't be active until the tools have been seen
        # by the StealthStation - i.e. the Stylus and SureTrack
        # transforms have been sent to Slicer
        self.ctk_pivot_box = ctk.ctkCollapsibleButton()
        self.ctk_pivot_box.setText("Pivot Calibration")
        self.ctk_pivot_box.setChecked(False)

        self.pivot_layout = qt.QVBoxLayout()
        # Radio buttons to choose which instrument to calibrate
        # QButtonGroup is just a logical grouping, not a widget!
        self.pivot_mode_buttons = qt.QButtonGroup()
        self.pivot_mode_probe = qt.QRadioButton("Ultrasound")
        self.pivot_mode_probe.setChecked(True)
        self.pivot_mode_probe.clicked.connect(self.choose_us_pivot)
        self.pivot_mode_buttons.addButton(self.pivot_mode_probe)
        self.pivot_mode_neuro = qt.QRadioButton("Neurostimulator")
        self.pivot_mode_neuro.setChecked(False)
        self.pivot_mode_neuro.clicked.connect(self.choose_neuro_pivot)
        self.pivot_mode_buttons.addButton(self.pivot_mode_neuro)
        # Set up the layout for these buttons
        self.pivot_mode_buttons_box = qt.QGroupBox()
        self.pivot_mode_buttons_layout = qt.QHBoxLayout()
        for radio_button in self.pivot_mode_buttons.buttons():
            self.pivot_mode_buttons_layout.addWidget(radio_button)
        self.pivot_mode_buttons_box.setLayout(self.pivot_mode_buttons_layout)
        self.pivot_layout.addWidget(self.pivot_mode_buttons_box)

        self.pivot_scroll_area = qt.QScrollArea()
        self.pivot = slicer.modules.pivotcalibration.widgetRepresentation()

        self.pivot_scroll_area.setWidget(self.pivot)
        self.pivot_scroll_area.setWidgetResizable(True)
        self.pivot_layout.addWidget(self.pivot_scroll_area)

        self.ctk_pivot_box.setLayout(self.pivot_layout)
        self.buttons.layout().addWidget(self.ctk_pivot_box)

        # Set the default calibration duration to 10
        calib_duration = 10
        calib_duration_widget = self.buttons.findChild(ctk.ctkDoubleSpinBox(),
                                                       u'durationTimerEdit')

        calib_duration_widget.setValue(calib_duration)
        # Disable the button (enabled if wait_for_transforms returns
        # true)
        self.ctk_pivot_box.setEnabled(True)
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
        # Button to save all transforms to file
        # Used for syncing with neuromonitoring data
        self.transform_save_btn = qt.QPushButton('Save Tip Transforms')
        self.transform_save_btn.clicked.connect(self.save_transforms)
        self.transform_save_btn.setEnabled(True)
        self.buttons.layout().addWidget(self.transform_save_btn)

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
            workflow.prepare_probe_pivot_cal()

            self.ctk_pivot_box.setEnabled(True)
            self.ctk_pivot_box.setChecked(True)
            self.transform_save_btn.setEnabled(True)
            self.checkTranformsTimer.stop()
            self.status_text.append("Enabling pivot calibration")
    
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

    # TODO: Refactor this function so that we don't need to duplicate in pivot_slicelet and sbn_slicelet
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
        
        self.update_main_plus_config(transforms)

        self.status_text.append("Updating PLUS config with new transforms")

    def update_main_plus_config(self, transforms):
        """ Update the US and Stim tip to tool transforms in the PLUS XML file.
        Read XML data in from the config file, do some regex magic to find the relevant parts
        and replace them with the new values, then write back to the config.

        Inputs: transforms - dictionary of transforms, which should contain
                             US and Stim Tip to Tool transforms.
        """
        x = transforms[Config.US_TO_US_TIP_TF]
        y = transforms[Config.NEUROSTIM_TIP_TO_NEUROSTIM_TF]

        # Flatten list of lists into single list
        us_tip_tf = [a for b in x for a in b]
        stim_tip_tf = [a for b in y for a in b]
 
        if not (us_tip_tf and stim_tip_tf):
            self.status_text.append("US Tip and Stim Tip transforms not found!")

        us_tip_to_us_string =      Config.US_TIP_TO_US_XML.format(*us_tip_tf)
        stim_tip_to_stim_string =  Config.STIM_TIP_TO_STIM_XML.format(*stim_tip_tf)

        plus_config = os.path.join(Config.PATH_TO_PLUS_SETTINGS,
                                   Config.PLUS_CONFIG_FILE)

        with open(plus_config, 'r') as plus_file:
            xml_data = plus_file.read()
        
        us_pattern =  re.compile("<Transform From=\"USTip\" To=\"US\"[\s\S]*?>")
        stim_pattern =  re.compile("<Transform From=\"StimTip\" To=\"Stim\"[\s\S]*?>")

        us_to_replace = us_pattern.search(xml_data).group(0)
        stim_to_replace = stim_pattern.search(xml_data).group(0)

        xml_data = xml_data.replace(us_to_replace, us_tip_to_us_string)
        xml_data = xml_data.replace(stim_to_replace, stim_tip_to_stim_string)

        with open(plus_config, "w+") as plus_file:
            plus_file.write(xml_data)



class TractographySlicelet(Slicelet):
    """ Creates the interface when module is run as a stand alone gui app.
    """
    #pylint: disable=useless-super-delegation
    def __init__(self):
        super(TractographySlicelet, self).__init__()


if __name__ == "__main__":

    import sys
    print(sys.argv)

    slicelet = TractographySlicelet()
    #slicelet.parent.showFullScreen()
