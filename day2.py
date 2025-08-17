def greet(name):
    return f"Welcome, {name}"

print(greet("Afraz Ahmad Khokhar"))

# import math
# print(math.sqrt(16))

import pandas as pd
from datetime import datetime

# df = pd.read_csv("Carmen July Numbers.csv")
# df.to_csv("Carmen July Numbers 2.csv",index=False)

df = pd.read_csv("1256_aug_deals.csv",parse_dates=['sales_date'])
# Current Date
today = datetime.now()



def mtd_deals_count():
    mtd_df = df[(df['sales_date'].dt.month == today.month)]
    mtd_count = len(mtd_df)
    closed_mtd = mtd_df[mtd_df['is_closed'] == True]
    print(f"Total MTD Deals: {mtd_count}")
    print(f"Closed MTD Deals: {len(closed_mtd)}")



def ytd_deals_count():
    ytd_df = df[(df['sales_date'].dt.year == today.year)]
    ytd_total = len(ytd_df)
    closed_ytd = ytd_df[ytd_df['is_closed'] == True]
    print(f"Total YTD Deals: {ytd_total}")
    print(f"Closed YTD Deals: {len(closed_ytd)}")

mtd_deals_count()
ytd_deals_count()
