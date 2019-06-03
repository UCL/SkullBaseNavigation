__all__ = ['BaseConfig', 'Config']

import os


class BaseConfig(object):
    """Base configuration settings for the skullbasenavigation project"""

    # PLUS settings
    PLUS_HOST = 'locahost'
    PLUS_PORT = 18944
    PATH_TO_PLUS_SETTINGS = 'PLUS_settings'
    PLUS_CONFIG_FILE = 'PlusDeviceSet_Server_StealthLinkTracker_pyIGTLink.xml'

    # pyIGTLink settings
    PYIGTLINK_TCP_IP = '128.16.0.3'
    PYIGTLINK_TCP_PORT = 7915
    PYIGTLINK_TIMEOUT = 5
    PYIGTLINK_FPS = 25

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
