'''
@Author: Dong Yi
@Date: 2020.10.13
@Description: 新的BRWSP，这是对原本的BRWSP对数据结构
重新进行整理，主要处理问题是当前节点的下一个节点的可能性好几个都是
相同的大小，意味着当前节点的下一步有许多可能性，这个时候就要利用传统
的BFS 和 DFS来进行遍历，寻找路径

2021.3.9 在原始的5折基础上把每一折拆分分别运行
'''

import math
import random
import h5py
import numpy as np
import sortscore
import matplotlib.pyplot as plt
from MakeSimilarityMatrix import MakeSimilarityMatrix


def CS(relmatrix, circ_gipsim_matrix):

    return  circ_gipsim_matrix

def DS(relmatrix, dis_gipsim_matrix):

    return dis_gipsim_matrix

# 计算当前节点邻居节点的可能性的大小
def compute_neighbor_prop(current_neighborhood_list, prev_neighborhood_list, current_node, prev_node, NMH, temp_path):

    prop_list = []
    for i in range(len(current_neighborhood_list)):
        x_node = current_neighborhood_list[i]
        # 首先判断参数
        if (x_node in current_neighborhood_list) and (x_node in prev_neighborhood_list):
            pesai = 0.12 # q为0.12
        else:
            pesai = 1 - 0.12
        if (x_node in current_neighborhood_list) and (x_node not in temp_path):
            sum_NMH = 0
            # 这个地方是把邻居节点current_neighborhood_list 中的节点的NMH中的值都加上
            for j in range(len(current_neighborhood_list)):
                sum_NMH += NMH[current_node, current_neighborhood_list[j]]
            propablity = (pesai * NMH[current_node, x_node]) / sum_NMH
            prop_list.append(propablity)
        else:
            prop_list.append(0)

    return prop_list


# 找到当前节点的邻居节点是哪些
def find_neighborhood(current_node, H_matrix):

    # Hmatrix中current_node这一横行都是当前节点的邻居节点
    neighborhood_array = np.where(H_matrix[current_node,:]!=0) # 从长度是622该节点的向量里寻找不为0的下标
    neighborhood_list = []
    for i in range(len(neighborhood_array[0])):
        neighborhood_list.append(neighborhood_array[0][i])

    return neighborhood_list

def find_max_prop(prop_list):
    maxindex_list = []
    max_of_prop = max(prop_list)
    for i in range(len(prop_list)):
        if max_of_prop == prop_list[i]:
            maxindex_list.append(i)

    return maxindex_list


def find_nextnode_list(current_node, prev_node, path_length, temp_path, H_matrix):
    current_node_neighborlist = []
    # 判断这个路径长度
    if path_length==0 : # 代表这个结点是第一个节点是论文中k=1的情况
        current_neighborhood_list = find_neighborhood(current_node, H_matrix)
        next_node = current_neighborhood_list[-1]
        current_node_neighborlist.append(next_node)
    else: # 代表这个节点不是第一个节点
        # 去寻找当前节点和前一个节点的邻接节点list
        current_neighborhood_list = find_neighborhood(current_node, H_matrix)
        prev_neighborhood_list = find_neighborhood(prev_node, H_matrix)
        prop_list = compute_neighbor_prop(current_neighborhood_list, prev_neighborhood_list, current_node, prev_node, NMH, temp_path)
        # 这个prop_list可能最大值有多个把他们全部找出来
        max_prop_index = find_max_prop(prop_list)
        for i in range(len(max_prop_index)):
            current_node_neighborlist.append(current_neighborhood_list[max_prop_index[i]])

    return current_node_neighborlist


