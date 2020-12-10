import pandas as pd
import pickle
from jpn_phn_format import get_area_code_df, parse_codes_to_list, format_jpn_phone
from example_generator import bad_jpn_phn

# Step 1: Scrape Japanese Area Codes and Pickle
area_codes_list = parse_codes_to_list(get_area_code_df())

with open('./data/area_code_lists.pkl', 'wb') as f:
    pickle.dump(area_codes_list, f)


# Step 2: Generate a test CSV as an example
bad_jpn_phn(300, gen_csv=True, insert_null=True)


# Step 3: Import our test CSV and Run the formatter

# declare necessary variables for function
test_jpn_phone_df = pd.read_csv('./data/test_phones.csv')
test_jpn_phone_df.reset_index(inplace=True, drop=True)

area_codes = './data/area_code_lists.pkl'

# run function
format_jpn_phone(test_jpn_phone_df, area_codes, gen_csv=True)

# troubleshooting example
formatted_phone_df = format_jpn_phone(test_jpn_phone_df, area_codes)

# regex that defines our ideal format for japanese phone numbers, +81 ##-####-#### or +81 #-####-####, in most cases
pfct_re = r'^(\+81 ([1-9]{1}-[1-9]\d{3}|[1-9]{2}-\d{3}|[1-9]{2}\d{1}-\d{2}|[1-9]{2}\d{2}-\d{1})-\d{4}|\+81 [' \
          r'789]0-\d{4}-\d{4}|\+81 50-\d{4}-\d{4}$)'

home_fail_df = formatted_phone_df[['Person ID', 'Home Phone', 'Formatted Home Phone']].loc[
        ~(formatted_phone_df['Formatted Home Phone'].str.fullmatch(pfct_re, na=False))].dropna()

print(home_fail_df)