import slicer

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



def create_transform_node(name):
  transform = slicer.vtkMRMLTransformNode()
  transform.SetName(name)
  slicer.mrmlScene.AddNode(transform)

  return transform


def set_node_visible(node):
  node.SetDisplayVisibility(1)

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

def set_parent_of_transform_hierarchy_node(child, parent):
  child.SetAndObserveTransformNodeID(parent.GetID())

