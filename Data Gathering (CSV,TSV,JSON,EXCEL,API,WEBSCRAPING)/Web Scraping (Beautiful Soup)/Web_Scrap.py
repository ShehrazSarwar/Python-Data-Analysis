from bs4 import BeautifulSoup
import requests
import csv

source = requests.get('https://codanics.com/webscraping-with-python/').text

soup = BeautifulSoup(source,'lxml')

csv_file = open('text_scrap.csv','w',encoding='utf-8') # encoding just for the emoji
csv_writter = csv.writer(csv_file)
csv_writter.writerow(['Headline','Summary','Video Link'])

article = soup.find('div', class_ = 'slide')

title = article.h1.text
print(title)

print()

paragraphs = article.find_all('p')
summary = ''
for p in paragraphs:
    summary = (summary + p.text).strip()
print(summary)

print()

video_link = article.find('div', class_ = 'center')
link = video_link.a['href']
print(link)

csv_writter.writerow([title,summary,link])

csv_file.close()