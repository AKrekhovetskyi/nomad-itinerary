import json
import re
from pathlib import Path

import pandas as pd

ALIASES = {
    "Czechia": "Czech Republic",
    "Viet Nam": "Vietnam",
    "The Gambia": "Gambia",
    "Kyrgyzstan": "Kyrgyz Republic",
    "DR Congo": "Democratic Republic of the Congo",
    "Congo": "Republic of the Congo",
    "United States": "United States of America",
    "US": "United States of America",
    "USA": "United States of America",
    "Turkiye": "Turkey",
    "East Timor": "Timor-Leste",
    "The Bahamas": "Bahamas",
}


def normalize_country(name: str) -> str | None:
    if pd.isna(name):
        return None

    name = name.strip()

    if name in ALIASES:
        name = ALIASES[name]
    return name


def detect_missing_values(
    file_path="Work & Travel.xlsx",
    first_sheet_name="By cost of living (2025)",
    second_sheet_name="By infrastructure",
    common_column_name="Country",
):

    df_first = pd.read_excel(file_path, sheet_name=first_sheet_name)
    df_second = pd.read_excel(file_path, sheet_name=second_sheet_name)
    first_df_values = df_first[common_column_name].to_list()
    for country_name in df_second[common_column_name]:
        if country_name not in first_df_values:
            print(country_name)


def format_converter(file_path="Work & Travel example.xlsx", convert_to="csv"):
    df = pd.read_excel(file_path)
    getattr(df, f"to_{convert_to}")(f"{file_path.split('.')[0]}.{convert_to}")


def parse_infrastructure_data():
    infrastructure_data = json.loads(Path("infrastructure.json").read_text())
    re_country = r"<a\s?href='https://theworldtravelindex\.com/en/.*?/.*?'>(.*?)</a>"
    country_to_score_map = {"Country": [], "Infrastructure score": []}
    for item in infrastructure_data["data"]:
        country_to_score_map["Country"].append(re.search(re_country, item[1]).group(1))
        country_to_score_map["Infrastructure score"].append(float(item[3]))
    df = pd.DataFrame.from_dict(country_to_score_map)
    df["Country"] = df["Country"].apply(normalize_country)

    print(df)
    return df


