# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing, 
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley.
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com

import random
import sys
import time
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import ConfigParser

# Read values from 
def load_config():
    config = ConfigParser.RawConfigParser()
    config.read('hub.config')
    # Load connection values
    global USERNAME
    USERNAME = config.get('Connection Values', 'username')
    global PASSWORD
    PASSWORD = config.get('Connection Values', 'password')
    global IP_ADDRESS
    IP_ADDRESS = config.get('Connection Values', 'ip_address')
    global KEYSPACE
    KEYSPACE = config.get('Connection Values', 'keyspace')
    #Load settings
    global INTERVAL
    INTERVAL = config.getint('Settings', 'interval')
    global CONN_TIMEOUT
    CONN_TIMEOUT = config.getint('Settings', 'connection_timeout')

def get_conditions(vineId, hubId, nodeId):
    # Temp range: 15-85 degrees F
    temperature = random.randint(15, 70)
    # Humidity range: 25-95%
    humidity = random.randint(25, 70)
    # Wetness range: 0-7000 k-Ohms
    leafwetness = random.randint(0, 70) 
    # Datasent timestamp
    datasent = int(time.time()*1000)
    conditions = (vineId, hubId, nodeId, datasent, temperature,
                  humidity, leafwetness)
    return conditions
    
def generate_dataset(itemCount):
    dataset = []
    for n in range(0, itemCount):
        # For the purposes of demonstration, populate vine_id 1.
        v = 1
        # For the purposes of demonstration, each hub supports 3 nodes.
        h = int(n/3)
        dataset.append(get_conditions(v, h, n))
    return dataset

def create_batch(dataset):
    prologue = ('INSERT INTO ' + KEYSPACE + '.environmental_data ( vineid, '
                'hubid, nodeid, datasent, temperature, humidity, leafwetness, '
                'batchsent ) VALUES ( ')
    epilogue = str(int(time.time()*1000)) + ' );\n'
    batch = 'BEGIN BATCH\n'
    # For each set of conditions in the data set, create a query
    for conditions in dataset:
        query = prologue
        i = 0
        # Add each value in the conditions to the query
        for value in conditions:
            query += str(value) + ', '
        # Add epilogue to insert statement
        query += epilogue
        batch += query
    batch += 'APPLY BATCH;'
    print batch
    return batch

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
    # Initialize DB connection
    auth = PlainTextAuthProvider(username = USERNAME, password = PASSWORD)
    cluster = Cluster(contact_points = [IP_ADDRESS], auth_provider = auth, 
        control_connection_timeout = CONN_TIMEOUT, 
        connect_timeout = CONN_TIMEOUT)
    session = cluster.connect(KEYSPACE)
    # Loop until user interrupt
    i = 1
    while 1:
        print ('\n   Dataset no: ' + str(i))
        i += 1
        # Generates CQL batch insertion string for each node
        batch = create_batch(generate_dataset(nodes))
        # Push batch to server, execute statement
        try:     
            session.execute(batch)
        except Exception as oops:
            print ('EXCEPTION:\n   ' + str(oops))
        bedtime()
    # If, for some reason, the loop exits, shutdown the connection.
    session.shutdown()
    
if __name__ == "__main__":
    main()
