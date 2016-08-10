from subprocess import call

import configparser
import json
import requests
import time


# Read values from
def load_config():
    config = configparser.RawConfigParser()
    config.read('hub_secret.config')

    # Load hub data
    global HUB_ID
    HUB_ID = config.get('Hub Data', 'hub_id')
    global VINE_ID
    VINE_ID = config.get('Hub Data', 'vine_id')
    global PUBLIC_KEY
    PUBLIC_KEY = config.get('Hub Data', 'public_key')
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
    line_count = sum(1 for line in output_file)  # NEED TO CLOSE FILE HERE IF PARSER USES 'WITH' STATEMENT
    output_file.close()

    # If no data was gathered, do nothing
    if line_count == 0:
        exit(0)

    return line_count


def delete_lines(line_count):
    # Delete lines read from stream file using the number of lines counted above
    command = "sed --in-place " + "1," + str(line_count) + "d " + IN_FILE_NAME
    call(command, shell=True)


def create_json(header, fileIn):
    # Parse data
    object = header
    object['hub_data'] = []

    with open(fileIn, 'r') as readIn:
        while True:
            # Skipping junk
            c = readIn.read(1)
            if not c:
                break
            readIn.read(31)
            # Read the json string
            json_string = readIn.readline()
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

                node_data = {}
                node_data['node_id'] = (data_json['NODEID'])
                node_data['temperature'] = (data_json['T'])
                node_data['humidity'] = (data_json['H'])
                node_data['leafwetness'] = (data_json['L'])
                node_data['data_sent'] = timestamp
                #        print(node_data)
                object['hub_data'].append(node_data)
            except ValueError:
                # If enter this block, means formatting of json data failed
                # Don't do anything with that data
                pass
            # Get ready for next data
            readIn.readline()

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
    send_data(create_json(get_header(), OUT_FILE_NAME))
    # print(batch)
    # r = requests.post(URL, data=json.dumps(batch))

if __name__ == "__main__":
    main()
