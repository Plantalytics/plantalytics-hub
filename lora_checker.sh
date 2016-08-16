#!/bin/sh

pgrep lora_client.py || ( ./lora_client.py & )


