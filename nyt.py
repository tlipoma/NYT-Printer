from requests import Session
import os
from datetime import datetime
import subprocess
import printTools as pt

def print_current_crossword():
	print_crossword(datetime.now())

def print_crossword(date):
	# Get username and pass
	user = os.environ['NYT_USERNAME']
	password = os.environ['NYT_PASSWORD']

	# Process date into link string
	date_string = date.strftime("%b%d%y")

	session = Session()
	# Log in
	request = session.post("https://myaccount.nytimes.com/mobile/login/smart/index.html", {"username":user, "password":password})

	# Download crossword
	if request.status_code == 200:
		request = session.get("http://www.nytimes.com/svc/crosswords/v2/puzzle/print/"+date_string +".pdf")

	# Save and print crossword
	if request.status_code == 200:
		# Save
		with open('current_crossword.pdf', 'wb') as f:
			f.write(request.content)
		# print
		pt.print_file('current_crossword.pdf')