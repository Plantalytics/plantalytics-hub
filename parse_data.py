import json
import requests

from subprocess import call

IN_FILE_NAME = "data_stream.txt"
OUT_FILE_NAME = "data_dump.txt"

BACKEND_IP_ADDRESS = "http://104.197.35.232:8000/"
ENV_VAR_ENDPOINT = "hub_data"

# Open data stream file, then read & copy all lines to a new file
input_file = open(IN_FILE_NAME, "r+")
content = input_file.read()
input_file.close()
output_file = open(OUT_FILE_NAME, "w+")
output_file.write(content)
output_file.close()

# Open the new file and count the number of lines acquired from the data stream file
output_file = open(OUT_FILE_NAME, "r")
line_count = sum(1 for line in output_file)

# If no data was gathered, do nothing
if line_count == 0:
    exit(0)

# Delete lines read from stream file using the number of lines counted above
command = "sed --in-place " + "1," + str(line_count) + "d " + IN_FILE_NAME
call(command, shell=True)

# Parse data (add later)


# Send data to Cassandra
while requests.put(BACKEND_IP_ADDRESS, data).status_code != 200:
    pass
