# Plantalytics Conduit

Scripts to enable a MultiConnect Conduit to act as a hub for the Plantalytics system data collection nodes.

## Setup

Setting up the Conduit is 9/10ths of the battle. The first step is to configure the network settings.

Then:

* Set DNS server:
  * Add `dns-nameservers 8.8.8.8 8.8.4.4` to /etc/network/interfaces
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

## Use

data_generator.py generates random data for display on the Plantalytics dashboard. Every five minutes, a new sample is generated and uploaded to the server.

## License

Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing, Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley.

This project is licensed under the MIT License. Please see the file LICENSE in this distribution for license terms.
