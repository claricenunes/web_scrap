###Crie um código em Python que faça WEB SCRAPING REAL (coleta de dados).

Os dados NÃO podem ser definidos manualmente.
NÃO use valores fixos (hardcoded).
NÃO simule dados.

O código deve:
1. Fazer uma requisição HTTP para o link informado
2. Ler o HTML retornado
3. Extrair dinamicamente do HTML APENAS os dados do MINISTRO:
   - nome
   - cargo (normalizar para "Ministro de Estado da Saúde",
     mesmo que esteja "Ministra" na página)
   - telefone
   - e-mail

Os valores só podem ser atribuídos a partir do conteúdo da página.
Use requests e BeautifulSoup.
Fonte única dos dados: (link)
