import pandas as pd
import numpy as np
import pickle


# get_area_code_df reads the "Dialing Codes in Japan" wiki and returns a dataframe with an area column,
# designating the area a code is used in, and a code column, with the area code {'area': code}
def get_area_code_df():
    # read all tables on the "Dialing Codes in Japan" wiki, which lists Japanese Area Codes
    area_code_df_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_dialing_codes_in_Japan')

    # concat all the tables
    area_code_df = pd.concat(area_code_df_list).reset_index(drop=True)

    # drop the first four rows (NaN, Country Code, International Call Prefix, Trunk Prefix) and second two columns
    # selecting only area column and area code column
    area_code_df = area_code_df.iloc[4:1694].rename(columns={0: "area", 1: "code"})

    return area_code_df


# parse_codes_to_list sorts and de-dupes area codes according to length
# sorting by length will be important later when we need to hyphenate numbers according to length
# parse_codes_to_list takes a two-column dataframe, {'area': code}, and returns six lists, from area code length 2-6
# and an additional list to check for outliers
def parse_codes_to_list(area_code_df):
    # push code column to list for parsing
    area_code_list = area_code_df['code'].to_list()

    # declare area code lists
    two_digit_code = []
    three_digit_code = []
    four_digit_code = []
    five_digit_code = []
    six_digit_code = []
    outlier_check = []

    # loop and sort area codes
    for code in area_code_list:
        # reading the area codes as df dropped the leading 0, so we add it back in, and add each area code to
        # its respective list, checking for duplicates
        if len(str(code)) == 1 and ('0' + str(code)) not in two_digit_code:
            two_digit_code.append('0' + str(code))
        elif len(str(code)) == 2 and ('0' + str(code)) not in three_digit_code:
            three_digit_code.append('0' + str(code))
        elif len(str(code)) == 3 and ('0' + str(code)) not in four_digit_code:
            four_digit_code.append('0' + str(code))
        elif len(str(code)) == 4 and ('0' + str(code)) not in five_digit_code:
            five_digit_code.append('0' + str(code))
        elif len(str(code)) == 5 and ('0' + str(code)) not in six_digit_code:
            six_digit_code.append('0' + str(code))
        else:
            outlier_check.append('0' + str(code))

    return two_digit_code, three_digit_code, four_digit_code, five_digit_code, six_digit_code, outlier_check


