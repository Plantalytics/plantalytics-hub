# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing, 
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley.
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com

import ConfigParser
import json
import requests
import subprocess
import time


# Read values from
def load_config():
    config = ConfigParser.RawConfigParser()
    config.read('hub_secret.config')

    # Load hub data
    global HUB_ID
    HUB_ID = int(config.get('Hub Data', 'hub_id'))
    global VINE_ID
    VINE_ID = int(config.get('Hub Data', 'vine_id'))
    global PUBLIC_KEY
    PUBLIC_KEY = str(config.get('Hub Data', 'public_key'))
    global IN_FILE_NAME
    IN_FILE_NAME = config.get('Hub Data', 'stream')
    global OUT_FILE_NAME
    OUT_FILE_NAME = config.get('Hub Data', 'dump')

    # Load connection values
    global URL
    URL = (config.get('Connection Values', 'protocol') + config.get('Connection Values', 'ip_address')
           + ':' + config.get('Connection Values', 'port') + '/' + config.get('Connection Values', 'endpoint'))

    # Load settings
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


def copy_lines():
    # Open data stream file, then read & copy all lines to a new file
    input_file = open(IN_FILE_NAME, "r+")
    content = input_file.read()
    input_file.close()
    output_file = open(OUT_FILE_NAME, "w+")
    output_file.write(content)
    output_file.close()


def count_lines():
    # Open the new file and count the number of lines acquired from the data stream file
    output_file = open(OUT_FILE_NAME, "r")
    line_count = sum(1 for line in output_file)
    output_file.close()

    # If no data was gathered, do nothing
    if line_count == 0:
        exit(0)

    return line_count


def delete_lines(line_count):
    # Delete lines read from stream file using the number of lines counted above
    command = "sed --in-place " + "1," + str(line_count) + "d " + IN_FILE_NAME
    subprocess.call(command, shell=True)


def create_json(header, fileIn):
    # Parse data
    object = header
    object['hub_data'] = []
    dict = {}
    node_num = 1
    with open(fileIn, 'r') as readIn:
        while True:
	    #Skipping junk
	    get_string = readIn.readline()
	    if not get_string:
		break
	    json_string = get_string.partition(" ")[2]

            # Read the json string
            #json_string = readIn.readline()
            timestamp = readIn.readline()
            # Remove the Endline char
            timestamp = timestamp[:-1]
            parsed_json = json.loads(json_string)

            # Grab that data
            # Extracting data might not be in json format, if corrupted dont do anything with it
            try:
                encode_data = (parsed_json['data'])
                data = encode_data.decode('base64')
                data_json = json.loads(data)
		#Uncomment line below to check data_json
		#print data_json
                
                node_data = {}
                node_data['node_id'] = int(data_json['NODEID'])
		node_data['temperature'] = float(data_json['T'])
                node_data['humidity'] = float(data_json['H'])
                node_data['leafwetness'] = float(data_json['L'])
                node_data['data_sent'] = int(float(timestamp))
		dict[node_data['node_id']] = node_data		
		#Uncomment line below to check dict
		#print dict
            except ValueError:
                # If enter this block, means formatting of json data failed
                # Don't do anything with that data
		print "FAILED"
                pass
            # Get ready for next data
            readIn.readline()
    for key, value in dict.iteritems():
	object['hub_data'].append(dict[key])
    object['batch_sent'] = int(time.time() * 1000)
    return object


def send_data(batch):
    # Send data to Cassandra
    while requests.put(URL, data=json.dumps(batch)).status_code != 200:
        pass


def main():
    load_config()
    copy_lines()
    delete_lines(count_lines())
    #print (create_json(get_header(), OUT_FILE_NAME))
    send_data(create_json(get_header(), OUT_FILE_NAME))

if __name__ == "__main__":
    main()
