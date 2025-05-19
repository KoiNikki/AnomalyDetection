#!/bin/bash

MALICIOUS_BASE="/root/AnomalyDetection/datasets/CB-DS"
MALICIOUS_NAME=(CVE-2016-9962  CVE-2019-5736  CVE-2022-0492  M-MKNOD  M-NET  M_SOCKET  M-SYS_ADMIN  M-SYS_MOD  M_UHELPER)

for name in "${MALICIOUS_NAME[@]}"; do
    TEST_MALICIOUS_DIR="${MALICIOUS_BASE}/${name}"
    bash run.sh "${TEST_MALICIOUS_DIR}"
    echo "Finished processing ${name}." >> "cbds_result.txt"
    echo "----------------------------------------" >> "cbds_result.txt"
done