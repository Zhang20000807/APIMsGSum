# API-Enhanced Code Summarization: A Method for Integrating API Information
This is the source code of **APIMsGSum**.

Obtain complete code and dataset in https://drive.google.com/drive/folders/1M56wx2xY0w7LUMBRl5cyltKoeC54M8XB?usp=sharing

# Runtime Environment
- 4 NVIDIA T100 GPUs 
- Ubuntu 20.04.5
- CUDA 11.3 (with CuDNN of the corresponding version)
- Python 3.9
- PyTorch 1.11
- PyTorch Geometric 2.0.4 

# Experiment on the Java Dataset
Download the source code from Google Drive

```angular2html
cd src_code/java/code_sum_39
python s1_preprocessor.py
python s1_graphpreprocessor.py
python s2_model.py
```



