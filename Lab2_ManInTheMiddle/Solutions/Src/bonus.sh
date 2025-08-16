while true; do
        sudo raw_packet eth1 02:42:0a:0a:28:02 0x0806 alice_bonus.bin
        sudo raw_packet eth1 02:42:0a:0a:28:03 0x0806 bob_bonus.bin
        sleep 1
done