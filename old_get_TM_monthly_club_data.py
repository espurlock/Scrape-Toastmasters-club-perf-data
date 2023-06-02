import sys, os, re, time
from bs4 import BeautifulSoup
import urllib.request

# today is 2023-05-04 (May the 4th be with you!) -- current TM year 2022-2023 will not be complete until after 2023-06-30
available_program_years = ('2022-2023',
       '2021-2022', '2020-2021', '2019-2020', '2018-2019', '2017-2018', '2016-2017',
       '2015-2016', '2014-2015', '2013-2014', '2012-2013', '2011-2012', '2010-2011',
       '2009-2010', '2008-2009')

program_year = ""
while program_year not in available_program_years:
    try:
        program_year = sys.argv[1]
    except: 
        print('Enter a valid Toastmasters program year like yyyy-yyyy, or "Q" to quit')
        print('Valid full years are currently 2008-2009 through 2021-2022')
        program_year = input('Toastmasters program year: ')
        if program_year.lower()[0] == "q":
            print("Exiting program")
            exit()

if program_year == available_program_years[0]:
    print("You have requested data for the current program year")
    print("The Toastmasters year runs from July (7) to June (6)")
    print("Enter the month or months that you want data for, e.g. '7 8 9' or '8 10 12 2 3' ")
    months = tuple(input("Months:").split())
else:
    months = (7,8,9,10,11,12,1,2,3,4,5,6)

# open the output file for writing (creating ./CSVs subdirectory if it doesn't already exist)
if not os.path.exists('./CSVs'):
    os.makedirs('CSVs')


# Here's the TM Club Performance URL template:
url = 'http://dashboards.toastmasters.org/{}/Club.aspx?month={}&id={}'

# we'll cycle through the months list and get the available districts each month
# I don't *think* Toastmasters adds or subtracts/merges districts in the middle of the TM year,
# but better to be safe than sorry
for month in months:
# create an output file, and write a file header to it
    output_file = open(f"./CSVs/{program_year}-{month}.csv", 'w')
    output_file.write(
        '"District","Division","Area","Club Number","Club Name",' +
        '"Club Status","Mem. Base","Active Members","Goals Met",' +
        '"CCs","Add. CCs","ACs","Add. ACs","CL/AL/DTMs","Add. CL/AL/DTMs",' +
        '"Level 1s","Level 2s","Add. Level 2s","Level 3s","Level 4s","Level 5s",' +
        '"New Members","Add. New Members",' +
        '"Off. Trained Round 1","Off. Trained Round 2",' +
        '"Mem. dues on time Oct & Apr","Off. List On Time",' +
        '"Club Distinguished Status","Program Year","Month"\n')
    
    # get the list of districts from the drop-down control on the Club Performance page:
    district = "F"   # I assume there will always be a Founder's District 
    html = urllib.request.urlopen(url.format(program_year, month, district)).read()
    soup = BeautifulSoup(html, 'lxml')
    dist_list = soup.find_all(id='cpContent_TopControls1_ddlDistricts')[0].contents
    districts = []
    for dist in dist_list:
        try:
            districts.append(dist.attrs['value'])
        except:
            pass

    # now we can go through the list of districts:
    for district in districts:
        # first, get the page's HTML and parse it:
        html = urllib.request.urlopen(url.format(program_year, month, district)).read()
        soup = BeautifulSoup(html, 'lxml')

        # the divisionArea_grid table encloses all the important content
        divisionArea_grid = soup.find_all('table', class_ = 'divisionArea_grid')[0]

        division = ""; area = ""

        for each_element in divisionArea_grid:
            
            # see if the current element is a Division subheader
            # this assumes Division IDs are all single alphabet characters, like A, B, C etc
            div_match = re.search('Division (.)', each_element.text)
            if div_match:
                # each division will have a new list of Areas, so reset this variable when a Division subheader is found:
                area = ""
                if re.search('Division for Clubs Pending Alignment', each_element.text):
                    division = '0D'   # this is the default Division ID for new clubs that haven't been put in a Division and Area yet
                else:
                    division = div_match.group(1)
            
            # see if the current element is an Area subheader
            # Areas are typically numbered - some Districts number each Division's areas starting with 1, 
            # but other Districts number all their Areas sequentially - 1, 2, 3, ... 50, 51, 52... etc
            area_match = re.search('Area (.+?) ', each_element.text)
            if area_match:
                if re.search('Area for Clubs Pending Alignment', each_element.text):
                    area = '0A'       # this is the default Area ID for new clubs that haven't been up in a Division and Area yet
                else:
                    area = area_match.group(1)

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

                    # after each club_row has been processed, we write the entire row to a CSV file
                    # the first 9 columns are the same for all program years:
                    output_file.write(f'"{district}","{division}","{area}",')
                    output_file.write(f'{club_number},"{club_name}","{club_status}",')
                    output_file.write(f'{membership_base},{membership_to_date},{goals_met},')

                    # the educational goals are different depending on the program year
                    # there was a transitional period from 2018-2020 when the old and new
                    # educational progams were both eligible for DCP goals
                    if program_year < '2018-2019':
                        # in the pre-transitional period, write the 6 traditional goals
                        for goal in goals[:6]: output_file.write(f'{goal},')
                        # then pad out the Pathways goals:
                        output_file.write('0,0,0,0,0,0,')
                        # then write out the remaining goals:
                        for goal in goals[6:]: output_file.write(f'{goal},')

                    elif program_year > '2019-2020':
                        # in the post-transitional period, pad out the traditional goals
                        output_file.write('0,0,0,0,0,0,')
                        # then write out the Pathways and other goals:
                        for goal in goals:
                            output_file.write(f'{goal},')

                    else:
                        # in the transitional period, there will be 12 educational goals:
                        for goal in goals:
                            output_file.write(f'{goal},')

                    # finally, write out the rest of the data row:
                    output_file.write(f'"{recog_status}","{program_year}",{month}\n')
                    print(f"District: {district}, Division: {division}, Area: {area}, Club name: {club_name}, Month: {month}, Program year: {program_year}")
                    time.sleep(0.5)
                    
        # this is the end of the District loop
        print()

    # and this is the end of the Month loop
    output_file.close()
