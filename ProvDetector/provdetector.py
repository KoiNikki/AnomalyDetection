import argparse
import os
import shutil

import numpy as np

from representationExtraction import *
from graphBuilding import graphBuilding
from Graph import *
from embedding import *
from anomalyDetection import *
from parser import *
import time
import multiprocessing
from functools import partial


G = []


def set_para(_T, _K, _t):
    global T, K, THRESHOLD
    T = _T
    K = _K
    THRESHOLD = _t


set_para(150, 25, 2)


def detect(train_data: str, test_data: str):
    """
    main scripts for provdetector
    Args:
        train_data (): train_graph path, should be like 'data/xxx'
        test_data (): test_graph path, should be like 'data/xxx'

    Returns:

    """
    # 设置论文中的时间窗口大小参数T、异常路径top数K、以及一张图中有多少路径判定为异常就告警

    # 输入格式转换，将原有图格式转换为流式的6元组边格式，放入所在目录data文件夹下同名目录

    # train_dataset = 'data/ProvDetector/' + train_data.split('data/')[1]
    # test_dataset = 'data/ProvDetector/' + test_data.split('data/')[1]
    #
    # folder_json_to_tuple(train_data, train_dataset)
    # folder_json_to_tuple(test_data, test_dataset)

    train_file_name_list = os.listdir(train_data)
    train_path_list = [os.path.join(train_data, i) for i in train_file_name_list]
    test_file_name_list = os.listdir(test_data)
    test_path_list = [os.path.join(test_data, i) for i in test_file_name_list]

    # print(train_path_list + test_path_list)
    G = graphBuilding(train_path_list + test_path_list)  # 构建数据源图
    extraction(G, T)  # 提取所有图中边的表示数据

    # print(train_path_list)
    # print(test_path_list)

    doc_ans_train = []
    doc_ans_test = []
    for i in range(len(G)):
        if i >= len(train_path_list):
            break
        # print(f"working on train {i}: {train_path_list[i]}")
        doc_ans_train += work(
            G[i], K
        )  # 对于指定的图，计算路径异常指数并找到排名前K条边;训练时需要多张图的话，可以分别对每张图G[i]执行此操作，将结果合并到一个doc_ans中即可

    for i in range(len(G)):
        if i < len(train_path_list):
            continue
        # print(f"working on test {i}: {test_path_list[i - len(train_path_list)]}")
        doc_ans_test += work(G[i], K)
    # print('work complete')

    train_vec, vec_ans = embedding(
        doc_ans_train, doc_ans_test, K
    )  # 路径特征嵌入，得到测试集中提取的每条路径各自的特征

    # exit(0)

    # print("predict")
    predict_ans = LOF(
        train_vec, vec_ans, doc_ans_train, doc_ans_test
    )  # 使用离群点检测算法得到每条路径的异常预测

    os.makedirs("result", exist_ok=True)
    with open(f'result/train_{THRESHOLD}_{train_data.split("/")[0]}.txt', "w") as f:
        for index, file_name in enumerate(train_file_name_list):
            doc = doc_ans_train[index * K : (index + 1) * K]
            for j in range(len(doc)):
                f.write(f"{file_name}\t{str(doc[j])}\n")

    alert = []
    with open(f'result/alert_{THRESHOLD}_{test_data.split("/")[0]}.txt', "w") as f:
        for index, file_name in enumerate(test_file_name_list):
            detection = predict_ans[index * K : (index + 1) * K]
            doc = doc_ans_test[index * K : (index + 1) * K]
            for j in range(len(detection)):
                f.write(
                    f"{file_name}\t{str(np.count_nonzero((detection == -1)))}\t{str(detection[j])}\t{str(doc[j])}\n"
                )
            if np.count_nonzero((detection == -1)) > THRESHOLD:
                alert.append(file_name.split(".")[0])
    return alert


def process_data(train_data, test_data):
    test_result = detect(train_data, test_data)
    return len(test_result)


def run(train_data, test_data_normal, test_data_malicious):
    count_ori_normal = len(os.listdir(test_data_normal))
    count_ori_attack = len(os.listdir(test_data_malicious))
    count_all = count_ori_attack + count_ori_normal

    FP = process_data(train_data, test_data_normal)
    TP = process_data(train_data, test_data_malicious)
    FN = count_ori_attack - TP
    TN = count_ori_attack - FP

    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    accuracy = (TP + TN) / count_all
    f1_score = (2 * precision * recall) / (precision + recall)

    print("precision:", precision, " recall:", recall, " f1_score:", f1_score, "accuracy:", accuracy)


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")

    parser = argparse.ArgumentParser(description="Run provdetector.")
    parser.add_argument(
        "--train_data",
        type=str,
        required=True,
        help="Path to the training data directory",
    )
    parser.add_argument(
        "--test_data_normal",
        type=str,
        required=True,
        help="Path to the normal test data directory",
    )
    parser.add_argument(
        "--test_data_malicious",
        type=str,
        required=True,
        help="Path to the malicious test data directory",
    )

    args = parser.parse_args()

    print(T, K, THRESHOLD)

    start_time = time.time()
    run(args.train_data, args.test_data_normal, args.test_data_malicious)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(elapsed_time)
