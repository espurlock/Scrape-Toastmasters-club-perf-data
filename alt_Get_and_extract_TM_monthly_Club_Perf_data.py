import sys, os, re, time, argparse
from bs4 import BeautifulSoup
import urllib.request
import sqlite3

def get_district_performance_html(program_year, district,  month=6):
    filename = f"./DEV/{program_year}/{month}/{district}.html"
    if os.path.isfile(filename):
        with open(filename) as fh:
            district_perf_html = fh.read()
        return district_perf_html
    url = f"http://dashboards.toastmasters.org/{program_year}/district.aspx?id={district}&month={month}"
    if not os.path.exists(f"./DEV/{program_year}/{month}/"):
        os.makedirs(f"./DEV/{program_year}/{month}")
    district_perf_html = urllib.request.urlopen(url).read().decode()
    with open(filename, 'w') as fh:
        fh.write(district_perf_html)
    return district_perf_html
    

def get_onclick_values(html):
    soup = BeautifulSoup(html, 'lxml')
    onclicks = soup.find_all(onclick=True)
    onclick_values = []
    for each in onclicks:
        onclick_values.append(each.attrs['onclick'])

    return onclick_values


def get_club_html(club_number, program_year, month):
    filename = f"./DEV/{program_year}/{month}/{club_number}.html"
    if os.path.isfile(filename):
        with open(filename) as fh:
            club_html = fh.read()
        return club_html
    url = f"http://dashboards.toastmasters.org/{program_year}/ClubReport.aspx?id={club_number}&month={month}"
    # if not os.path.exists(f"./DEV/{program_year}/{month}/"):
    #     os.makedirs(f"./DEV/{program_year}/{month}")
    club_html = urllib.request.urlopen(url).read().decode()
    with open(filename, 'w') as fh:
        fh.write(club_html)
    return club_html


def get_membership_and_goals_met(club_soup):
    # this helper function gets the 'Base' and 'To Date' membership numbers
    #   from the middle chart at the top of the club status page
    charts = club_soup.find_all('table', class_ = 'clubStatusChart')
    middle_chart = charts[1]
    mem_nums = middle_chart.find_all('td', class_ = 'chart_table_big_numbers')
    base = int(mem_nums[0].text)
    to_date = int(mem_nums[1].text)
    right_chart = charts[2]
    goals_met = int(right_chart.find('span', class_ = 'chart_table_big_numbers').text)
    return base, to_date, goals_met

def get_club_status(club_soup):
    # first, see if club has been suspended:
    spans = club_soup.find_all('span')
    for span in spans:
        sus = re.search('Suspended\s+(\d+/\d+/\d{4})', span.text)
        if sus:
            return f"Suspended {sus.group(1)}"
    # if club has not been suspended, get the number of members 'To Date'
    base, to_date, goals_met = get_membership_and_goals_met(club_soup)
    if to_date == 0:
        return "Ineligible"
    elif to_date < 8:
        return "Low"
    else:
        return "Active"
    
def get_goal_numbers(club_soup):
    '''This function returns a list of goal counts from the main area of the club data page'''
    goal_rows = club_soup.find_all('tr', class_ = 'Grid_Top_Row')
    goals = [int(row.find('td', class_ = 'Grid_Table_yellow').text) for row in goal_rows]
    return goals

def get_recog_status(club_soup):
    h2 = club_soup.h2
    if h2.text.endswith("President's Distinguished"):
        return 'P'
    elif h2.text.endswith("Select Distinguished"):
        return 'S'
    elif h2.text.endswith("Distinguished"):
        return 'D'
    return ''

    
