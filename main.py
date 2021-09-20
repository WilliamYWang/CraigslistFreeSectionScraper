# Free stuff on Craigslist gets sold instantly.
# Building a web scrapper (bot) to see when there is free scrap metral from Craigslist. Web scrapper finds when someone
# posts about scrap metal on Craigslist free section. Instantly messages me when someone posts. This way 
# we can have a web scrapper constantly checking in the Craigslist free sections throughout the day so
# I don't have to refresh the page 24/7 monitoring when someone posts about scrap metal. Want to get the data for all the free stuff in LA on Craigslist and we want to 
# sift through it specifically for the the postings about scrap metal. Get email when there is free scrapmetal
# CTRL + / to comment multiple selected lines
# CTRL + l to select current line
# CTRL + K CTRL + U to uncomment multiple selected line
# CTRL + N to create new file
# Shift + Alt + F to format code
# Widows + Tab to show multiple desktops
# Widows + D to minimize all widows
# Alt+ Up/Down to move selected code
# CTRL + C can copy current line without selecting 
# Google 'Python' + whatever question you are seeking
# Height text and press (, {, [ to place (), {}, [] around the text

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime

DRIVER_PATH = r"C:\Users\willi\webdrivers\chromedriver.exe"
BASE_URL = 'https://losangeles.craigslist.org'
QUERY = 'metal'

options = Options()
options.headless = True
options.add_argument("--widow-size=1920,1200")
driver = webdriver.Chrome(executable_path=DRIVER_PATH)


# Take each post and see how long it has been posted. Also obtains the URL to easily click it. Print results to a 
# file and print the total number of results to stdout
def outputResults(posts):
    print(f'{len(posts)} results containing "{QUERY}"')
    with open("results.txt", "w") as f:

        for i, post in enumerate(posts):
            titleDiv= post.find('a', class_='result-title')
            postTitle = titleDiv.get_text()
            postURL = titleDiv.get('href')
            postTimeText = post.find('time').get('datetime')
            postTime = datetime.strptime(postTimeText, '%Y-%m-%d %H:%M')
            ellapsedMinutes = (datetime.now() - postTime)
            print(f'{i}:   {postTitle}:   {ellapsedMinutes}    {postURL}', file=f)
            postURL = post.find('a', 'result-title')

# Steps through each page of Craigslist's Free Section and add's each post (and it's respective attributes) to a 
# list and returns the amount of posts in the Craiglist's Free Section
def stepThroughPages(posts, pageLink):
    driver.get(BASE_URL + pageLink)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    nextButton = soup.find('a', class_='next')
    posts.extend(soup.find_all('li', 'result-row'))


    if nextButton is None: return posts
    return stepThroughPages(posts, nextButton.get('href'))

totalPosts = stepThroughPages([], '/search/zip')
totalPosts = [post for post in totalPosts if QUERY 
in post.find('a', class_='result-title').get_text().lower()]

outputResults(totalPosts)
driver.quit()

# Add twilio to text/email me (HTTP post request to sendgrid library and sendgrid sends email to inbox)