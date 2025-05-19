#!/bin/bash

input_dir="/root/AnomalyDetection/datasets/DVSA/dvsa-merge-attack-over-priviledge/sysdig"
output_dir="/root/AnomalyDetection/datasets/DVSAC/dvsa-merge-attack-over-priviledge"

for log_file in "$input_dir"/*.log; do
    file_name=$(basename "$log_file")
    output_log_file="$output_dir/$file_name"
    python convert.py "$log_file" "$output_log_file"
done
