import sys, os, re, time, datetime
from datetime import datetime as DT
from bs4 import BeautifulSoup
import urllib.request

def extract_Club_data(html):
    """
    This function parses an input string of web page HTML showing Distinguished Club Program (DCP) data
    (retrieved from dashboards.toastmasters.org/{program year}/Club.aspx?month={month #}&id={district ID}')
    for all the clubs in the district in the web page data. 
    
    This function does NOT distinguish between the traditional, transitional, and Pathways periods --
    all available DCP educational data is returned. In other words, the calling program will need to 
    keep track of which DCP program is in effect (based on Program Year) to know how to interpret
    the returned list.

    The DCP data is returned as a standard Python list. The returned list will have this format:
    [ Division (str), Area (str), Club number (int), Club name (str), 
      Club status (str, values 'Active', 'Low', 'Ineligible', or 'Suspended <mm/dd/yyyy>'),
      Membership Base as of July 1 (int), Active Members (int), # Goals Met (int),
      Educational goals achieved - 6 goals for traditional and Pathways periods, 12 goals for transitional period (int),
      New Members (int, up to a count of 4), additional new members (int),
      Officers trained in Round 1 (int, 0-7), Officers trained in Round 2 (int, 0-7),
      Club member dues submitted on time for Oct and Apr periods (int, 0-2),
      Office lists submitted on time for June and December periods (int, 0-2),
      Club Distinguished Status (str, values "", "D", "S", or "P")
    ]
    total 21 elements (traditional or Pathways periods) or 27 elements (Transitional DCP period)
    """
    
    soup = BeautifulSoup(html, 'lxml')

    # create the empty return list:
    dcp_data = []

    # the divisionArea_grid table encloses all the important content
    divisionArea_grid = soup.find_all('table', class_ = 'divisionArea_grid')[0]

    division = ""; area = ""

    for each_element in divisionArea_grid:
        # see if the current element is a Division subheader
        # this assumes active Division IDs are all single alphabet characters, like A, B, C etc
        div_match = re.search('Division (.)', each_element.text)
        if div_match:
            # each division will have a new list of Areas, so reset this variable when a Division subheader is found:
            area = ""
            if re.search('Division for Clubs Pending Alignment', each_element.text):
                division = '0D'   # this is the default Division ID for new clubs that haven't been put in a Division and Area yet
            else:
                division = div_match.group(1)   
            continue
        
        # see if the current element is an Area subheader
        # Areas are typically numbered - some Districts number each Division's areas starting with 1, 
        # but other Districts number all their Areas sequentially - 1, 2, 3, ... 50, 51, 52... etc
        area_match = re.search('Area (.+?) ', each_element.text)
        if area_match:
            if re.search('Area for Clubs Pending Alignment', each_element.text):
                area = '0A'       # this is the default Area ID for new clubs that haven't been up in a Division and Area yet
            else:
                area = area_match.group(1)
            continue

        # see if the current element contains one or more rows with club data
        try:
            club_rows = each_element.find_all('tr', class_ = 'club_gray')
        except:
            # the current `each_element` is not a Tag element,
            # so it threw an AttributeError when we tried to do .find_all()
            club_rows = None
        
        if club_rows:
            for club_row in club_rows:
                
                # each row is a new list - initialize with the current Division and Area:
                row = [division, area]

                club_number = int(club_row.find('span', class_ = "redFont").text)
                row.append(club_number)
            
                club_name = club_row.find_all('td', class_ = "Grid_Title_top5")[0]['title']
                row.append(club_name)

                # membership_to_date (current Active member count) is needed in order to determine Club Status:
                membership_to_date = int(club_row.find('td', class_ ='Grid_Table title_gray').text)

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
                row.append(club_status)
                
                membership_base = int(club_row.find('th', class_ ='Grid_Table_yellow').text)
                row.append(membership_base)

                row.append(membership_to_date)

                goals_met = int(club_row.find('span', class_ = 'goalsMetBorder').text)
                row.append(goals_met)

                goal_cells = club_row.find_all('th', class_ = re.compile('Grid_Title_goal'))
                for each_cell in goal_cells:
                    row.append(int(each_cell.text))
                
                recog_status = club_row.find('img', class_ ='recog_status')['src']
                match recog_status.lower():
                    case 'images/d.png' : recog_status = 'D'
                    case 'images/s.png' : recog_status = 'S'
                    case 'images/p.png' : recog_status = 'P'
                    case _: recog_status = ''
                row.append(recog_status)

                # the row is complete, so add it to the dcp_data list:
                dcp_data.append(row)


    return dcp_data


