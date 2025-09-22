from bs4 import BeautifulSoup
import requests

url = 'https://py4e-data.dr-chuck.net/comments_2173557.html'

html_ = requests.get(url).text

soup = BeautifulSoup(html_,'lxml')

count = 0
count_sum = 0

for number in soup.find_all('span', class_ = 'comments'):
    count += 1
    count_sum += int(number.text)

print('Count',count)
print('Sum',count_sum)