import csv, argparse, os

# get the filename
parser = argparse.ArgumentParser()
parser.add_argument('csv_file')
csv_file = parser.parse_args().csv_file

# rename the source file so we can use the original csv_file as the output file
path, orig_name = os.path.split(csv_file)
fn, ext = os.path.splitext(orig_name)
sourcefile = os.path.join(path, fn + '_orig' + ext)
os.rename(csv_file, sourcefile)

DAYS = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
#try:
infile = open(sourcefile, newline='')
outfile = open(csv_file, 'w', newline='')
reader = csv.DictReader(infile)
writer = csv.DictWriter(outfile, fieldnames = reader.fieldnames + ['Date'])
writer.writeheader()
for row in reader:
    years = tuple(map(int, row['Program Year'].split('-')))
    month = int(row['Month'])
    if month < 7:
        year = years[1]
    else:
        year = years[0]
    day = DAYS[month]
    if (month == 2) and (year % 4 == 0): day = 29
    row['Date'] = f"{year}-{month:02d}-{day:02d}"
    writer.writerow(row)

# except Exception as e:
#     print('Something went wrong - did you supply a valid input file on the command line?')
#     print(e)