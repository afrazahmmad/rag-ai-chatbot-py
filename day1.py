import json
import pandas as pd

data = [
    {"id": 1, "deal_amount":10},
    {"id": 2, "deal_amount":20},
    {"id": 3, "deal_amount":30},
    {"id": 4, "deal_amount":40},
]


total_deals = len(data)

all_deal_amounts = [d['deal_amount'] for d in data]
max_value_deals = [d for d in data if d["deal_amount"] > 20]

print("All deals, ", max_value_deals, "Deals count ", len(max_value_deals))

print("Total Sales:", total_deals)

name = "Afraz"
age = 33
sales = 99
is_active = True


if sales > 80:
    print("Achieved")
else:
    print("Not achieved")

# for i in range(1,33):
#     print("You are ", i, " Years old" )

count = 1

while count <= 2:
    if (count % 2 == 0):
        print("Count is even now: ",count)
    else:
        print("Count is odd now: ", count)
    count +=1



# name = input("Your name ? ")
# print("Kese ho ", name, " ?")

try:
    with open('some_randon.json') as f:
        data = f.read()
except FileNotFoundError:
    print("File nhi mili")


try:
    with open("Carmen July Numbers.csv") as carmen_data_file:
        carmen_data = carmen_data_file.read()
        print("total records", len(carmen_data))
except FileNotFoundError:
    print("File not found")


# try:
#     with open("Carmen July Numbers.csv") as carmen_data_file:
#         carmen_data = json.load(carmen_data_file)
#         print("total records", len(carmen_data))
# except FileNotFoundError:
#     print("File not found")


carmen_deals = [cd[0] for cd in carmen_data]
print("Total deals",len(all_deal_amounts))
print("Max parts sales",max(carmen_deals))
print("Min part sales",min(carmen_deals))