def path_split_full(path):
    path_parts = []
    while path != '':
        parts = os.path.split(path)
        path_parts.append(parts[1])
        path = parts[0]
    path_parts.reverse()
    return path_parts


def get_current_TM_program_year():
    ''' Returns a string representing the current Toastmasters program year, like '2022-2023'
        Toastmasters program years start in July and end in June of the next year'''
    yr, mon = datetime.date.today().year, datetime.date.today().month
    if mon >= 7: 
        return f"{yr}-{yr+1}"
    else: 
        return f"{yr-1}-{yr}"


def is_valid_TM_program_year(prog_year):
    '''
    tests the prog_year parameter (str) to see if it is a valid Toastmasters program year, 
    like '2008-2009', '2009-2010', ... '2021-2022', '2022-2023', etc
    future years are not valid
    '''
    p_y = re.match('^\d\d\d\d-\d\d\d\d$', prog_year)
    if not p_y:
        return False
    if prog_year < '2008-2009' or prog_year > get_current_TM_program_year():
        return False
    y1, y2 = (int(y) for y in prog_year.split('-'))
    if y2 != y1 + 1 :
        return False
    else:
        return True


def create_output_CSV(prog_year, month='', district=''):
    ''' This function creates the output CSV file, writes the header line, and returns the filename 
        All files are created as ./CSVs/prog_year[_month[_district]].csv (no subdirectories)'''

    filename = f"./CSVs/{prog_year}"
    if month: filename += f"_{month}"
    if district: filename += f"_{district}"
    filename += ".csv"
        
    with open(filename, 'w') as fh:
        fh.write(
        '"District","Division","Area","Club Number","Club Name",' +
        '"Club Status","Mem. Base","Active Members","Goals Met",' +
        '"CCs","Add. CCs","ACs","Add. ACs","CL/AL/DTMs","Add. CL/AL/DTMs",' +
        '"Level 1s","Level 2s","Add. Level 2s","Level 3s","Level 4s","Level 5s",' +
        '"New Members","Add. New Members",' +
        '"Off. Trained Round 1","Off. Trained Round 2",' +
        '"Mem. dues on time Oct & Apr","Off. List On Time",' +
        '"Club Distinguished Status","Program Year","Month"\n')
    return filename
 

def pad_dcp_data_with_zeros(dcp_data, prog_year):
    '''Each dcp_data row can have either 21 columns (traditional or Pathways educational goal only)
       or 27 columns (in the transitional period which included 2018-2019 and 2019-2020).
       In order to be able to compare early and later years to the transitional middle years,
       we need to add 6 columns of 0s for the traditional (pre-2018) or Pathways (post-2020) periods'''
    if len(dcp_data) == 21:
        if prog_year < '2018-2019':
            dcp_data[14:14] = [0,0,0,0,0,0]
        elif prog_year > '2019-2020':
            dcp_data[8:8] = [0,0,0,0,0,0]
    return dcp_data
       

def format_mixed_list_as_csv_string(mixed_list):
    csv_string = ''
    for element in mixed_list:
        if type(element) == str: 
            csv_string += f'"{element}",'
        else:
            csv_string = csv_string + str(element) + ','
    if len(csv_string) > 1 and csv_string[-1] == ',':
        csv_string = csv_string[:-1]
    return csv_string


def append_dcp_data(dcp_data, district, prog_year, month, output_filename):
    '''
        '''
    output_fh = open(output_filename, 'a')
    for row in dcp_data:
        output_fh.write(f'"{district}",')
        if len(row) == 21:
            # if the row only has 21 elements, we need to pad it with nulls:
            if prog_year > '2019-2020':
                output_fh.write(format_mixed_list_as_csv_string(row[:8]))
                output_fh.write(',,,,,,,')
                output_fh.write(format_mixed_list_as_csv_string(row[8:]))
            else:
                output_fh.write(format_mixed_list_as_csv_string(row[:14]))
                output_fh.write(',,,,,,,')
                output_fh.write(format_mixed_list_as_csv_string(row[14:]))
        else:
            output_fh.write(format_mixed_list_as_csv_string(row))    
        output_fh.write(f',"{prog_year}","{month}"\n')
    output_fh.close()


