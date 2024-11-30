import pandas as pd
import csv
from ics import Calendar, Event

# import (convert ics to csv)
with open('mockuser193@gmail.com.ics', 'r') as file:
    cal = Calendar(file.read())

with open('events.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    csvwriter.writerow(['Event Name', 'Start Date', 'End Date', 'Description', 'Location'])

    for event in cal.events:
        csvwriter.writerow([event.name, event.begin.format('YYYY-MM-DD HH:mm:ss'),
        event.end.format('YYYY-MM-DD HH:mm:ss'), event.description or '', event.location or ''])

data = pd.read_csv('events.csv')

print(data)

# export (convert back from ics to csv)
csv_file = 'events.csv'
ics_file = 'events.ics'

clndr =Calendar()

with open(csv_file, mode='r') as file:
    reader = csv.DictReader(file)

    for row in reader:
        event = Event()
        event.name = row['Event Name']
        event.begin = f"{row['Start Date']}"
        event.end = f"{row['End Date']}"
        event.description = row.get('Description', '')
        event.location = row.get('Location', '')

        clndr.events.add(event)

with open(ics_file, mode='w') as file:
    file.writelines(clndr)