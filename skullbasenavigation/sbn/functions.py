""" Functions required to implement Slicer workflow. """

import logging
import os
import time

import qt
import slicer
import vtk

from .config import Config


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


def create_volume_node(name):
    """Create a volume node with the given name, and add it to the scene."""
    node = slicer.vtkMRMLScalarVolumeNode()
    node.SetName(name)
    slicer.mrmlScene.AddNode(node)
    return node


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


def load_probe_image(name, model):
    """Loads a model from a file and assign a name to the node.
    Inputs: name - the name of the node
            model - the name of the model file (this should be in the
                    models subdirectory"""
    # Slicer wants an absolute path to the STL image.
    # This assumes we are at the top level of the repository.
    img_path = os.path.join(os.getcwd(), "models", model)

    success, img_node = slicer.util.loadModel(img_path, returnNode=True)
    if success:
        img_node.SetName(name)
    else:
        # TODO Raise or log something
        pass
    return img_node


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
    if node.GetName() == Config.US_IMG:
        # no longer needed
        # set_ultrasound_visible(node)
        pass
    # 3D CT Model
    elif node.GetName() == Config.MR_IMG:
        set_MR_model_visible(node)

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


def set_MR_model_visible(node):
    """
    CT Model is a 3D volume - set to visible.
    """
    logic = slicer.modules.volumerendering.logic()
    displayNode = logic.CreateVolumeRenderingDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    displayNode.UnRegister(logic)
    logic.UpdateDisplayNodeFromVolumeNode(displayNode, node)
    node.AddAndObserveDisplayNodeID(displayNode.GetID())


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


def get_plus_remote_connector_selector():
    """
    Get the combo box that controls which connector node the PlusRemote module
    uses.

    This is not straightforward because different versions of the module have
    different layouts, and in some of them the widgets lack names.

    :return: The combo box, as a qMRMLNodeComboBox instance.
    """
    # Finding the right selector box is easy if the widgets have names...
    plus_remote_widget = slicer.modules.plusremote.widgetRepresentation()
    try:
        param_box = next(w for w in plus_remote_widget.children()
                         if w.name == "ParametersCollapsibleButton")
        combo_box = next(w for w in param_box.children()
                         if w.name == "OpenIGTLinkConnectorNodeSelector")
    except StopIteration:
        # ...otherwise we have to try by position!
        # NB: If we have moved any parts of PlusRemote to the slicelet, this
        # index may change (but since the reconstruction buttons come after
        # the parameter box, we should be OK...)
        param_box = plus_remote_widget.children()[2]
        # The layout and order of the widgets varies between versions, so it's
        # safer to search by type of widget than by position.
        combo_box = param_box.findChild(slicer.qMRMLNodeComboBox)
    return combo_box


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


def check_add_timestamp_to_filename_box(ctk_recon_box):
    """
    Check the 'Add timestamp to filename' box in the Live Reconstruction widget
    to avoid overriding the output file when multiple reconstructions are
    performed.
    """
    # Go through the hierarchy of widgets and stuff
    ctk_recon_box_widgets = ctk_recon_box.children()
    # Return all the check boxes by class name
    chk_box = [child for child in ctk_recon_box_widgets
               if child.className() == "QCheckBox"]
    # Searching in Slicer, the check box we need is in position 2
    add_timestamp_checkbox = chk_box[2]
    # Finally check that box
    add_timestamp_checkbox.setChecked(True)


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


def get_neurostim_transform(return_flag=False):
    """Return a specific neurostim transform"""
    # TODO: Check this is working as my PLUS server isn't compiled with
    # the Stealthlink. Assuming there is only one element
    neurostim_transform_nodes = slicer.mrmlScene.GetNodesByName(
        Config.NEUROSTIM_TIP_TO_RAS)
    neurostim_transform_nodes.InitTraversal()
    # Assuming there is only one node with that name
    neurostim_transform_node = neurostim_transform_nodes.GetNextItemAsObject()
    # Check if node exists
    if neurostim_transform_node is None:
        return None
    if return_flag:
        return neurostim_transform_node
    # Reformat under a 4x4 matrix
    neurostim_tf = neurostim_transform_node.GetTransformToParent()
    matrix4x4 = neurostim_tf.GetMatrix()
    array = get_vtkmartrix4x4_as_array(matrix4x4)
    return array


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


