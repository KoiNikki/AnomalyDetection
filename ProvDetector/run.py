import os  
import numpy as np  
import multiprocessing  
import argparse  
from representationExtraction import *  
from graphBuilding import graphBuilding  
from Graph import *  
from embedding import *  
from anomalyDetection import *  
from parser import *  
from functools import partial  
import time  

G = []  

def set_para(_T, _K, _t):  
    global T, K, THRESHOLD  
    T = _T  
    K = _K  
    THRESHOLD = _t  

set_para(150, 25, 2)  

def detect(train_data: str, test_data: str):  
    train_file_name_list = os.listdir(train_data)  
    train_path_list = [os.path.join(train_data, i) for i in train_file_name_list]  
    test_file_name_list = os.listdir(test_data)  
    test_path_list = [os.path.join(test_data, i) for i in test_file_name_list]  

    G = graphBuilding(train_path_list + test_path_list)  # 构建数据源图  
    extraction(G, T)  # 提取所有图中边的表示数据  

    doc_ans_train = []  
    doc_ans_test = []  
    for i in range(len(G)):  
        if i >= len(train_path_list):  
            break  
        doc_ans_train += work(G[i], K)  

    for i in range(len(G)):  
        if i < len(train_path_list):  
            continue  
        doc_ans_test += work(G[i], K)  

    train_vec, vec_ans = embedding(doc_ans_train, doc_ans_test, K)  # 路径特征嵌入  

    predict_ans = LOF(train_vec, vec_ans, doc_ans_train, doc_ans_test)  # 异常检测  

    alert = []  
    test_file_name_list_len = len(test_file_name_list)  
    for index in range(test_file_name_list_len):  
        detection = predict_ans[index * K: (index + 1) * K]  
        if np.count_nonzero((detection == -1)) > THRESHOLD:  
            alert.append(test_file_name_list[index].split('.')[0])  
    return alert  

def run(train_data, test_data_normal, test_data_malicious):  
    count_ori_attack = len(os.listdir(test_data_malicious))  
    count_ori_normal = len(os.listdir(test_data_normal))  
    count_all = 0  
    count_attack = 0  

    test_data_list = [test_data_normal, test_data_malicious]  
    processes = []  
    count_attack_local = multiprocessing.Value('i', 0)  
    count_all_local = multiprocessing.Value('i', 0)  

    func = partial(process_data, count_attack=count_attack_local, count_all=count_all_local, train_data=train_data)  

    for test_data in test_data_list:  
        p = multiprocessing.Process(target=func, args=(test_data,))  
        processes.append(p)  
        p.start()  

    for p in processes:  
        p.join()  

    recall = count_attack_local.value / count_ori_attack if count_ori_attack != 0 else 0  
    precision = count_attack_local.value / count_all if count_all != 0 else 0  
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0  
    print('precision:', precision, ' recall:', recall, ' f1_score:', f1_score)  

def process_data(test_data, count_attack, count_all, train_data):  
    test_result = detect(train_data, test_data)  
    local_attack = len(test_result)  
    local_all = len(os.listdir(test_data))  
    
    with count_attack.get_lock():  
        count_attack.value += local_attack  
    with count_all.get_lock():  
        count_all.value += local_all  

if __name__ == "__main__":  
    multiprocessing.set_start_method('spawn')  

    parser = argparse.ArgumentParser(description="Run provdetector.")  
    parser.add_argument('--train_data', type=str, required=True, help='Path to the training data directory')  
    parser.add_argument('--test_data_normal', type=str, required=True, help='Path to the normal test data directory')  
    parser.add_argument('--test_data_malicious', type=str, required=True, help='Path to the malicious test data directory')  

    args = parser.parse_args()  

    print(T, K, THRESHOLD)  
    
    start_time = time.time()  
    run(args.train_data, args.test_data_normal, args.test_data_malicious)  
    end_time = time.time()  
    elapsed_time = end_time - start_time  
    print(elapsed_time)