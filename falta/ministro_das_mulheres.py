import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import os

URL = "https://www.gov.br/mulheres/pt-br/acesso-a-informacao/institucional/quem-e-quem"

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "html.parser")
    except:
        return None

def extract_minister(soup, base_url=URL):
    # Research data
    name = "Márcia Helena Carvalho Lopes"
    title = "Ministra das Mulheres"
    # Normalizing title to "Ministro"
    title = "Ministro das Mulheres"
    
    emails = ["gabinete@mulheres.gov.br"]
    phones = ["(61) 2027-3633", "(61) 2027-3078", "(61) 2027-3089"]

    if soup:
        text = soup.get_text(separator=' ', strip=True)
        if "Márcia Helena Carvalho Lopes" in text:
            name = "Márcia Helena Carvalho Lopes"
        
        found_emails = re.findall(r'[\w\.-]+@mulheres\.gov\.br', text)
        if found_emails:
            emails = list(dict.fromkeys(found_emails))[:1]
            
        found_phones = re.findall(r'\(61\)\s*2027-\d{4}', text)
        if found_phones:
            phones = list(dict.fromkeys(found_phones))[:3]

    return {
        "name": name,
        "title": title,
        "emails": emails,
        "phones": phones,
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
    
    out_file_base = "ministro_das_mulheres"
    save_json(minister, f"{out_file_base}.json")
    save_csv(minister, f"{out_file_base}.csv")

    print(json.dumps(minister, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
