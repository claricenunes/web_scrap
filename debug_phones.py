import requests
import re
url = 'https://www.gov.br/cgu/pt-br/acesso-a-informacao/institucional/quem-e-quem/gabinete-ministerial'
resp = requests.get(url, timeout=15)
text = resp.text
nums = re.findall(r"\(\d{2}\)\s*\d{4,5}-?\d{4}", text)
print('FOUND_NUMS:', nums)
for i, line in enumerate(text.splitlines()):
    if 'Telefone' in line or 'telefone' in line or re.search(r"\(\d{2}\)", line):
        print(i+1, line.strip())
