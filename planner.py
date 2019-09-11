
from urllib.request import urlopen
from tkinter import *
from re import findall, finditer, MULTILINE, DOTALL
import sqlite3


# Downloader
def download(url = 'http://www.wikipedia.org/',
             target_filename = 'download',
             filename_extension = 'html'):

    # Import an exception raised when a web server denies access
    # to a document
    from urllib.error import HTTPError

    # Open the web document for reading
    try:
        web_page = urlopen(url)
    except ValueError:
        raise Exception("Download error - Cannot find document at URL '" + url + "'")
    except HTTPError:
        raise Exception("Download error - Access denied to document at URL '" + url + "'")
    except:
        raise Exception("Download error - Something went wrong when trying to download " + \
                        "the document at URL '" + url + "'")

    # Read its contents as a Unicode string
    try:
        web_page_contents = web_page.read().decode('UTF-8')
    except UnicodeDecodeError:
        raise Exception("Download error - Unable to decode document at URL '" + \
                        url + "' as Unicode text")

    # Write the contents to a local text file as Unicode
    # characters (overwriting the file if it
    # already exists!)
    try:
        text_file = open(target_filename + '.' + filename_extension,
                         'w', encoding = 'UTF-8')
        text_file.write(web_page_contents)
        text_file.close()
    except:
        raise Exception("Download error - Unable to write to file '" + \
                        target_file + "'")

    # Return the downloaded document to the caller
    return web_page_contents



# Name of the planner file
planner_file = 'planner.html'

# set window size
mainWindowSize = '300x500'
childWindowSize = '500x350'

# define web and local sources
source = ['https://suncorpstadium.com.au/what-s-on.aspx',
	      'https://thetivoli.com.au/events',
		  'https://www.ticketmaster.com.au/riverstage-brisbane-tickets-brisbane/venue/155825']
archive = 'archive/'
local = ['suncorpstadium',
		 'tivoli',
		 'riverstage']

# set main image location
#imgGUI = 'EntertainmentBanner.png'
imgGUI = 'guiplanner.png'

# event data container
# each category occupies a list of dictionary with the following keys:
# title - event name (string)
# date - event date (string)
# time - event start time (string)
# image - image web source for the event (string) 
eventData = [[], [], []]

# database initials
dbFile = 'entertainment_planner.db'

# GUI

