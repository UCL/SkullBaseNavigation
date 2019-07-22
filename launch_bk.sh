igtlink_servers=$(ps aux | grep -ic surgerybk)
if [[ $igtlink_servers != 0 ]]; then
    echo "Killing $igtlink_servers pyIGTLink servers"
    kill -9 $(ps aux | grep -i surgerybk | awk '{print $1}' )
fi
sksurgerybk 1
$SHELL