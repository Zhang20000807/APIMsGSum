import codecs
from config import *
import pickle
import json
from transformers import AutoTokenizer, AutoModel
import torch
import re
import time
import torch.nn as nn
import tqdm

with codecs.open(train_avail_data_path, 'rb') as f:
    train_data = pickle.load(f)
# print("texts:", train_data['ids'])
with codecs.open("../graph_data/train_graphdata.json", 'rb') as f1:
    graph_data = json.load(f1)
graph_dict = {}
for item in graph_data:
    idx = item["id"]
    graph_dict[idx] = item["graph"]
train_data['graph'] = []
for idx in train_data['ids']:
    train_data['graph'].append(graph_dict[idx + 1])
print("train_data:", train_data.keys())
print("code_asts:", train_data['code_asts'][0].keys())
print("graph:", train_data['graph'][0].keys())
print("text_dic:", train_data['text_dic'].keys())
with open(train_avail_data_path, 'wb') as f:
    pickle.dump(train_data, f)

with codecs.open(valid_avail_data_path, 'rb') as f:
    valid_data = pickle.load(f)
# print("texts:", valid_data['ids'])
with codecs.open("../graph_data/valid_graphdata.json", 'rb') as f1:
    graph_data = json.load(f1)
graph_dict = {}
for item in graph_data:
    idx = item["id"]
    graph_dict[idx] = item["graph"]
valid_data['graph'] = []
for idx in valid_data['ids']:
    valid_data['graph'].append(graph_dict[idx + 1])
print("valid_data:", valid_data.keys())
print("code_asts:", valid_data['code_asts'][0].keys())
print("graph:", valid_data['graph'][0].keys())
print("text_dic:", valid_data['text_dic'].keys())
with open(valid_avail_data_path, 'wb') as f:
    pickle.dump(valid_data, f)
    
with codecs.open(test_avail_data_path, 'rb') as f:
    test_data = pickle.load(f)
# print("texts:", test_data['ids'])
with codecs.open("../graph_data/test_graphdata.json", 'rb') as f1:
    graph_data = json.load(f1)
graph_dict = {}
for item in graph_data:
    idx = item["id"]
    graph_dict[idx] = item["graph"]
test_data['graph'] = []
for idx in test_data['ids']:
    test_data['graph'].append(graph_dict[idx + 1])
print("test_data:", test_data.keys())
print("code_asts:", test_data['code_asts'][0].keys())
print("graph:", test_data['graph'][0].keys())
print("text_dic:", test_data['text_dic'].keys())
with open(test_avail_data_path, 'wb') as f:
    pickle.dump(test_data, f)