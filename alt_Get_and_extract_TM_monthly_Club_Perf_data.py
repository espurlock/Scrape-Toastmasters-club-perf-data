import sys, os, re, time
from bs4 import BeautifulSoup
import urllib.request

def get_district_performance_html(program_year, district,  month=6):
    url = f"http://dashboards.toastmasters.org/{program_year}/district.aspx?id={district}&month={month}"
    return urllib.request.urlopen(url).read()

def get_onclick_values(html):
    soup = BeautifulSoup(html, 'lxml')
    onclicks = soup.find_all(onclick=True)
    onclick_values = []
    for each in onclicks:
        onclick_values.append(each.attrs['onclick'])

    return onclick_values

program_year = '2013-2014'
district = '93'
month = 7

html = get_district_performance_html(program_year, district, month)
onclick_values = get_onclick_values(html)

division = ''
area = ''

for each_str in onclick_values:
    
    expand_area = re.search("expand_area\('division(.+)_area(.+)_clubs'\)", each_str)
    if expand_area:
        division = expand_area.group(1)
        area = expand_area.group(2)
        print(f"Division: {division}, Area: {area}")
    
    club_report_link = re.search("window.location.href='ClubReport.aspx\?id=(\d+)'", each_str)
    if club_report_link:
        club_number = club_report_link.group(1)
        print(f"  Club number: {club_number}")

