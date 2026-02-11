
import requests
from bs4 import BeautifulSoup
import re

def scrape_ministro():
    url = "https://www.gov.br/agricultura/pt-br/acesso-a-informacao/institucional/quem-e-quem-novo/ministro-e-staff"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao acessar a página: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Procurar pelo bloco do Ministro
    # O padrão observado é que o cargo e nome estão em uma div (às vezes com classe dcelink)
    # E os contatos estão logo abaixo.
    
    dados_ministro = {
        "nome": None,
        "cargo": "Ministro de Estado da Saúde", # Normalização solicitada pelo usuário
        "telefone": None,
        "e-mail": None
    }

    # Encontrar a tag que contém "Ministro de Estado" ou "Ministra de Estado"
    # Usamos regex para ignorar case e variações
    target_pattern = re.compile(r"Ministr[ao] de Estado", re.I)
    
    # Procurar em todas as divs que podem conter o texto
    for div in soup.find_all("div"):
        text = div.get_text(strip=True)
        if target_pattern.search(text) and not any(x in text for x in ["Gabinete", "Secretaria", "Adjunto"]):
            # Extrair nome: geralmente no formato "Cargo - NOME - ..."
            # Ex: "Ministro de Estado – CARLOS HENRIQUE BAQUETA FÁVARO - Curriculum"
            match_name = re.search(r"–\s*([^–-]+?)\s*-", text)
            if match_name:
                dados_ministro["nome"] = match_name.group(1).strip()
            else:
                # Tenta outra forma se o padrão falhar
                name_parts = text.split("–")
                if len(name_parts) > 1:
                    dados_ministro["nome"] = name_parts[1].split("-")[0].strip()

            # Se encontrou o nome, busca telefone e email nos próximos elementos
            if dados_ministro["nome"]:
                # Percorrer irmãos ou elementos subsequentes
                current = div
                limit = 10 # Limite de busca para não varrer a página toda
                while current and limit > 0:
                    current = current.find_next()
                    if not current:
                        break
                    
                    inner_text = current.get_text(separator=' ', strip=True)
                    
                    # Extrair telefone
                    if not dados_ministro["telefone"]:
                        phone_match = re.search(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}", inner_text)
                        if "Tel:" in inner_text or phone_match:
                            # Tenta pegar todo o conteúdo de telefone que pode ter barras /
                            tel_val = re.search(r"(?:Tel:)?\s*(\(?\d{2}\)?[\s\d/-]+)", inner_text)
                            if tel_val:
                                dados_ministro["telefone"] = tel_val.group(1).strip()

                    # Extrair e-mail
                    if not dados_ministro["e-mail"]:
                        email_match = re.search(r"([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})", inner_text, re.I)
                        if email_match:
                            dados_ministro["e-mail"] = email_match.group(1).strip()
                    
                    # Se achamos os dois, paramos
                    if dados_ministro["telefone"] and dados_ministro["e-mail"]:
                        break
                    limit -= 1
                break

    # Exibir resultados
    print(f"Nome: {dados_ministro['nome']}")
    print(f"Cargo: {dados_ministro['cargo']}")
    print(f"Telefone: {dados_ministro['telefone']}")
    print(f"E-mail: {dados_ministro['e-mail']}")

if __name__ == "__main__":
    scrape_ministro()
