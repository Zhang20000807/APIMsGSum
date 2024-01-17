import random
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare
import scipy.stats as stats

df = pd.read_csv('HEdata/scores.csv')

data_array = df.values

data_array = np.array(data_array)

column_stds = np.std(data_array, axis=0)
print(column_stds)

p_values = []

for i in range(3):
    method1_scores = data_array[:, i]
    method2_scores = data_array[:, i+3]
    t_stat, p_val = stats.wilcoxon(method1_scores, method2_scores)
    p_values.append(p_val)

print(f'p-values for the paired t-tests comparing method 1 and method 2: {p_values}')


