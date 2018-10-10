import slicer
import time

def connect_to_OpenIGTLink(name, host, port):
  cnode=slicer.vtkMRMLIGTLConnectorNode()
  slicer.mrmlScene.AddNode(cnode)
  cnode.SetName(name)
  cnode.SetTypeClient(host, port)
  cnode.Start()

  return cnode

def create_needle_model(name, length, radius, tip_radius):
  #TODO: Set colour
  show_markers = False
  create_model_module_logic = slicer.modules.createmodels.logic()
  needle = create_model_module_logic.CreateNeedle(length, radius, tip_radius, show_markers)
  needle.SetName(name)

  return needle


def create_linear_transform_node(name):
  # Use LinearTransformNode rather than just TransformNode
  # as Pivot calibration requires a linear one
  transform = slicer.vtkMRMLLinearTransformNode()
  transform.SetName(name)
  slicer.mrmlScene.AddNode(transform)

  return transform


def set_node_visible(node):

  #TODO: Better way to identify the nodes, other than checking the name

  #UltraSound
  if node.GetName() == 'Image_Reference':
      set_ultrasound_visible(node)

  #3D CT Model
  elif node.GetName() == '':
      set_CT_model_visible(node)

  else:
    node.SetDisplayVisibility(1)


def set_ultrasound_visible(node):
    slicer.util.setSliceViewerLayers(background=node)

def set_CT_model_visible(node):
    logic = slicer.modules.volumerendering.logic()
    
    displayNode = logic.CreateVolumeRenderingDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    displayNode.UnRegister(logic)
    logic.UpdateDisplayNodeFromVolumeNode(displayNode, node)


def set_node_invisible(node):
  node.SetDisplayVisibility(0)


def get_item_id_by_name(item):

  if not isinstance(item, str):
    print ("Error: String input required")
    return -1

  #See here for more info https://www.slicer.org/wiki/Documentation/Nightly/ScriptRepository#Subject_hierarchy
  subject_hierarchy_node = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)

  scene_item_ID = subject_hierarchy_node.GetSceneItemID()

  item_ID = subject_hierarchy_node.GetItemChildWithName(scene_item_ID, item)

  return item_ID


def check_if_item_exists(item_ID):
  invalid_item_ID = slicer.vtkMRMLSubjectHierarchyNode.GetInvalidItemID()

  if item_ID != invalid_item_ID:
    return True

  else:
    return False


def check_if_item_is_transform(item_ID):

  subject_hierarchy_node = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
  item_owner_type = subject_hierarchy_node.GetItemOwnerPluginName(item_ID)

  if item_owner_type == 'Transforms':
    return True
  
  else:
    return False 

def does_node_exist_as_a_transform(name):

    item_ID = get_item_id_by_name(name)
    item_exists = check_if_item_exists(item_ID)
    item_is_transform = check_if_item_is_transform(item_ID)

    if item_exists and item_is_transform:
        return True
    
    return False

def set_parent_of_transform_hierarchy_node(child, parent):
  child.SetAndObserveTransformNodeID(parent.GetID())


def remove_unused_widgets_from_pivot_calibration():

    # Some of the widgets to hide are children of the pivot_calibration window
    # Some are children of other/parent widgets
    pivot_cal_widget = slicer.modules.pivotcalibration.widgetRepresentation()
    parent_widget = pivot_cal_widget.parentWidget()

    # Make a list of all the widgets that we want to search through
    widgets_to_check = pivot_cal_widget.children() + parent_widget.children()
    unwanted_widget_names = ['IOCollapsibleButton', 'HelpCollapsibleButton']

    for widget in widgets_to_check:
        if widget.name in unwanted_widget_names:
            widget.hide()

    
def set_pivot_transforms(input_transform, output_transform):

    pivot_cal_widget = slicer.modules.pivotcalibration.widgetRepresentation()

    # Find the combo box widgets, should only be 2
    combo_box_type = slicer.qMRMLNodeComboBox()
    combo_boxes = pivot_cal_widget.findChildren(combo_box_type)

    input_combo_box_name = 'InputComboBox'
    output_combo_box_name = 'OutputComboBox'

    for box in combo_boxes:
        if box.name == input_combo_box_name:
            input_combo_box = box
        
        if box.name == output_combo_box_name:
            output_combo_box = box

    #Set the input (ToolToReference) and output (ToolTipToTool) transforms
    input_combo_box.setCurrentNode(input_transform)
    output_combo_box.setCurrentNode(output_transform)


def get_model_over_IGTLink(igtlink_node):
    igt_remote_widget = slicer.modules.openigtlinkremote.widgetRepresentation()

    combo_box_type = slicer.qMRMLNodeComboBox()

    combo_box_widgets = igt_remote_widget.findChildren(combo_box_type)

    connector_combo_box_name = 'connectorNodeSelector'

    for box in combo_box_widgets:
        if box.name == connector_combo_box_name:
            box.setCurrentNode(igtlink_node)


def query_remote_list(igt_connector):
    igt_query = slicer.vtkMRMLIGTLQueryNode()
    igt_query.SetQueryType(igt_query.TYPE_GET)
    #igt_query.SetQueryStatus(igt_query.STATUS_PREPARED)
    igt_query.SetIGTLName("image")

    igt_connector.PushQuery(igt_query)

def query_remote_item(igt_connector):
    igt_query = slicer.vtkMRMLIGTQueryNode()



    