# 注意这个函数是非常重要的函数，就是在这里进行BFS和DFS的结合
def find_path(start, destination, L, H_matrix, NMH, maxiter):
    # 定义搜集起始节点到终点的所有路径
    total_path_list = []
    for i in range(maxiter):
        current_node = start
        prev_node = start
        temp_path = []
        queue = []
        seen_node = set()
        path_length = -1

        queue.append(current_node)
        seen_node.add(current_node)
        while len(queue)>0 and path_length < L:
            # 开始遍历队列弹出第一个节点
            prev_node = current_node
            current_node = queue.pop(0)
            temp_path.append(current_node)
            path_length += 1
            if current_node == destination:
                break;
            # 找到当前这个节点的邻居节点
            next_node_list = find_nextnode_list(current_node, prev_node, path_length, temp_path, H_matrix)
            # 将当前邻居结点随机选择一个（这是为什么要重复那么多次的原因）
            ran_current_node_list = random.sample(next_node_list, 1)
            for w in ran_current_node_list:
                if w not in seen_node:
                    queue.append(w)
                    seen_node.add(w)
                else: # 如果选中的这个节点出现在seen_node,即之前出现过，则重新选择一遍，避免环路出现
                    ran_current_node_list = random.sample(next_node_list, 1)
        if temp_path[-1] != destination:
            continue
        else:
            total_path_list.append(temp_path)
    # 对total_path_list去重
    final_path_list = []
    for item in total_path_list:
        if item not in final_path_list:
            final_path_list.append(item)

    return final_path_list


# 从这里开始预测从起点i 到 终点 j的预测值
def predict_sore(start, destination, L, H_matrix, NMH, maxiter):

    total_path_list = find_path(start, destination, L, H_matrix, NMH, maxiter)
    score_list = []
    score_sum = 1
    for i in range(len(total_path_list)):
        for j in range(len(total_path_list[i])):
            if j != len(total_path_list[i])-1:
                score_sum = score_sum * NMH[total_path_list[i][j], total_path_list[i][j+1]]
        # 要把这一条路径score_sum求次幂,其中的1是alpha=1
        score_sum = score_sum**(1*(len(total_path_list[i])-1))
        score_list.append(score_sum)
    score_array = np.array(score_list)
    predictscore = np.sum(score_array)

    return predictscore


