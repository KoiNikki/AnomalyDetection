#!/bin/bash  

# Define the paths to the data directories  
TRAIN_DATA="/home/yichi/Ayane/AnomalyDetection/Data/train"  
TEST_DATA_NORMAL="/home/yichi/Ayane/AnomalyDetection/Data/test_normal"  
TEST_DATA_MALICIOUS="/home/yichi/Ayane/AnomalyDetection/Data/test_malicious"

# Run the Python script with the defined arguments  
python3.9 run.py --train_data "$TRAIN_DATA" --test_data_normal "$TEST_DATA_NORMAL" --test_data_malicious "$TEST_DATA_MALICIOUS"
