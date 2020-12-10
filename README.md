# Introduction

jpn_phn_format addresses a somewhat niche use-case that is typically a non-issue given the prevalence of gate-keeping phone number validation—it takes in a CSV of phone numbers, identifies the Japanese numbers, and formats them into a properly-hyphenated, country code-appended configuration—typically either +81 ##-####-#### or +81 #-####-####

## Usage
jpn_phn_format contains three main functions in jpn_phn_format.py for the main process and an additional function in example_generator.py to create example data.

### jpn_phn_format.py
**get_area_code_df()** scrapes Japanese area codes from [Wikipedia](https://en.wikipedia.org/wiki/List_of_dialing_codes_in_Japan) and returns a data frame with an area column, designating the area a code is used in, and a code column, with the area code {'area': code}.
```python
from jpn_phn_format import get_area_code_df

area_code_df = get_area_code_df()
```

**parse_codes_to_list(area_code_df)** takes in a data frame of area codes and their respective areas (the data frame indicated above), and returns a list of lists of unique area codes sorted by length
```python
from jpn_phn_format import get_area_code_df, parse_codes_to_list

area_code_df = get_area_code_df()

area_codes_list = parse_codes_to_list(area_code_df)
```

**format_jpn_phone(jpn_phone_df, area_code_list_path, gen_csv=False)** takes three parameters:

*jpn_phn_df - A data frame with a 'Person ID' column and any number of additional phone number columns.*


*area_code_list_path -  A relative path to a pickled area codes file.*


*gen_csv=False - Defaults to False. If set to True, will export a CSV containing the original jpn_phn_df with a formatted phone number column added for each respective column.*


```python
from jpn_phn_format import format_jpn_phone

# declare necessary variables for function
test_jpn_phn_df = pd.read_csv('./data/test_phones.csv')
test_jpn_phn_df.reset_index(inplace=True, drop=True)

area_codes = './data/area_code_lists.pkl'
```

### example_generator.py
As I cannot make the data I wrote this for public, I wrote a function that generates random, example Japanese phone number and Person ID data. As the goal is to fix inconsistently-formatted phone numbers, example_generator.py generates a couple different types of poor and inconsistently-formatted numbers. It is not as quite as creative as the original dataset (non-Japanese numbers included, typos, other creative formatting), but illustrates the purpose of this repo.
**bad_jpn_phn(total, area_code_pkl='./data/area_code_lists.pkl', gen_csv=False, insert_null=False)** takes three parameters:
*total - The total number of phone numbers you would like to generate.*

*area_code_pkl -  A relative path to a pickled area codes file.*

*gen_csv=False - Defaults to False. If set to True, will export a CSV containing a "Person ID" column, with IDs, as well as two test phone columns, 'Home Phone', 'Business Phone'.*

*insert_null - Defaults to False. If set to True, will randomly replace 20% of the generated phone numbers with Null values.*

```python
from example_generator import bad_jpn_phn

# Step 2: Generate a test CSV as an example
bad_jpn_phn(10000, gen_csv=True, insert_null=True)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
