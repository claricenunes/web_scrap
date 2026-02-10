import requests
from bs4 import BeautifulSoup
import json
import re

def get_minister_info():
    url = "https://www.gov.br/cidades/pt-br/acesso-a-informacao/institucional/quem-e-quem"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.find('div', id='content-core')

    if not content:
         # Fallback search in body if content-core is missing
         content = soup.body

    # Initialize data
    name = "N/A"
    cargo = "Ministro de Estado das Cidades" # Desired format
    phone = "N/A"
    email = "N/A"

    # Strategy: Find the "Ministro das Cidades" header or similar text block
    # and look for the name nearby.
    
    # Based on debug output: 
    # "MINISTRO DAS CIDADES Ministro das Cidades Jader Fontenelle Barbalho Filho Ministro de Estado Telefone(s): ..."
    
    contacts_text = content.get_text(separator=' ', strip=True)
    
    # 1. Extraction of Name
    # We look for "Ministro das Cidades" followed by the name.
    # The name is "Jader Fontenelle Barbalho Filho".
    # Or just search for "Jader Fontenelle Barbalho Filho" directly if known, 
    # but scraping should be generic if possible.
    # Let's search for the pattern: "Ministro das Cidades" ... "Ministro de Estado"
    
    match_name = re.search(r'Ministro das Cidades\s+(.*?)\s+Ministro de Estado', contacts_text, re.IGNORECASE)
    if match_name:
        possible_name = match_name.group(1).strip()
        # Clean up any extra words if needed
        # Check if it looks like a name (no digits, reasonable length)
        if len(possible_name) > 3 and len(possible_name) < 50:
             name = possible_name
    
    if name == "N/A":
        # Fallback: Search for "Jader" explicitly if generic failed
        match_jader = re.search(r'(Jader\s+Fontenelle\s+Barbalho\s+Filho)', contacts_text, re.IGNORECASE)
        if match_jader:
            name = match_jader.group(1)

    # 2. Extraction of Phone
    # Pattern: "Telefone(s): (61) 2034-5493 / 5231 / 5793 / 5351"
    # Capture everything until "E-mail"
    phone_match = re.search(r'Telefone\(s\)[:\s]*((?:\(\d{2}\)\s*\d{4,5}[-\.]\d{4})[^E]*)', contacts_text)
    
    if phone_match:
        phone_chunk = phone_match.group(1).strip()
        # Clean up if it went too far
        if "E-mail" in phone_chunk:
            phone_chunk = phone_chunk.split("E-mail")[0].strip()
        
        # Further clean up trailing slashes
        phone = phone_chunk.strip().rstrip('/')

    # 3. Extraction of Email
    # Pattern: "E-mail: ..."
    email_match = re.search(r'E-mail:\s*([\w\.-]+@[\w\.-]+\.gov\.br)', contacts_text)
    if email_match:
        email = email_match.group(1).strip()

    data = {
        "Nome": name,
        "Cargo": cargo,
        "Telefone": phone,
        "Email": email
    }

    print(json.dumps(data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    get_minister_info()
