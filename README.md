# Plantalytics Conduit

Scripts to enable a MultiConnect Conduit to act as a hub for the Plantalytics system data collection nodes.

## What Each File does

1. lora_client.py is a python program that uses MQTT to subscrible to "lora/+/+". It will print the data it recieves and add a timestamp.
2. lora_checker.sh is a cron script to check if the lora_client.py is running.
3. parse_data.py takes data_stream.txt lines and moves them to data_dump.txt for parsing of data and preparing data to send to backend API. Here are the steps:
	1.  Load configs from secert config file. 
	2.  Copy lines from data_stream.txt to data_dump.txt.
	3.  Delete the successfully copied lines from the data_stream.txt.
	4.  Decrypt thte data, parse the data, check if it is readable, then add to dictionary.
	5.  Get batch ready for back-end.
	6.  Keep sending the batch until back-end recieves the batch.
4. data_generator.py is a test file. Testing if back-end can recieve static data batch. NOT NEEDED in final product.

## Setting up the Conduit

Setting up the Conduit is 9/10ths of the battle. The first step is to configure the network settings.

Then:
* Two opinions to set up Internet connection(Recommand opinon 2):
  1. Static(Add all lines into /etc/network/interfaces)
    * Modify `address 192.168.2.1` to fit your wanted static ip-address for the conduit
    * Modify `netmask 255.255.255.0` to match netmask of your rounter
    * Add `gateway: ###.###.#.##` the address needs to be your rounter ip-address
    * Add `dns-nameservers 8.8.8.8 8.8.4.4` to set DNS server
    * Add `post-up echo "nameserver 8.8.8.8" > /etc/resolv.conf`
    * Save and quit. In command line `ifdown eth0 && ifup eth0` to have changes take effect
    * Ping a site to test internet connection
  2. DHCP(Edit lines into /etc/network/interfaces)
    * Modity `iface eth0 inet static` into `iface eth0 inet dhcp`
    * Save and quit. In command line `ifdown eth0 && ifup eth0` to have changes take effect
    * Ping a site to test internet connection
    * Command `ifconfig` shows the address, netmask and other networking things of the conduit
* Set up LoRa(Assuming LoRa mCard is installed and LoRa antenna is attached.)
  * Execute commands:
    * `mkdir /var/config/lora`
    * `cp /opt/lora/lora-network-server.conf.sample /var/config/lora/lora-network-server.conf`
  * Edit the /var/config/lora/lora-network-server.conf and modify the settings as needed. But here is what we did:
    * Change "public": false to "public": true.
    * Comment out lines in "network". "name" and "passphrase".
    * Add lines "eui" and "key". Make sure they match the nodes eui and key:
	* `"eui": "XX:XX:XX:XX:XX:XX:XX:XX",` eui matches node's
	* `"key": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX"` key matches node's
  * Restart the network server by executing:
	* `/etc/init.d/lora-network-server restart`
  * To start the mosquitto client:
	* `mosquitto_sub -t lora/+/+ -v`
* Set up Python based on the instructions from [Multitech](http://www.multitech.net/developer/software/mlinux/mlinux-software-development/python/), execute the following commands:
  * `opkg update`
  * `opkg install python-pip`
  * `wget https://bootstrap.pypa.io/ez_setup.py --no-check-certificate`
  * `python ez_setup.py`
  * `pip install requests`
* Install Git:
  * `opkg install git`
* Clone repository
* Update the *** values in hub.config as appropriate.

After taking these steps, it is possible to download and run the softare needed to connect the node data to the database!

## Cron Daemon

The Cron Daemon is used to schedule scripts to run at select intervals.

* The 'mosquitto' script (which reads & saves data from the nodes) is started upon system boot and runs 
continuously:
  * '@reboot /home/root/plantalytics-hub/mqtt.sh > /dev/null'

* A checker is ran every five minutes to ensure the 'mosquitto' script is running as intended:
  * '*/5 * * * * /home/root/plantalytics-hub/mqtt_checker.sh > /dev/null'

* The Python parsing script which gathers the data retrieved from the 'lora_client.py' 
script, parses it into a JSON object, then sends it to the database (runs every five minutes):
  * '*/5 * * * * /home/root/plantalytics-hub/parse_data.py > /dev/null'

To create Cron jobs on a new Hub:
  * # crontab -e
  * add the lines above to the file, save & close
  * crontab should report success
  * add executable permissions to the relevant files, e.g.,
  * # chmod +x /home/root/plantalitics-hub/lora_client.py

## Use

data_generator.py generates random data for display on the Plantalytics dashboard. Every five minutes, a new sample is generated and uploaded to the server.

## License

Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing, Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley.

This project is licensed under the MIT License. Please see the file LICENSE in this distribution for license terms.
