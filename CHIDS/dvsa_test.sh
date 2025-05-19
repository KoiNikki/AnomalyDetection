#!/bin/bash

malicious_base_dir="/root/AnomalyDetection/datasets/DVSAC"
malicious_name=(dvsa-merge-attack-broken-access  dvsa-merge-attack-event-injection  dvsa-merge-attack-over-priviledge)

for name in "${malicious_name[@]}"; do
    test_malicious_dir="${malicious_base_dir}/${name}"
    bash test.sh "${test_malicious_dir}" >> "dvsa_result.txt" 2>&1
    echo "Finished processing ${name}." >> "dvsa_result.txt"
    echo "----------------------------------------" >> "dvsa_result.txt"
done
echo "All tests completed successfully."