#!/bin/bash

src_dir="datasets/CB-DS/NORMAL"
train_dir="datasets/CB-DS/TRAIN"
test_dir="datasets/CB-DS/TEST"

mkdir -p "$train_dir"
mkdir -p "$test_dir"

rm -rf "$train_dir"/*
rm -rf "$test_dir"/*

# 获取所有 .log 文件，随机排序
all_files=($(ls "$src_dir"/*.log | shuf))
total=${#all_files[@]}

# 计算 X% 的文件数量
subset_count=$(( total * 50 / 100 ))

# 获取 X% 子集文件
subset_files=("${all_files[@]:0:subset_count}")

# 计算子集中的80%数量
train_count=$(( subset_count * 8 / 10 ))

# 复制8成到TRAIN，2成到TEST
for i in "${!subset_files[@]}"; do
  if (( i < train_count )); then
    cp "${subset_files[i]}" "$train_dir/"
  else
    cp "${subset_files[i]}" "$test_dir/"
  fi
done

