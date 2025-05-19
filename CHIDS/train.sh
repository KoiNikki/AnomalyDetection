#!/bin/bash  

train_dir="/root/AnomalyDetection/datasets/HRC/hr-merge-benign-train"
output_dir="HR-model"

start_time=$(date +%s)

python run.py baseline \
  --td $train_dir \
  --od $output_dir

end_time=$(date +%s)
execution_time=$((end_time - start_time))
execution_time_formatted=$(printf '%02d:%02d:%02d\n' $((execution_time/3600)) $((execution_time%3600/60)) $((execution_time%60)))
echo "Execution time: $execution_time_formatted"
