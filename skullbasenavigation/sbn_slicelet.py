""" Slicelet for SBN Project """

import qt
import ctk
import slicer

from slicer.ScriptedLoadableModule import *

from sbn import workflow, functions

#pylint: disable=useless-object-inheritance
# Pylint thinks that passing 'object' as an argument is
# unnecessary, but that is incorrect.

class Slicelet(object):
    """A slicer slicelet is a module widget that comes up in stand alone mode
    implemented as a python class.
    This class provides common wrapper functionality used by all slicer modlets.
    """

    def __init__(self):

        self.parent = qt.QSplitter()
        self.parent.orientation = qt.Qt.Horizontal

        # Left side of splitter
        self.control_panel = qt.QSplitter(self.parent)
        self.control_panel.orientation = qt.Qt.Vertical

        # Buttons Widget
        button_widget_index = 0

        self.buttons = qt.QFrame(self.control_panel)
        self.control_panel.setCollapsible(button_widget_index, False)

        self.buttons.setLayout(qt.QVBoxLayout())

        self.connect_btn = qt.QPushButton("Connect to OpenIGTLink")
        self.buttons.layout().addWidget(self.connect_btn)

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

        # Disable some buttons (they are enabled if wait_for_transforms returns
        # true)
        self.ctk_pivot_box.setEnabled(False)

        # Button callbacks
        self.connect_btn.clicked.connect(workflow.connect)

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

        # Right side of splitter
        # 3D/Slice Viewer
        self.layoutManager = slicer.qMRMLLayoutWidget()
        self.layoutManager.setMRMLScene(slicer.mrmlScene)
        self.layoutManager.setLayout(
            slicer.vtkMRMLLayoutNode.SlicerLayoutDefaultView)
        self.parent.addWidget(self.layoutManager)

        self.parent.show()

    def check_if_models_exist(self):
        """ Check if a the CT and ultrasound models have been
        loaded.
        """
        # TODO - tidy up
        ultrasound_name = 'Image_Reference'
        CT_name = ''

        ultrasound_id = functions.get_item_id_by_name(ultrasound_name)
        ct_id = functions.get_item_id_by_name(CT_name)

        ultrasound_exists = functions.check_if_item_exists(ultrasound_id)
        ct_exists = functions.check_if_item_exists(ct_id)

        if (ultrasound_exists and ct_exists):
            workflow.set_visible()
            self.checkModelsTimer.stop()

    def check_if_transforms_active(self):
        """ Check if the transform is active"""
        all_active = workflow.wait_for_transforms()

        if all_active:
            workflow.create_models()
            workflow.prepare_pivot_cal()
            workflow.set_transform_hierarchy()

            self.ctk_pivot_box.setEnabled(True)
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
            "createmodels"]
        module_labels = ["Data", "Volumes", "IGTLink", "Models"]

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
