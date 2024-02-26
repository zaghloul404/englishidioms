#!/bin/bash

# Loop to run the Python script 19 times
for i in {1..19}
do
    python M_validate.py  # Run the Python script
    sleep 900  # Sleep for 15 minutes (900 seconds)
done
