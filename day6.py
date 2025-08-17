import pandas as pd

df_csv = pd.read_csv('Carmen July Numbers.csv')
print(df_csv.head(2))
print("Tail")
print(df_csv.tail(2))
print(df_csv[['ADV-NO','RO']].head(2))

print(df_csv.sort_values(by=['RO-DATE'],ascending=[False]).head(4))
print(df_csv.sort_values(by=['CUST-NAME','RO-DATE'],ascending=[True,False]).head(4))
df_internal_ps_30 = df_csv[df_csv['Internal Parts Sales'] > 30].head(40)
print(df_internal_ps_30[:2])
df_internal_ps_30.to_csv('df_internal_ps_30.csv',index=False)


#

import json

with open('REY_new_2_ro_451351_20250807_101649.json','r') as file:
    data = json.load(file)


print("Raw JSON:")
print(data)

df = pd.DataFrame(data)
print(df.head())
df.to_csv('rey_json_to_csv.csv')
df_flat = pd.json_normalize(data)
print(df_flat)
df_flat.to_csv('df_flat.csv')
df.to_excel('data_to_excel.xlsx',index=False)

