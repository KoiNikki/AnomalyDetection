#!/bin/bash  

model_dir=/home/yichi/Ayane/AnomalyDetection/CHIDS/output
test_normal_dir=/home/yichi/Ayane/AnomalyDetection/Data/test_normal
test_malicious_dir=/home/yichi/Ayane/AnomalyDetection/Data/test_malicious
 
python3.9 run.py evaluate \
  --ss "$model_dir/seen_syscalls.pkl" \
  --sa "$model_dir/seen_args.pkl" \
  --fm "$model_dir/max_freq.pkl" \
  --tm "$model_dir/model.h5" \
  --tl "$model_dir/thresh_list.pkl" \
  --ns "$test_normal_dir" \
  --ms "$test_malicious_dir"