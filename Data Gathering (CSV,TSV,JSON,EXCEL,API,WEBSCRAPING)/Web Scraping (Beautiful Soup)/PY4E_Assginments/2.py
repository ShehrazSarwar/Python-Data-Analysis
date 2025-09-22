from bs4 import BeautifulSoup
import requests

url = 'http://py4e-data.dr-chuck.net/known_by_Ammarah.html'

html_ = requests.get(url).text

soup = BeautifulSoup(html_,'lxml')

count = int(input('Enter count: '))
position = int(input('Enter position: '))

print('Retrieving:',url)
while count > 0:
    soup = soup.find_all('a')
    url = soup[position-1]['href']
    print('Retrieving:',url)
    html_ = requests.get(url).text
    soup = BeautifulSoup(html_, 'lxml')
    count -= 1

