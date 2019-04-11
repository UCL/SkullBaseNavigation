""" Functions required to implement Slicer workflow. """

import time
import datetime
import logging
import json
import os
import slicer

def connect_to_OpenIGTLink(name, host, port):
    """
    Create an link to a OpenIGTLink server.
    """
    cnode = slicer.vtkMRMLIGTLConnectorNode()
    slicer.mrmlScene.AddNode(cnode)
    cnode.SetName(name)
    cnode.SetTypeClient(host, port)
    cnode.Start()

    return cnode


def is_connected(connector):
    """Check whether an IGT connection has been successful.

    :param connector: A vtkMRMLIGTConnectorNode instance.
    :return: True if the node's status indicates it is connected, else False.
    """
    time.sleep(1)  # wait a bit because the state does not update immediately
    # In Slicer 4.10, this attribute is called StateConnected, but in previous
    # versions it is called STATE_CONNECTED. There is no easy way to check what
    # version we are running, but we can check for both...
    try:
        connected_state = slicer.vtkMRMLIGTLConnectorNode.StateConnected
    except AttributeError:
        connected_state = slicer.vtkMRMLIGTLConnectorNode.STATE_CONNECTED
    return connector.GetState() == connected_state


def create_needle_model(name, length, radius, tip_radius):
    """
    Create a model that can be used to represent the style/probe.
    """
    # TODO: Set colour
    show_markers = False
    create_model_module_logic = slicer.modules.createmodels.logic()
    needle = create_model_module_logic.CreateNeedle(
        length, radius, tip_radius, show_markers)
    needle.SetName(name)

    return needle


def create_linear_transform_node(name):
    """
    Create a transform node.
    Use LinearTransformNode rather than just TransformNode
    as Pivot calibration requires a linear one
    """
    transform = slicer.vtkMRMLLinearTransformNode()
    transform.SetName(name)
    slicer.mrmlScene.AddNode(transform)

    return transform


def set_node_visible(node):
    """
    Set a node visible.
    The method of setting visiblity differs depending on data type.
    """
    # TODO: Better way to identify the nodes, other than checking the name

    # UltraSound
    if node.GetName() == 'Image_SureTrack2Tip':
        set_ultrasound_visible(node)

    # 3D CT Model
    elif node.GetName() == 'CT_scan':
        set_CT_model_visible(node)

    else:
        node.SetDisplayVisibility(1)


def set_ultrasound_visible(node):
    """
    Ultrasound data is an image - set to visible in the slice viewer.
    """
    slicer.util.setSliceViewerLayers(background=node)
    # Get all the red slice node
    red_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
    # Get the US node ID
    node_id = node.GetID()
    enable_volume_reslice(red_slice_node, node_id)
    slicer.util.setSliceViewerLayers(background=node)

def enable_volume_reslice(slice_node, node_id):
    """Use the Volume Reslice Driver module to display the correct US slice in
    the 3D viewer
    """
    # Get the logic from the Volume Slice Driver module
    reslice_logic = slicer.modules.volumereslicedriver.logic()
    reslice_logic.SetDriverForSlice(node_id, slice_node)
    # Make the slice visible in the 3D viewer
    slice_node.SetSliceVisible(True)

def set_CT_model_visible(node):
    """
    CT Model is a 3D volume - set to visible.
    """
    logic = slicer.modules.volumerendering.logic()

    displayNode = logic.CreateVolumeRenderingDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    displayNode.UnRegister(logic)
    logic.UpdateDisplayNodeFromVolumeNode(displayNode, node)


def set_node_invisible(node):
    """
    Set node invisible.
    """
    node.SetDisplayVisibility(0)


def get_item_id_by_name(item):
    """
    Geth the node ID by looking up the node name in the subject hierarchy.
    """

    if not isinstance(item, str):
        print("Error: String input required")
        return -1

    # See here for more info
    # https://www.slicer.org/wiki/Documentation/Nightly/ScriptRepository#Subject_hierarchy
    subject_hierarchy_node = \
        slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(
            slicer.mrmlScene)

    scene_item_ID = subject_hierarchy_node.GetSceneItemID()

    item_ID = subject_hierarchy_node.GetItemChildWithName(scene_item_ID, item)

    return item_ID


def check_if_item_exists(item_ID):
    """
    Check if the item with the given ID exists in the subject hierarchy.
    """
    invalid_item_ID = slicer.vtkMRMLSubjectHierarchyNode.GetInvalidItemID()

    if item_ID != invalid_item_ID:
        return True

    return False


def check_if_item_is_transform(item_ID):
    """
    Check if the given node ID coresponds to a transform.
    """
    subject_hierarchy_node = \
        slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(
            slicer.mrmlScene)
    item_owner_type = subject_hierarchy_node.GetItemOwnerPluginName(item_ID)

    if item_owner_type == 'Transforms':
        return True

    return False


def does_node_exist_as_a_transform(name):
    """
    Check if a node exists, and that it is a transform.
    """
    item_ID = get_item_id_by_name(name)
    item_exists = check_if_item_exists(item_ID)
    item_is_transform = check_if_item_is_transform(item_ID)

    if item_exists and item_is_transform:
        return True

    return False


