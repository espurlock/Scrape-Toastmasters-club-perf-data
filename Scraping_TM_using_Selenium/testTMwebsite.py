import urllib.request, urllib.error

yrs = ['2021-2022', '2020-2021', '2019-2020', '2018-2019', '2017-2018', '2016-2017',
       '2015-2016', '2014-2015', '2013-2014', '2012-2013', '2011-2012', '2010-2011',
       '2009-2010', '2008-2009']

for yr in yrs:
    url = f"http://dashboards.toastmasters.org/{yr}/Club.aspx?month=6&id=01"
    print(url)
    try:
        html = urllib.request.urlopen(url).read().decode()
        if 'An error has occured' in html:
            print('An error has occurred', yr)
    except:
        print("Error occurred in urllib.request()", yr)
    print()