
import requests
from bs4 import BeautifulSoup
import re

def extrair_dados_ministra_cultura():
    """
    Realiza o web scraping dos dados da Ministra da Cultura a partir da URL informada.
    """
    url = "https://www.gov.br/cultura/pt-br/composicao/gabinete-da-ministra"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao acessar a página: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    dados = {
        "nome": "Não encontrado",
        "cargo": "Ministro de Estado da Cultura", # Normalizado conforme solicitação posterior
        "telefone": "Não encontrado",
        "e-mail": "Não encontrado"
    }

    # 1. Extração do Nome
    # Pelo que vimos, o nome está dentro de uma tag <p class="nome-autoridade"> ou similar
    nome_tag = soup.find(string=re.compile(r"MARGARETH\s+MENEZES", re.I))
    if nome_tag:
        parent = nome_tag.parent
        # Limpar espaços e formatação e normalizar para Title Case
        dados["nome"] = " ".join(parent.get_text().split()).strip().title()
    else:
        # Fallback caso a estrutura mude levemente
        cargo_p = soup.find("p", class_="cargo-autoridade")
        if cargo_p:
            item_div = cargo_p.find_parent(class_="item")
            if item_div:
                nome_p = item_div.find(class_="nome-autoridade")
                if nome_p:
                    dados["nome"] = nome_p.get_text(strip=True).title()

    # 2. Extração de Telefone e E-mail
    # Como os dados não estão aparentes na estrutura de "item", vamos buscar no HTML todo por padrões
    conteudo_texto = soup.get_text(separator=' ', strip=True)
    
    # Busca de Telefone (padrão Brasil)
    # Tenta encontrar algo no formato (XX) XXXX-XXXX ou similar
    match_tel = re.search(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}", conteudo_texto)
    if match_tel:
        dados["telefone"] = match_tel.group(0).strip()
    
    # Busca de E-mail
    match_email = re.search(r"([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})", conteudo_texto, re.I)
    if match_email:
        dados["e-mail"] = match_email.group(1).strip()
    
    # Caso especial: se houver contato no rodapé ou em blocos específicos
    # No caso do MinC, se não encontrarmos, verificamos se há algum link 'mailto'
    if dados["e-mail"] == "Não encontrado":
        mailto = soup.find("a", href=re.compile(r"mailto:", re.I))
        if mailto:
            dados["e-mail"] = mailto['href'].replace("mailto:", "").strip()

    return dados

if __name__ == "__main__":
    print("Iniciando Web Scraping (Ministério da Cultura)...")
    resultado = extrair_dados_ministra_cultura()
    
    if resultado:
        print("-" * 30)
        print(f"Nome: {resultado['nome']}")
        print(f"Cargo: {resultado['cargo']}")
        print(f"Telefone: {resultado['telefone']}")
        print(f"E-mail: {resultado['e-mail']}")
        print("-" * 30)
