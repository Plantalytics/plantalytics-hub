# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing, 
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley.
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com

import ConfigParser
import json
import random
import requests
import sys
import time

# Read values from 
def load_config():
    config = ConfigParser.RawConfigParser()
    config.read('hub.config')
    # Load hub data
    global HUB_ID 
    HUB_ID = config.get('Hub Data', 'hub_id')
    global VINE_ID
    VINE_ID = config.get('Hub Data', 'vine_id')
    global PUBLIC_KEY
    PUBLIC_KEY = config.get('Hub Data', 'public_key')
    # Load connection values
    global URL
    URL = ('http://' + config.get('Connection Values', 'ip_address')
        + ':' + config.get('Connection Values', 'port') + '/hub_data')
    #Load settings
    global INTERVAL
    INTERVAL = config.getint('Settings', 'interval')
    global CONN_TIMEOUT
    CONN_TIMEOUT = config.getint('Settings', 'connection_timeout')
    
def get_header():
    # Constructs the hub meta data portion of the JSON object.
    header = {}
    header['key'] = PUBLIC_KEY
    header['vine_id'] = VINE_ID
    header['hub_id'] = HUB_ID
    return header

def get_node_data(nodeId):
    # Constructs the node_data JSON objects for each node.
    node_data = {}
    node_data['node_id'] = nodeId
    # Temp range: 15-85 degrees F
    node_data['temperature'] = random.randint(15, 70)
    # Humidity range: 25-95%
    node_data['humidity'] = random.randint(25, 70)
    # Wetness range: 0-7000 k-Ohms
    node_data['leafwetness'] = random.randint(0, 70) 
    # Data timestamp
    node_data['data_sent'] = int(time.time()*1000)
    return node_data
    
def create_json(header, itemCount):
    object = header
    object['hub_data'] = []
    # For each node, create a data set and add it to the object.
    for n in range(0, itemCount):
        object['hub_data'].append(get_node_data(n))
    # Add the batch timestamp.
    object['batch_sent'] = int(time.time()*1000)
    print object
    return object

def bedtime():
    increment = 15
    total = INTERVAL/increment
    # Sleep for interval in 15 second increments
    for t in range(0, total):
        time.sleep(increment)
    
def main():    
    # Parse the first supplied argument as a positive integer. If this 
    #   succeeds, launch the loop with the speficied input.
    try:
        input = sys.argv[1]
        nodes = int(input)
        assert nodes > 0
    # Otherwise, run with a 21 node sample
    except:
        nodes = 21    
    # Load .cfg
    load_config()
    # Initialize JSON object with meta data
    header = get_header()
    # Loop until user interrupt
    i = 1
    while 1:
        print ('\nDataset no: ' + str(i) + '\n')
        i += 1
        # Generates CQL batch insertion string for each node
        batch = create_json(header, nodes)
        r = requests.put(URL, data=json.dumps(batch))
        bedtime()
    # If, for some reason, the loop exits, shutdown the connection.
    session.shutdown()
    
if __name__ == "__main__":
    main()
