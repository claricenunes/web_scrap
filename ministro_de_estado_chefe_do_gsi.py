import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import os

# Main URL provided by user
URL = "https://www.gov.br/gsi/pt-br/composicao/gabinete/ministro"
# Fallback URL based on portal patterns
FALLBACK_URL = "https://www.gov.br/gsi/pt-br/acesso-a-informacao/institucional/quem-e-quem"

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return BeautifulSoup(resp.content, "html.parser")
    except Exception:
        pass
    return None

def extract_minister(soup, base_url=URL):
    name = "Não encontrado"
    title = "Ministro de Estado Chefe do Gabinete de Segurança Institucional"
    emails = []
    phones = []

    if soup:
        # Search for the container of the Minister
        # In GSI, the first "dados-possoa" usually belongs to the Minister
        containers = soup.find_all("div", class_=re.compile(r'dados-p[oe]ssoa'))
        
        target_container = None
        for c in containers:
            if "MINISTRO" in c.get_text().upper():
                target_container = c
                break
        
        if not target_container and containers:
            target_container = containers[0] # Fallback to first one
            
        search_area = target_container if target_container else soup
        
        # Name: look for <a> inside target container or <img> alt
        name_tag = search_area.find("a", href=re.compile(r'marcos|amaro', re.I))
        if not name_tag:
             name_tag = search_area.find("img", alt=re.compile(r'\w+'))
        
        if name_tag:
            name = name_tag.get("alt") or name_tag.get_text(strip=True)
        
        # If name still not found, search for h1 or first bold text
        if name == "Não encontrado":
            name_p = search_area.find(class_="nome")
            if name_p:
                name = name_p.get_text(strip=True)

        # Contacts: look for spans or just grep text
        text = search_area.get_text(" ", strip=True)
        phones = re.findall(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', text)
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)

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
    
    out_file_base = "ministro_de_estado_chefe_do_gsi"
    save_json(minister, f"{out_file_base}.json")
    save_csv(minister, f"{out_file_base}.csv")

    print(json.dumps(minister, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
