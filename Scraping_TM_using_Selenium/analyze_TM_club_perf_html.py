from bs4 import BeautifulSoup
import re
import urllib.request

#file_path = "C:\\Python\\web_scraping\\venv\\HTML\\2021-2022\\6\\f.html"
#with open(file_path) as fh:
#    soup = BeautifulSoup(fh, 'lxml')

yr = '2015-2016'
dist = '01'
url = f"http://dashboards.toastmasters.org/{yr}/Club.aspx?month=6&id={dist}"
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')

# the divisionArea_grid table encloses all the important content
divisionArea_grid = soup.find_all('table', class_ = 'divisionArea_grid')[0]

division = ""; area = ""

for each_element in divisionArea_grid:
    
    div_match = re.search('Division (.)', each_element.text)
    if div_match:
        area = ""
        if re.search('Division for Clubs Pending Alignment', each_element.text):
            division = '0D'
        else:
            division = div_match.group(1)
    
    area_match = re.search('Area (.+?) ', each_element.text)
    if area_match:
        if re.search('Area for Clubs Pending Alignment', each_element.text):
            area = '0A'
        else:
            area = area_match.group(1)
        # print(f"Division = {division}, Area = {area}")

    # if not div_match and not area_match:
    #     print(f"================ Division: {division}  Area: {area} ======================")
    #     print(each_element)
    #     print("================ element end ========================")

    # see if the current element contains one or more rows with club data
    try:
        club_rows = each_element.find_all('tr', class_ = 'club_gray')
    except:
        # the current `each_element` is not a Tag element,
        # so it threw an AttributeError when we tried to do .find_all()
        club_rows = None
    
    if club_rows:
        for club_row in club_rows:
            club_name = club_row.find_all('td', class_ = "Grid_Title_top5")[0]['title']
            club_number = int(club_row.find('span', class_ = "redFont").text)
            membership_base = int(club_row.find('th', class_ ='Grid_Table_yellow').text)
            membership_to_date = int(club_row.find('td', class_ ='Grid_Table title_gray').text)
            goals_met = int(club_row.find('span', class_ = 'goalsMetBorder').text)
            
            recog_status = club_row.find('img', class_ ='recog_status')['src']
            match recog_status.lower():
                case 'images/d.png' : recog_status = 'D'
                case 'images/s.png' : recog_status = 'S'
                case 'images/p.png' : recog_status = 'P'
                case _: recog_status = ''

            suspended_date = ''
            spans = club_row.find_all('span')
            for span in spans:
                span_match = re.search('Susp (\d+/\d+/\d+)', span.text)
                if span_match: 
                    suspended_date = span_match.group(1)

            if suspended_date:
                club_status = f"Suspended {suspended_date}"
            elif membership_to_date == 0:
                club_status = "Ineligible"
            elif membership_to_date < 8:
                club_status = "Low"
            else:
                club_status = "Active"
            
            goals = []
            goal_cells = club_row.find_all('th', class_ = re.compile('Grid_Title_goal'))
            for each_cell in goal_cells:
                goals.append(int(each_cell.text))
            
            print(f"Division: {division}, Area: {area}, Club # {club_number}: '{club_name}',")
            print(f"Status: {club_status}, Base: {membership_base}, To Date: {membership_to_date}, Goals met: {goals_met}")
            print(goals)
            print(f"Recognition: {recog_status}")
            print()