# 导入 csv 库
# 获取单method名称下max-pooling的API信息
import csv
import json
import re
from tqdm import tqdm
import pickle
from difflib import SequenceMatcher
import nltk
from nltk.translate import bleu
from nltk.translate.bleu_score import SmoothingFunction
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from collections import Counter

import pandas as pd

with open("./data/method_return.csv", mode="r", encoding="utf-8") as f1:
    # 基于打开的文件，创建csv.reader实例
    reader = csv.reader(f1)

    # 获取第一行的header
    header = next(reader)
    print(header[0], header[1], header[2])  # method,return_type,return_description
    dict_return = {}
    # 逐行获取数据，并输出
    for row in tqdm(reader):
        # print("{} {} {}".format(row[0], row[1], row[2]))
        temp = row[0].split('.')
        ClassName = temp[len(temp) - 2]
        SimpleName = temp[len(temp) - 1].split('(')[0]
        ClassAndMethodName = SimpleName
        dict_return[ClassAndMethodName] = []
        dict_return[ClassAndMethodName].append({"return_type": row[1], "return_description": row[2]})
        # data.at[index_data, 'SimpleName'] = SimpleName
        # data.at[index_data, 'description'] = row[2]
        # data.at[index_data, 'MethodName'] = row[1]
        # data.at[index_data, 'ClassAndMethodName'] = ClassName + '.' + SimpleName
        # if data.at[index_data, 'ClassAndMethodName'] in list_CaN:
        #     Dict_CaN[data.at[index_data, 'ClassAndMethodName']].append(row[2])
        # else:
        #     list_CaN.append(data.at[index_data, 'ClassAndMethodName'])
        #     Dict_CaN[data.at[index_data, 'ClassAndMethodName']] = []
        #     Dict_CaN[data.at[index_data, 'ClassAndMethodName']].append(row[2])
        #
        # index_data = index_data + 1
dict_result = {}
for MethodName in tqdm(dict_return.keys()):
    if MethodName in dict_return.keys():
        dict_Class = {}
        # 比较Type
        big_score = 0
        for dic in dict_return[MethodName]:
            score = 0
            type = dic["return_type"]
            for type_cmp in dict_return[MethodName]:
                candidate = re.findall(r'\w+', type)
                reference = [re.findall(r'\w+', type_cmp["return_type"])]
                score = score + sentence_bleu(reference, candidate, weights=(1, 0, 0, 0))
            score = score / len(dict_return[MethodName])
            if score >= big_score:
                big_score = score
                dict_Class['return_type'] = type
        # 比较des
        big_score = 0
        for dic in dict_return[MethodName]:
            score = 0
            type = dic["return_description"]
            for type_cmp in dict_return[MethodName]:
                candidate = re.findall(r'\w+', type)
                reference = [re.findall(r'\w+', type_cmp["return_description"])]
                score = score + sentence_bleu(reference, candidate, weights=(0.25, 0.25, 0.25, 0.25))
            score = score / len(dict_return[MethodName])
            if score >= big_score:
                big_score = score
                dict_Class['return_description'] = type
                if dict_Class['return_description'] == "":
                    dict_Class['return_description'] = "return_description"

        dict_result[MethodName] = dict_Class
    else:
        print("ERROR!")
        exit()
print(dict_result)

Dict_sam = {}
Dict_sam_key = []
Dict_sam_value = []
# 以读方式打开文件
with open("./temp/temp3.csv", mode="r", encoding="utf-8") as f:
    # 基于打开的文件，创建csv.reader实例
    reader = csv.reader(f)
    # Dict = {}
    # 获取第一行的header
    header = next(reader)
    print(header[0], header[1], header[2], header[3], header[4], header[5])
    for row in tqdm(reader):
        # SimpleName,num,bleu score,description,MethodName,all score
        Dict = {}
        Dict["SimpleName"] = row[0]
        Dict["num"] = row[1]
        Dict["bleu_score"] = row[2]
        Dict["description"] = row[3]
        Dict["MethodName"] = row[4]
        Dict["all_score"] = row[5]
        if row[0] in dict_result.keys():
            Dict["return_type"] = dict_result[row[0]]["return_type"]
            Dict["return_description"] = dict_result[row[0]]["return_description"]
        else:
            Dict["return_type"] = "return_type"
            Dict["return_description"] = "return_description"
        Dict_sam[Dict["SimpleName"]] = Dict
        Dict_sam_key.append(row[0])
        Dict_sam_value.append(Dict)
        print(row[0], Dict)

print(Dict_sam_key)
print(Dict_sam_value)
with open("result/sample_api_msg.pkl", 'wb') as f:
    pickle.dump(Dict_sam, f)
with open('result/sample_api_msg.json', 'w') as f:
    json.dump(Dict_sam, f, indent=4)
