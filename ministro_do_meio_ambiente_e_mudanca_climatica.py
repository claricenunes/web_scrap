import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import os

# Updated URL for MMA
URL = "https://www.gov.br/mma/pt-br/acesso-a-informacao/institucional/quem-e-quem"

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
    # Default values
    name = "Não encontrado"
    title = "Ministro de Estado do Meio Ambiente e Mudança do Clima"
    emails = []
    phones = []

    if soup:
        # Find the container for the Minister
        # The structure on the site uses a div with class 'dados-possoa' (or 'dados-pessoa')
        containers = soup.find_all("div", class_=re.compile(r'dados-p[oe]ssoa'))
        
        target_container = None
        for container in containers:
            cargo_p = container.find("p", class_="cargo")
            if cargo_p and "MINISTRO" in cargo_p.get_text().upper():
                target_container = container
                break
        
        # If not found by explicit class, search for the role in text
        if not target_container:
            role_tag = soup.find(string=re.compile(r"Gabinete da Ministra", re.IGNORECASE))
            if role_tag:
                target_container = role_tag.find_parent(["div", "p"])
        
        search_area = target_container if target_container else soup

        # Extract info
        name_p = search_area.find("p", class_="nome")
        if name_p:
            name = name_p.get_text(strip=True)
        else:
            # Fallback for name
            strong = search_area.find("strong")
            if strong:
                name = strong.get_text(strip=True).split("-")[0].strip()

        # Phone
        phone_p = search_area.find("p", class_="telefone")
        text = search_area.get_text(" ", strip=True)
        
        phones_found = re.findall(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', text)
        suffixes = re.findall(r'/\s*(\d{4})', text)
        
        final_phones = []
        for p in phones_found:
            final_phones.append(p)
            if suffixes:
                prefix_match = re.match(r'(\(?\d{2}\)?\s?\d{4,5}-?)', p)
                if prefix_match:
                    prefix = prefix_match.group(1)
                    for s in suffixes:
                        final_phones.append(f"{prefix}{s}")
        
        phones = list(dict.fromkeys(final_phones)) if final_phones else phones_found
        
        # Email
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
    
    out_file_base = "ministro_do_meio_ambiente_e_mudanca_climatica"
    save_json(minister, f"{out_file_base}.json")
    save_csv(minister, f"{out_file_base}.csv")

    print(json.dumps(minister, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
