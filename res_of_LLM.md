#### Code Llama

```
(llama) root@XXX:~/code/code-llama/codellama# torchrun --nproc_per_node 1 test.py \

--ckpt_dir CodeLlama-7b-Instruct/ \
--tokenizer_path CodeLlama-7b-Instruct/tokenizer.model \
--max_seq_len 1024 --max_batch_size 4
/root/anaconda3/lib/python3.9/site-packages/scipy/__init__.py:155: UserWarning: A NumPy version >=1.18.5 and <1.25.0 is required for this version of SciPy (detected version 1.25.2
warnings.warn(f"A NumPy version >={np_minversion} and <{np_maxversion}"
initializing model parallel with size 1
initializing ddp with size 1
initializing pipeline with size 1
Loaded in 13.88 seconds
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4000/4000 [3:23:35<00:00,  3.05s/it]
bleu: 25.08073538385577
rouge: 99.95
meteor: 28.159202183310896
```

#### ChatGPT

```
(NL2CODE) XXX@XXXMacBook-Air gpt-3.5-turbo-instruct % python test_metric.py
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 8714/8714 [00:00<00:00, 2429969.09it/s]
8714
8075
bleu: 33.61597896615243
rouge: 73.892586642185
meteor: 26.49152820722054
```

