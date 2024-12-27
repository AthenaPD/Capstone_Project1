import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}


def get_zip_code(address):
    zipcode_pattern = r"\b\d{5}\b"
    match = re.search(zipcode_pattern, address)
    if match:
        return match.group().strip()
    return None

def get_street_info(address):
    pattern = r"(\d+\s+[a-zA-z\s]+\s*),\s*\w+\s*\w*\s*,*\s*([A-Z]{2})\s*"
    match = re.search(pattern, address)
    if match:
        return match.group(1).strip()
    return None

def get_city(address):
    pattern = r",*\s*(\w+\s*\w*)\s*,*\s*([A-Z]{2})\s*"
    match = re.search(pattern, address)
    if match:
        return match.group(1).strip().lower().title()
    return None

def get_state(address):
    pattern = r",*\s*([A-Z]{2})\s*"
    match = re.search(pattern, address)
    if match:
        return match.group(1).strip().upper()
    return None


def get_page_data(num_page=1, headers=HEADERS):
    """
    This function 
    1) accept the page number and header
    2) scrape the vets' data
    3) save each vet into a dictionary, which is added to a list of vets
    4) output the vets list
    """
    url = f"https://fearfreepets.com/fear-free-directory?p={num_page}&address=95110&category=0&center=37.354611%2C-121.918866&zoom=12&is_mile=1&directory_radius=100&view=grid&filter=1&field_role=Veterinarian"
    
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    vets = soup.find_all("div", id=re.compile("sabai-entity-content-"))
    ids =[int(vet['id'].replace("sabai-entity-content-", '')) for vet in vets]
    clinics = [
        vet.find("div", class_="sabai-directory-custom-fields-practice-individual-summary").get_text(strip=True)
        if vet.find("div", class_="sabai-directory-custom-fields-practice-individual-summary") is not None 
        else vet.find('a').get_text(strip=True).replace('Dr. ', '').replace('&', 'and') for vet in vets]
    names = [vet.find('a').get_text(strip=True).replace('Dr. ', '').replace('&', 'and') for vet in vets]
    locations = [
        vet.find('span', class_='sabai-googlemaps-address sabai-googlemaps-address-0').get_text(strip=True)
        for vet in vets]
    streets = [get_street_info(address) for address in locations]
    cities = [get_city(address) for address in locations]
    states = [get_state(address) for address in locations]
    zipcodes = [get_zip_code(address) for address in locations]
    phones = [vet.find('span', itemprop='telephone').get_text(strip=True) 
              if vet.find('span', itemprop='telephone') is not None else '' for vet in vets]
    websites = [
        vet.find('div', class_='sabai-directory-contact-website').find('a')['href'] 
        if vet.find('div', class_='sabai-directory-contact-website') is not None else ''
        for vet in vets]
    
    return clinics, streets, cities, states, zipcodes, phones, websites, names, ids

def get_95110_data(tot_pages=11):

    clinic_list = []
    street_list = []
    city_list = []
    state_list = []
    zipcode_list = []
    phone_list = []
    website_list = []
    vet_list = []
    ffid_list = []

    for i in range(tot_pages):
        clinics, streets, cities, states, zipcodes, phones, websites, vets, ffids = get_page_data(num_page=i+1, headers=HEADERS)
        print(f'Got page {i+1}')
        clinic_list.extend(clinics)
        street_list.extend(streets)
        city_list.extend(cities)
        state_list.extend(states)
        zipcode_list.extend(zipcodes)
        phone_list.extend(phones)
        website_list.extend(websites)
        vet_list.extend(vets)
        ffid_list.extend(ffids)

    clinics_dict = dict(name=clinic_list, street_address=street_list, city=city_list, state=state_list,
                        zip_code=zipcode_list, phone=phone_list, website=website_list)
    clinics_pd = pd.DataFrame(clinics_dict)
    clinics_pd['name_upper'] = clinics_pd['name'].astype(str).str.upper()
    clinics_pd['city_upper'] = clinics_pd['city'].astype(str).str.upper()
    clinics_pd.drop_duplicates(subset=['name_upper', 'city_upper', 'zip_code'], inplace=True, ignore_index=True, 
                               keep='last')
    clinics_pd['db_id'] = clinics_pd.index + 1

    vets_dict = dict(name=vet_list, fear_free_id=ffid_list, clinic=clinic_list, street_address=street_list, 
                     city=city_list, state=state_list, zip_code=zipcode_list)
    vets_pd_no_id = pd.DataFrame(vets_dict)
    vets_pd_no_id['clinic_upper'] = vets_pd_no_id['clinic'].astype(str).str.upper()
    vets_pd_no_id['city_upper'] = vets_pd_no_id['city'].astype(str).str.upper()
    vets_pd = vets_pd_no_id.merge(clinics_pd[['name_upper', 'street_address', 'city_upper', 'state', 'zip_code', 'db_id']], 
                                  how='left', 
                                  left_on=['clinic_upper', 'city_upper', 'zip_code'], 
                                  right_on=['name_upper', 'city_upper', 'zip_code'])

    

    clinics_pd.drop(['name_upper', 'city_upper'], axis=1, inplace=True)
    clinics_pd.to_csv("clinics_debug.csv", index=False)
    clinics_pd.drop('db_id', inplace=True)
    clinics_pd.to_csv("clinics.csv", index=False)

    vets_pd.drop(['clinic_upper', 'city_upper', 'clinics', ], axis=1, inplace=True)
    vets_pd.to_csv('vets_debug.csv', index=False)
    vets_pd.drop(['clinics', 'street_address_x', 'city', 'state_x', 'zip_code', 'name_upper', 
                  'street_address_y', 'state_y'], axis=1, inplace=True)
    vets_pd.rename(columns={'db_id': 'clinic_id'}, inplace=True)
    vets_pd.drop_duplicates(subset=['name', 'clinic_id'], inplace=True, ignore_index=True)
    vets_pd.to_csv('vets.csv', index=False)

get_95110_data()
