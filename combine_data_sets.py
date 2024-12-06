import pandas as pd
import re

def normalize_address(address):
    address = re.sub(r"-\d+$", "", address.strip())
    match = re.search(r'[\wäöüõÄÖÜÕ]+(?:\s[\wäöüõÄÖÜÕ]+)*\s+\d+', address)
    if match:
        return match.group(0).strip()
    return address.strip()

def expand_accessibility_addresses(row):
    raw_addresses = row['Aadress'].split("//")
    addresses = []
    street_name = ""
    
    for raw_address in raw_addresses:
        normalized = normalize_address(raw_address)
        match = re.search(r'([\wäöüõÄÖÜÕ\s]+)\s+\d+', normalized)
        if match:
            street_name = match.group(1).strip()
            addresses.append(normalized)
        else:
            if street_name:
                addresses.append(f"{street_name} {normalized}")
    
    return [(addr, row['Teenustase']) for addr in addresses]

def create_alternative_address(address):
    if " tn" in address:
        return address.replace(" tn", "")
    else:
        return re.sub(r'(\D+?)\s*(\d+)', r'\1 tn \2', address)

def match_accessibility(kv_address, accessibility_df):
    match = accessibility_df[accessibility_df['Normalized_Aadress'] == kv_address]
    if not match.empty:
        return match.iloc[0]['Teenustase']
    
    alternative = create_alternative_address(kv_address)
    match = accessibility_df[accessibility_df['Normalized_Aadress'] == alternative]
    if not match.empty:
        return match.iloc[0]['Teenustase']
    
    return "-"

def match_noise_pollution(kv_address, noise_df, fallback_value):
    match = noise_df[noise_df['lahiaadres'] == kv_address]
    if not match.empty:
        return match.iloc[0]['MYRAKLASS']
    
    alternative = create_alternative_address(kv_address)
    match = noise_df[noise_df['lahiaadres'] == alternative]
    if not match.empty:
        return match.iloc[0]['MYRAKLASS']
    
    return fallback_value


if __name__ == "__main__":
 
    kv_listings = pd.read_csv("data/kv_listings.csv")
    accessibility = pd.read_csv("data/accessibility.csv")
    noise_pollution = pd.read_csv("data/noise_pollution.csv")

    noise_pollution_tartu = noise_pollution[noise_pollution['taisaadres'].str.contains("Tartu", case=False, na=False)]
    noise_pollution_filtered = noise_pollution_tartu[['lahiaadres', 'MYRAKLASS']]
    noise_pollution_filtered.loc[:, 'MYRAKLASS'] = noise_pollution_filtered['MYRAKLASS'].astype(int)

    mean_myraklass = noise_pollution_filtered['MYRAKLASS'].mean()

    expanded_accessibility = accessibility.apply(
        expand_accessibility_addresses, axis=1
    ).explode().reset_index(drop=True)

    expanded_accessibility_df = pd.DataFrame(
        expanded_accessibility.tolist(), columns=['Normalized_Aadress', 'Teenustase']
    )

    kv_listings['Normalized_Address'] = kv_listings['Address'].apply(normalize_address)

    kv_listings['Accessibility'] = kv_listings['Normalized_Address'].apply(
        lambda addr: match_accessibility(addr, expanded_accessibility_df)
    )

    kv_listings['MYRAKLASS'] = kv_listings['Normalized_Address'].apply(
        lambda addr: match_noise_pollution(addr, noise_pollution_filtered, mean_myraklass)
    )

    kv_listings['MYRAKLASS'] = pd.to_numeric(kv_listings['MYRAKLASS'], errors='coerce')

    kv_listings = kv_listings.drop(columns=['Normalized_Address'])

    kv_listings.to_csv("data/kv_listings_with_accessibility_and_noise.csv", index=False)

    print("Dataset updated and saved as 'data/kv_listings_with_accessibility_and_noise.csv'")
