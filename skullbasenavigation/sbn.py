from slicer_functions import *

def connect():
    igt_connector = connect_to_OpenIGTLink('OpenIGT', 'localhost', 18905)
    
    return igt_connector

def set_visible():
        scene = slicer.mrmlScene

        ultrasound_volume_name = 'Image_Reference'
        ct_volume_name = ''
        
        ultrasound_node = scene.GetFirstNodeByName(ultrasound_volume_name)
        ct_node = scene.GetFirstNodeByName(ct_volume_name)

        set_node_visible(ultrasound_node)
        set_node_visible(ct_node)

    
def wait_for_transforms():
    transforms = ['StylusToRas', 'StylusToReference', 'SureTrack2ToRas']

    for transform in transforms:
        if does_node_exist_as_a_transform(transform):
            return False
    
    return True

def create_models():
    stylus = create_needle_model("StylusModel", 100, 1, 0.1)
    probe = create_needle_model("ProbeModel", 100, 0.5, 0.2)

def prepare_pivot_cal():
    
    tf_tip2suretrack = create_linear_transform_node("Tip2SureTrack")
    tf_suretrack2ras = slicer.mrmlScene.GetFirstNodeByName("SureTrack2ToRas")

    set_pivot_transforms(tf_suretrack2ras, tf_tip2suretrack)
    
    remove_unused_widgets_from_pivot_calibration()

def set_transform_hierarchy():
    scene = slicer.mrmlScene

    tf_tip2suretrack = scene.GetFirstNodeByName("Tip2SureTrack")
    tf_suretrack2ras = scene.GetFirstNodeByName("SureTrack2ToRas")
    tf_stylus2ras = scene.GetFirstNodeByName("StylusToRas")

    stylus = scene.GetFirstNodeByName("StylusModel")
    probe = scene.GetFirstNodeByName("ProbeModel")

    set_parent_of_transform_hierarchy_node(stylus, tf_stylus2ras)
    set_parent_of_transform_hierarchy_node(probe, tf_tip2suretrack)
    set_parent_of_transform_hierarchy_node(tf_tip2suretrack, tf_suretrack2ras)
