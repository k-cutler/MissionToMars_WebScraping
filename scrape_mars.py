# Import dependencies
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import os
import pymongo

def init_browser():
    # connects path to chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    # chromedriver
    browser = init_browser()

    # create python dictionary to store the data
    mars_data = {}

    # *** SCRAPE MARS NEWS ***
    # Visit URL
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=\
    publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')
    # Use Beautiful Soup's find() method to navigate and retrieve attributes
    news_title = soup.find('div', class_="content_title").find('a').text
    news_p = soup.find('div', class_="article_teaser_body").text

    # store data in dictionary
    mars_data['news_title'] = news_title
    mars_data['news_p'] = news_p

    # *** SCRAPE MARS SPACE IMAGES - FEATURED IMAGE ***
    # Visit URL
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_url)
    # Use splinter to click to get to the full size image
    browser.click_link_by_partial_text('FULL IMAGE')
    # JPL HTML object
    jpl_html = browser.html
    # Parse with bs
    jpl_soup = bs(jpl_html, 'html.parser')
    # Use BS's find() method to navigate and retrieve attributes
    featured_image = jpl_soup.find('img', class_="fancybox-image")
    # Store featured image URL as f string
    featured_image_url = f'https://www.jpl.nasa.gov{featured_image}'

    # store data in dictionary
    mars_data['featured_image_url'] = featured_image_url

    # *** SCRAPE MARS WEATHER TWITTER ***
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    # Retrieve page with the requests module
    twitter_response = requests.get(twitter_url)
    # Create BS object; parse with html.parser
    twitter_soup = bs(twitter_response.text, 'html.parser')
    # Use BS's find() method to navigate and retrieve attributes
    twitter_result = twitter_soup.find('div', class_="js-tweet-text-container")
    # Use BS's find() method to retrieve text of tweet
    mars_weather = twitter_result.find('p', class_="js-tweet-text").text

    # store data in dictionary
    mars_data['mars_weather'] = mars_weather

    # *** SCRAPE MARS FACTS***
    facts_url = 'https://space-facts.com/mars/'
    # Use Pandas read_html function to scrape for facts table
    facts_table = pd.read_html(facts_url)
    # print(facts_table)
    # print(facts_table) is pulling two tables, use index [1] to only return Mars facts
    mars_facts_table = facts_table[1]
    # Pandas dataframe
    facts_df = mars_facts_table
    # Create column names
    facts_df.columns = ['Description', 'Value']
    # Reset index to Description
    mars_facts_df = facts_df.set_index('Description')
    # Use Pandas to_html to convert to a HTML table string
    mars_facts_html = mars_facts_df.to_html()

    # store in dictionary
    mars_data['mars_facts'] = mars_facts_html

    # *** SCRAPE MARS HEMISPHERE IMAGES ***
    # Visit URL
    hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemi_url)
    # Hemi HTML object
    hemi_html = browser.html
    # Parse HTML with BS
    hemi_soup = bs(hemi_html, 'html.parser')
    # Create a list to store dictionaries
    hemi_list = []
    # Use bs to find_all image titles to click
    image_titles = hemi_soup.find_all('h3')
    # Loop through each title, click to find full image, store as dictionaries, append to list
    for image_title in image_titles:
        # store title text as variable
        link = image_title.text
        # use splinter to click the title's link
        browser.click_link_by_partial_text(link)
        # create second html browser for next page
        hemi_html_2 = browser.html
        # create second bs parser for next page
        hemi_soup_2 = bs(hemi_html_2, 'html.parser')
        # find image attributes for url ending
        partial_img_url = hemi_soup_2.find('img', class_="wide-image")['src']
        # store image url as f string
        img_url = f'https://astrogeology.usgs.gov{partial_img_url}'
        # store result in a dictionary
        hemi_dict = {"title": link,
                    "img_url": img_url}
        # append dictionary to the list
        hemi_list.append(hemi_dict)
        # use browser's back function to go back to home page to click next title
        browser.back()

    # store data in dictionary
    mars_data['hemisphere_image_urls'] = hemi_list

    # close the browser after scraping
    browser.quit()

    # return results
    return mars_data