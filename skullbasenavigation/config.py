__all__ = ['BaseConfig', 'Config']

import os


class BaseConfig(object):
    """Base configuration settings for the skullbasenavigation project"""

    # PLUS settings
    PLUS_HOST = 'localhost'
    PLUS_PORT = 18944
    PATH_TO_PLUS_SETTINGS = 'PLUS_settings'
    PLUS_CONFIG_FILE = 'PlusDeviceSet_Server_StealthLinkTracker_pyIGTLink.xml'
    PLUS_EXEC_PATH = ''

    # pyIGTLink settings for BK5000
    BK_TCP_IP = '128.16.0.3'
    BK_TCP_PORT = 7915
    BK_TIMEOUT = 5
    BK_FPS = 25

    # IGTLink connector settings
    IGTLINK_CONNECTOR_NAME = 'OpenIGT'

    # Transform names
    STYLUSTOREFERENCE_TF = 'StylusToReference'
    SURETRACK2TORAS_TF = 'SureTrack2ToRas'
    SURETRACK2TIPTOSURETRACK2_TF = 'SureTrack2TipToSureTrack2'
    REFERENCETORAS_TF = 'ReferenceToRas'

    # Image names
    CT_IMG = 'SLD-001'
    US_IMG = 'Image_SureTrack2Tip'
    PROBE_IMG = 'BK_Probe'

    # Volume names
    SCOUTSCAN_VOL = 'ScoutScan'
    LIVERECONSTRUCTION_VOL = 'liveReconstruction'

    # Model names
    STYLUS_MOD = 'StylusModel'
    PROBE_MOD = 'ProbeModel'

    # Output directory
    OUTPUT_DIR = 'name'

Config = BaseConfig
