#! /bin/bash

mosquitto_sub -t lora/+/+ -v > data_stream.txt
