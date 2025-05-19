#!/bin/bash

base_dir="datasets/CB-DS-scap"
output_dir="datasets/CB-DS"

for scene_name_dir in "$base_dir"/*/; do
  scene_name=$(basename "$scene_name_dir")

  for scap_file in "$scene_name_dir"/*.scap; do
    [ -e "$scap_file" ] || continue

    filename=$(basename "$scap_file" .scap)
    log_dir="$output_dir/$scene_name"
    log_file="$log_dir/$filename.log"

    echo "Processing $scap_file -> $log_file"

    mkdir -p "$log_dir"
    sysdig -r "$scap_file" > "$log_file"

    if [ $? -ne 0 ]; then
      echo "Error processing $scap_file" >&2
    fi
  done
done