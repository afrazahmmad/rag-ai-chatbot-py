import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


data = {
    "Days": [1,2,3,4,5,6,7],
    "Sales":[2,4,6,8,10,12,14],
}

df = pd.DataFrame(data)

input = df[['Days']]
output = df['Sales']

# print(input,output)
model = LinearRegression()
model.fit(input,output)

# future_days = np.array([[20],[21],[22],[23],[24],[25],[26]])
future_days = np.arange(8,15).reshape(-1,1)
predictions = model.predict(future_days)

for day,pred in zip(future_days.flatten(),predictions):
    print(f"Predicted Sales for Day {day}: {pred:.2f}")
#
# print("-------")
# for i in range(len(future_days)):
#     day = future_days[i][0]
#     prediction = predictions[i]
#     print(f"Prediction Sales for Day {day}: {prediction:.2f}")
#
#
# print("-------")
# flattened_days = future_days.flatten()
#
# for d in range(len(flattened_days)):
#     predic = predictions[d]
#     day = flattened_days[d]
#     print(f"Prediction sales for Day {day}: {predic:.2f}")
#
#
# for day, pred in zip(flattened_days,predictions):
#     print(f"Pred sale for Day {day} : {pred:.1f} ")
#
#
#
#
# df['Ad_Spend'] = [2,5,7,12,2,19,7,4,9,1]
# x = df[['Days','Ad_Spend']]
# y = df['Sales']
# model.fit(x,y)
#
# import matplotlib.pyplot as plt
#
# plt.scatter(df['Days'],y, color='blue',label='Actual')
# plt.scatter(df['Days'],model.predict(x), color='red',label='Predicted')
# plt.legend()
# plt.show()
#
#
# #Line chart
# plt.figure(figsize=(10, 5))
# plt.plot(df['Days'],y,'bo-',label="Actual Sales")
# plt.plot(future_days,predictions,'r--',label="Predicted Sales")
# plt.xlabel('Day')
# plt.ylabel('Sales')
# plt.title("Line Chart - Actual vs Predicted Sales")
# plt.legend()
# plt.show()
#
# # bar chart
#
# plt.figure(figsize=(10,5))
#
# plt.bar(df['Days'],y,color='blue',label='Actual Sales')
# plt.bar(flattened_days,predictions,color='green',alpha=0.5,label='Predicted Sales')
# plt.xlabel("Days")
# plt.ylabel("Sales")
# plt.title("Sales predictions")
# plt.legend()
# plt.show()
#
#
# from sklearn.metrics import mean_squared_error, r2_score
#
# y_pred = model.predict(x)
# print("MSE:", mean_squared_error(y, y_pred))
# print("R² Score:", r2_score(y, y_pred))
#
#

#
# import pandas as pd
# import matplotlib.pyplot as plt
#
# df = pd.read_csv("../debugging/multiple_stores_data.csv")
# store_id = 1256
#
#
# def get_metrics(data):
#     total_deals = len(data)
#     new_units = len(data[data['new_used_cpo'].str.lower() == 'n'])
#     used_units = len(data[data['new_used_cpo'].str.lower() == 'u'])
#     front_gross = data['front_end_gross'].sum()
#     back_gross = data['back_end_gross'].sum()
#     total_gross = data['total_gross'].sum()
#     trade_count = data['trade_1_vin'].notna().sum()
#
#     return {
#         "Total Deals": total_deals,
#         "New Units": new_units,
#         "Used Units": used_units,
#         "Front End Gross": front_gross,
#         "Back End Gross": back_gross,
#         "Total Gross": total_gross,
#         "Trade Units": trade_count
#     }
#
#
# # Get metrics for each store
# store_grouped = df.groupby("store_id").apply(get_metrics).apply(pd.Series)
# store_grouped_2 = df.groupby("store_id").apply(get_metrics).apply(pd.Series)
# print(store_grouped_2)
#
# # Selected store metrics
# store_metrics = store_grouped.loc[store_id]
# store_metrics_2 = store_grouped_2.loc[store_id]
# print(store_metrics_2)
#
# # Market average (excluding this store)
# market_avg_metrics = store_grouped.drop(store_id).mean()
# market_avg_metrics_2 = store_grouped_2.drop(store_id).mean()
#
#
# # Comparison DataFrame
# comparison_df = pd.DataFrame({
#     "Metric": store_metrics.index,
#     f"Store {store_id}": store_metrics.values,
#     "Market Avg per Store": market_avg_metrics.values
# })
# comparison_df["Difference"] = comparison_df[f"Store {store_id}"] - comparison_df["Market Avg per Store"]
#
# print(comparison_df)
#
# # Visualization
# comparison_df.plot(x="Metric", y=[f"Store {store_id}", "Market Avg per Store"], kind="bar")
# plt.title(f"Store {store_id} vs Market Average per Store")
# plt.ylabel("Value")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