if __name__ == '__main__':

    # 定义后面要用的超参数
    fold = 1
    L = 3  # 路径长度
    maxiter = 10
    # 读取关系数据
    # with h5py.File('./Data/disease-circRNA.h5', 'r') as hf:
    #     circrna_disease_matrix = hf['infor'][:]

    # with h5py.File('./Data/circRNA_cancer/circRNA_cancer.h5', 'r') as hf:
    #     circrna_disease_matrix = hf['infor'][:]

    # with h5py.File('./Data/circRNA_disease_from_circRNADisease/association.h5', 'r') as hf:
    #     circrna_disease_matrix = hf['infor'][:]

    with h5py.File('../../Data/circ2Traits/circRNA_disease.h5','r') as hf:
        circrna_disease_matrix = hf['infor'][:]

    # 划分训练集为五份为后面五折实验做准备
    index_tuple = (np.where(circrna_disease_matrix == 1))
    one_list = list(zip(index_tuple[0], index_tuple[1]))
    random.shuffle(one_list)

    # 要把这个circ2Traits存储下来
    with h5py.File('../../Data/circ2Traits/one_list.h5', 'w') as hf:
        hf['infor'] = one_list

    split = math.ceil(len(one_list) / 5)

    all_tpr = []
    all_fpr = []
    all_recall = []
    all_precision = []
    all_accuracy = []
    all_F1 = []


    test_index = one_list[(fold - 1) * split:(fold - 1)* split + split]
    new_circrna_disease_matrix = circrna_disease_matrix.copy()
    # 抹除已知关系
    for index in test_index:
        new_circrna_disease_matrix[index[0], index[1]] = 0
    roc_circrna_disease_matrix = new_circrna_disease_matrix + circrna_disease_matrix
    rel_matrix = new_circrna_disease_matrix

    # 计算相似高斯相似矩阵
    make_sim_matrix = MakeSimilarityMatrix(rel_matrix)
    circ_gipsim_matrix, dis_gipsim_matrix = make_sim_matrix.circsimmatrix, make_sim_matrix.dissimmatrix

    # 这里把高斯相似矩阵存一下，方便下次直接读取
    # with h5py.File('../../Data/circ2Traits/GIP_sim_matrix_from_circ2Traits.h5', 'w') as hf:
    #     hf['circ_gipsim_matrix'] = circ_gipsim_matrix
    #     hf['dis_gipsim_matrix'] = dis_gipsim_matrix

    with h5py.File('../../Data/circ2Traits/GIP_sim_matrix_from_circ2Traits.h5', 'r') as hf:
        circ_gipsim_matrix = hf['circ_gipsim_matrix'][:]
        dis_gipsim_matrix = hf['dis_gipsim_matrix'][:]

    # 原文中计算CS是使用circRNA的表达谱
    # 原文中计算DS是使用disease的语义相似性（基于DOSE包）
    CS_matrix = CS(rel_matrix, circ_gipsim_matrix)
    DS_matrix = DS(rel_matrix, dis_gipsim_matrix)

    # 构造异构矩阵H，这里因为没有其他附加数据H矩阵简化了中间行和中间列
    H_matrix = np.vstack((np.hstack((CS_matrix, rel_matrix)), np.hstack((rel_matrix.T, DS_matrix))))

    # 求H矩阵的度矩阵D
    D_matrix = np.zeros((H_matrix.shape[0], H_matrix.shape[1]))
    for i in range(H_matrix.shape[0]):
        row_sum = np.sum(H_matrix[i,:])
        D_matrix[i,i] = row_sum

    # 利用特征值和特征向量求出D矩阵的-1/2次方
    v, Q = np.linalg.eig(D_matrix)
    V = np.diag(v**(-0.5))
    D_half = Q * V * np.linalg.inv(Q)

    NMH = np.dot(D_half, H_matrix, D_half)

    # 开始预测
    prediction_matrix = np.zeros((rel_matrix.shape[0], rel_matrix.shape[1]))

    for i in range(prediction_matrix.shape[0]):
        for j in range(prediction_matrix.shape[1]):
            prediction = predict_sore(i, j+533, L, H_matrix, NMH, maxiter) # 因为关系矩阵在H矩阵上层右侧左边还有一个circRNA的关系矩阵关系矩阵大小为533*533
            prediction_matrix[i,j] = prediction

    aa = prediction_matrix.shape
    bb = roc_circrna_disease_matrix.shape
    zero_matrix = np.zeros((prediction_matrix.shape[0], prediction_matrix.shape[1]))
    print(prediction_matrix.shape)
    print(roc_circrna_disease_matrix.shape)

    score_matrix_temp = prediction_matrix.copy()
    score_matrix = score_matrix_temp + zero_matrix
    minvalue = np.min(score_matrix)
    score_matrix[np.where(roc_circrna_disease_matrix == 2)] = minvalue - 20
    sorted_circrna_disease_matrix, sorted_score_matrix = sortscore.sort_matrix(score_matrix,
                                                                                   roc_circrna_disease_matrix)

    tpr_list = []
    fpr_list = []
    recall_list = []
    precision_list = []
    accuracy_list = []
    F1_list = []
    for cutoff in range(sorted_circrna_disease_matrix.shape[0]):
        P_matrix = sorted_circrna_disease_matrix[0:cutoff + 1, :]
        N_matrix = sorted_circrna_disease_matrix[cutoff + 1:sorted_circrna_disease_matrix.shape[0] + 1, :]
        TP = np.sum(P_matrix == 1)
        FP = np.sum(P_matrix == 0)
        TN = np.sum(N_matrix == 0)
        FN = np.sum(N_matrix == 1)
        tpr = TP / (TP + FN)
        fpr = FP / (FP + TN)
        tpr_list.append(tpr)
        fpr_list.append(fpr)
        recall = TP / (TP + FN)
        precision = TP / (TP + FP)
        recall_list.append(recall)
        precision_list.append(precision)
        accuracy = (TN + TP) / (TN + TP + FN + FP)
        F1 = (2 * TP) / (2 * TP + FP + FN)
        F1_list.append(F1)
        accuracy_list.append(accuracy)
    all_tpr.append(tpr_list)
    all_fpr.append(fpr_list)
    all_recall.append(recall_list)
    all_precision.append(precision_list)
    all_accuracy.append(accuracy_list)
    all_F1.append(F1_list)

    tpr_arr = np.array(all_tpr)
    fpr_arr = np.array(all_fpr)
    recall_arr = np.array(all_recall)
    precision_arr = np.array(all_precision)
    accuracy_arr = np.array(all_accuracy)
    F1_arr = np.array(all_F1)

    # 用h5py数据形式将它存储下来
    with h5py.File('./BRWSP_5fold_result_fold1.h5', 'w') as hf:
        hf['tpr_arr'] = tpr_arr
        hf['fpr_arr'] = fpr_arr
        hf['recall_arr'] = recall_arr
        hf['precision_arr'] = precision_arr
        hf['accuracy_arr'] = accuracy_arr
        hf['F1_arr'] = F1_arr


