import json
import time
import ConfigParser
import requests

# Read values from 
def load_config():
    config = ConfigParser.RawConfigParser()
    config.read('hub_secret.config')
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

def create_json(header, fileIn):
  object = header
  object['hub_data'] = []

  with open(fileIn, 'r') as readIn:
    while True:
      #Skipping junk
      c = readIn.read(1)
      if not c:
	  break
      readIn.read(31)
      #Read the json string
      json_string = readIn.readline()
      timestamp = readIn.readline()
      #Remove the Endline char
      timestamp = timestamp[:-1]
      parsed_json = json.loads(json_string)

      #Grab that data
      #Extracting data might not be in json format, if corrupted dont do anything with it
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
        #If enter this block, means formatting of json data failed
        #Don't do anything with that data
        pass
      #Get ready for next data
      readIn.readline()
  object['batch_sent'] = int(time.time()*1000)
#  print object
  return object


def main():
  load_config()
  header = get_header()
  batch = create_json(header, "output.txt")
  print(batch)
  #r = requests.post(URL, data=json.dumps(batch))
  #Send data to Cassandra
  #while requests.put(URL, data=json.dumps(batch)).status_code != 200:
  #  pass
  r = requests.post(URL, data=json.dumps(batch))
  print(r.status_code)


if __name__ == "__main__":
    main()