visa = {
    "Monaco": "Not required",
    "Cayman Islands": "Required",
    "Singapore": "Required",
    "Switzerland": "Not required",
    "Iceland": "Not required",
    "Hong Kong": "Not required",
    "Bahamas": "Required",
    "Luxembourg": "Not required",
    "Ireland": "Required",
    "United States of America": "Required",
    "Liechtenstein": "Not required",
    "United Kingdom": "Required",
    "Netherlands": "Not required",
    "Australia": "Required",
    "Norway": "Not required",
    "Denmark": "Not required",
    "Israel": "Not required",
    "United Arab Emirates": "Not required",
    "Canada": "Required",
    "Austria": "Not required",
    "Vanuatu": "Not required",
    "Qatar": "Not required",
    "Andorra": "Not required",
    "Turkmenistan": "Required",
    "Germany": "Not required",
    "Belgium": "Not required",
    "New Zealand": "Required",
    "France": "Not required",
    "Sweden": "Not required",
    "Cyprus": "Not required",
    "Malta": "Not required",
    "Finland": "Not required",
    "Italy": "Not required",
    "Seychelles": "Required",
    "Spain": "Not required",
    "Marshall Islands": "Not required",
    "Curacao": "Not required",
    "Slovenia": "Not required",
    "Kuwait": "Required",
    "Portugal": "Not required",
    "Solomon Islands": "Required",
    "Estonia": "Not required",
    "Czech Republic": "Not required",
    "Croatia": "Not required",
    "Maldives": "Required",
    "Barbados": "Not required",
    "Poland": "Not required",
    "Saint Kitts and Nevis": "Not required",
    "Equatorial Guinea": "Required",
    "Sierra Leone": "Required",
    "San Marino": "Not required",
    "Uruguay": "Not required",
    "Panama": "Not required",
    "Slovakia": "Not required",
    "Costa Rica": "Not required",
    "Saudi Arabia": "Required",
    "Greece": "Not required",
    "Lithuania": "Not required",
    "Bahrain": "Required",
    "Cuba": "Required",
    "Ethiopia": "Required",
    "Comoros": "Required",
    "Jamaica": "Not required",
    "Ivory Coast": "Required",
    "Palau": "Required",
    "Saint Lucia": "Required",
    "Latvia": "Not required",
    "Niger": "Required",
    "El Salvador": "Not required",
    "Guyana": "Required",
    "Laos": "Required",
    "Senegal": "Required",
    "South Korea": "Not required",
    "Antigua and Barbuda": "Not required",
    "Japan": "Not required",
    "Trinidad and Tobago": "Required",
    "Lebanon": "Required",
    "Hungary": "Not required",
    "Serbia": "Not required",
    "Brunei": "Not required",
    "Armenia": "Not required",
    "Grenada": "Not required",
    "Montenegro": "Not required",
    "Democratic Republic of the Congo": "Required",
    "Taiwan": "Required",
    "Sao Tome and Principe": "Required",
    "Guinea": "Required",
    "Dominica": "Not required",
    "Belize": "Required",
    "Albania": "Not required",
    "Oman": "Not required",
    "Tonga": "Required",
    "South Africa": "Required",
    "Mexico": "Required",
    "Saint Vincent": "Not required",
    "Palestine": "Not required",
    "Cape Verde": "Required",
    "Guatemala": "Not required",
    "Chile": "Not required",
    "Bulgaria": "Not required",
    "Mozambique": "Required",
    "Romania": "Not required",
    "Namibia": "Required",
    "Georgia": "Not required",
    "Burkina Faso": "Required",
    "Jordan": "Required",
    "Sudan": "Required",
    "Russia": "Not required",
    "Turkey": "Not required",
    "Guinea-Bissau": "Required",
    "Cameroon": "Required",
    "Suriname": "Required",
    "Nigeria": "Required",
    "Angola": "Required",
    "Zimbabwe": "Required",
    "Mongolia": "Not required",
    "Moldova": "Not required",
    "Peru": "Not required",
    "Thailand": "Not required",
    "Argentina": "Not required",
    "Ecuador": "Not required",
    "Colombia": "Not required",
    "Fiji": "Not required",
    "Honduras": "Not required",
    "Togo": "Required",
    "Venezuela": "Required",
    "Mauritius": "Not required",
    "Dominican Republic": "Not required",
    "Bosnia and Herzegovina": "Not required",
    "Cambodia": "Required",
    "Iraq": "Required",
    "Zambia": "Required",
    "Benin": "Required",
    "Samoa": "Required",
    "North Macedonia": "Not required",
    "Azerbaijan": "Not required",
    "Burundi": "Required",
    "Nauru": "Required",
    "Nicaragua": "Not required",
    "Morocco": "Required",
    "Brazil": "Not required",
    "Kenya": "Required",
    "Bolivia": "Required",
    "Tanzania": "Required",
    "Somalia": "Required",
    "Gabon": "Required",
    "Rwanda": "Required",
    "Malaysia": "Not required",
    "Tajikistan": "Not required",
    "Tuvalu": "Required",
    "Kyrgyz Republic": "Not required",
    "Uzbekistan": "Not required",
    "Uganda": "Required",
    "Mauritania": "Required",
    "Paraguay": "Not required",
    "Kazakhstan": "Not required",
    "China": "Required",
    "Ukraine": "Not required",
    "Lesotho": "Required",
    "Ghana": "Required",
    "Botswana": "Required",
    "Vietnam": "Required",
    "Philippines": "Required",
    "Myanmar": "Required",
    "Iran": "Required",
    "Djibouti": "Required",
    "Indonesia": "Required",
    "Mali": "Required",
    "Belarus": "Not required",
    "Gambia": "Required",
    "Sri Lanka": "Required",
    "Papua New Guinea": "Required",
    "Haiti": "Not required",
    "Malawi": "Required",
    "Syria": "Required",
    "Yemen": "Required",
    "Chad": "Required",
    "Madagascar": "Required",
    "Kiribati": "Not required",
    "Liberia": "Required",
    "Eritrea": "Required",
    "Central African Republic": "Required",
    "South Sudan": "Required",
    "Timor-Leste": "Required",
    "Eswatini": "Not required",
    "Tunisia": "Not required",
    "Algeria": "Required",
    "Afghanistan": "Required",
    "India": "Required",
    "Bangladesh": "Required",
    "Bhutan": "Required",
    "Libya": "Required",
    "Egypt": "Required",
    "Pakistan": "Required",
    "Nepal": "Required",
}


def convert_visa():
    visa_to_df = {"Country": [], "Visa required": []}
    for country, requirement in visa.items():
        visa_to_df["Country"].append(country)
        if requirement == "Required":
            visa_to_df["Visa required"].append(50)
        else:
            visa_to_df["Visa required"].append(100)

    df = pd.DataFrame.from_dict(visa_to_df)
    df["Country"] = df["Country"].apply(normalize_country)
    df.to_csv("ai_generated_visa_requirements.csv")

    print(df)


if __name__ == "__main__":
    convert_visa()
