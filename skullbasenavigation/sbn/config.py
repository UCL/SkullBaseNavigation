"""Configuration parameters for the Slicelet and workflow."""

__all__ = ['BaseConfig', 'Config']


class BaseConfig:
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
    STYLUS_TO_REFERENCE_TF = 'StylusToReference'

    # US
    US_TO_RAS_TF = 'USToRas'
    US_TO_US_TIP_TF = 'USTipToUS'

    # CUSA
    #CUSA_TO_RAS_TF = 'CUSAToRas'

    # Neurostim probe
    NEUROSTIM_TO_RAS_TF = 'StimToRas'
    NEUROSTIM_TIP_TO_NEUROSTIM_TF = 'StimTipToStim'
    NEUROSTIM_TIP_TO_RAS = 'StimTipToRas'

    REFERENCETORAS_TF = 'ReferenceToRas'

    # Image names
    CT_IMG = 'SLD-001'
    US_IMG = 'Image_USTip'
    PROBE_IMG = 'BK_Probe'

    # Volume names
    SCOUTSCAN_VOL = 'ScoutScan'
    LIVERECONSTRUCTION_VOL = 'liveReconstruction'

    # Model names
    STYLUS_MOD = 'StylusModel'
    PROBE_MOD = 'ProbeModel'
    #CUSA_MOD = 'CusaModel'
    NEUROSTIM_MOD = 'NeurostimModel'

    # Output directories
    TF_OUTPUT_DIR = 'outputs/transforms/'
    SCENE_OUTPUT_DIR = 'outputs/scenes/'

Config = BaseConfig
