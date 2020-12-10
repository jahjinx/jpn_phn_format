import pandas as pd
import pickle
import random
import numpy as np


def bad_jpn_phn(total, area_code_pkl='./data/area_code_lists.pkl', gen_csv=False, insert_null=False):
    # area code lists load in
    with open(area_code_pkl, 'rb') as f:
        two_digit_code, three_digit_code, four_digit_code, five_digit_code, six_digit_code, outlier_check = pickle.load(f)

    # options for country codes
    country_code = ['81', '+81', '(81)', '(+81)', ' 81', ' +81', ' (81)', ' (+81)', '81 ', '+81 ', '(81) ', '(+81) ',
                    ' 81 ', ' +81 ', ' (81) ', ' (+81) ']
    country_codeless = ['', ' ']

    # options for area codes
    # All Japanese phone numbers are 10 digits long (11 if 0 is appended to the area code)
    # We'll just use two-digit codes so that we don't have to account for number length beyond 10 or 11 digits
    area_codes = two_digit_code
    area_codes_zeroless = [x.lstrip('0') for x in area_codes]

    # 050 is japanese IP phone, the rest are mobile codes
    mobile_codes = ['080', '070', '090', '050']
    mobile_codes_zeroless = [x.lstrip('0') for x in mobile_codes]

    # Lets guess all the places people can place a space, dash, or nothing all together
    inner_delineation = [' ', '', '-']
    outer_delineation = [' ', '']

    # Dump all generated numbers to a list
    jpn_phn_list = []

    for i in range(total):
        # collate grouped lists above so that no larger set of values are outweighed by a smaller set of values
        rand_prefix = random.choice([country_code, country_codeless])
        rand_area_mobile_code = random.choice([area_codes, area_codes_zeroless, mobile_codes_zeroless, mobile_codes])
        rand_inner_delineation = random.choice([inner_delineation, ['']])

        # after the country code and area/mobile code, we need two unique groups of four random numbers
        second_four = random.randint(1000, 9999)
        third_four = random.randint(1000, 9999)

        # option for four-by-four spacing
        # if we want another pattern, we can do if i % 2 == 0, etc.
        random_phone = random.choice(rand_prefix) + random.choice(outer_delineation) + \
                       str(random.choice(rand_area_mobile_code)) + random.choice(rand_inner_delineation) + \
                       str(second_four) + random.choice(rand_inner_delineation) + str(third_four)

        jpn_phn_list.append(random_phone)

    if gen_csv:
        person_ids = random.sample(range(1, total + 1), total)
        phone_dict = {'Home Phone': bad_jpn_phn(total), 'Business Phone': bad_jpn_phn(total)}

        if insert_null:
            # generate df from dict
            gen_csv_df = pd.DataFrame(phone_dict)
            # randomly replace 20% of values with NaN
            gen_csv_df = gen_csv_df.mask(np.random.random(gen_csv_df.shape) < .2)
            # assign person id column to dataframe
            gen_csv_df['Person ID'] = person_ids
            # reorder columns
            gen_csv_df = gen_csv_df[['Person ID', 'Home Phone', 'Business Phone']]
            # export to csv
            gen_csv_df.to_csv('./data/test_phones.csv', index=False)

        else:
            # generate df from dict
            gen_csv_df = pd.DataFrame(phone_dict)
            # assign person id column to dataframe
            gen_csv_df['Person ID'] = person_ids
            # reorder columns
            gen_csv_df = gen_csv_df[['Person ID', 'Home Phone', 'Business Phone']]
            # export to csv
            gen_csv_df.to_csv('./data/test_phones.csv', index=False)

        print('test.csv generated in ./data')

    else:
        return jpn_phn_list
