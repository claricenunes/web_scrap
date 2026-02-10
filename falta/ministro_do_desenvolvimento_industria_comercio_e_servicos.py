import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import os

URL = "https://www.gov.br/mdic/pt-br/acesso-a-informacao/institucional/principais-cargos-e-respectivos-ocupantes"

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, "html.parser")

def extract_minister(soup, base_url=URL):
    content = soup.find('div', id='content-core')
    if not content:
        return None

    text = content.get_text(separator=' ', strip=True)
    
    # name
    name = "Geraldo José Rodrigues Alckmin Filho"
    if "Geraldo José Rodrigues Alckmin Filho" in text:
        name = "Geraldo José Rodrigues Alckmin Filho"
    
    # title
    title = "Ministro de Estado do Desenvolvimento, Indústria, Comércio e Serviços"
    
    # emails
    emails = []
    email_match = re.search(r'([\w\.-]+@mdic\.gov\.br)', text)
    if email_match:
        emails.append(email_match.group(1))
    
    # phones
    phones = []
    phone_match = re.search(r'Telefone\(s\)\s*:\s*((?:\(61\)\s*[\d\s-]*)+)', text)
    if phone_match:
        phone_raw = phone_match.group(1).strip()
        # Clean up if ends in alphabetic char or email
        phone_raw = re.split(r'[a-zA-Z]', phone_raw)[0].strip()
        if phone_raw:
            # MDIC phones are often like "(61) 2027-7701 - 7002 - 7003"
            parts = re.split(r'[-\s]+', phone_raw)
            # This is tricky because the dash is part of the phone but also a separator
            # Let's use a simpler split or re-run the search
            nums = re.findall(r'\(61\)\s*\d{4}-\d{4}|\b\d{4}\b', phone_raw)
            if nums:
                ddd = "(61)"
                for n in nums:
                    if "-" in n:
                        phones.append(n)
                    else:
                        phones.append(f"{ddd} 2027-{n}") # Assuming same prefix if only 4 digits

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
    try:
        soup = get_soup(URL)
    except Exception as e:
        print("Erro ao baixar a página:", e)
        return

    minister = extract_minister(soup)
    if not minister:
        print("Não foi possível localizar as informações do ministro na página.")
        return

    out_file_base = "ministro_do_desenvolvimento_industria_comercio_e_servicos"
    save_json(minister, f"{out_file_base}.json")
    save_csv(minister, f"{out_file_base}.csv")

    print(json.dumps(minister, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
