__all__ = ['BaseConfig', 'Config']

import os


class BaseConfig(object):
    """Base configuration settings for the skullbasenavigation project"""

    # PLUS settings
    PLUS_HOST = 'locahost'
    PLUS_PORT = 18944
    PLUS_PATH = '/path/to/PLUS'

    # pyIGTLink settings
    PYIGTLINK_HOST = 123
    PYIGTLINK_PORT = 123

    # IGTLink connector settings
    IGTLINK_NAME = 'name'

    # Transform names
    STYLUSTOREFERENCE_TF = 'StylusToReference'
    SURETRACK2TORAS_TF = 'SureTrack2ToRas'
    SURETRACK2TIPTOSURETRACK2_TF = 'SureTrack2TipToSureTrack2'
    REFERENCETORAS_TF = 'ReferenceToRas'

    # Image names
    CT_IMG = 'CT_scan'
    US_IMG = 'Image_SureTrack2Tip'
    PROBE_IMG = 'BK_Probe'

    # Volume names
    SCOUTSCAN_VOL = 'ScoutScan'
    LIVERECONSTRUCTION_VOL = 'liveReconstruction'

    # Model names
    STYLUS_MOD = 'StylusModel'
    PROBE_MOD = 'ProbeModel'

    # Node IDs and classes
    SLICENODERED_ID = 'vtkMRMLSliceNodeRed'
    LINEARTRANSFORMNODE_CLS = 'vtkMRMLLinearTransformNode'

    # Output directory
    OUTPUT_DIR = 'name'

Config = BaseConfig
