import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime

# URL do site
URL = "https://www.gov.br/casacivil/pt-br/composicao/gabinete-do-ministro/quem-e-quem-1"

def fazer_requisicao(url):
    """
    Faz a requisição HTTP ao site
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer requisição: {e}")
        return None

def extrair_dados(html):
    """
    Extrai os dados dos ministros e membros do gabinete
    """
    soup = BeautifulSoup(html, 'html.parser')
    dados = []

    # 1) Localiza a célula que contém o Ministro (normalmente a primeira tabela/linha relevante)
    tabelas = soup.find_all('table')
    ministro_nome = ''
    ministro_cargo = ''

    for tabela in tabelas:
        for linha in tabela.find_all('tr'):
            celulas = linha.find_all('td')
            if not celulas:
                continue
            texto = celulas[0].get_text(separator='\n', strip=True)
            linhas_texto = [l.strip() for l in texto.split('\n') if l.strip()]
            if not linhas_texto:
                continue

            # identifica linhas que mencionam "Ministro"
            if any('Ministro' in l for l in linhas_texto):
                # conforme solicitado, as informações estão trocadas: o nome está no cargo e o cargo no nome
                # tentativa simples: se houver pelo menos 2 linhas, invertemos
                if len(linhas_texto) >= 2:
                    ministro_nome = linhas_texto[1]
                    ministro_cargo = linhas_texto[0]
                else:
                    # fallback: usa o primeiro item como nome
                    ministro_nome = linhas_texto[0]
                    ministro_cargo = 'Ministro'
                break
        if ministro_nome:
            break

    # 2) Extrai telefone e email do Gabinete (procura pelo bloco "Gabinete" e captura os contatos próximos)
    gabinete_telefone = ''
    gabinete_email = ''
    # varre blocos de texto procurando por palavras-chave
    all_blocks = [b.get_text(separator='\n', strip=True) for b in soup.find_all(['div','section','table','td','p'])]
    for block in all_blocks:
        if 'Gabinete' in block or 'Gabinete do Ministro' in block or 'Chefe de Gabinete' in block:
            # procura telefones e emails no bloco
            linhas = [l.strip() for l in block.split('\n') if l.strip()]
            for l in linhas:
                if 'Telefone' in l or 'Telefones' in l:
                    gabinete_telefone = l.replace('Telefone:', '').replace('Telefones:', '').replace('Telefone(s):', '').strip()
                if 'E-mail' in l or 'E-mail :' in l or 'E-mail:' in l:
                    gabinete_email = l.replace('E-mail:', '').replace('E-mail :', '').strip()
            # se encontrou pelo menos um contato, para
            if gabinete_telefone or gabinete_email:
                break

    # fallback: busca global por qualquer email/telefone se não encontrado no bloco "Gabinete"
    if not gabinete_email:
        import re as _re
        all_text = soup.get_text('\n')
        emails = _re.findall(r'[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}', all_text)
        if emails:
            gabinete_email = emails[0]
    if not gabinete_telefone:
        import re as _re
        all_text = soup.get_text('\n')
        phones = _re.findall(r'\(?\d{2}\)?\s*\d{4,5}[-/\s]?\d{4}', all_text)
        if phones:
            gabinete_telefone = ' / '.join(phones[:3])

    if ministro_nome or ministro_cargo:
        dados.append({
            'name': ministro_nome,
            'title': ministro_cargo,
            'telefone_gabinete': gabinete_telefone,
            'email_gabinete': gabinete_email,
            'data_coleta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return dados

def salvar_csv(dados, nome_arquivo='ministros.csv'):
    """
    Salva os dados em formato CSV
    """
    if not dados:
        print("Nenhum dado para salvar")
        return
    
    df = pd.DataFrame(dados)
    df.to_csv(nome_arquivo, index=False, encoding='utf-8')
    print(f"[OK] Dados salvos em {nome_arquivo}")
    print(f"  Total de registros: {len(dados)}")

def salvar_json(dados, nome_arquivo='ministros.json'):
    """
    Salva os dados em formato JSON
    """
    if not dados:
        print("Nenhum dado para salvar")
        return
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"[OK] Dados salvos em {nome_arquivo}")
    print(f"  Total de registros: {len(dados)}")

def exibir_dados(dados, limite=5):
    """
    Exibe os dados extraídos
    """
    if not dados:
        print("Nenhum dado para exibir")
        return
    
    print(f"\n{'='*80}")
    print(f"DADOS EXTRAÍDOS - Primeiros {limite} registros")
    print(f"{'='*80}\n")
    
    for i, item in enumerate(dados[:limite], 1):
        print(f"{i}. Nome: {item.get('name','')}")
        print(f"   Cargo: {item.get('title','')}")
        print(f"   Telefone (Gabinete): {item.get('telefone_gabinete', '')}")
        print(f"   Email (Gabinete): {item.get('email_gabinete', '')}")
        print()

def main():
    """
    Função principal
    """
    print("Iniciando webscraping...")
    print(f"URL: {URL}\n")
    
    # Faz a requisição
    html = fazer_requisicao(URL)
    if not html:
        return
    
    # Extrai os dados
    print("Extraindo dados...")
    dados = extrair_dados(html)
    
    if dados:
        # Exibe os primeiros dados
        exibir_dados(dados, limite=5)
        
        # Salva em CSV
        salvar_csv(dados)
        
        # Salva em JSON
        salvar_json(dados)
        
        print(f"\n[OK] Sucesso! Total de {len(dados)} registros extraídos.")
    else:
        print("Nenhum dado foi extraído. Verifique a estrutura do site.")

if __name__ == "__main__":
    main()
