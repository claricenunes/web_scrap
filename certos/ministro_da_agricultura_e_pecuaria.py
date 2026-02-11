
import requests
from bs4 import BeautifulSoup
import re

def extrair_dados_ministro():
    """
    Realiza o web scraping dos dados do Ministro a partir do site oficial do MAPA.
    """
    url = "https://www.gov.br/agricultura/pt-br/acesso-a-informacao/institucional/quem-e-quem-novo/ministro-e-staff"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Fazer a requisição HTTP
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao acessar a página: {e}")
        return None

    # Ler o HTML retornado
    soup = BeautifulSoup(response.content, "html.parser")

    # Estrutura para os dados finais
    dados = {
        "nome": "Não encontrado",
        "cargo": "Ministro de Estado da Agricultura e Pecuária", # Normalizado conforme solicitação
        "telefone": "Não encontrado",
        "e-mail": "Não encontrado"
    }

    # Padrão para identificar a linha do Ministro/Ministra
    padrao_ministro = re.compile(r"Ministr[ao] de Estado", re.I)
    
    # Busca dinâmica no HTML
    for div in soup.find_all("div"):
        texto_div = div.get_text(strip=True)
        
        # Identifica se a div contém o cargo de Ministro (e não é gabinete ou assessoria)
        if padrao_ministro.search(texto_div) and not any(x in texto_div for x in ["Gabinete", "Assessoria", "Adjunto"]):
            
            # 1. Extrair Nome
            # Geralmente no formato: "Cargo – NOME – Curriculum" ou similar
            match_nome = re.search(r"–\s*([^–-]+?)\s*-", texto_div)
            if match_nome:
                dados["nome"] = match_nome.group(1).strip().title()
            else:
                partes = texto_div.split("–")
                if len(partes) > 1:
                    dados["nome"] = partes[1].split("-")[0].strip().title()

            # 2. Extrair Telefone e E-mail (buscando nos elementos seguintes)
            current = div
            for _ in range(15): # Busca nos próximos 15 elementos para garantir
                current = current.find_next()
                if not current:
                    break
                
                txt = current.get_text(separator=' ', strip=True)
                
                # Procura telefone se ainda não tiver encontrado
                if dados["telefone"] == "Não encontrado":
                    match_tel = re.search(r"(?:Tel:)?\s*(\(?\d{2}\)?[\s\d/-]{8,})", txt)
                    if match_tel:
                        dados["telefone"] = match_tel.group(1).strip()

                # Procura e-mail se ainda não tiver encontrado
                if dados["e-mail"] == "Não encontrado":
                    match_email = re.search(r"([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})", txt, re.I)
                    if match_email:
                        dados["e-mail"] = match_email.group(1).strip()
                
                if dados["telefone"] != "Não encontrado" and dados["e-mail"] != "Não encontrado":
                    break
            
            # Se encontrou o ministro, não precisa continuar o loop de divs
            break

    return dados

if __name__ == "__main__":
    print("Iniciando Web Scraping...")
    resultado = extrair_dados_ministro()
    
    if resultado:
        print("-" * 30)
        print(f"Nome: {resultado['nome']}")
        print(f"Cargo: {resultado['cargo']}")
        print(f"Telefone: {resultado['telefone']}")
        print(f"E-mail: {resultado['e-mail']}")
        print("-" * 30)
