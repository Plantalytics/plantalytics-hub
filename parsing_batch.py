import json

with open("output.txt", 'r') as readIn:
  while True:
#Skipping junk
    c = readIn.read(1)
    if not c:
	break
    readIn.read(31)
#Read the json string
    json_string = readIn.readline()
    parsed_json = json.loads(json_string)

#Grab that data
    data = (parsed_json['data'])
    timestamp = (parsed_json['timestamp'])

    print(data)
    print(timestamp + '\n')
    readIn.readline()
