# scraping_toastmasters_club_data
Python 3 code used to retrieve and parse data for Toastmasters Distinguished Club Program (DCP) Club data

Contents:
## Get_TM_monthly_HTML.py
This script copies the club information for all Toastmasters Districts for a single 'program year' from the DCP dashboards site.
The Toastmasters program year starts on July 1 and ends on June 30 of the next year.
For example, program year '2019-2020' started on July 1 2019 and ended on June 30 2020.

Exampe usage: 
  `python ./Get_TM_monthly_HTML.py 2019-2020`
  This will:
  1. Create a subdirectory ./HTML  (if it doesn't already exist)
  2. Create a subdirectory ./HTML/2019-2020  (if it doesn't already exist)
  3. Create a subdirectory ./HTML/2019-2020/7  (if it doesn't already exist)
  4. Retrieve the list of Toastmasters districts from the drop-down control on
     http://dashboards.toastmasters.org/2019-2020/Club.aspx?month=7&id=F
  5. Retrieve each available district's club performance data for July 2019 in descending order
     (District U, District F, District 122, District 121...District 02, District 01)
  6. Repeat steps 3, 4, and 5 for month 8, month 9...month 12, month 1...month 5, month 6

  `python ./Get_TM_monthly_HTML.py 2019-2020 6`
  This will perform steps 1-5 as above, but will only retrieve month 6 (June 2020)


## Extract_Club_data_from_HTML.py
This script uses the Beautiful Soup library to parse the downloaded club performance data 
from `Get_TM_monthly_HTML.py` and saves it to a file in the ./CSVs subdirectory

Example usage:
  `python ./Extract_Club_data_from_HTML.py ./HTML/2021-2022`
  This will:
  1. Create the ./CSVs subdirectory (if it doesn't already exist)
  2. Create a file `./CSVs/2021-2022.csv` (will overwrite an existing file)
  3. Parse each district's file in `./HTML/2021-2022/1` (January 2022) 
     and append to `./CSVs/2021-2022.csv`
  4. Repeat step 3 for months 10, 11, 12, 2, 3, ... 8, 9

  `python ./Extract_Club_data_from_HTML.py ./HTML/2021-2022/7`
  This will:
  1. Create the ./CSVs subdirectory (if it doesn't already exist)
  2. Create a file `./CSVs/2021-2022_7.csv`
  3. Parse each district's file in `./HTML/2021-2022/7/`
     and append to `./CSVs/2021-2022_7.csv`

  `python ./Extract_Club_data_from_HTML.py ./TEST/2022-2023/7/U.html`
  This will: 
  1. Create the ./CSVs subdirectory (if it doesn't already exist)
  2. Create a file `./CSVs/2022-2023_7_U.csv`
  3. Parse the July 2022 club performance data and store it in `./CSVs/2022-2023_7_U.csv`


  ## old_get_TM_monthly_club_data.py
  This script downloads, parses, and saves the club performance data to a .csv file.
  This was my first attempt. I decided to separate the download and parsing functions
  to two separate scripts (`Get_TM_monthly_HTML.py` and `Extract_Club_data_from_HTML.py`)
  in order to keep from hitting the Toastmasters Dashboards site excessively while testing.
  I am keeping it as a reference for future scripts - e.g., a script to get the listing of
  districts in regions for a given program year (there will be only one such file per year) 