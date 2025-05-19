#!/bin/bash  

# Define the paths to the data directories  
TRAIN_DATA="/root/AnomalyDetection/datasets/HRC/hr-merge-benign-train"  
TEST_DATA_NORMAL="/root/AnomalyDetection/datasets/HRC/hr-merge-benign-test"  
TEST_DATA_MALICIOUS=$1


start_time=$(date +%s)

# Run the Python script with the defined arguments  
python run.py --train_data "$TRAIN_DATA" --test_data_normal "$TEST_DATA_NORMAL" --test_data_malicious "$TEST_DATA_MALICIOUS"

end_time=$(date +%s)
execution_time=$((end_time - start_time))
execution_time_formatted=$(printf '%02d:%02d:%02d\n' $((execution_time/3600)) $((execution_time%3600/60)) $((execution_time%60)))
echo "Execution time: $execution_time_formatted"