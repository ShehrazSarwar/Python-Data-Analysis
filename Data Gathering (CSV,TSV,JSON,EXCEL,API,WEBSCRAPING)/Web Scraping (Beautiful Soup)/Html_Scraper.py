from bs4 import BeautifulSoup
import requests

with open('simple.html') as htlm_file:
    soup = BeautifulSoup(htlm_file,'lxml')

for article in soup.find_all('div', class_ = 'article'):
    headline = article.h2.a.text
    print(headline)

    summary = article.p.text
    print(summary)

    print()