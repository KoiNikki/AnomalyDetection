#!/bin/bash

MALICIOUS_BASE="/root/AnomalyDetection/datasets/DVSAC"
MALICIOUS_NAME=(dvsa-merge-attack-broken-access  dvsa-merge-attack-event-injection  dvsa-merge-attack-over-priviledge)

for name in "${MALICIOUS_NAME[@]}"; do
    TEST_MALICIOUS_DIR="${MALICIOUS_BASE}/${name}"
    bash run.sh "${TEST_MALICIOUS_DIR}"
    echo "Finished processing ${name}." >> "dvsa_result.txt"
    echo "----------------------------------------" >> "dvsa_result.txt"
done