def get_club_data(club_soup):
    ''' This function parses the club_html page using BeautifulSoup and returns a list containing the Club DCP data '''
    status = get_club_status(club_soup)
    base, to_date, goals_met = get_membership_and_goals_met(club_soup)
    goals = get_goal_numbers(club_soup)
    recog_status = get_recog_status(club_soup)

    return [status, base, to_date, goals_met] + goals + [recog_status]



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('program_year', 
                         help="Toastmasters 'program year' like '2008-2009' (earliest available), '2022-2023', etc")
    parser.add_argument('month', default='7', 
                         help="Numeric month of the Toastmasters program year - program year starts in July (7) and ends in June (6)")
    parser.add_argument('district', 
                         help="Toastmasters district id - number or 'F' for Founder's, 'U' for Undistricted")

    args = parser.parse_args()
    program_year = args.program_year
    district = args.district
    month = args.month
    print(f"Program year: {program_year}, District: {district}, Month: {month}")
    
    if not os.path.exists('./DB/'):
        os.makedirs('./DB/')

    perf_conn = sqlite3.connect(f'./DB/{program_year}_{district}.sqlite')
    perf_cursor = perf_conn.cursor()

    perf_cursor.execute('''CREATE TABLE IF NOT EXISTS club_performance (
        district VARCHAR(4), division VARCHAR(4), area VARCHAR(4), "Club Number" INTEGER, "Club Name" VARCHAR(255),
        "Club Status" VARCHAR(32), "Mem. Base" INTEGER, "Active Members" INTEGER, "Goals Met" INTEGER,
        "CCs" INTEGER, "Add. CCs" INTEGER, "ACs" INTEGER, "Add. ACs" INTEGER, "CL/AL/DTMs" INTEGER, "Add. CL/AL/DTMs" INTEGER,
        "Level 1s" INTEGER, "Level 2s" INTEGER, "Add. Level 2s" INTEGER, "Level 3s" INTEGER, "Level 4s" INTEGER, "Level 5s" INTEGER,
        "New Members" INTEGER, "Add. New Members" INTEGER, "Off. Trained Round 1" INTEGER, "Off. Trained Round 2" INTEGER,
        "Mem. dues on time Oct & Apr" INTEGER, "Off. List On Time" INTEGER, "Club Distinguished Status" VARCHAR(1),
        "Program Year" VARCHAR(9), month INTEGER 
        )
    ''')

    perf_insert_stmt_prefix = '''INSERT INTO club_performance (district, division, area, "Club Number", "Club Name", '''
    perf_insert_club_data_start = ''' "Club Status", "Mem. Base", "Active Members", "Goals Met", '''
    trad_insert_stmt = ''' "CCs", "Add. CCs", "ACs", "Add. ACs", "CL/AL/DTMs", "Add. CL/AL/DTMs", '''
    pw_insert_stmt = ''' "Level 1s", "Level 2s", "Add. Level 2s", "Level 3s", "Level 4s", "Level 5s", '''
    common_perf_insert_stmt = '''
      "New Members", "Add. New Members", "Off. Trained Round 1", "Off. Trained Round 2", 
        "Mem. dues on time Oct & Apr", "Off. List On Time", "Club Distinguished Status", 
    '''
    perf_insert_stmt_suffix = '''
          "Program Year", month)
       VALUES ( 
    '''

    club_conn = sqlite3.connect('./DB/club_db.sqlite')
    club_cursor = club_conn.cursor()
    club_cursor.execute('''CREATE TABLE IF NOT EXISTS clubs (
        "Club Number" INTEGER NOT NULL, 
        "Chartered" VARCHAR(10)
    )
    ''')


    html = get_district_performance_html(program_year, district, month)
    soup = BeautifulSoup(html, 'lxml')
    # onclick_values = get_onclick_values(html)
    onclicks = soup.find_all(onclick=True)

    division = ''
    area = ''

    for tag in onclicks:

        expand_area = re.search("expand_area\('division(.+)_area(.+)_clubs'\)", tag.attrs['onclick'])
        if expand_area:
            division = expand_area.group(1).strip()
            area = expand_area.group(2).strip()
            print()
            print(f"Division: {division}, Area: {area}")

        club_report_link = re.search("window.location.href='ClubReport.aspx\?id=(\d+)'", tag.attrs['onclick'])
        if club_report_link:
            club_number = club_report_link.group(1)
            for each_child in tag.children:
                if 'title' in each_child.attrs:
                    club_name = each_child.attrs['title']
            print(f"  Club number: {club_number}, Club name: {club_name}")

            club_soup = BeautifulSoup(get_club_html(club_number, program_year, month), 'lxml')

            try:
                club_data = get_club_data(club_soup)
            except Exception as e:
                print(f"Could not get club data for club # {club_number}, {program_year}/{month}")
                print(e)
                club_data = []

            if len(club_data) == 23:  # this should be the most common branch for this 'alt' extract script
                perf_insert_stmt = perf_insert_stmt_prefix + perf_insert_club_data_start + \
                                   trad_insert_stmt + pw_insert_stmt + common_perf_insert_stmt + \
                                   perf_insert_stmt_suffix + 29*'?, ' + '?)'
            elif len(club_data) == 17 and program_year < '2016-2017':
                perf_insert_stmt = perf_insert_stmt_prefix + perf_insert_club_data_start + \
                                   trad_insert_stmt + common_perf_insert_stmt + \
                                   perf_insert_stmt_suffix + 23*'?,' + '?)'
            elif len(club_data) == 17 and program_year > '2019-2020':
                perf_insert_stmt = perf_insert_stmt_prefix + perf_insert_club_data_start + \
                                   pw_insert_stmt + common_perf_insert_stmt + \
                                   perf_insert_stmt_suffix + 23*'?,' + '?)'
            else:  # something was wrong with the Club Status page
                club_data = []
                perf_insert_stmt = perf_insert_stmt_prefix + perf_insert_stmt_suffix + 6*'?,' + '?)'
            
            perf_cursor.execute(perf_insert_stmt, tuple(
                    [district, division, area, int(club_number), club_name] + club_data + [program_year, int(month)]
                ))


    perf_conn.commit()