# format_jpn_phone takes in a dataframe with a primary key column and any number of additional phone number columns
# you may also pass df_check = 'home_fail', 'mobile_fail', or 'business_fail' to print a dataframe of phone numbers
# that failed the format process
def format_jpn_phone(jpn_phone_df, area_code_list_path, gen_csv=False):
    # area code lists load in
    with open(area_code_list_path, 'rb') as f:
        two_digit_code, three_digit_code, four_digit_code, five_digit_code, six_digit_code, outlier_check = pickle.load(
            f)

    # define the regex statements we will use

    # CASE 1: (no country code) Find all Japanese validated numbers without a country code, lead zero optional
    # then lstrip zero, replace dashes and spaces with nospace
    # USAGE: Find all japanese phone numbers without a country code and strip all but the numbers
    no_cc_jpn = r'^(0?([1-9]{1}(-|\s)?[1-9]\d{3}|[1-9]{2}(-|\s)?\d{3}|[1-9]{2}\d{1}(-|\s)?\d{2}|[1-9]{2}\d{2}(' \
                r'-|\s)?\d{1})(-|\s)?\d{4}|0?[789]0(-|\s)?\d{4}(-|\s)?\d{4}|0?50(-|\s)?\d{4}(-|\s)?\d{4})$'

    # CASE 2: Do the same with country code numbers, while lstripping all iterations of the country code
    # USAGE: Find all japanese numbers with a country code, with or without lead 0, and strip of all but numbers
    cc_jpn = r'^(\+?\s*\(?\+?81\)?\s*-?)(0?([1-9]{1}(-|\s)?[1-9]\d{3}|[1-9]{2}(-|\s)?\d{3}|[1-9]{2}\d{1}(-|\s)?\d{' \
             r'2}|[1-9]{2}\d{2}(-|\s)?\d{1})(-|\s)?\d{4}|0?[789]0(-|\s)?\d{4}(-|\s)?\d{4}|0?50(-|\s)?\d{4}(-|\s)?\d{' \
             r'4})$'

    # USAGE: To capture all of the stripped numbers and validate them as japanese to add the 0 back on
    no_cc_nozro_jpn = r'^([1-9]{1}[1-9]\d{3}|[1-9]{2}\d{3}|[1-9]{2}\d{1}\d{2}|[1-9]{2}\d{2}\d{1})\d{4}|[789]0\d{4}\d{' \
                      r'4}|50\d{4}\d{4}$'

    # CASE 3: Finds cell phone numbers and IP phones with leading zero and no spaces/dash/country code
    # USAGE: Used first to add hypens to cell phone numbers
    cell_no_cc_w_zro_jpn = r'^0[789]0\d{4}\d{4}|050\d{4}\d{4}$'

    # CASE 4: No country code, with leading zero, no dash, no space
    # USAGE: Acts as safety to validate numbers for checks against area codes and formatting
    no_cc_jpn_w_zro = r'^(0([1-9]{1}[1-9]\d{3}|[1-9]{2}\d{3}|[1-9]{2}\d{1}\d{2}|[1-9]{2}\d{2}\d{1})\d{4}|0[789]0\d{' \
                      r'4}\d{4}|050\d{4}\d{4})$'

    # CASE 5: Finds cell phone numbers and IP phones with perfect, +81 0(7|8|9|5)0-0000-0000 formatting
    # USAGE: Used to copy japanese cell phone numbers from home phone field to mobile phone field if empty
    cell_pfct_jpn = r'^\+81 [789]0-\d{4}-\d{4}|\+81 50-\d{4}-\d{4}$'

    # CASE 6: no country code, with leading zero, with dash
    # USAGE: Acts as a safety to validate numbers for checks against area codes and formatting
    no_cc_jpn_w_zro_w_dsh = r'^(0([1-9]{1}-?[1-9]\d{3}|[1-9]{2}-?\d{3}|[1-9]{2}\d{1}-?\d{2}|[1-9]{2}\d{2}-?\d{' \
                            r'1})-?\d{4}|0[789]0-?\d{4}-?\d{4}|050-?\d{4}-?\d{4})$'

    # loop through each column in the dataframe, reformat the Japanese phone numbers, and add them to new columns
    for column in jpn_phone_df:

        # person ID is what we'll batch upload on, do not alter
        if column == 'Person ID':
            pass

        else:
            # strip whitespace from left and right of phone numbers
            jpn_phone_df[column] = jpn_phone_df[column].str.strip()

            # create formatted phone number columns and fill them with NaN
            # we will add the formatted numbers to these columns
            formatted_col_name = f'Formatted {column}'
            jpn_phone_df[formatted_col_name] = np.nan

            # move Japanese no-country-code numbers to formatted column
            # removing dashes and spaces, leaving only bare numbers
            jpn_phone_df.loc[(jpn_phone_df[column].str.fullmatch(no_cc_jpn, na=False)), formatted_col_name] = \
                jpn_phone_df[column].str.replace('-| ', '')

            # move all the +81 numbers to formatted column
            # removing dashes, spaces, and iterations of +81, leaving only bare numbers
            jpn_phone_df.loc[(jpn_phone_df[column].str.fullmatch(cc_jpn, na=False)), formatted_col_name] = \
                jpn_phone_df[column].str.replace('-| |^(\+?\s*\(?\+?81\)?\s*-?)', '')

            # now that we have clean, undashed, unspaced numbers,
            # lstrip any leading zeros, and add the leading 0 back to all numbers
            # adding the leading zero in allows us to match more accurately to the scraped area codes
            jpn_phone_df.loc[
                (jpn_phone_df[formatted_col_name].str.fullmatch(no_cc_nozro_jpn, na=False)), formatted_col_name] = \
                '0' + (jpn_phone_df[formatted_col_name]).str.lstrip('0')

            # Fullmatch and Add Hypen to all cell phones (numbers that start with 070/080/090/050)
            jpn_phone_df.loc[
                (jpn_phone_df[formatted_col_name].str.fullmatch(cell_no_cc_w_zro_jpn, na=False)), formatted_col_name] = \
                jpn_phone_df[formatted_col_name].str[:-8] + '-' + jpn_phone_df[formatted_col_name].str[-8:-4] + '-' + \
                jpn_phone_df[formatted_col_name].str[-4:]

            # Waterfall from longest area codes (4 digits incl leading zero) to shortest (2 digit incl leading zero).
            # no_cc_jpn_w_zro looks for unhyphenated phone numbers,
            # will not pick up completed numbers w/overlapping codes
            jpn_phone_df.loc[(jpn_phone_df[formatted_col_name].str.fullmatch(no_cc_jpn_w_zro, na=False)) & (
                jpn_phone_df[formatted_col_name].str[0:4].isin(four_digit_code)), formatted_col_name] = \
                jpn_phone_df[formatted_col_name].str[:-6] + '-' + jpn_phone_df[formatted_col_name].str[-6:-4] + '-' + \
                jpn_phone_df[formatted_col_name].str[-4:]

            jpn_phone_df.loc[(jpn_phone_df[formatted_col_name].str.fullmatch(no_cc_jpn_w_zro, na=False)) & (
                jpn_phone_df[formatted_col_name].str[0:3].isin(three_digit_code)), formatted_col_name] = \
                jpn_phone_df[formatted_col_name].str[:-7] + '-' + jpn_phone_df[formatted_col_name].str[-7:-4] + '-' + \
                jpn_phone_df[formatted_col_name].str[-4:]

            jpn_phone_df.loc[(jpn_phone_df[formatted_col_name].str.fullmatch(no_cc_jpn_w_zro, na=False)) & (
                jpn_phone_df[formatted_col_name].str[0:2].isin(two_digit_code)), formatted_col_name] = \
                jpn_phone_df[formatted_col_name].str[:-8] + '-' + jpn_phone_df[formatted_col_name].str[-8:-4] + '-' + \
                jpn_phone_df[formatted_col_name].str[-4:]

            # IMPERATIVE, this line copies any original values that are not formatted, to the new formatted phone columns
            # VC will delete numbers if the value is blank, this is just one safety measure to prevent that
            jpn_phone_df.loc[
                (jpn_phone_df[column].notnull()) & (jpn_phone_df[formatted_col_name].isnull()), formatted_col_name] = \
                jpn_phone_df[column]

            # lstrip the leading zero once more and add in the country code
            # Does so on japan-validated numbers as various validations at multiple steps increases accuracy
            jpn_phone_df.loc[
                (jpn_phone_df[formatted_col_name].str.fullmatch(no_cc_jpn_w_zro_w_dsh, na=False)), formatted_col_name] = \
                '+81 ' + jpn_phone_df[formatted_col_name].str.lstrip('0')

    if gen_csv:
        jpn_phone_df.to_csv('./data/jpn_phn_formatted.csv', index=False)
        print('jpn_phn_formatted.csv generated in ./data')

    else:
        pass

    return jpn_phone_df
