# 导入 csv 库
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
data = pd.DataFrame(columns=['SimpleName', 'description', 'MethodName'])
index_data = 0
list_CaN = []  # class and name
Dict_CaN = {}
# 以读方式打开文件
with open("./data/class_method.csv", mode="r", encoding="utf-8") as f:
    # 基于打开的文件，创建csv.reader实例
    reader = csv.reader(f)

    # 获取第一行的header
    header = next(reader)
    print(header[0], header[1], header[2])

    # 逐行获取数据，并输出
    for row in tqdm(reader):
        # print("{} {} {}".format(row[0], row[1], row[2]))
        temp = row[0].split('.')
        ClassName = temp[len(temp)-1]
        SimpleName = row[1][len(row[0])+1:].split('(')[0]
        # print(SimpleName)
        data.at[index_data, 'SimpleName'] = SimpleName
        data.at[index_data, 'description'] = row[2]
        data.at[index_data, 'MethodName'] = row[1]
        data.at[index_data, 'ClassAndMethodName'] = ClassName+'.'+SimpleName
        if data.at[index_data, 'ClassAndMethodName'] in list_CaN:
            Dict_CaN[data.at[index_data, 'ClassAndMethodName']].append(row[2])
        else:
            list_CaN.append(data.at[index_data, 'ClassAndMethodName'])
            Dict_CaN[data.at[index_data, 'ClassAndMethodName']] = []
            Dict_CaN[data.at[index_data, 'ClassAndMethodName']].append(row[2])
        index_data = index_data + 1

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
            ClassAndMethodName = ClassName + '.' + SimpleName
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

    result = []
    for ClassAndMethodName in tqdm(list_CaN):
        dict_Class = {}
        dict_Class["MethodName"] = ClassAndMethodName
        des_list = Dict_CaN[ClassAndMethodName]
        dict_Class["des"] = des_list[0]
        big_score = 0
        for des in des_list:
            score = 0
            for des_cmp in des_list:
                reference = [re.findall(r'\w+', des_cmp)]
                candidate = re.findall(r'\w+', des)
                score = score + sentence_bleu(reference, candidate, weights=(0.25, 0.25, 0.25, 0.25))
            score = score / len(des_list)
            if score >= big_score:
                big_score = score
                dict_Class["des"] = des_cmp
        dict_Class['bleu score'] = big_score


        if ClassAndMethodName in dict_return.keys():
            # 比较Type
            big_score = 0
            for dic in dict_return[ClassAndMethodName]:
                score = 0
                type = dic["return_type"]
                for type_cmp in dict_return[ClassAndMethodName]:
                    candidate = re.findall(r'\w+', type)
                    reference = [re.findall(r'\w+', type_cmp["return_type"])]
                    score = score + sentence_bleu(reference, candidate, weights=(1, 0, 0, 0))
                score = score / len(dict_return[ClassAndMethodName])
                if score >= big_score:
                    big_score = score
                    dict_Class['return_type'] = type_cmp["return_type"]
            # 比较des
            big_score = 0
            for dic in dict_return[ClassAndMethodName]:
                score = 0
                type = dic["return_description"]
                for type_cmp in dict_return[ClassAndMethodName]:
                    candidate = re.findall(r'\w+', type)
                    reference = [re.findall(r'\w+', type_cmp["return_description"])]
                    score = score + sentence_bleu(reference, candidate, weights=(0.25, 0.25, 0.25, 0.25))
                score = score / len(dict_return[ClassAndMethodName])
                if score >= big_score:
                    big_score = score
                    dict_Class['return_description'] = type_cmp["return_description"]
                    if dict_Class['return_description'] == "":
                        dict_Class['return_description'] = "return_description"

        else:
            dict_Class['return_type'] = "return_type"
            dict_Class['return_description'] = "return_description"




        result.append(dict_Class)


    print(result[0])
    api_msg = {}
    for item in result:
        api_msg[item["MethodName"]] = item
    print(api_msg)
    # with open("result/api_msg.pkl", 'wb') as f:
    #     pickle.dump(api_msg, f)
    with open('result/api_msg.json', 'w') as f:
        json.dump(api_msg, f, indent=4)
    """'XMLReaderFactory.createXMLReader': {'MethodName': 'XMLReaderFactory.createXMLReader', 'des': 'Attempt to create 
    an XML reader from a class name. Given a class name, this method attempts to load and instantiate the class as an XML 
    reader.Note that this method will not be usable in environments where the caller (perhaps an applet) is not permitted 
    to load classes dynamically.', 'bleu score': 0.5, 'return_type': 'XMLReader', 'return_description': 'A new XML 
    reader.'} """






    # print(data)
    # num_SimpleName = len(list(dict.fromkeys(data["SimpleName"])))
    # print("共有{}个API，其中SimpleName共{}个".format(index_data, num_SimpleName))
    # data.to_csv("temp/temp4.csv", index=False)


