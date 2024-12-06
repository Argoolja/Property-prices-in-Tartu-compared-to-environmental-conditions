import pandas as pd
import re

kv_listings = pd.read_csv("data/kv_listings.csv")
accessibility = pd.read_csv("data/accessibility.csv")

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


expanded_accessibility = accessibility.apply(
    expand_accessibility_addresses, axis=1
).explode().reset_index(drop=True)

expanded_accessibility_df = pd.DataFrame(
    expanded_accessibility.tolist(), columns=['Normalized_Aadress', 'Teenustase']
)

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

kv_listings['Normalized_Address'] = kv_listings['Address'].apply(normalize_address)

kv_listings['Accessibility'] = kv_listings['Normalized_Address'].apply(
    lambda addr: match_accessibility(addr, expanded_accessibility_df)
)

kv_listings = kv_listings.drop(columns=['Normalized_Address'])

kv_listings.to_csv("data/kv_listings_with_accessibility.csv", index=False)

print("Dataset updated and saved as 'data/kv_listings_with_accessibility.csv'")
