import codecs

from tqdm import tqdm
from nltk.tokenize import word_tokenize

from cbleu import *
from rouge import Rouge
import json
import time
import random
import nltk
import re
import javalang
import numpy as np
import time
from eval.translate_metric import get_corp_bleu1,get_corp_bleu2,get_corp_bleu3,get_corp_bleu4,get_corp_bleu,get_meteor,get_rouge,get_cider,get_nltk33_sent_bleu,get_google_sent_bleu

def word_tknz(s):
    pattern = r'[a-zA-Z]+'
    tokens = re.findall(pattern, s)
    item_str = [token.lower() for token in tokens]
    if len(item_str) == 0:
        item_str = ["a"]
    return item_str

with codecs.open("raw_data/test_data.json", 'rb') as f1:
    ids = []
    codes = []
    comments, comments1 = [], []
    output = []
    data = json.load(f1)

    for item in tqdm(data):
        comments.append(item["text"])
        comments1.append(item["text"])

    with open('ans_gpt.txt', 'r', encoding='utf-8') as fp:
        output = fp.readlines()
    with open('ans_cl.txt', 'r', encoding='utf-8') as fp:
        output1 = fp.readlines()

    print(len(comments))
    count = 0
    for i in range(len(comments)):
        if output[i] == "\n" or output[i] == " \n":
            output[i] = "a"
            comments[i] = "a"
            count += 1
    print(len(comments)-count)
    print(len(comments), len(output))
    comments = [word_tknz(sent) for sent in comments]
    comments1 = [word_tknz(sent) for sent in comments1][:8712]
    output = [word_tknz(sent) for sent in output]
    output1 = [word_tknz(sent) for sent in output1]

    print("*" * 40, "GPT 3.5", "*" * 40)
    print("ROUGE: ", get_rouge(comments, output))
    print("*"*40, "Code Llama", "*"*40)
    print("ROUGE: ", get_rouge(comments1, output1))