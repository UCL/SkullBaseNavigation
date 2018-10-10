import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
from ui.form import Ui_Form
import sbn

class Slicelet(object):
  """A slicer slicelet is a module widget that comes up in stand alone mode
  implemented as a python class.
  This class provides common wrapper functionality used by all slicer modlets.
  """
  # TODO: put this in a SliceletLib
  # TODO: parse command line arge


  def __init__(self, widgetClass=None):
    
    self.parent = qt.QSplitter()
    self.parent.orientation = qt.Qt.Horizontal
    
    ## Left side of splitter
    self.control_panel = qt.QSplitter(self.parent)
    self.control_panel.orientation = qt.Qt.Vertical
   
    #self.parent.addWidget(self.control_panel)

    # Buttons Widget
    button_widget_index = 0

    self.buttons = qt.QFrame()
    self.buttons.setLayout(qt.QVBoxLayout())

    self.advanced_options_checkbox = qt.QCheckBox("Show Advanced Settings")
    self.advanced_options_checkbox.stateChanged.connect(self.toggle_tab_panel)
    self.buttons.layout().addWidget(self.advanced_options_checkbox)

    self.add_connect_to_IGTLink_button()
    self.test_widget = qt.QWidget()
    self.ui=Ui_Form()
    self.ui.setupUi(self.test_widget)
    test_widget_index = 1
    #self.setupUi(self.test_widget)
    
    self.control_panel.insertWidget(test_widget_index, self.test_widget)
    self.control_panel.insertWidget(button_widget_index,self.buttons)
    self.control_panel.setCollapsible(test_widget_index,False)

    self.control_panel.setCollapsible(button_widget_index,False)

    # Tabbed modules - hide by default
    tab_widget_index = 2
    self.tabWidget = qt.QTabWidget()
    self.tabWidget.hide()
    self.add_tab_widgets()

    self.control_panel.insertWidget(tab_widget_index, self.tabWidget) 



    ## Right side of splitter
    # 3D/Slice Viewer
    self.layoutManager = slicer.qMRMLLayoutWidget()
    self.layoutManager.setMRMLScene(slicer.mrmlScene)
    self.layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutDefaultView)
    self.parent.addWidget(self.layoutManager)

    self.parent.show()    

  def add_connect_to_IGTLink_button(self):
    self.connect_to_IGTL_frame = qt.QFrame()
    self.connect_to_IGTL_frame.setLayout(qt.QGridLayout())
    
    self.connect_to_IGTL_button = qt.QPushButton("Connect")
    self.ip_edit_text = qt.QTextEdit("localhost")
    self.port_edit_text = qt.QTextEdit("18904")

    self.connect_to_IGTL_frame.layout().addWidget(qt.QLabel("OpenIGTLink Settings"),1,1,1,2, qt.Qt.AlignHCenter)
    self.connect_to_IGTL_frame.layout().addWidget(qt.QLabel("IP:"),2,1)
    self.connect_to_IGTL_frame.layout().addWidget(qt.QLabel("Port:"),3,1)
    self.connect_to_IGTL_frame.layout().addWidget(self.ip_edit_text, 2,2)
    self.connect_to_IGTL_frame.layout().addWidget(self.port_edit_text,3,2)
    self.connect_to_IGTL_frame.layout().addWidget(self.connect_to_IGTL_button,4,1,4,2, qt.Qt.AlignHCenter )


 
    # self.connect_to_IGTL_form.addRow(qt.QLabel("IP:"), self.ip_edit_text)
    # self.connect_to_IGTL_form.addRow(qt.QLabel("Port:"), self.port_edit_text)

    # self.connect_to_IGTL_frame.layout().addLayout(self.connect_to_IGTL_form)
    # self.connect_to_IGTL_frame.layout().addWidget(self.connect_to_IGTL_button)

    

    self.buttons.layout().addWidget(self.connect_to_IGTL_frame)

  def setupUi(self, Form):
    Form.resize(350, 519)
    self.verticalLayoutWidget = qt.QWidget(Form)
    self.verticalLayoutWidget.setGeometry(qt.QRect(40, 30, 271, 441))
    self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
    self.verticalLayout = qt.QVBoxLayout(self.verticalLayoutWidget)
    self.verticalLayout.setContentsMargins(0, 0, 0, 0)
    self.verticalLayout.setObjectName("verticalLayout")
    self.checkBox = qt.QCheckBox(self.verticalLayoutWidget)
    self.checkBox.setObjectName("checkBox")
    self.verticalLayout.addWidget(self.checkBox)
    self.pushButton = qt.QPushButton(self.verticalLayoutWidget)
    self.pushButton.setObjectName("pushButton")
    self.verticalLayout.addWidget(self.pushButton)

    self.retranslateUi(Form)


  def retranslateUi(self, Form):
    _translate = qt.QCoreApplication.translate
    Form.setWindowTitle(_translate("Form", "Form"))
    self.checkBox.setText(_translate("Form", "CheckBox"))
    self.pushButton.setText(_translate("Form", "PushButton"))

  def add_tab_widgets(self):
    module_names = ["data","volumerendering","openigtlinkif","openigtlinkremote","pivotcalibration","createmodels"]
    module_labels = ["Data","Volumes", "IGTLink", "IGT Remote", "Calibrate", "Models"]

    for name, label in zip(module_names, module_labels) :
      self.scrollArea = qt.QScrollArea()
      widget = getattr(slicer.modules, name).widgetRepresentation()
      self.scrollArea.setWidget(widget)
      self.scrollArea.setWidgetResizable(True)
      self.tabWidget.addTab(self.scrollArea, label)


  def toggle_tab_panel(self):
    if self.advanced_options_checkbox.isChecked():
      self.tabWidget.show()
    else:
      self.tabWidget.hide()


  def showIn3D(self):
    # Turn on the 3D Volume view for the loaded node

    nodes = slicer.mrmlScene.GetNodesByName('MRHead')
    first_item_index = 0
    node = nodes.GetItemAsObject(first_item_index)
    node.SetDisplayVisibility(0)

    self.loadDataButton.setText(node.GetDisplayVisibility())
    node.SetDisplayVisibility(1)

  

class TractographySlicelet(Slicelet):
  """ Creates the interface when module is run as a stand alone gui app.
  """

  def __init__(self):
    super(TractographySlicelet,self).__init__()


if __name__ == "__main__":
  # TODO: need a way to access and parse command line arguments
  # TODO: ideally command line args should handle --xml

  import sys
  print( sys.argv )

  slicelet = TractographySlicelet()

