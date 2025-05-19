#!/bin/bash

MALICIOUS_BASE="/root/AnomalyDetection/datasets/HRC"
MALICIOUS_NAME=(hr-merge-attack-dos  hr-merge-attack-less  hr-merge-attack-warm1  hr-merge-attack-warm2)

for name in "${MALICIOUS_NAME[@]}"; do
    TEST_MALICIOUS_DIR="${MALICIOUS_BASE}/${name}"
    bash run.sh "${TEST_MALICIOUS_DIR}"
    echo "Finished processing ${name}." >> "hr_result.txt"
    echo "----------------------------------------" >> "hr_result.txt"
done