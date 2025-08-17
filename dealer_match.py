import pandas as pd

def clean_numeric(val):
    try:
        val_str = str(val).strip().replace(',', '')
        return float(val_str) if val_str else 0.0
    except:
        return 0.0

def split_by_pipe_and_tilde(val):
    if not val or pd.isna(val):
        return []
    groups = val.split('|')
    nested = [group.split('~') if group else [] for group in groups]
    nested = [[item.strip() for item in group] for group in nested]
    return nested

def calculate_customer_parts_sum(cwi_str, tot_part_sale_str):
    cwi_nested = split_by_pipe_and_tilde(cwi_str)
    tot_part_sale_nested = split_by_pipe_and_tilde(tot_part_sale_str)
    total = 0.0

    for g in range(len(cwi_nested)):
        cwi_group = cwi_nested[g]
        tot_group = tot_part_sale_nested[g] if g < len(tot_part_sale_nested) else []

        max_len = max(len(cwi_group), len(tot_group))
        cwi_group += [''] * (max_len - len(cwi_group))
        tot_group += ['0'] * (max_len - len(tot_group))

        for i in range(max_len):
            if cwi_group[i].upper() == 'C':
                total += clean_numeric(tot_group[i])
    return total

# Files
dealer_file = "Carmen July Numbers.csv"
raw_file = "NorthGeorgiaROsWithNewFields.csv"

dealer_df = pd.read_csv(dealer_file, dtype=str)
raw_df = pd.read_csv(raw_file, dtype=str)

# Clean column names
dealer_df.columns = dealer_df.columns.str.strip()
raw_df.columns = raw_df.columns.str.strip()

# Lowercase RO columns for matching
dealer_df['RO'] = dealer_df['RO'].str.strip().str.lower()
raw_df['RECID'] = raw_df['RECID'].str.strip().str.lower()

results = []

for idx, dealer_row in dealer_df.iterrows():
    ro = dealer_row['RO']
    dealer_val = clean_numeric(dealer_row['Customer Parts Sales'])

    raw_rows = raw_df[raw_df['RECID'] == ro]

    if raw_rows.empty:
        results.append({
            'RO': ro,
            'Dealer_Customer_Parts_Sales': dealer_val,
            'Raw_Customer_Parts_Sum': None,
            'Raw_CWI': None,
            'Raw_CWI_PTS_DV': None,
            'Raw_TOT_PART_SALE_BY_JOB_DR': None,
            'Raw_TOT_PART_SALE_BY_JOB_DR_List': None,
            'Raw_UNIT_PRICE': None,
            'Raw_QTY_ORD': None,
            'Raw_UNIT_PRICE_x_QTY_ORD': None,
            'Raw_OPT': None,
            'Raw_OPT_List': None,
            'Raw_SPG_ACCPT_DECLN_DR': None,
            'Raw_SPG_ACCPT_DECLN_DR_List': None,
            'Match': False,
            'Note': 'RO not found in raw data'
        })
        continue

    raw_row = raw_rows.iloc[0]

    # CWI related
    cwi = raw_row.get('CWI', '')
    cwi_pts_dv = raw_row.get('CWI-PTS-DV', '')

    # Parts sales
    tot_part_sale = raw_row.get('TOT-PART-SALE-BY-JOB-DR', '')
    tot_part_sale_list = split_by_pipe_and_tilde(tot_part_sale)

    # Unit Price & Qty Ord
    unit_price = raw_row.get('UNIT-PRICE', '')
    qty_ord = raw_row.get('QTY-ORD', '')
    unit_price_list = split_by_pipe_and_tilde(unit_price)
    qty_ord_list = split_by_pipe_and_tilde(qty_ord)

    # Multiply unit price × qty ord
    multiplied_values = []
    for g in range(len(unit_price_list)):
        price_group = unit_price_list[g]
        qty_group = qty_ord_list[g] if g < len(qty_ord_list) else []
        max_len = max(len(price_group), len(qty_group))
        price_group += ['0'] * (max_len - len(price_group))
        qty_group += ['0'] * (max_len - len(qty_group))
        multiplied_values.append([
            clean_numeric(price_group[i]) * clean_numeric(qty_group[i])
            for i in range(max_len)
        ])

    # OPT column
    opt_val = raw_row.get('OPT', '')
    opt_list = split_by_pipe_and_tilde(opt_val)

    # Decline column
    decline_val = raw_row.get('SPG-ACCPT-DECLN-DR', '')
    decline_list = split_by_pipe_and_tilde(decline_val)

    raw_sum = calculate_customer_parts_sum(cwi, tot_part_sale)
    match = abs(dealer_val - raw_sum) < 0.01

    results.append({
        'RO': ro,
        'Dealer_Customer_Parts_Sales': dealer_val,
        'Raw_Customer_Parts_Sum': raw_sum,
        'Raw_CWI': cwi,
        'Raw_CWI_PTS_DV': cwi_pts_dv,
        'Raw_TOT_PART_SALE_BY_JOB_DR': tot_part_sale,
        'Raw_TOT_PART_SALE_BY_JOB_DR_List': str(tot_part_sale_list),
        'Raw_UNIT_PRICE': unit_price,
        'Raw_QTY_ORD': qty_ord,
        'Raw_UNIT_PRICE_x_QTY_ORD': str(multiplied_values),
        'Raw_OPT': opt_val,
        'Raw_OPT_List': str(opt_list),
        'Raw_SPG_ACCPT_DECLN_DR': decline_val,
        'Raw_SPG_ACCPT_DECLN_DR_List': str(decline_list),
        'Match': match,
        'Note': '' if match else 'Values do not match'
    })

result_df = pd.DataFrame(results)

print(result_df)
result_df.to_csv("customer_parts_sales_full_debug.csv", index=False)
