import requests
from dotenv import load_dotenv
import os
import json

load_dotenv() # loads env vars: api url & key

def send_request(payload):
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv("STALLION_API_KEY")}"
  }

  rates_url = f"{os.getenv("STALLION_API_BASE_URL")}rates"

  response = requests.post(rates_url, json=payload, headers=headers).json()

  if response['success'] == True and len(response['rates']) != 0:
    return response['rates']
  else:
    return None


def avg_speed(delivery_days):
  
  result = 0

  if delivery_days:

    if '-' not in delivery_days:
      result =  int(delivery_days)

    else:
      total = 0
      for n in delivery_days.split('-'):
        total = total + int(n)

      result = total // 2

  # print(f"{delivery_days} => ({result})")
  return result


"""
Given a long string of shipping method, returns a short carrier name that matches most.
"""
def get_carrier(shipping_method):
  
  carriers = [
    "USPS",
    "FedEx",
    "PostNL",
    "APC",
    "UPS",
    "Canada Post",
    "Fleet Optics",
    "ICS",
    "UniUni",
  ]

  first_word = shipping_method.split()[0]

  for carrier in carriers:
    if first_word.lower() in carrier.lower():
      return carrier

  return first_word


def filter_rates(rates, country_code):
  # list of rates, 1st = cheapest, 2nd = trackable cheapest, (optional) 3rd = fastest delivery if not included.
  chosen_rates = []
  
  if country_code.upper() in ["CA", "US"]:
    chosen_rates.extend(rates[:3])

  else:

    # add the cheapest rate
    chosen_rates.append(rates[0])

    for i in range(1, len(rates)):
      if chosen_rates[0]["trackable"] or (not chosen_rates[0]["trackable"] and rates[i]["trackable"]):
        chosen_rates.append(rates[i])
        break

    fastest_rate = sorted(rates, key=lambda r: (avg_speed(str(r["delivery_days"]))))[0]
    
    # check if the fastest rate is already in chosen_rates based on price
    if not any(map(lambda r: r["total"] == fastest_rate["total"], chosen_rates)):
      # If the fastest rate's price is not in chosen_rates, add it
      chosen_rates.append(fastest_rate)

  return chosen_rates



def get_rates(country_code, province_code = "", postal_code = "", min_weight=0, max_weight=0.6):

  payload = {   # construct the payload for the request
    "to_address": {
      "name": "Testing Customer",
      "company": "string",
      "address1": "string", 
      "address2": "string",
      "city": "Rock Springs",
      "province_code": str(province_code) if str(province_code) != "nan" else "",
      "postal_code": str(postal_code) if str(postal_code) != "nan" else "",
      "country_code": str(country_code) if str(country_code) != "nan" else "",
      "phone": "string",
      "email": "example@gmail.com",
      "is_residential": True
    },
    "is_return": False,
    "weight_unit": "lbs",     
    "weight": max_weight,           
    "length": 25,             
    "width": 20,              
    "height": 2,              
    "size_unit": "cm",        
    "items": [                
      {
        "description": "Testing Book Rates",
        "sku": "SKU123",
        "quantity": 1,
        "value": 0.1,
        "currency": "CAD",
        "country_of_origin": "CA",
        "hs_code": "123456"
      }
    ],
    "package_type": "Large Envelope Or Flat", 
    "postage_types": [],
    "signature_confirmation": False,          
    "insured": False,                         
    "region": "ON",                           
  }

  rates = send_request(payload)
  
  # if response didn't contain rates/ error occured, return nothing
  if not rates:
    return None

  # list of rates, 1st = cheapest, 2nd = trackable cheapest, (optional) 3rd = fastest delivery if not included.
  chosen_rates = filter_rates(rates, country_code)

  formatted_rates = []

  for rate in chosen_rates:

    shipping_method = str(rate["postage_type"])
    carrier = get_carrier(shipping_method)
    
    if "tracked" not in shipping_method.lower():
      shipping_method = shipping_method + (" Untracked" if rate['trackable'] == False else " Tracked")
    
    if rate['delivery_days'] != '':
      shipping_method = f"{shipping_method} {str(rate['delivery_days'])} Days"

    # update the rate in place.
    r = {
        'Shipping method': shipping_method,
        'Carrier': carrier,
        'Minimal weight': min_weight,
        'Maximal weight': max_weight,
        'Minimal price': None,
        'Maximal price': None,
        'Price': rate["total"],
        'Country code (ISO 2)': country_code,
        'Province code': province_code
    }

    formatted_rates.append(r)
  
  return formatted_rates


# rates = get_rates("US", "FM", "96941")
# if rates:
#   print(json.dumps(rates, indent=4))
# else:
#   print("NO RATES")
