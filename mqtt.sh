#! /bin/bash

mosquitto_sub -t lora/+/+ -v > output.txt
