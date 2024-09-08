import pandas as pd
# import get_rates as r
import numpy as np  # Import numpy to use np.nan
import postal_code_generator as p


"""
Derives a list of unique country codes, using a list of unique combinations of country & province codes.
"""
def get_locations_from_country_codes():
  file_path = "country_codes_full.csv"
  codes_df = pd.read_csv(file_path)

  countries_set = set()

  for index, row in codes_df.iterrows():
    
    # country_prov = (row['Country Code'], row['Province code'], np.nan)
    # if not pd.isnull(row['Country code (ISO 2)']):
    countries_set.add(row['Country Code'])

  new_df = pd.DataFrame(list(countries_set), columns=['Country Code'])
  new_df = new_df.sort_values(by=['Country Code']).reset_index(drop=True)

  new_df.to_csv('country_codes_unique.csv', index=False)


"""
Derives a list of country-province code tuples, from the old shipping rates file.
"""
def get_locations_from_old_list():
  file_path = "old_shipping_data.csv"
  old_df = pd.read_csv(file_path)

  countries_set = set()

  for index, row in old_df.iterrows():
    country_prov = (row['Country code (ISO 2)'], row['Province code'], np.nan)
    if not pd.isnull(row['Country code (ISO 2)']):
      countries_set.add(country_prov)

  new_df = pd.DataFrame(list(countries_set), columns=['Country Code', 'Province Code', 'Postal Code'])
  new_df = new_df.sort_values(by=['Country Code', 'Province Code']).reset_index(drop=True)

  new_df.to_csv('shipping_locations.csv', index=False)


"""
Using a list of country codes (ISO 2), requests were sent to the API to check if the province code is requried. 
This is done to narrow down the number of requests to be sent in the final stage, and keep only the required shipping zones.
"""
def narrow_down_country_codes():
  locs_file_path= "country_codes_unique.csv"
  locs_df = pd.read_csv(locs_file_path)

  results = []

  for index, row in locs_df.iterrows():
    if index % 5 == 0:  # Check if we have reached the limit
      print(f"[{index}] done!")

    country_code = str(row['Country Code'])
    province_code = ""
    postal_code = ""
    
    # send request to api endpoint
    response = r.get_rates(country_code, province_code, postal_code) 

    formatted_res = {
      'Country Code' : country_code,
      'Success' : response['success'],
      'Message': ''
      
    }

    if (response['success'] != True):
      formatted_res['Message'] = response['errors']
    else:
      formatted_res['Message'] = len(response['rates'])

    results.append(formatted_res)


  results_df = pd.DataFrame(results)
  results_df.to_csv('api_results.csv', index=False)

  print("\n\n========DONE========")


"""
Given a csv filename with all country & province codes, filters only US/CA, generates postal codes for each entry.
Saves to new csv.
Used Filename: "country_codes_full.csv"
"""
def generate_US_CA_zones(file_name):

  df = pd.read_csv(file_name)
  df_us_ca = df[df["Country Code"].isin(["US", "CA"])]
  
  # For US/CA countries, generate postal/zip codes using get_postal_code
  df_us_ca["Postal Code"] = df_us_ca.apply(lambda row: p.get_postal_code(row["Country Code"], row["Province"], row["Province Code"]), axis=1)

  df_us_ca.to_csv("zones_US_CA.csv", index=False)
  


"""
Generates the final zones data file, including US and Canada with province/state & postal/zip codes

The file format it accepts:
Country,Country Code,Province,Province Code

This function will iterate through each row, 
  1. Eliminate all provinces/states for countries, except US & CA (since doesn't change price)
  2. For US & CA - generate and store a postal code using the get_postal_code function.
"""
def generate_final_zones_data():
  
  # file containing all country codes, including CA & US to be eliminated.
  df = pd.read_csv("country_codes_full.csv")

  df_other_countries = df[~df["Country Code"].isin(["US", "CA"])]
  df_us_ca = pd.read_csv("zones_US_CA.csv")

  # Remove province information & rows (unnecessary)
  df_other_countries = df_other_countries.drop_duplicates(subset=["Country", "Country Code"])
  df_other_countries["Province"] = ""
  df_other_countries["Province Code"] = ""
  df_other_countries["Postal Code"] = ""

  
  # Combine the filtered non-US/CA countries and updated US/CA rows
  df_final = pd.concat([df_other_countries, df_us_ca], ignore_index=True)

  # Save the final DataFrame to a CSV file
  df_final.to_csv("final_zones_data.csv", index=False)

  print("Final zones data has been generated and saved to final_zones_data.csv")


generate_final_zones_data()