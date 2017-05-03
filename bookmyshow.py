import sys
import getopt
import urllib
import urllib.request
import re
import ast
import json
import smtplib
import pprint
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import time
import datetime
import pytz
import http.client


# The below code will generate the date required to push to the URL.

# print(goURL)
# goURL = 'https://in.bookmyshow.com/buytickets/khaidi-no-150-hyderabad/movie-hyd-ET00045498-MT/20170130'


def getDates( searchFrom , searchFor ):
	"Start from searchFrom and generate dates for the next 'searchFor' days "
	"This returns the list of formatted dates for to push to the URL"
	if(searchFrom == ''):
		searchFromDateObj = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
		searchFrom = searchFromDateObj.strftime('%Y%m%d')
	else:
		searchFromDateObj = datetime.datetime.strptime(searchFrom,'%Y%m%d')
		searchFrom = searchFromDateObj.strftime("%Y%m%d")
	# print(type(dateToday))
	# print(dateToday)
	listOfDates = []
	listOfDates.append(searchFrom)
	i = 1
	while(i <= searchFor-1):
		tempDate = datetime.datetime.strptime(searchFrom, "%Y%m%d")
		targetDate = tempDate + datetime.timedelta(days=1)
		listOfDates.append(targetDate.strftime('%Y%m%d'))
		searchFrom = targetDate.strftime('%Y%m%d')
		i = i + 1
	print('Searching for : ')
	print(listOfDates)
	return listOfDates



def getAvailableShowsForADay( goURL , prefferedTheatres=[]):

   ticketsPage = urllib.request.urlopen(goURL)

   #prefferedTheatres = ['Forum','Inorbit','Asian','Manjeera']

   ticketsSoup = BeautifulSoup(ticketsPage,'lxml')
   # ticketsSoup = BeautifulSoup(ticketsPage)
   # print(ticketsSoup)

   theatresLiList = ticketsSoup.findAll('li',attrs={"class":re.compile('list'),"data-sub-region-id":'HYD'})
   # print(theatresLiList)

   avaialbleTheatres = []

   avaialbleFinalList = []


   for theatre in theatresLiList:
   	   for preffered in prefferedTheatres:
   	   	  if(theatre.attrs['data-name'].lower().find(preffered.lower()) != -1):
   	   	  	avaialbleTheatres.append(theatre)

   for theatre in avaialbleTheatres:
   	   bodyDiv = theatre.findAll('div',attrs={"class":re.compile('body')})[0]
   	   child_bodyDivs = bodyDiv.find_all('div',attrs={"data-online":'Y'})
   	   for time in child_bodyDivs:
	   	   popup = time.contents[0].attrs['data-cat-popup']
	   	   jsonPopup = json.loads(popup)
	   	   if(len(jsonPopup)):
	   	   	for item in jsonPopup:
	   	   		if(float(item["price"]) <= 150 and item["availabilityText"].lower() == "available"):
	   	   			avaialbleFinalList.append({"Name" : theatre.attrs['data-name'], "Time" : time.contents[0].attrs['data-display-showtime']})
	   	   			# print(avaialbleFinalList) 
   # 
   # 
   return avaialbleFinalList


def getDayName(number):
    if (number == 0):
      return "Monday"
    elif number == 1:
      return "Tuesday"
    elif (number == 2):
      return "Wednesday"
    elif (number == 3):
      return "Thursday"
    elif (number == 4):
      return "Friday"
    elif (number == 5):
      return "Saturday"
    else:
      return "Sunday"

def isValidDate(goURL, date):
	soup = BeautifulSoup(urllib.request.urlopen(goURL),'lxml')
	selected = soup.find_all("li",attrs={"class":re.compile('.*_active.*')})[0].contents[1]
	selectedDate = selected.attrs['href'].split('/')[-1]
	if(selectedDate.lower() == "today"):
		if(datetime.datetime.now(pytz.timezone('Asia/Calcutta')).strftime('%Y%m%d') == date):
			return True
	elif(selectedDate.lower() == 'tomorrow'):
		tempDate = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
		targetDate = tempDate + datetime.timedelta(days=1)
		if(targetDate.strftime('%Y%m%d') == date):
			return True
	elif(selectedDate == date):
		return True
	else:
		return False


