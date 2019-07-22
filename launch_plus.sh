plus_servers=$(ps aux | grep -ic plus)
if [[ $plus_servers != 0 ]]; then
    echo "Killing $plus_servers PLUS servers"
    kill -9 $(ps aux | grep -i plus | awk '{print $1}' )
fi
/c/Users/SBN/PlusApp-2.6.0.20190221-StealthLink-Win32/bin/PlusServer.exe --config-file="/c/Users/SBN/Code/skullbasenavigation/PLUS_settings/PlusDeviceSet_Server_StealthLinkTracker_pyIGTLink.xml" --verbose=4
$SHELL