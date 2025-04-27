import xml.etree.ElementTree as ET
import re
import json
from datetime import datetime
import csv
import requests

def fillDateAndTime(object, text) -> None:
    object["Date"] = ""
    date_tray = text.split(', ')
    day_details = date_tray[1].split(' ')
    day_number = int(day_details[0])
    month = month_map[day_details[1]]
    year = int(day_details[2])
    time_details = day_details[3].split(':')
    hour = int(time_details[0])
    minute = int(time_details[1])
    second = int(time_details[2])
    timezone = "UTC" + day_details[4]
    object["Date"] = [year, month, day_number, hour, minute, second,]
    return

def fillTitlePlaceHostDate(object, text) -> None:
    object["Place"] = "N/A"
    object["Host"] = "N/A"
    text_arr = text.split(": ")
    object["shortDate"] = text_arr[0]
    object["Title"] = text_arr[1]
    if len(text_arr) > 2:
        host_details = text_arr[2].split(' at ')
        if len(host_details) > 1:
            object["Place"] = host_details[1].strip()
        object["Host"] = host_details[0].strip()
    return

def fillDescriptionUrl(object, text_list) -> None:
    object["Long Description"] = ""
    object["Event Url"] = ""
    tracker = []
    for item in text_list:
        if item == "":
            continue
        item = item.split(' | ')[0]
        tracker.append(item.replace('<p>', '').replace('</p>', '').replace('<a>', '').replace('</a>', '').replace('a href=\"', '').replace('<', '').replace('>', '').replace('\"View on site', ''))
    object["Event Url"] = tracker.pop()
    url = object["Event Url"]
    object["Long Description"] = "".join(tracker)

    return

def isScrapeValid():
    csvFile = []
    recentLog = []
    
    with open('logs.csv', mode ='r') as fd:
        csvFile = list(csv.reader(fd))
        
    for i in range(len(csvFile)-1, -1, -1):
        if csvFile[i] != []:
            recentLog = csvFile[i]
            break
    if not recentLog:
        return True, 0
        
    logged_date = recentLog[0]
    logged_check = int(recentLog[1])
    current_date = datetime.now()
    todayDate = f"{current_date.year}-{current_date.month}-{current_date.day}"
    true_case = (logged_date != todayDate) or (logged_date == todayDate and logged_check < 8)
    return true_case, logged_date, todayDate, logged_check

def logData(loggedDate, todayDate, count):
    current_date = datetime.now()
    formatted_date = f"{current_date.year}-{current_date.month}-{current_date.day}"
    with open('logs.csv', mode ='a', newline='') as fd:
        writer = csv.writer(fd)
        if loggedDate == todayDate:
            writer.writerow([formatted_date, count])
        else:
            writer.writerow([formatted_date, 0])
        
def updateEventFeed():
    url = 'https://calendar.udallas.edu/calendar.xml'
    response = requests.get(url)
    if response.status_code == 200:
        xml_content = response.content
        with open('file.xml', 'wb') as file:
            file.write(xml_content)
    else:
        print(f'Failed to retrieve the XML file. Status code: {response.status_code}')

if "__main__" == __name__:
    isValid, loggedDate, todayDate, checkCount = isScrapeValid()
    if isValid:
        updateEventFeed()

        tree = ET.parse('file.xml')
        root = tree.getroot()
        items = root.findall('./channel/item')

        objects = {}
        object = {}
        month_map = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9, "Oct":10,"Nov":11,"Dec":12}
        day_map = {"Mon":"Monday","Tue":"Tuesday","Wed":"Wednesday","Thu":"Thursday","Fri":"Friday","Sat":"Saturday","Sun":"Sunday"}

        for i, item in enumerate(items):
            for child in item:
                if child != None:
                    if child.text != None:
                        text_list = child.text.split('\n')
                        text = text_list[0]
                        if re.match(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-zA-Z0-9\s]*", text):
                            fillDateAndTime(object, text)
                        if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Oct|Nov|Dec)[a-zA-Z0-9\s]*', text):
                            fillTitlePlaceHostDate(object, text)
                        if len(text_list) > 1:
                            fillDescriptionUrl(object, text_list)
                    if len(child.attrib) != 0 and 'isPermaLink' not in child.attrib:
                        object["image URL"] = child.attrib['url']
                    if len(object) == 8:
                        object["Capacity"] = -1
                        object["Approved"] = True
                        object["Short Description"] = 'N/A'
                        key = re.sub(r"[^a-zA-Z0-9]+", "", object["Title"]+"".join([str(detail) for detail in object["Date"]]))
                        objects |= {key: object}
                        object = {}

        with open('events.json', 'w') as fd:
            fd.write(json.dumps({"Scraped Events": objects}, indent=4))
        logData(loggedDate, todayDate, checkCount+1)
        print("scrape successful and data saved")
    else:
        print('exceeded update limit')