import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

URL = "https://fearfreepets.com/fear-free-directory?p=1&address=95110&category=0&center=37.354611%2C-121.918866&zoom=12&is_mile=1&directory_radius=100&view=grid&filter=1&field_role=Veterinarian"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

r = requests.get(URL, headers=headers)
# print(r.status_code)

soup = BeautifulSoup(r.content, 'html5lib')
# print(soup.prettify())

vets = soup.find_all("div", id=re.compile("sabai-entity-content-")) #158695 

ids =[int(vet['id'].replace("sabai-entity-content-", '')) for vet in vets]
clinics = [
    vet.find("div", class_="sabai-directory-custom-fields-practice-individual-summary").get_text(strip=True)
    if vet.find("div", class_="sabai-directory-custom-fields-practice-individual-summary") is not None else ''
    for vet in vets]
names = [vet.find('a').get_text(strip=True).replace('Dr. ', '') for vet in vets]
locations = [
    vet.find('span', class_='sabai-googlemaps-address sabai-googlemaps-address-0').get_text(strip=True)
    for vet in vets
]
locations = [re.sub(r"\s*,", ",", address) for address in locations]

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
        return match.group(1).strip()
    return None

def get_state(address):
    pattern = r",*\s*([A-Z]{2})\s*"
    match = re.search(pattern, address)
    if match:
        return match.group(1).strip()
    return None

streets = [get_street_info(address) for address in locations]
cities = [get_city(address) for address in locations]
states = [get_state(address) for address in locations]
zipcodes = [get_zip_code(address) for address in locations]
phones = [vet.find('span', itemprop='telephone').get_text(strip=True) 
if vet.find('span', itemprop='telephone') is not None else '' for vet in vets]
websites = [
    vet.find('div', class_='sabai-directory-contact-website').find('a')['href'] 
    if vet.find('div', class_='sabai-directory-contact-website') is not None else ''
    for vet in vets
    ]
print(locations)
print(streets)