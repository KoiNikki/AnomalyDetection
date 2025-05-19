#!/bin/bash

malicious_base_dir="/root/AnomalyDetection/datasets/HRC"
malicious_name=(hr-merge-attack-dos  hr-merge-attack-less  hr-merge-attack-warm1  hr-merge-attack-warm2)

for name in "${malicious_name[@]}"; do
    test_malicious_dir="${malicious_base_dir}/${name}"
    bash test.sh "${test_malicious_dir}" >> "hr_result.txt" 2>&1
    echo "Finished processing ${name}." >> "hr_result.txt"
    echo "----------------------------------------" >> "hr_result.txt"
done
echo "All tests completed successfully."