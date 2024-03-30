import codecs

from tqdm import tqdm

from cbleu import *
from rouge import Rouge
import os
import openai
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
from sentence_transformers import SentenceTransformer, util
from nltk.translate.bleu_score import sentence_bleu
from nltk.util import ngrams
from collections import Counter

openai.api_key = "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"

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

def retry_with_exponential_backoff(
        func,
        initial_delay: float = 1,
        exponential_base: float = 2,
        jitter: bool = True,
        max_retries: int = 10,
        errors: tuple = (openai.error.RateLimitError,),
):
    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        while True:
            try:
                return func(*args, **kwargs)

            except errors as e:
                num_retries += 1

                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                delay *= exponential_base * (1 + jitter * random.random())
                time.sleep(delay)

            except Exception as e:
                raise e

    return wrapper

@retry_with_exponential_backoff
def completion_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)

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
    print(sum_rouge / cnt)
    print(sum_meteor / cnt)

exampler_what = "You are an expert Java programmer, please describe the functionality of the method:\n\"\"\"" + "Example Code1:\n" + example_code + "The comment is: Starts the background initialization"
with codecs.open("raw_data/test_data.json", 'rb') as f1:
    ids = []
    codes = []
    comments = []
    output = []
    data = json.load(f1)
    with open('ans.txt', 'a') as fp:
        for item in tqdm(data):
            ids.append(item["id"])
            codes.append(item["code"])
            comments.append(item["text"])

            new_prompt = exampler_what + "\n#For the test code:\n" + item["code"] + "\n# The comment is: "
            new_prompt = new_prompt[:4097]
            response = completion_with_backoff(model="gpt-3.5-turbo-instruct", prompt=new_prompt, max_tokens=30)

            cur_ans = response["choices"][0]["text"].split('\n')[0]
            fp.write(cur_ans + '\n')

    with open('ans.txt', 'r', encoding='utf-8') as fp:
        output = fp.readlines()

    # print(comments, output)
    test_metric(comments, output)
"""
result:
26.282951653781534
66.55955932981409
26.49152820722054
"""