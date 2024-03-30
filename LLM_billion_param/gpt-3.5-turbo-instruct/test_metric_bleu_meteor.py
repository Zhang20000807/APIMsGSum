import codecs

from tqdm import tqdm

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
import random

def test_meteor(hypothesis, reference):
    import nltk
    from nltk.translate.meteor_score import meteor_score
    from nltk.tokenize import word_tokenize

    # 确保 hypothesis 和 reference 都是分词后的列表
    hypothesis_tokens = word_tokenize(hypothesis)
    reference_tokens_list = [word_tokenize(ref) for ref in reference]  # 假设 reference 是一个包含多个参考的列表

    meteor = meteor_score(reference_tokens_list, hypothesis_tokens)
    return meteor

def test_metric(references, candidates):
    sum_bleu, sum_rouge, sum_meteor = 0, 0, 0
    cnt = 0
    rouge_score = Rouge()
    for i in range(len(references)):
        candidate = candidates[i]
        reference = references[i]
        cnt += 1
        sum_bleu += (nltk_sentence_bleu(candidate, reference) * 100)
        sum_rouge += (rouge_score.calc_score(candidate, reference) * 100)
        sum_meteor += (test_meteor(candidate, [reference]) * 100)
    print(sum_bleu / cnt)
    print(sum_meteor / cnt)

with codecs.open("raw_data/test_data.json", 'rb') as f1:
    ids = []
    codes = []
    comments = []
    output = []
    data = json.load(f1)
    with open('ans.txt', 'a') as fp:
        for item in tqdm(data):
            comments.append(item["text"])

    with open('ans.txt', 'r', encoding='utf-8') as fp:
        output = fp.readlines()

    print(len(comments))
    count = 0
    for i in range(len(comments)):
        if output[i] == "\n":
            comments[i] = "\n"
            count += 1
    print(len(comments)-count)
    test_metric(comments, output)

