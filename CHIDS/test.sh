#!/bin/bash  

model_dir="/root/AnomalyDetection/CHIDS/DVSA-model"
test_normal_dir="/root/AnomalyDetection/datasets/DVSAC/dvsa-merge-benign-test"
test_malicious_dir=$1

start_time=$(date +%s)
 
python run.py evaluate \
  --ss "$model_dir/seen_syscalls.pkl" \
  --sa "$model_dir/seen_args.pkl" \
  --fm "$model_dir/max_freq.pkl" \
  --tm "$model_dir/model.h5" \
  --tl "$model_dir/thresh_list.pkl" \
  --ns "$test_normal_dir" \
  --ms "$test_malicious_dir"

end_time=$(date +%s)
execution_time=$((end_time - start_time))
execution_time_formatted=$(printf '%02d:%02d:%02d\n' $((execution_time/3600)) $((execution_time%3600/60)) $((execution_time%60)))
echo "Execution time: $execution_time_formatted"
