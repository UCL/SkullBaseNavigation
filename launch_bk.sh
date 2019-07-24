igtlink_servers=$(ps aux | grep -ic sksurgerybk)
if [[ $igtlink_servers != 0 ]]; then
    echo "Killing $igtlink_servers pyIGTLink servers"
    kill -9 $(ps aux | grep -i sksurgerybk | awk '{print $1}' )
fi
sksurgerybk 1
$SHELL