def set_slice_opacity(opacity):
    """ Set the opacity of the foreground volumes in slice view. """
    slicer.util.setSliceViewerLayers(foregroundOpacity=opacity / 100.0)


def create_neurostim_point(response, timestamp, show):
    """Mark the location of neurostimulation in the 3D viewer.

    Show in green if there was a response, otherwise in red. If show=False
    is spedcified, the point will not be displayed automatically.

    :param response: bool indicating whether there was a response.
    :param timestamp: string containing a timestamp used to label the model.
    :param show: bool indicating whether to display the point or not.
    :return: the node representing the response point.
    """
    # Get location and fail if not found
    tf = get_neurostim_transform(return_flag=True)
    if not tf:
        raise RuntimeError("Could not find neurostim transform node!")
    # Create a new transform to hold this location
    # We don't need a Linear need specifically (and it's becoming deprecated),
    # but since we have a function for creating nodes already...
    new_tf = create_linear_transform_node("NeurostimTransform_" + timestamp)
    new_tf.SetMatrixTransformToParent(tf.GetMatrixTransformToParent())
    # Create a model to display the location
    sphere = slicer.modules.createmodels.logic().CreateSphere(5)  # radius = 5
    sphere.SetName("NeurostimModel_" + timestamp)
    colour = (0, 255, 0) if response else (255, 0, 0)
    sphere.GetDisplayNode().SetColor(*colour)  # takes colour as RGB
    # Place the model according to the transform
    set_parent_of_transform_hierarchy_node(sphere, new_tf)
    # The sphere is shown by default; hide it if that is not desired
    sphere.SetDisplayVisibility(show)
    # To show sphere outline in slice viewers, if desired, use:
    sphere.GetDisplayNode().SetSliceIntersectionVisibility(True)
    return sphere


def load_data_from_file(data_type, segmentation=False):
    """Choose a file containing a volume or segmentation and return the
    resulting node.

    :param data_type: string describing the data (shown in dialog)
    :param segmentation: True if loading a segmentation, or False for a volume
    :return: the node containing the loaded data, or None if no file
    is selected.
    """
    dialog = qt.QFileDialog()
    dialog.setFileMode(dialog.ExistingFile)
    # This has to be set after the file mode, or it will be overwritten
    dialog.setLabelText(dialog.Accept, "Load " + data_type)
    # Display dialog and load the first selected file (if multiple)
    if dialog.exec_():
        # Use the appropriate Slicer method depending on what we are loading
        # These methods return a tuple (success::bool, node), but only if
        # returnNode is explicitly specified
        if segmentation:
            _, node = slicer.util.loadSegmentation(dialog.selectedFiles()[0],
                                                   returnNode=True)
        else:
            # When loading a volume, we can pass an extra parameter so Slicer
            # doesn't display it in the slice viewers automatically
            _, node = slicer.util.loadVolume(dialog.selectedFiles()[0],
                                             {"show": False},
                                             returnNode=True)
        return node
    return None


def load_registration_tf():
    """Choose a file and load the transform contained therein.

    This is intended for reading the particular format of transforms
    that is produced by the image registration pipeline.
    """
    dialog = qt.QFileDialog()
    dialog.setFileMode(dialog.ExistingFile)
    # This has to be set after the file mode, or it will be overwritten
    dialog.setLabelText(dialog.Accept, "Load Transform")
    # Display dialog
    if dialog.exec_(): # pylint: disable=no-else-return
        # Read the chosen file (or the first, if multiple are chosen)
        tf_file = dialog.selectedFiles()[0]
        # Slicer's loadTransform method doesn't seem to like the format of
        # our transform files, so we have to read them ourselves.
        with open(tf_file, 'r') as infile:
            data = [line.strip().split(" ") for line in infile]
        # Data is now a list of lists of strings.
        # Flatten the list as the VTK method requires, and convert to numbers
        data = map(float, sum(data, []))
        tf_node = slicer.util.getNode(Config.REGISTRATION_TF)
        if not tf_node:  # Create the transform if it doesn't exist already
            tf_node = create_linear_transform_node(Config.REGISTRATION_TF)
        # Create a VTK matrix from the data and use it for the transform
        m = vtk.vtkMatrix4x4()
        m.DeepCopy(data)
        tf_node.SetMatrixTransformToParent(m)
        return tf_node
    else:
        return None
