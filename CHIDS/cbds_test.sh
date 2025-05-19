#!/bin/bash

malicious_base_dir="/root/AnomalyDetection/datasets/CB-DS"
malicious_name=("CVE-2016-9962" "CVE-2019-5736" "CVE-2022-0492" "M_SOCKET" "M_UNHELPER" "M-MKNOD" "M-NET" "M-SYS_ADMIN" "M-SYS_MOD")

for name in "${malicious_name[@]}"; do
    test_malicious_dir="${malicious_base_dir}/${name}"
    bash test.sh "${test_malicious_dir}" >> "cbds_result.txt" 2>&1
    echo "Finished processing ${name}." >> "cbds_result.txt"
    echo "----------------------------------------" >> "cbds_result.txt"
done
echo "All tests completed successfully."