def set_parent_of_transform_hierarchy_node(child, parent):
    """
    Set the parent of a transform node.
    """
    child.SetAndObserveTransformNodeID(parent.GetID())


def remove_unused_widgets_from_pivot_calibration():
    """
    Remove unused child widgets from the Pivot calibration widget, to make
    the interface clearer.
    Some of the widgets to hide are children of the pivot_calibration window
    Some are children of other/parent widgets.
    """
    pivot_cal_widget = slicer.modules.pivotcalibration.widgetRepresentation()
    parent_widget = pivot_cal_widget.parentWidget()

    # Make a list of all the widgets that we want to search through
    widgets_to_check = pivot_cal_widget.children() + parent_widget.children()
    unwanted_widget_names = ['IOCollapsibleButton', 'HelpCollapsibleButton']

    for widget in widgets_to_check:
        if widget.name in unwanted_widget_names:
            widget.hide()


def set_pivot_transforms(input_transform, output_transform):
    """
    Set the input and output transforms to use for the pivot calibration.
    """
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

    # Set the input (ToolToReference) and output (ToolTipToTool) transforms
    input_combo_box.setCurrentNode(input_transform)
    output_combo_box.setCurrentNode(output_transform)


def set_model_widget_connector(igtlink_node):
    """
    To load the CT model from the StealthStation, we use the
    OpenIGTLinkRemote module. The openIGTLink connection node needs
    to be set to the one we have already created.
    """
    igt_remote_widget = slicer.modules.openigtlinkremote.widgetRepresentation()

    combo_box_type = slicer.qMRMLNodeComboBox()

    combo_box_widgets = igt_remote_widget.findChildren(combo_box_type)

    connector_combo_box_name = 'connectorNodeSelector'

    for box in combo_box_widgets:
        if box.name == connector_combo_box_name:
            box.setCurrentNode(igtlink_node)


def query_remote_list(igt_connector):
    """
    Query the OpenIGTLinkRemote node to get a list of available models.
    There should only be one - the CT model.
    """
    igt_query = slicer.vtkMRMLIGTLQueryNode()
    igt_query.SetQueryType(igt_query.TYPE_GET)
    # igt_query.SetQueryStatus(igt_query.STATUS_PREPARED)
    igt_query.SetIGTLName("image")

    igt_connector.PushQuery(igt_query)


def query_remote_item():
    """
    Retrieve an item from the OpenIGTLinkRemote node.
    """
    igt_query = slicer.vtkMRMLIGTQueryNode()

    return igt_query

def get_all_transforms():
    """ Return a dictionary of all the transforms in the
    current hierarchy.
    :return: Dictionary of transforms, or None if no transforms in hierarchy.
    """
    transform_nodes = slicer.mrmlScene.GetNodesByClass(
        'vtkMRMLLinearTransformNode')
    transform_nodes.InitTraversal()

    tf_node = transform_nodes.GetNextItemAsObject()

    if tf_node is None:
        return None

    transforms = {}
    while tf_node:
        tf = tf_node.GetTransformToParent()
        matrix4x4 = tf.GetMatrix()

        array = get_vtkmartrix4x4_as_array(matrix4x4)
        tf_name = tf_node.GetName()

        # Update dictionary
        transforms[tf_name] = array

        tf_node = transform_nodes.GetNextItemAsObject()

    return transforms

def save_transforms():
    """ Write all transforms in the current hierarchy to a file,
    where the filename contains a timestamp. """
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    transforms = get_all_transforms()

    if not transforms:
        return

    directory = 'outputs/'

    # Create dir if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = directory + 'transforms_' + current_time + '.json'
    with open(filename, 'w') as f:
        json.dump(transforms, f, indent=4)

def get_vtkmartrix4x4_as_array(matrix4x4):
    """ Iterate through elements of vtkMatrix4x4 and call
    GetElement(i, j).
    :param matrix4x4: instance of vtkMatrix4x4
    :return: List of lists. Each sub list is a row in the matrix """

    n = 4
    array = [[0 for x in range(n)] for y in range(n)]

    for i in range(n):
        for j in range(n):
            elem = matrix4x4.GetElement(i, j)
            array[i][j] = elem

    return array

def remove_all_transforms():
    """ Remove all transform nodes from scene/hierarchy. """
    logging.debug("Removing all transforms.")
    transform_nodes = slicer.mrmlScene.GetNodesByClass(
        'vtkMRMLLinearTransformNode')
    transform_nodes.InitTraversal()
    tf_node = transform_nodes.GetNextItemAsObject()

    while tf_node:
        slicer.mrmlScene.RemoveNode(tf_node)
        tf_node = transform_nodes.GetNextItemAsObject()

    # Check that no nodes remain
    transform_nodes = slicer.mrmlScene.GetNodesByClass(
        'vtkMRMLLinearTransformNode')
    transform_nodes.InitTraversal()
    tf_node = transform_nodes.GetNextItemAsObject()

    if tf_node:
        raise ValueError(
            "Tried to delete all transform nodes, but it didn't work!")
