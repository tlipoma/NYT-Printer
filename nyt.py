from requests import Session
import os
from datetime import datetime

def download_current_crossword():
	download_crossword(datetime.now())

def download_crossword(date):
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
	
	# Save crossword
	if request.status_code == 200:
		with open('current_crossword.pdf', 'wb') as f:
			f.write(request.content)

