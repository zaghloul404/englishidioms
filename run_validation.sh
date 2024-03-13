#!/bin/bash

# macbook air struggles to go through the 18395 entries in one go, so i broke down the task into
# 19 smaller pieces in M_validate. this scripts executes M_validate 19 times with 10 minutes
# break between each iteration to allow the computer to cool down.

# Loop to run the Python script 19 times
for i in {1..19}
do
    python M_validate.py  # Run the Python script
    sleep 600  # Sleep for 10 minutess
done
