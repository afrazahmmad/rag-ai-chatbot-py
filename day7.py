import pandas as pd
import json
import os

def load_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.csv':
        df = pd.read_csv(file_path)
    elif ext == '.json':
        with open(file_path,'r') as jf:
            json_data = json.load(jf)
            df = pd.DataFrame(json_data)
    else:
        raise ValueError('file type not supported!')
    return df

def filter_data(df,adv_no=None):
    if adv_no and 'ADV-NO' in df.columns:
        df = df[df['ADV-NO'] == adv_no]

    return df

def show_summary(df):
    num_cols = df.select_dtypes(include=['number']).columns
    if len(num_cols) > 0:
        print(df[num_cols].describe())
    else:
        print("No numeric columns for summary.")

def main():
    file_path = input("File ? ").strip()
    print(file_path)
    adv_no = input("Enter Advisor No (or leave blank): ").strip()


    try:
        df = load_file(file_path)
        print("File loaded")
        print(df.head(2))

        adv_no = int(adv_no) if adv_no else None

        filtered_df = filter_data(df,adv_no)
        print(filtered_df)

        print("show_summary")
        print(show_summary(filtered_df))

        save_to_excel = input("Do you want to save as excel ?").strip().lower()

        if save_to_excel == 'y':
            filtered_df.to_excel('filtered_df.xlsx',index=False)


    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()