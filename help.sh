#!/bin/bash  

INPUT_DIR="/home/yichi/Ayane/AnomalyDetection/Data/CVE-2016-9962_"  
OUTPUT_DIR="/home/yichi/Ayane/AnomalyDetection/Data/CVE-2016-9962"  

# 创建输出文件夹（如果不存在）  
mkdir -p "$OUTPUT_DIR"  

for scap_file in "$INPUT_DIR"/*.scap; do  
    # 获取文件名（不含扩展名）  
    filename=$(basename -- "$scap_file")  
    filename="${filename%.*}"  

    # 输出文件路径  
    output_file="$OUTPUT_DIR/$filename.log"  

    # 使用 sysdig 读取 scap 文件并输出到 log 文件  
    sysdig -r "$scap_file" > "$output_file"  
    echo "Processed $scap_file to $output_file"  
done