class MainWindow(Frame):
	
	# initialization
	def __init__(self, master = None):
		Frame.__init__(self, master)
		self.master = master
		
		# offline option
		self.offline = IntVar()

		# category items
		self.itemsCategory1 = list()
		self.itemsCategory2 = list()
		self.itemsCategory3 = list()

		self.itemSelected1 = list()
		self.itemSelected2 = list()
		self.itemSelected3 = list()

		# category capture
		self.capture = ["Sports on Suncorp Stadium",
				   		"Live Music at Tivoi",
				   		"Public Events on Riverstage Brisbane"]

		# print items
		self.buttonPrint = Button(self, text = "Print planner (0 events selected)", command = self.saveHTML)
		self.labelPrinted = Label(text = "")

		self.initialWindow()

	def initialWindow(self):
		# set title
		self.master.title("Entertainment Guide")
		self.pack(fill=BOTH, expand=1)

		# set image
		img = PhotoImage(file = imgGUI)
		labelImage = Label(self, image = img)
		labelImage.image = img
		labelImage.pack(fill = X, expand = "yes")

		# set offline option
		checkOffline = Checkbutton(self, variable = self.offline, text = "Work Offline", selectcolor = 'red')#, selectcolor = 'blue')
		checkOffline.pack()

		# set buttons
		frameCategoy = LabelFrame(self, text = "Select Category")
		buttonCategory1 = Button(frameCategoy, text = self.capture[0], command = self.showCategory1)
		buttonCategory2 = Button(frameCategoy, text = self.capture[1], command = self.showCategory2)
		buttonCategory3 = Button(frameCategoy, text = self.capture[2], command = self.showCategory3)
		frameCategoy.pack(fill = X, padx = 5, pady = 10)
		buttonCategory1.pack(fill = X, padx = 10, pady = 5)
		buttonCategory2.pack(fill = X, padx = 10, pady = 5)
		buttonCategory3.pack(fill = X, padx = 10, pady = 5)

		# set print and db options
		self.buttonPrint.pack(fill = X, padx = 20, pady = 15)
		buttonDB = Button(self, text = "Save to DataBase", command = self.saveDB)
		buttonDB.pack(fill = X, padx = 20)
		self.labelPrinted.pack()

	# category 1 methods
	def showCategory1(self):
		self.labelPrinted.config(text = "")
		frame = Toplevel(self)
		frame.wm_title(self.capture[0])
		frame.geometry(childWindowSize)
		frame.config(background = 'yellow')
		items = self.getItems1()
		capture = Label(frame, text = self.capture[0], font = ("Comic Sans MS", 18), background = 'yellow').pack()
		for i in range(len(items)):
			self.itemSelected1.append(IntVar())
			tmp = Checkbutton(frame, 
							  text = items[i],
							  anchor = "w",
							  variable = self.itemSelected1[i], 
							  command = self.selectItem,
							  background = 'yellow')
			tmp.pack(fill = 'both')
			self.itemsCategory1.append(items[i])
		uri = Label(frame, text = source[0], fg="blue", anchor = "w", background = 'yellow')
		uri.pack(fill = 'both')


	def getItems1(self):
		if (self.offline.get() == 0): # work online
			contents = download(url = source[0],
								target_filename = archive + local[0])
		else: # work offline
			contents = open(archive + local[0] + ".html", encoding = "utf-8").read()
		# find events by patterns
		dates = re.findall(r'<h7 class="event-date[a-z- ]*">([A-Za-z0-9 ,]+)</h7>', contents)
		times = re.findall(r'<h5 class="event-time.*[Ss]tart [Tt]ime (.*)</h5>', contents)
		titles = re.findall(r'<h6 class="event-title">(.+)</h6>', contents)
		images = re.findall(r'<img src="([A-Za-z0-9/?\-=.]+)"', contents)
		#print("{} {} {} {}".format(len(dates), len(times), len(titles), len(images)))
		# buld list of 10 events and returnt it
		events = list()
		for i in range(min(10, len(dates))):
			eventData[0].append({"title":titles[i], "date":dates[i], "time":times[i], "image":images[i]})
			events.append(dates[i] + " @ " + times[i] + ": " + titles[i])
		return events

	# category 2 methods
	def showCategory2(self):
		self.labelPrinted.config(text = "")
		frame = Toplevel(self)
		frame.wm_title(self.capture[1])
		frame.geometry(childWindowSize)
		frame.config(background = 'yellow')
		items = self.getItems2()
		capture = Label(frame, text = self.capture[1], font = ("Comic Sans MS", 18), background = 'yellow').pack()
		for i in range(len(items)):
			self.itemSelected2.append(IntVar())
			tmp = Checkbutton(frame, 
							  text = items[i],
							  anchor = "w",
							  variable = self.itemSelected2[i], 
							  command = self.selectItem,
							  background = 'yellow')
			tmp.pack(fill = 'both')
			self.itemsCategory2.append(items[i])
		uri = Label(frame, text = source[1], fg="blue", anchor = "w", background = 'yellow')
		uri.pack(fill = 'both')

	def getItems2(self):
		if (self.offline.get() == 0): # work online
			contents = download(url = source[1],
								target_filename = archive + local[1])
		else: # work offline
			contents = open(archive + local[1] + ".html", encoding = "utf-8").read()
		# find events by pattern
		titles = re.findall(r'<div class="image-title">(.*)</div>', contents)
		dates = re.findall(r'[A-Z][a-z]{2}\s\d{1,2}\s[A-Z][a-z]{2}\s\d{4}', contents)
		images = re.findall(r'<noscript><img src=\"([A-Za-z0-9/?\-=.]+)\"', contents)
		#print("{} {} {}".format(len(dates), len(titles), len(images)))
		# buld list of 10 events and returnt it
		events = list()
		for i in range(min(10, len(dates))):
			eventData[1].append({"title":titles[i].replace("&#039;", "'"), "date":dates[i], "time":None, "image":images[i]})
			events.append(dates[i] + ": " + titles[i].replace("&#039;", "'"))
		return events

	# category 3 mrthods
	def showCategory3(self):
		self.labelPrinted.config(text = "")
		frame = Toplevel(self)
		frame.wm_title(self.capture[2])
		frame.geometry(childWindowSize)
		frame.config(background = 'yellow')
		items = self.getItems3()
		capture = Label(frame, text = self.capture[2], font = ("Comic Sans MS", 18), background = 'yellow').pack()
		for i in range(len(items)):
			self.itemSelected3.append(IntVar())
			tmp = Checkbutton(frame, 
							  text = items[i],
							  anchor = "w",
							  variable = self.itemSelected3[i], 
							  command = self.selectItem,
							  background = 'yellow')
			tmp.pack(fill = 'both')
			self.itemsCategory3.append(items[i])
		uri = Label(frame, text = source[2], fg="blue", anchor = "w", background = 'yellow')
		uri.pack(fill = 'both')

	def getItems3(self):
		if (self.offline.get() == 0): # work online
			contents = download(url = source[2],
								target_filename = archive + local[2])
		else: # work offline
			contents = open(archive + local[2] + ".html", encoding = "utf-8").read()
		# find events by pattern
		m = re.findall(r'"Offer","description":"([A-Za-z0-9@|:\- ]+)', contents)
		# buld list of 10 events and returnt it
		events = list()
		for i in range(min(10, len(m))):
			e = re.split(r"[|@]", m[i])
			eventData[2].append({"title":e[0].strip(), "date":e[1].strip(), "time":e[2].strip(), "image":None})
			events.append(e[1].strip() + " @ " + e[2].strip() + ": " + e[0].strip())
		return events


	def selectItem(self):
		count = 0
		# count selected events
		for i in self.itemSelected1:
			count += i.get()
		for i in self.itemSelected2:
			count += i.get()
		for i in self.itemSelected3:
			count += i.get()
		# show amount of selected events
		self.buttonPrint.config(text = "Print planner ({} events selected)".format(count))

	def saveHTML(self):
		with open(planner_file, "w") as f:
			f.write("""<!DOCTYPE html>
					<html>
					<head><title>What's On Planner</title></head>
					<body>
					<p align=\"center\"><img src=\"https://whitesalmonspringfestival.com/springfest/wp-content/uploads/EntertainmentBanner.jpg\"></p>""")
			# category 1
			# count selected events
			count = 0
			for i in self.itemSelected1:
				count += i.get()
			totalCount = count
			if count > 0:
				# web root
				wroot = re.match(r'http[s]?://[a-z\-.]+', source[0]).group()
				#print(wroot)
				f.write("<h2 align=\"center\">" + self.capture[0] + "</h2>\n<table align=\"center\" border=\"1\">\n")
				for i in range(len(self.itemSelected1)):
					if self.itemSelected1[i].get() == 1:
						f.write("<tr><td>\n<div><img src=\"" + wroot + eventData[0][i]["image"] + "\" width=\"375\" height=\"250\"></div>\n" +
								"<h3>" + eventData[0][i]["title"] + "</h3>\n" +
								"<p>" + eventData[0][i]["date"] + " @ " + eventData[0][i]["time"] + "</p>\n</td></tr>")
				f.write("</table>")
			# category 2
			count = 0
			for i in self.itemSelected2:
				count += i.get()
			totalCount += count
			if count > 0:
				# web root
				wroot = re.match(r'http[s]?://[a-z\-.]+', source[1]).group()
				#print(wroot)
				f.write("<h2 align=\"center\">" + self.capture[1] + "</h2>\n<table align=\"center\" border=\"1\">\n")
				for i in range(len(self.itemSelected2)):
					if self.itemSelected2[i].get() == 1:
						f.write("<tr><td>\n<div><img src=\"" + wroot + eventData[1][i]["image"] + "\" width=\"375\" height=\"250\"></div>\n" +
								"<h3>" + eventData[1][i]["title"] + "</h3>\n" +
								"<p>" + eventData[1][i]["date"] + "</p>\n</td></tr>")
				f.write("</table>")
			# category 3
			count = 0
			for i in self.itemSelected3:
				count += i.get()
			totalCount += count
			if count > 0:
				f.write("<h2 align=\"center\">" + self.capture[2] + "</h2>\n<ul>\n")
				for i in range(len(self.itemSelected3)):
					if self.itemSelected3[i].get() == 1:
						f.write("<li>\n<h3>" + eventData[2][i]["title"] + "</h3>\n" +
								"<p>" + eventData[2][i]["date"] + " @ " + eventData[2][i]["time"] + "</p>\n</li>\n")
				f.write("</ul>")

			# no event selected
			if totalCount == 0:
				f.write("<h1 align=\"center\">No events planned!</h1>\n")

			f.write("""<p>
					<h4>Events sources:</h4>
					<a href=\"https://suncorpstadium.com.au/what-s-on.aspx\">https://suncorpstadium.com.au/what-s-on.aspx</a><br>
					<a href=\"https://thetivoli.com.au/events\">https://thetivoli.com.au/events</a><br>
					<a href=\"https://www.ticketmaster.com.au/riverstage-brisbane-tickets-brisbane/venue/155825\">https://www.ticketmaster.com.au/riverstage-brisbane-tickets-brisbane/venue/155825</a><br>
					</p>
					</body></html>""")

		# show print result messege
		self.labelPrinted.config(text = "Printed!")

	# part B method
	# save to DataBase
	def saveDB(self):
		# set connection to db
		dbConnection = sqlite3.connect(dbFile)
		dbCursor = dbConnection.cursor()
		# delete previous data
		dbCursor.execute("DELETE FROM events")
		# add selected events to db
		# category 1
		for i in range(len(self.itemSelected1)):
			if self.itemSelected1[i].get() == 1:
				dbCursor.execute("INSERT INTO events(event_name, event_date) VALUES(?, ?)", (eventData[0][i]["title"], eventData[0][i]["date"]))
		# category 2
		for i in range(len(self.itemSelected2)):
			if self.itemSelected2[i].get() == 1:
				dbCursor.execute("INSERT INTO events(event_name, event_date) VALUES(?, ?)", (eventData[1][i]["title"], eventData[1][i]["date"]))
		# category 3
		for i in range(len(self.itemSelected3)):
			if self.itemSelected3[i].get() == 1:
				dbCursor.execute("INSERT INTO events(event_name, event_date) VALUES(?, ?)", (eventData[2][i]["title"], eventData[2][i]["date"]))
		# save data
		dbConnection.commit()
		# show info message
		self.labelPrinted.config(text = "Saved to DB")


mainWindow = Tk()
mainWindow.geometry(mainWindowSize)

app = MainWindow(mainWindow)

mainWindow.mainloop()