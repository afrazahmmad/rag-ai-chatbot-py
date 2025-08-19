import pandas as pd

def clean_numeric(val):
    try:
        val_str = str(val).strip().replace(',', '')
        return float(val_str) if val_str and val_str.lower() != 'nan' else 0.0
    except:
        return 0.0

def split_by_pipe_and_tilde(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return []
    s = str(val)
    if s.strip() == '' or s.lower() == 'nan':
        return []
    groups = s.split('|')
    nested = [group.split('~') if group else [] for group in groups]
    nested = [[item.strip() for item in group] for group in nested]
    return nested

def calculate_qty_price_sum(cwi_pts_dv_str, qty_ship_str, unit_price_str, category):
    """
    Multiply QTY-SHIP * UNIT-PRICE according to CWI-PTS-DV (C, W, I).
    Sums across all groups/items that match the given category.
    """
    cwi_pts_nested = split_by_pipe_and_tilde(cwi_pts_dv_str)
    qty_ship_nested = split_by_pipe_and_tilde(qty_ship_str)
    unit_price_nested = split_by_pipe_and_tilde(unit_price_str)

    total = 0.0
    for g in range(len(cwi_pts_nested)):
        cwi_group = cwi_pts_nested[g]
        qty_group = qty_ship_nested[g] if g < len(qty_ship_nested) else []
        price_group = unit_price_nested[g] if g < len(unit_price_nested) else []

        max_len = max(len(cwi_group), len(qty_group), len(price_group))
        cwi_group += [''] * (max_len - len(cwi_group))
        qty_group += ['0'] * (max_len - len(qty_group))
        price_group += ['0'] * (max_len - len(price_group))

        for i in range(max_len):
            if str(cwi_group[i]).upper() == category.upper():
                qty = clean_numeric(qty_group[i])
                price = clean_numeric(price_group[i])
                total += qty * price
    return total


# Files
dealer_file = "Carmen July Numbers.csv"
raw_file = "NGTMerged.csv"

dealer_df = pd.read_csv(dealer_file, dtype=str)
raw_df = pd.read_csv(raw_file, dtype=str)

# Clean column names
dealer_df.columns = dealer_df.columns.str.strip()
raw_df.columns = raw_df.columns.str.strip()

# Lowercase RO columns for matching
dealer_df['RO'] = dealer_df['RO'].str.strip().str.lower()
raw_df['RECID'] = raw_df['RECID'].str.strip().str.lower()

results = []

for _, dealer_row in dealer_df.iterrows():
    ro = dealer_row['RO']

    # Dealer values
    dealer_customer_parts_sales = clean_numeric(dealer_row.get('Customer Parts Sales', 0))
    dealer_w_parts_sales = clean_numeric(dealer_row.get('Warranty Parts Sales', 0))
    dealer_i_parts_sales = clean_numeric(dealer_row.get('Internal Parts Sales', 0))
    dealer_t_parts_sales = dealer_customer_parts_sales + dealer_w_parts_sales + dealer_i_parts_sales

    # Match raw row by RECID (RO)
    raw_rows = raw_df[raw_df['RECID'] == ro]

    if raw_rows.empty:
        results.append({
            'RO': ro,
            'Dealer_Customer_Parts_Sales': dealer_customer_parts_sales,
            'Dealer_W_Parts_Sales': dealer_w_parts_sales,
            'Dealer_I_Parts_Sales': dealer_i_parts_sales,
            'Dealer_T_Parts_Sales': dealer_t_parts_sales,
            'Note': 'RO not found in raw data'
        })
        continue

    raw_row = raw_rows.iloc[0]

    # Extract only the needed raw fields
    qty_ord = raw_row.get('QTY-ORD', '')
    qty_ship = raw_row.get('QTY-SHIP', '')
    unit_price = raw_row.get('UNIT-PRICE', '')
    cwi_pts_dv = raw_row.get('CWI-PTS-DV', '')

    # Optional pass-through fields
    c_part_sls = clean_numeric(raw_row.get('C-PART-SLS-DV', ''))
    w_part_sls = clean_numeric(raw_row.get('W-PART-SLS-DV', ''))
    i_part_sls = clean_numeric(raw_row.get('I-PART-SLS-DV', ''))
    t_part_sls = clean_numeric(raw_row.get('T-PART-SLS-DV', ''))

    # Qty * Price calculations (by C/W/I via CWI-PTS-DV)
    raw_customer_qtyprice_sum = calculate_qty_price_sum(cwi_pts_dv, qty_ship, unit_price, 'C')
    raw_warranty_qtyprice_sum = calculate_qty_price_sum(cwi_pts_dv, qty_ship, unit_price, 'W')
    raw_internal_qtyprice_sum = calculate_qty_price_sum(cwi_pts_dv, qty_ship, unit_price, 'I')
    raw_total_qtyprice_sum = (
        raw_customer_qtyprice_sum + raw_warranty_qtyprice_sum + raw_internal_qtyprice_sum
    )

    # ==== MATCH CHECKS with rounding ====
    cp_matched = (
        round(dealer_customer_parts_sales, 2) == round(raw_customer_qtyprice_sum, 2) and
        round(raw_customer_qtyprice_sum, 2) == round(c_part_sls, 2)
    )
    wp_matched = (
        round(dealer_w_parts_sales, 2) == round(raw_warranty_qtyprice_sum, 2) and
        round(raw_warranty_qtyprice_sum, 2) == round(w_part_sls, 2)
    )
    ip_matched = (
        round(dealer_i_parts_sales, 2) == round(raw_internal_qtyprice_sum, 2) and
        round(raw_internal_qtyprice_sum, 2) == round(i_part_sls, 2)
    )
    tp_matched = (
        round(dealer_t_parts_sales, 2) == round(raw_total_qtyprice_sum, 2) and
        round(raw_total_qtyprice_sum, 2) == round(t_part_sls, 2)
    )

    results.append({
        'RO': ro,
        'Dealer_Customer_Parts_Sales': dealer_customer_parts_sales,
        'Raw_Customer_Parts_QtyPrice_Sum': raw_customer_qtyprice_sum,
        'C-PART-SLS-DV': c_part_sls,
        'CP-Matched': "Yes" if cp_matched else "No",

        'Dealer_W_Parts_Sales': dealer_w_parts_sales,
        'Raw_W_Parts_QtyPrice_Sum': raw_warranty_qtyprice_sum,
        'W-PART-SLS-DV': w_part_sls,
        'WP-Matched': "Yes" if wp_matched else "No",

        'Dealer_I_Parts_Sales': dealer_i_parts_sales,
        'Raw_I_Parts_QtyPrice_Sum': raw_internal_qtyprice_sum,
        'I-PART-SLS-DV': i_part_sls,
        'IP-Matched': "Yes" if ip_matched else "No",

        'Dealer_T_Parts_Sales': dealer_t_parts_sales,
        'Raw_T_Parts_QtyPrice_Sum': raw_total_qtyprice_sum,
        'T-PART-SLS-DV': t_part_sls,
        'TP-Matched': "Yes" if tp_matched else "No",

        # Raw fields side-by-side
        'QTY-ORD': qty_ord,
        'QTY-SHIP': qty_ship,
        'UNIT-PRICE': unit_price,
        'CWI-PTS-DV': cwi_pts_dv,
    })

result_df = pd.DataFrame(results)
print(result_df)
result_df.to_csv("ro_comparison.csv", index=False)
