import numpy as np

arr1 = np.array([1,2,3,4,5])
arr2 = np.array([10,20,30,40,50])

print(arr1 + arr2)
print(arr1 * arr2)
print(arr1 .mean())
print(np.sqrt(arr1))
import math
print(math.sqrt(16))

# [1,2,3]
# [4,5,6]
matrix = np.array([[1,2,3],[4,5,6]])
print(matrix.shape)
print(matrix.sum())
print(matrix.sum(axis=0))
print(matrix.sum(axis=1))

import pandas as pd

sales_date = {
    'Date': pd.date_range('2025-08-01','2025-08-14'),
    'Sales' : [100, 200, 150, 300, 250, 400, 350, 500, 450, 600,800,900,1000,1500]
}
# print(sales_date)

df = pd.DataFrame(sales_date)
df.index.name= 'Sr# '
# print(df)

df['(3 Day moving avg)'] = df['Sales'].rolling(3).mean().round(1)
df['(5 Day moving avg)'] = df['Sales'].rolling(3).mean().round(1)
#
# df = df.fillna('--')
# # print(df)
#
# sales = np.array([100, 200, 150, 300, 250, 400, 350, 500, 450, 600])
# weights = np.ones(3) / 3
# moving_avg = np.convolve(sales,weights, mode='valid')
# print(moving_avg)
#
# ma_df = pd.DataFrame(moving_avg)
# ma_df.to_csv('moving_avg.csv')
# z_scores = (sales - np.mean(sales)) / np.std(sales)
#
#
# print(z_scores)

sales = [100, 200, 150, 300, 250, 4000,9000]
df = pd.DataFrame({'Sales': sales})

df['Cumulative Sales'] = np.cumsum(df['Sales'])
df['Daily % change'] = df['Sales'].pct_change() * 100
df = df.fillna(0)
print(df)

mean_sales = np.mean(sales)
std_sales = np.std(sales)

df['Z-Score'] = (df['Sales'] - mean_sales) / std_sales
df['Anomaly'] = np.where(abs(df['Z-Score']) > 2, 'Yes', 'No')
print(std_sales)
print(mean_sales)
print(df)

df.to_csv('sales_data.csv')

arr = np.array([1,2,3,4])
print(arr[arr>3])