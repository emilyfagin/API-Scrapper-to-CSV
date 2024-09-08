import pandas as pd
import numpy as np  # Import numpy to use np.nan
import get_rates as r
import json

failed_set = set()
zones_df = pd.read_csv("final_zones_data.csv", keep_default_na=False)
# zones_df = pd.read_csv("zones_US_CA.csv", keep_default_na=False)
weight_points = [0, 0.6, 1.2]

def produce_weight_sheet(min_weight, max_weight):
  
  rates_list = []
  
  for index, row in zones_df.iterrows():
    # if index < 5:
      
      rates = r.get_rates(row['Country Code'], row['Province Code'], row['Postal Code'], min_weight, max_weight)
      
      if rates:
        print(f"({len(rates)}) rates for [{min_weight}-{max_weight}] === {row['Country']}, {row['Country Code']}")
        rates_list.extend(rates)
      else:
        if str(row['Province Code']) == "nan":
          failed_set.add((str(row["Country Code"]), str(row["Country"])))
          print(f"{row["Country Code"]} ------- NONE FOUND:")
        else:
          failed_set.add((str(row["Country Code"]), str(row["Country"]), str(row['Province Code'])))
          print(f"{row["Country Code"]}-{str(row['Province Code'])} ------- NONE FOUND:")

  rates_df = pd.DataFrame(rates_list, columns=[
    'Shipping method',
    'Carrier',
    'Minimal weight',
    'Maximal weight',
    'Minimal price',
    'Maximal price',
    'Price',
    'Country code (ISO 2)',
    'Province code'
  ])

  rates_df = rates_df.fillna("")
  rates_df.to_csv(f"shipping_rates({min_weight}-{max_weight}).csv", index=False)
  rates_df = rates_df.sort_values(
    by=['Country code (ISO 2)', 'Province code', 'Maximal weight', 'Price'],
    ascending=[True, True, True, True]
  )

  print(f"Sheet for the weight class [{min_weight}-{max_weight}] generated.....")

  return rates_list


"""
Generates a json file with the codes & names of the countries that failed to get a rate
"""
def generate_failed_json():

  failed_list = []

  for item in failed_set:
    if len(item) == 2:
      failed_list.append({
        "Country Code": item[0],
        "Country": item[1]
      })
    else:
      failed_list.append({
        "Country Code": item[0],
        "Country": item[1],
        "Province Code": item[2]
      })


  with open("failed.json", 'w') as file:
    json.dump(failed_list, file, indent=4)



def produce_final_sheet(final_sheet_name):

  complete_list = []

  for i in range(1, len(weight_points)):
    min_weight = weight_points[i-1]
    max_weight = weight_points[i]

    complete_list.extend(produce_weight_sheet(min_weight, max_weight))

  rates_df = pd.DataFrame(complete_list, columns=[
    'Shipping method', 
    'Carrier', 
    'Minimal weight', 
    'Maximal weight', 
    'Minimal price', 
    'Maximal price', 
    'Price', 
    'Country code (ISO 2)', 
    'Province code'
  ])

  rates_df = rates_df.fillna("")

  sorted_df = rates_df.sort_values(
    by=['Country code (ISO 2)', 'Province code', 'Maximal weight', 'Price'],
    ascending=[True, True, True, True]
  )

  sorted_df.to_csv(f"{final_sheet_name}.csv", index=False)

  generate_failed_json()


produce_final_sheet("full_shipping_rates")