def getAvailableShowsAndEmail( findMovie,searchFrom ,searchFor , bookmyshow_base, goHref, toEmail , prefferedTheatres=[]):
	goURL_base = bookmyshow_base + goHref
	listOfDatesRequired = getDates(searchFrom , searchFor)
	foundTickets = False
	finalMessage = 'Below is the list of all the available shows for the next ' + str(searchFor) + " days \n"
	for day in listOfDatesRequired:
		dayInDateTime = datetime.datetime.strptime(day, "%Y%m%d")
		dayInFormat = dayInDateTime.strftime('%d-%m-%Y')
		dayInFormat_req = dayInDateTime.strftime('%Y%m%d')
		dayNumber = dayInDateTime.weekday()
		goURL = goURL_base[:-9]+dayInFormat_req
		print(goURL)

		if (not isValidDate(goURL,dayInFormat_req)):
			continue

		msg1 = "******************** List of  Shows for  "+ dayInFormat +" - "+ getDayName(dayNumber) +" " "****************\n"
		# if(datetime.datetime.now().strftime('%d-%m-%Y') == dayInFormat   and datetime.datetime.now().hour > 22):
		# 	continue
		listOfShows = getAvailableShowsForADay(goURL , prefferedTheatres)
		if(len(listOfShows) == 0):
			msg2 = "The movie is not being screened for this day at any of your preferred theatres.\n\n"
		else:
			foundTickets = True
			msg2 =  getFormattedMessage(listOfShows,goURL)
		finalMessage = finalMessage + msg1 + msg2
		# print(finalMessage)

	print(finalMessage)

	if(foundTickets):
		print("Found tickets")
		print("Sending email")
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login("YOUR_GMAIL_ID_HERE","YOUR_GMAIL_PASSWORD_HERE")
		encodedmsg = MIMEText(finalMessage.encode('utf-8'), _charset='utf-8')
		encodedmsg["Subject"] = "-".join(findMovie) + " Tickets"
		fromEmail = "YOUR_GMAIL_ID_HERE"
		server.sendmail(fromEmail,toEmail, encodedmsg.as_string())
		server.quit()
		print('Email sent!!')
		
	else:
		print("Did not find tickets")

	return foundTickets


		 # pp.pprint(listOfShows)
		 # print("\n")
		 # print("\n")
#getAvailableShows(10)


def getFormattedMessage(finallist , goURL):
		message = ''
		for item in finallist:
			message = message + item["Name"]+" : "+item["Time"]+"\n"

		message = message +"\n"+"Booking link : " + goURL + "\n\n"

		return message 



def findTickets(argv):
	try:
		opts,args = getopt.getopt(argv,'',["movie=","theaters=","email=","searchFrom=","searchFor="])
	except getopt.GetoptError:
		print("Error occured.. Exiting!")
		exit()

	findMovie = ''
	prefferedTheatres = []
	toEmail = ''
	searchFrom = ''
	searchFor = 1 # searchFor is optional. If not given searches only for TODAY

	for opt,arg in opts:
		# print(arg)
		if(opt =='--movie'):
			findMovie = arg.split(",")
		if(opt == '--theaters'):
			prefferedTheatres = arg.split(",")
		if(opt == '--email'):
			toEmail = arg
		if(opt == '--searchFrom'):
			searchFrom = arg
		if(opt == '--searchFor'):
		    searchFor = int(arg)

	if(len(findMovie) == 0):
		print("Error: Need movie name.. Exiting!")
		exit()
	if(len(prefferedTheatres) == 0):
		print("Error: Need Theatres list.. Exiting!")
		exit()
	if(toEmail == ''):
		print(toEmail)
		print("Error: Need email address to send.. Exiting!")
		exit()

	bookmyshow_base = 'https://in.bookmyshow.com'
	# The below is the URL that we get on clicking on Movies link in the drop down of ALL in BMS
	url = 'https://in.bookmyshow.com/hyderabad'
	html = urllib.request.urlopen(url)
	# print(findMovie)

	soup = BeautifulSoup(html,'lxml')
	buytickets_list = soup.findAll('a',href=re.compile('^\/buytickets'))
	final_list = buytickets_list
	goHref = ''
	for movie in final_list:
		lowerHref = movie.attrs['href'].lower()
		match = True
		for x in findMovie:
			if(lowerHref.find(x.lower()) == -1):
			  	match = False
			  	break
		if(match):
  			goHref = movie.attrs['href']
  			break

	if(goHref == ''):
	  	print('Could not find movie : ',findMovie)
	  	return False

	goURL = bookmyshow_base + goHref
	foundTickets = getAvailableShowsAndEmail(findMovie , searchFrom, searchFor , bookmyshow_base , goHref , toEmail , prefferedTheatres)
	return foundTickets


def findTicketsRecursively(args):
	while(1 == 1):
		try :
			foundTickets = findTickets(args)
			if(foundTickets):
				break
			else:
				print("Re-trying in 2 mins")
		except Exception as e:
			# Might have got some problems with dates not being available or something. Should try again. 
			print(e)
			print('Tryig again..')
		# findTickets(args)


		time.sleep(2*60)

findTicketsRecursively(sys.argv[1:])
