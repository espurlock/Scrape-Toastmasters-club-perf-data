from selenium import webdriver
from selenium.webdriver.support.ui import Select
from random import randint
import time, os, json, re, sys

def get_district_selector(driver):
    ''' This helper function takes a Selenium driver that has been already been
    connected to http://dashboards.toastmasters.org, and returns a Selenium
    Select object for the 'Select a District' drop-down control '''
    try:
        selector = Select(driver.find_element('css selector', 
                    '#cpContent_TopControls1_ddlDistricts'))
    except:
        selector = Select(driver.find_element('css selector', 
                    '#cpContent_TopControls2_ddlDistricts'))
    return selector


def select_district(selector, dist):
    ''' This helper function selects the Toastmasters District on the Toastmasters 
    Distinguished Performance Reports page at http://dashboards.toastmasters.org
    
    The `selector` parameter is a Selenium Select() object created by 
    the get_district_selector() function
    
    The `dist` parameter can be an integer or string (e.g. '99'), 
    or a text string like 'District 100' '''
    dist = str(dist)
    if len(dist) == 1 and dist >= '0' and dist <= '9':
        dist = '0' + dist
    if not re.search('^District\s', dist):
        dist = 'District ' + dist

    selector.select_by_visible_text(dist)
    return


def dump_district_list(selector, filename='TM_district_list.json'):
    ''' This helper function writes the list of Toastmasters districts from the drop-down
    control on http://dashboards.toastmasters.org

    `selector` is a Selenium Select object created by the get_district_selector() function

    `filename` is a string that will be used as the name of the file that this function creates
    The file will be overwritten if it exists '''
    fh = open(filename, 'w')
    fh.write(json.dumps([d.text for d in selector.options]))
    fh.close


def get_prog_year_selector(driver):
    ''' This helper function takes a Selenium driver that has been already been
    connected to http://dashboards.toastmasters.org, and returns a Selenium
    Select object for the 'Select a District' drop-down control '''
    try:
        prog_year_selector = Select(driver.find_element('css selector',
                                              '#cpContent_TopControls1_ddlProgramYear'))
    except:
        prog_year_selector = Select(driver.find_element('css selector',
                                              '#cpContent_TopControls2_ddlProgramYear'))
    return prog_year_selector


def get_prog_year_list(prog_year_selector):
    ''' This helper function is used to get the list of currently available Toastmasters Program Years
    from the drop-down control on the Dashboards page '''
    return [py.text for py in prog_year_selector.options]


def select_prog_year(prog_year_selector, prog_year):
    ''' This helper function selects the Toastmasters District on the Toastmasters 
    Distinguished Performance Reports page at http://dashboards.toastmasters.org
    
    The `prog_year_selector` parameter is a Selenium Select() object created by 
    the get_prog_year_selector() function

    The `prog_year` parameter is a valid TM program year, between '2008-2009' and '2022-2023'
    (or '<last year>-<this year>' ) '''
    prog_year_list = get_prog_year_list(prog_year_selector)
    if prog_year in prog_year_list:
        prog_year_selector.select_by_visible_text(prog_year)
        return
    # if we got here, something's wrong with the prog_year parameter
    if not prog_year:
        print("Please enter a valid TM program year like '2022-2023' on the command line")
    else:
        print("Program year:", prog_year, 
              "entered on command line does not match any currently available program year")
        print("Please enter a program year between", prog_year_list[-1], "and", 
              prog_year_list[0], "on the command line")
    exit()


def dump_prog_year_list(prog_year_selector, filename='currently_available_TM_prog_years.json'):
    ''' Just what it says on the tin - dumps a list of the currently available TM program years to disk.
    It overwrites any previous list file '''
    fh = open(filename, 'w')
    fh.write(json.dumps([py.text for py in prog_year_selector.options]))
    fh.close()


