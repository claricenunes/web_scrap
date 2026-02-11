import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import os

URL = "https://www.gov.br/saude/pt-br/composicao/quem-e-quem"

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "html.parser")
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def extract_minister(soup, base_url=URL):
    # Default values
    name = "Não encontrado"
    title = "Ministro de Estado da Saúde"
    emails = []
    phones = []

    if soup:
        # Find the container for the Minister
        # The structure on the site uses a div with class 'dados-possoa' (or 'dados-pessoa')
        containers = soup.find_all("div", class_=re.compile(r'dados-p[oe]ssoa'))
        
        for container in containers:
            cargo_p = container.find("p", class_="cargo")
            if cargo_p and "MINISTRO" in cargo_p.get_text().upper():
                # Found the minister's container
                name_p = container.find("p", class_="nome")
                if name_p:
                    name = name_p.get_text(strip=True)
                
                # Use the scraped title and normalize it
                title = cargo_p.get_text(strip=True)
                # Cleanup title if it has " (A) " and normalize to title case
                title = title.replace("(A)", "").replace("  ", " ").strip().title()
                # Ensure "Da" and "De" are lowercase for the correct title format
                title = title.replace(" De ", " de ").replace(" Da ", " da ").replace(" Do ", " do ")
                
                # Extract phones
                phone_p = container.find("p", class_="telefone")
                if phone_p:
                    phone_text = phone_p.get_text(" ", strip=True)
                    # Pattern for full numbers
                    full_pattern = r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}'
                    primary_numbers = re.findall(full_pattern, phone_text)
                    
                    # Look for suffixes (like /2580)
                    suffixes = re.findall(r'/(\d{4})', phone_text)
                    
                    final_phones = []
                    for p in primary_numbers:
                        final_phones.append(p)
                        if suffixes:
                            # Reconstruct from prefix (e.g., (61) 3315-XXXX)
                            prefix_match = re.match(r'(\(?\d{2}\)?\s?\d{4,5}-?)', p)
                            if prefix_match:
                                prefix = prefix_match.group(1)
                                for s in suffixes:
                                    final_phones.append(f"{prefix}{s}")
                    
                    if not final_phones:
                        # Fallback to general regex if no primary found with full pattern
                        final_phones = re.findall(full_pattern, phone_text)
                        
                    phones = final_phones
                
                # Extract emails
                email_p = container.find("p", class_="email")
                if email_p:
                    email_text = email_p.get_text(" ", strip=True)
                    emails = re.findall(r'[\w\.-]+@[\w\.-]+', email_text)
                
                # If emails not found in dedicated p, search whole container
                if not emails:
                    emails = re.findall(r'[\w\.-]+@[\w\.-]+', container.get_text())
                
                break

    return {
        "name": name,
        "title": title,
        "emails": list(dict.fromkeys(emails)),
        "phones": list(dict.fromkeys(phones)),
        "source": base_url
    }

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_csv(data, path):
    keys = ["name", "title", "emails", "phones", "source"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        row = {k: ("; ".join(data[k]) if isinstance(data[k], list) else data.get(k, "")) for k in keys}
        writer.writerow(row)

def main():
    soup = get_soup(URL)
    minister = extract_minister(soup)
    
    out_file_base = "ministro_da_saude"
    save_json(minister, f"{out_file_base}.json")
    save_csv(minister, f"{out_file_base}.csv")

    print(json.dumps(minister, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
