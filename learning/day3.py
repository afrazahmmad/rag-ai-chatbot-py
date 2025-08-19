# #
# # stores_list = ['Afraz','Ahmad','Khokhar']
# # print(stores_list[0])
# # stores_list.append('IT')
# # # print(stores_list)
# #
# # # for n in stores_list:
# # #     print(n)
# #
# #
# #
# # # emp_dict = {"Name": "Afraz Ahmad Khokhar","Age": 33}
# # # emp_dict["Company"] = "Renesis Tech"
# # # print(emp_dict)
# # # for emp_key,emp_value in emp_dict.items():
# # #     print(emp_key, " -> ", emp_value)
# #
# #
# # import json
# #
# #
# # data = {
# #     "Deals":[
# #         {"Name": "Deal-ID", "Value": "451351"},
# #         {"Name": "Gross-Profit", "Value": "1200"},
# #         {"Name": "Salesperson", "Value": "Ali Khan"}
# #     ]
# # }
# #
# # flattened = {item["Name"]: item["Value"] for item in data['Deals']}
# #
# # print(flattened)
# #
# # def flattened_deal(deals_data):
# #     return {item['Name']:item['Value'] for item in deals_data}
# #
# #
# # print(flattened_deal(data['Deals']))
# #
# ros = [
#     {"Deal-ID": "451351", "Gross-Profit": "1200", "PartsSale": "30"},
#     {"Deal-ID": "451352", "Gross-Profit": "400", "PartsSale": "300"},
# ]
#
# def flatten_ro(ro_data):
#     return {
#         "Deal-ID": ro_data["Deal-ID"],
#         "Gross-Profit": ro_data["Gross-Profit"],
#         "PartsSale": ro_data["PartsSale"],
#     }
#
# import pandas as pd
# flattened_list = [flatten_ro(ro) for ro in ros]
# df = pd.DataFrame(flattened_list)
# df.reset_index(inplace=True)
# df.rename(columns={"index": "Sr No"}, inplace=True)
# # df.index.name = 'Sr#'
# print(df)
#
# nested_data = {
#     "Deal": {
#         "Deal-ID": "451351",
#         "Customer": {
#             "Name": "Ali",
#             "Contact": {
#                 "Phone": "123456789",
#                 "Email": "ali@example.com"
#             }
#         },
#         "Sales": {
#             "Gross-Profit": 1200,
#             "Parts": {
#                 "PartsSale": 30,
#                 "PartsCost": 20
#             }
#         }
#     }
# }
#
# def flatten_json(data, parent_key="", sep="."):
#     items = {}
#     for key, value in data.items():
#         new_key = f"{parent_key}{sep}{key}" if parent_key else key
#         if isinstance(value, dict):
#             items.update(flatten_json(value, new_key, sep=sep))
#         else:
#             items[new_key] = value
#     return items
#
# # Use function
# import pandas as pd
# flat_data = flatten_json(nested_data)
# print(flat_data)
#
# df = pd.DataFrame([flat_data])
# df.to_csv('test.csv',index=False)
#


import pandas as pd

#
# # Sample sales data
# data = {
#     'Store': ['A', 'A', 'B', 'B', 'C', 'C', 'A'],
#     'Month': ['Jan', 'Jan', 'Jan', 'Feb', 'Mar', 'Feb', 'Feb'],
#     'Sales': [1000, 1200, 900, 1100, 1500, 1300, 1400]
# }
#
# df = pd.DataFrame(data)
# df.index.name = 'Sr#'
# print("Original data")
# print(df)
#
# df.to_csv('test.csv',index=False)
#
#
# group_by_store_sales = df.groupby('Store')['Sales'].sum().reset_index()
# print(group_by_store_sales)
# group_by_store_sales.to_csv('group_by_store_sales.csv',index=False)
#
# total_sales_per_month = df.groupby('Month')['Sales'].sum().reset_index()
# print(total_sales_per_month)
# total_sales_per_month.to_csv('total_sales_per_month.csv',index=False)
#
# avg_sales_per_month = df.groupby('Month')['Sales'].mean().reset_index()
# print(avg_sales_per_month)
# avg_sales_per_month.to_csv('avg_sales_per_month.csv',index=False)
#
# multi_agg = df.groupby('Store').agg(
#     Total_Sales = ('Sales','sum'),
#     Avg_Sales = ('Sales','mean'),
#     Max_Sales = ('Sales','max'),
#     Min_Sales = ('Sales','min'),
# ).reset_index()
# print(multi_agg)
#
# multi_agg.to_csv('multi_agg.csv',index=False)
#
#
# monthly_deals_count = df.groupby('Store')['Month'].count().reset_index()
# monthly_deals_count.rename(columns={'Month': 'Monthly Count'},inplace=True)
# monthly_deals_count.index.name = 'Sr#'
# print(monthly_deals_count)
# monthly_deals_count.to_csv('monthly_deals_count.csv',index=False)
#
# sorted_by_month = df.sort_values(by='Sales',ascending=True)
# print(sorted_by_month)


data = {
    'Store': ['Karachi', 'Karachi', 'Lahore', 'Lahore', 'Karachi','Lahore'],
    'Employee': ['Ali', 'Sara', 'Ali', 'Sara', 'John','Ali'],
    'Deals': [5, 7, 6, 4, 8,12],
    'SalesDate': ['2025-08-01', '2025-08-05', '2025-08-20', '2025-08-10', '2025-08-12', '2025-08-13'],
    'GrossProfit': [1200, 1500, 1000, 2000, 1800, 2500],
}


df = pd.DataFrame(data)

deals_by_store_and_employee = df.groupby(['Employee','Store'])['Deals'].sum().reset_index()
deals_by_store_and_employee = deals_by_store_and_employee.sort_values(by='Deals',ascending=False)
deals_by_store_and_employee.rename(columns = {'Deals': 'Total Deals'},inplace = True)

print(deals_by_store_and_employee)

import datetime as dt

today = dt.datetime.today()

df['SalesDate'] = pd.to_datetime(df['SalesDate'])

mtd_deals_df = df[(df['SalesDate'].dt.month == today.month)]

employees_by_profit = mtd_deals_df.groupby(['Store','Employee'])['GrossProfit'].sum().reset_index()

print("Mtd Deals")
print(mtd_deals_df)
print(employees_by_profit)

agg_df = df.groupby(['Employee','Store']).agg({
    'GrossProfit': ['sum', 'mean', 'count']
}).reset_index()
print("Mtd agg_df")
print(agg_df)

agg_df = agg_df[agg_df[('GrossProfit','sum')] > 1000]

agg_df.sort_values(by = ('GrossProfit','sum'),ascending=False,inplace=True)

print("Profit more than 1000")
print(agg_df)

df['Week'] = df['SalesDate'].dt.isocalendar().week
weekly_sales = df.groupby(['Week', 'Employee'])['GrossProfit'].sum().reset_index()

print("weekly sales")
print(weekly_sales)
