#!/bin/sh

pgrep mqtt.sh || ( ./mqtt.sh & )