def select_month(driver, month):
    ''' This helper function selects the TM month from the drop-down on the TM Dashboards page
    where month is a 3-letter abbreviation like 'Jun', 'May', ... 'Jul', 'Aug' '''
    try:
        selector = Select(driver.find_element('css selector',
                                              '#cpContent_TopControls1_ddlMonth'))
    except:
        selector = Select(driver.find_element('css selector',
                                              '#cpContent_TopControls2_ddlMonth'))
    selector.select_by_visible_text(month)
    return


def download_the_CSV(driver):
    ''' This helper function clicks the CSV dropdown, which downloads the CSV automatically
    (provided this has been set in Firefox) to the default download directory '''
    try:
        selector = Select(driver.find_element('css selector', '#cpContent_TopControls1_ddlExport'))
    except:
        selector = Select(driver.find_element('css selector', '#cpContent_TopControls2_ddlExport'))
    selector.select_by_value('CSV')

    
if __name__ == '__main__':
    # grab the TM program year (like '2021-2022') if it has been passed in on the command line
    if len(sys.argv) == 2:
        prog_year = sys.argv[1]
    else:
        prog_year = ''

    target_directory = 'c:\\python\\web_scraping\\venv\\CSVs\\' + prog_year

    # you can append the TM program year to the Dashboards URL, 
    # like http://dashboards.toastmasters.org/2020-2021/
    # but for this script, we'll navigate to the Dashboards home, then validate the program year
    tm_dashboards_url = 'http://dashboards.toastmasters.org/'
    # start Firefox and navigate to the TM Dashboards page
    driver = webdriver.Firefox()
    try:
        # navigate to the TM site:
        driver.get(tm_dashboards_url)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        exit()
    time.sleep(randint(1,5))

    if prog_year:
        prog_year_selector = get_prog_year_selector(driver)
        select_prog_year(prog_year_selector, prog_year)
        time.sleep(randint(1,5))
        if not os.path.exists(target_directory):
            os.mkdir(target_directory)

    # now get the list of Districts, using the helper functions defined above,
    # and get the CSV of Club Performance data for each district 
    district_selector = get_district_selector(driver)
    district_list = [d.text for d in district_selector.options]
    if district_list[0] == 'Select a District': district_list = district_list[1:]
    district_list.reverse()
    # long for-in loop starts here:
    for district in district_list:
        district_selector = get_district_selector(driver)
        select_district(district_selector, district) 
        time.sleep(randint(1,5))

        # if the prog_year was supplied on the command line, get the June (end of year) data,
        # otherwise just use the default current month selection
        if prog_year:
            select_month(driver, 'Jun')
            time.sleep(randint(1,5))

        # this next block didn't seem to be necessary for 2021-2022, so leave it out for now
        # as_of_day = Select(driver.find_element('css selector', '#cpContent_TopControls2_ddlAsOf'))
        # as_of_day.click()
        # time.sleep(1)

        # this next block *IS* necessary if you want the Club Performance, rather than the Dist Perf
        try:
            club_perf_tab = driver.find_element('link text', 'Club Performance')
            club_perf_tab.click()
        except:
            pass  # assume the Club Performance tab has been selected previously
        time.sleep(randint(1,5))

        # download the CSV to the default directory set in Firefox:
        download_the_CSV(driver)
        time.sleep(randint(10,20))

        # if everything went all right, the Club_Performance.csv has been saved (with that name)
        # in the default Firefox download directory
        # so now let's rename it a bit more appropriately
        new_CSV_name = ( target_directory + '\\District' + 
                         district.split()[1] + '_Club_Performance_' + prog_year + '.csv')
        os.rename('C:\\Users\\user\\Downloads\\Club_Performance.csv', new_CSV_name)
        time.sleep(randint(15,30))

        if prog_year:
            prog_year_selector = get_prog_year_selector(driver)
            select_prog_year(prog_year_selector, prog_year)
            time.sleep(randint(1,5))
        else:
            break

        # this is the end of the long for-in loop through the district_list

    driver.quit()
