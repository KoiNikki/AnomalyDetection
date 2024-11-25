#!/bin/bash  

# 源文件夹和目标文件夹  
SOURCE_DIR="/home/yichi/Ayane/AnomalyDetection/Data/PHP_CWE-434"  
DEST_DIR="/home/yichi/Ayane/AnomalyDetection/Data/test_malicious"  

# 要复制的文件数量  
NUM_FILES=99  

# 清理目标文件夹内的文件  
rm -rf "$DEST_DIR"/*  

# 随机选择文件并复制  
shuf -n $NUM_FILES -e "$SOURCE_DIR"/* | xargs -I {} cp {} "$DEST_DIR"