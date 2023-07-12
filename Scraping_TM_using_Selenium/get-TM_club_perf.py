import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import sys

url = 'http://dashboards.toastmasters.org/2008-2009/Club.aspx?month=6&id='
html = urllib.request.urlopen(url + 'U').read()
soup = BeautifulSoup(html, 'html.parser')

dist_list = soup.find_all(id='cpContent_TopControls1_ddlDistricts')[0].contents
dists = []
for dist in dist_list:
    try:
        dists.append(dist.attrs['value'])
    except:
        pass

print(f"Total district count: {len(dists)}")

for dist in dists:
    html = urllib.request.urlopen(url + dist).read().decode()
    with open('C:\\Python\\web_scraping\\venv\\HTML\\2008-2009\\6\\' + dist + '.html', 'w') as fh:
        fh.write(html)
              