import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging


class Slicelet(object):
  """A slicer slicelet is a module widget that comes up in stand alone mode
  implemented as a python class.
  This class provides common wrapper functionality used by all slicer modlets.
  """
  # TODO: put this in a SliceletLib
  # TODO: parse command line arge


  def __init__(self, widgetClass=None):
    self.parent = qt.QFrame()
    self.top_splitter = qt.QSplitter()
    self.top_splitter.orientation=qt.Qt.Horizontal

    self.parent.setLayout( qt.QHBoxLayout() )

    self.parent.layout().addWidget(self.top_splitter)
    #splitter
    self.splitter = qt.QSplitter()
    self.splitter.orientation = qt.Qt.Vertical
    self.top_splitter.addWidget(self.splitter)

    # buttons - top frame
    self.buttons = qt.QFrame()
    self.buttons.setLayout( qt.QVBoxLayout() )
    self.loadDataButton = qt.QPushButton("Connect to PLUS")
    self.buttons.layout().addWidget(self.loadDataButton)
    self.loadDataButton.connect('clicked()', slicer.app.ioManager().openAddVolumeDialog)
    self.showIn3DButton = qt.QPushButton("Check Data")
    self.buttons.layout().addWidget(self.showIn3DButton)
    self.showIn3DButton.connect('clicked()', self.showIn3D)
    self.addDataButton = qt.QPushButton("Calibration")
    self.buttons.layout().addWidget(self.addDataButton)
    self.addDataButton.connect("clicked()",slicer.app.ioManager().openAddDataDialog)
    self.loadSceneButton = qt.QPushButton("Load Scene")
    self.buttons.layout().addWidget(self.loadSceneButton)
    self.loadSceneButton.connect("clicked()",slicer.app.ioManager().openLoadSceneDialog)

    self.splitter.addWidget(self.buttons)

    # bottom frame
    self.bottomFrame = qt.QFrame()
    self.bottomFrame.setLayout(qt.QVBoxLayout() )
    self.splitter.addWidget(self.bottomFrame)

    #tab widget
    self.tabWidget = qt.QTabWidget()
    self.bottomFrame.layout().addWidget(self.tabWidget)

    module_name_label_pairs = [ ["volumerendering", "Volumes"],
                                ["openigtlinkif", "IGTLink"],
                                ["openigtlinkremote", "IGT Remote"],
                                ["pivotcalibration", "Calibrate"],
                                ["createmodels","Models"]]

    module_names = ["data","volumerendering","openigtlinkif","openigtlinkremote","pivotcalibration","createmodels"]
    module_labels = ["Data","Volumes", "IGTLink", "IGT Remote", "Calibrate", "Models"]

    for name, label in zip(module_names, module_labels) :
      self.scrollArea = qt.QScrollArea()
      widget = getattr(slicer.modules, name).widgetRepresentation()
      self.scrollArea.setWidget(widget)
      self.scrollArea.setWidgetResizable(True)
      self.tabWidget.addTab(self.scrollArea, label)

    # moduleSelector = slicer.qSlicerModuleSelectorToolBar()
    # moduleSelector.setModuleManager(slicer.app.moduleManager())
    # self.buttons.addWidget(moduleSelector)

    # layout
    layoutManager = slicer.qMRMLLayoutWidget()
    layoutManager.setMRMLScene(slicer.mrmlScene)
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutDefaultView)
    self.top_splitter.addWidget(layoutManager)

    self.parent.show()    

  # def addModule(module_name):
  #   scrollArea = qt.QScrollArea()
  #   widget = getattr(slicer.modules, module_name).widgetRepresentation()
  #   scrollArea.setWidget(widget)
  #   self.tabWidget.addTab(scrollArea, module_name)
  
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
