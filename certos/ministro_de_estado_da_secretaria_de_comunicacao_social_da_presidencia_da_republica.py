import requests
from bs4 import BeautifulSoup
import json

def get_minister_info():
    url = "https://www.gov.br/secom/pt-br/acesso-a-informacao/institucional/quem-e-quem"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Strategy: Find the cargo paragraph that contains "Ministro de Estado" or "Ministra de Estado"
    # and then get the parent container to extract other details.
    
    cargo_element = soup.find(lambda tag: tag.name == "p" and "cargo" in tag.get("class", []) and 
                             ("Ministro de Estado" in tag.text or "Ministra de Estado" in tag.text))

    if not cargo_element:
        print("Minister information not found.")
        return

    # normalization: "Ministra" -> "Ministro"
    cargo_text = cargo_element.get_text(strip=True)
    if "Ministra" in cargo_text:
        cargo_text = cargo_text.replace("Ministra", "Ministro")

    # Parent container usually has the name, phone, and email as siblings or children
    # Based on debug output, it seems to be a div with class "dados-possoa" (or similar)
    container = cargo_element.find_parent("div")
    
    if not container:
        print("Container for minister details not found.")
        return

    # Name
    name_tag = container.find("p", class_="nome")
    name = name_tag.get_text(strip=True) if name_tag else "N/A"

    # Phone
    phone_tag = container.find("p", class_="telefone")
    if phone_tag:
        # Extract text, remove label "Telefone(s):"
        phone_text = phone_tag.get_text(strip=True)
        # simplistic cleanup
        phone = phone_text.split(":")[-1].strip()
    else:
        phone = "N/A"

    # Email
    email_tag = container.find("p", class_="email")
    if email_tag:
        email_text = email_tag.get_text(strip=True)
        email = email_text.split(":")[-1].strip()
    else:
        email = "N/A"

    data = {
        "Nome": name,
        "Cargo": cargo_text,
        "Telefone": phone,
        "Email": email
    }

    # Print nicely formatted JSON
    print(json.dumps(data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    get_minister_info()