def log_problem_html(prog_year, month, district):
    prob_filename = './LOGS/PROBLEM_HTMLs/' + DT.now().strftime("%Y%m%d")
    print(f" - logging file to {prob_filename}")
    with open(prob_filename, 'a') as prob_fh:
        prob_fh.write(f"{prog_year} {month} {district}\n")


def process_file_list(files, root, prog_year, month, output_filename):
    print(f"Program year {prog_year} Month # {month} - Districts processed:")
    for each_file in files:
        district, _ext = os.path.splitext(each_file)
        fullpath = os.path.join(root, each_file)
        with open(fullpath) as fh:
            html = fh.read()
        if 'An error has occured' in html:
            print(f"\n{fullpath} contains 'An error has occured'", end='')
            log_problem_html(prog_year, month, district)
            continue
        try:
            dcp_data = extract_Club_data(html)
        except Exception as e:
            print(f"\n{fullpath} raised '{e=}' in extract_Club_data()", end='')
            log_problem_html(prog_year, month, district)
            continue
        if dcp_data is None or len(dcp_data) == 0:
            print(f"\n{fullpath} contains no Club DCP data", end='')
            log_problem_html(prog_year, month, district)
            continue
        append_dcp_data(dcp_data, district, prog_year, month, output_filename)
        sys.stdout.write(district + ' ')
        sys.stdout.flush()


if __name__ == '__main__':

    # make sure the output and log file directories exist
    if not os.path.exists(f"./CSVs/"):
        os.makedirs(f"./CSVs")
    if not os.path.exists(f"./LOGS/PROBLEM_HTMLs/"):
        os.makedirs(f"./LOGS/PROBLEM_HTMLs/")

    # get the HTML file or directory containing HTML files: 
    html_src = ''
    while not os.path.exists(html_src)
        try:
            html_src = sys.argv[1]
            assert os.path.exists(html_src)
        except:
            print()
            print("Usage: enter a file or subdirectory of the HTML/ directory")
            print("e.g. ./HTML/2021-2022, or ./HTML/2020-2021/6, or ./HTML/2019-2020/7/01.html")
            html_src = input("Enter file or directory: ")
        
    # we now have a valid HTML file or directory, so process it
    html_src = os.path.normpath(html_src)
    path_parts = path_split_full(html_src)
    if os.path.isfile(html_src):
        if len(path_parts) >= 4 and \
            is_valid_TM_program_year(path_parts[-3]) and \
            path_parts[-2] in ('7','8','9','10','11','12','1','2','3','4','5','6'):
            prog_year = path_parts[-3]
            month = path_parts[-2]
            district, _ext = os.path.splitext(path_parts[-1])
            output_filename = create_output_CSV(prog_year, month, district)
            with open(html_src) as fh:
                html = fh.read()
            dcp_data = extract_Club_data(html)
            append_dcp_data(dcp_data, district, prog_year, month, output_filename)

    elif os.path.isdir(html_src):
        if len(path_parts) >= 2 and \
            is_valid_TM_program_year(path_parts[-2]) and \
            path_parts[-1] in ('7','8','9','10','11','12','1','2','3','4','5','6'):
            prog_year = path_parts[-2]
            month = path_parts[-1]
            # use the prog_year and month to create a CSV file like './CSVs/2022-2023_7.csv' :
            output_filename = create_output_CSV(prog_year, month)
            files = os.listdir(html_src)
            root = html_src
            process_file_list(files, root, prog_year, month, output_filename)

        elif len(path_parts) >= 1 and is_valid_TM_program_year(path_parts[-1]):
            prog_year = path_parts[-1]
            output_filename = create_output_CSV(prog_year)
            for each_dir in os.walk(html_src):
                root, _subdirs, files = each_dir
                if len(files) > 1:
                    month = os.path.split(root)[-1]
                    print()
                    process_file_list(files, root, prog_year, month, output_filename)

    else:
        print(f"Invalid HTML source directory or file:\n  {html_src}")
        print("Please try again with a valid HTML source directory or file")
        exit()
