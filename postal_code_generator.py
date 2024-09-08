import pgeocode
import requests
from dotenv import load_dotenv
import os

load_dotenv()

"""
Sends api request to retrieve the capital city of the state/province.
Returns the capital if request is successful, otherwise none.
"""
def get_capital(country_code, prov_code):  
  headers = {
    'x-rapidapi-key': str(os.getenv("RAPID_API_KEY")),
    'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
  }
    
  response = requests.get(f"https://wft-geo-db.p.rapidapi.com/v1/geo/countries/{country_code}/regions/{prov_code}", headers=headers)

  if response.status_code == 200:
    return response.json()['data']['capital']
  else:
    return None
  

"""
Returns a bunch of cities/places in the province/state
"""
def get_places(country_code, prov_code):
  headers = {
    'x-rapidapi-key': str(os.getenv("RAPID_API_KEY")),
    'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
  }
    
  response = requests.get(f"https://wft-geo-db.p.rapidapi.com/v1/geo/countries/{country_code}/regions/{prov_code}/places", headers=headers)

  if response.status_code == 200:
    return response.json()['data']
  else:
    return None


"""
Generates a postal/zip code from the provided country code, 
and province/state name (prov_name).
"""
def get_postal_code(country_code, prov_name, prov_code):
  print(f"{country_code}-{prov_name}-{prov_code}")
  nomi = pgeocode.Nominatim(country_code.upper())

  loc_info = nomi.query_location(prov_name, top_k=10)
  
  valid_found = None

  def get_found_index(loc_info):
    valid_found = None
    for i in range(len(loc_info)):
      if loc_info['state_code'].iloc[i].upper() == prov_code:
        print("=====================VALID FOUND=====================")
        print(f"State: {loc_info['state_name'].iloc[i]}\t\t=> {loc_info['postal_code'].iloc[i]}")
        print("=====================================================")
        valid_found = i + 1 # to avoid 0 index being classified as False
        break
    return valid_found

  if not loc_info.empty:
    valid_found = get_found_index(loc_info)
  
  # if province name didn't return a valid postal code, try with capital
  if not valid_found:
    
    capital = get_capital(country_code, prov_code)
    if capital:
      print(f"Capital found: {capital}")
      loc_info = nomi.query_location(capital, top_k=50)
      print(loc_info)
      valid_found = get_found_index(loc_info)
  
  if not valid_found:
    cities = get_places(country_code, prov_code)
    if cities and len(cities) > 0:
      for city in cities:
        print(f"CITY: {city['name']}")

  # if still invalid return, return None.
  if valid_found:

    postal_code = loc_info['postal_code'].iloc[valid_found - 1] # ensure index notation by subtracting 1

    # complete Canadian postal code if it is only the first 3 characters
    if country_code.upper() == "CA" and len(postal_code) == 3:
      postal_code = postal_code + " 1A1"

    print(f"|{postal_code}|")
    return postal_code
  
  else:
    return None

  
# print(pgeocode.Nominatim('US').query_location("Samoa", top_k=2))
# print(pgeocode.Nominatim('US').query_location("Charleston", top_k=50))
# print(pgeocode.Nominatim('US').query_location("Concord", top_k=50))
# print(pgeocode.Nominatim('US').query_postal_code("96799"))

# print(get_postal_code("US", "Vermont", "VT"))