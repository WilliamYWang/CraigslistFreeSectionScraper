from bs4 import BeautifulSoup
import requests
import pandas as pd
from twilio.rest import Client
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

BASE_URL = os.getenv('BASE_URL')
ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
FROM_PHONE = os.getenv('FROM_PHONE')
TO_PHONE = os.getenv('TO_PHONE')
SEEN_POSTS = "posts.txt"

# Load the list of seen posts
def loadSeenPosts():
    with open(SEEN_POSTS, 'r') as f:
        return set(line.strip() for line in f)


# Update the list of seen posts
def saveSeenPosts(posts):
    with open(SEEN_POSTS, 'w') as f:
        for post in posts:
            f.write(post + '\n')


# Send a text message to a phone number
def sendNotification(posts):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        body=f"New posts found:\n" + "\n".join([f"{index}. {post}" for index, post in enumerate(posts, start=1)]),
        from_=FROM_PHONE,
        to=TO_PHONE
    )
    logger.info('SMS sent successfully. Message SID: {}', message.sid)


# Output the results to a CSV file and print the results to stdout
def printAndSaveToFile(posts):
    df = pd.DataFrame(posts, columns=['Title','Location','URL'])
    df.to_csv('results.csv', index=False)

    for i, post in enumerate(posts):
        logger.info(f'{i}:   Title: {post[0]}   Location: {post[1]}    URL: {post[2]}')
    logger.info(f'{len(posts)} new posts')


# Step through each page and add each post to a list
def stepThroughPages():
    response = requests.get(f"{BASE_URL}&s=0").text
    soup = BeautifulSoup(response, 'html.parser')
    ol_element = soup.find('ol', class_='cl-static-search-results')
    li_elements = ol_element.find_all('li', class_='cl-static-search-result')
    return [(post.get('title', 'No title attribute'),
         post.find('div', class_='location').get_text(strip=True) if post.find('div', class_='location') else 'No location provided',
         post.find('a').get('href'))
        for post in li_elements]


def main():
    seenPosts = loadSeenPosts()
    currentPosts = stepThroughPages()
    currentUrls = set(post[2] for post in currentPosts)
    newPosts = currentUrls - seenPosts

    if newPosts:
        printAndSaveToFile(currentPosts)
        sendNotification(newPosts)
    else:
        logger.info('No new posts')

    saveSeenPosts(currentUrls)


if __name__ == '__main__':
    main()