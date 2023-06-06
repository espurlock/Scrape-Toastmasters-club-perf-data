import sys, os, re, time, random
import urllib.request
from bs4 import BeautifulSoup

# today is 2023-05-04 (May the 4th be with you!) -- current TM year 2022-2023 will not be complete until after 2023-06-30
available_program_years = ('2022-2023',
       '2021-2022', '2020-2021', '2019-2020', '2018-2019', '2017-2018', '2016-2017',
       '2015-2016', '2014-2015', '2013-2014', '2012-2013', '2011-2012', '2010-2011',
       '2009-2010', '2008-2009')

program_year = ""
while program_year not in available_program_years:
    if len(sys.argv) == 0:
        print('Enter a valid Toastmasters program year like yyyy-yyyy, or "Q" to quit')
        print('(Valid full years are currently 2008-2009 through 2021-2022)')
        program_year = input('Toastmasters program year and (optional) months: ').split(' ')
        if program_year.lower()[0] == "q":
            print("Exiting program")
            exit()
        elif len(program_year) > 1:
            months = tuple(program_year[1:])
            program_year = program_year[0]
    else:
        program_year = sys.argv[1]

if program_year == available_program_years[0]:
    print("You have requested data for the current program year")
    print("The Toastmasters year runs from July (7) to June (6)")
    print("Enter the month or months that you want data for, e.g. '7 8 9' or '8 10 12 2 3' ")
    months = tuple(input("Months:").split())
else:
    months = ('7','8','9','10','11','12','1','2','3','4','5','6')

if len(sys.argv) > 2:
    months = tuple(sys.argv[2:])

for m in months:
    if m not in ('7','8','9','10','11','12','1','2','3','4','5','6'):
        print("Invalid month value supplied: ", m)
        print("Valid month values are 7-12 and 1-6 - exiting program")
        exit()

print()
print(f"Program Year == {program_year}, retrieving months {months}")
print()

# create the HTML subdirectory if it doesn't already exist)
if not os.path.exists('./HTML'):
    print("Creating ./HTML directory")
    os.makedirs('HTML')

# we'll cycle through the months list and get the available districts each month
# I don't *think* Toastmasters adds or subtracts/merges districts in the middle of the TM year,
# but better to be safe than sorry
for month in months:
    url = 'http://dashboards.toastmasters.org/{}/Club.aspx?month={}&id={}'
    # for some reason, July 2022 shows no data "As of 10-Aug-2022", but the previous "As of" day (8/9/2022) is ok
    if program_year == available_program_years[0] and month == '7':
        url += '&day=8/9/2022'

    # create an output directory if it doesn't already exist:
    if not os.path.exists(f"./HTML/{program_year}/{month}/"):
        os.makedirs(f"./HTML/{program_year}/{month}/")

    print(f"Retrieving Club Performance web pages for Program Year {program_year} month {month}: ")
    print(f"Districts retrieved and saved in ./HTML/{program_year}/{month}/ :")
    
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
    # reverse the district list, so we can tell how many we have to go while retrieving
    districts.reverse()

    # let's count 'em down:
    for district in districts:
        if not os.path.exists(f"./HTML/{program_year}/{month}/{district}.html"):
            # first, get the page's HTML:
            html = urllib.request.urlopen(url.format(program_year, month, district)).read().decode()
            # then write it to the file:
            with open(f"./HTML/{program_year}/{month}/{district}.html", 'w') as fh:
                fh.write(html)
            sys.stdout.write(district + ' ')
            sys.stdout.flush()
            time.sleep(3 * random.random())

    print()
    print(f"Finished with Program Year {program_year}, month {month}")
    print()
