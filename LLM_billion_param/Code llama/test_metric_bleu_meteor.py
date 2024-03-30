# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.
from typing import Optional
import fire
import codecs

from tqdm import tqdm

from cbleu import *
from rouge import Rouge
import os
import json
import time
import random
import nltk
import re
import javalang
import numpy as np
import time
import random
import heapq
import argparse
from collections import defaultdict
from multiprocessing import Pool
import heapq
from collections import defaultdict
from nltk.translate.bleu_score import sentence_bleu
from nltk.util import ngrams
from collections import Counter
from llama import Llama
import copy


example_code = """
public synchronized boolean start() {
    if (!isStarted()) {
    final ExecutorService tempExec;
    executor = getExternalExecutor();
    if (executor == null) {
        executor = tempExec = createExecutor();
    } 
    else {
        tempExec = null;}
        future = executor.submit(createTask(tempExec));
        return true;
    }
    return false;
}
"""

init_inst_example = [
            {
                "role": "system",
                "content": "You are an expert Java programmer, please describe the functionality of the method in a short word(less than 40):\n\"\"\"" + "Example Code1:\n" + example_code + "The comment is: Starts the background initialization",
            },
            {
                "role": "user",
                "content": "",
            }
        ]

init_inst_noexample = [
            {
                "role": "system",
                "content": "You are an expert Java programmer, please describe the functionality of the method in a short word(less than 40):\n\"\"\"",
            },
            {
                "role": "user",
                "content": "",
            }
        ]

def add_marker_to_method_body(code):
    # 正则表达式匹配Java方法体开始
    pattern = re.compile(r'(\{)(\s*\n\s*)')
    # 替换匹配的字符串为原字符串加上标记
    return pattern.sub(r'\1\2""" <FILL>\n', code, count=1)

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
        sum_meteor += (test_meteor(candidate, [reference]) * 100)
    print(sum_bleu / cnt)
    print(sum_meteor / cnt)

def main(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0.2,
    top_p: float = 0.95,
    max_seq_len: int = 512,
    max_batch_size: int = 4,
    max_gen_len: Optional[int] = None,
):
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    with codecs.open("raw_data/test_data.json", 'rb') as f1:
        ids = []
        codes = []
        comments = []
        output = []
        data = json.load(f1)
        counter = 0
        prompts = []
        for item in tqdm(data):
            counter += 1
            ids.append(item["id"])
            codes.append(item["code"])
            comments.append(item["text"])
            p = "\n#For the test code:\n" + item["code"] + "\n# The comment is: "
            copy_of_init_inst_noexample = copy.deepcopy(init_inst_noexample)
            copy_of_init_inst_noexample[1]["content"] = p[:900]
            prompts.append(copy_of_init_inst_noexample)
            if counter == max_batch_size:
                results = generator.chat_completion(
                    prompts,  # type: ignore
                    max_gen_len=max_gen_len,
                    temperature=temperature,
                    top_p=top_p,
                )
                for instruction, result in zip(prompts, results):
                    with open('ans.txt', 'a') as fp:
                        fp.write(result['generation']['content'].split('\n', 1)[0] + '\n')
                prompts = []
                counter = 0

        with open('ans.txt', 'r', encoding='utf-8') as fp:
            output = fp.readlines()

        test_metric(comments, output)

if __name__ == "__main__":

    fire.Fire(main)

"""
torchrun --nproc_per_node 1 test_metric_bleu_meteor.py \
>     --ckpt_dir CodeLlama-7b-Instruct/ \
>     --tokenizer_path CodeLlama-7b-Instruct/tokenizer.model \
>     --max_seq_len 1024 --max_batch_size 4
"""