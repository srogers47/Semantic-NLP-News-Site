#!/usr/bin/env python3 

import asyncio
import asyncpg 
import aiohttp
from bs4 import BeautifulSoup as BS 
import datetime 
import json 

#NOTE: This program needs a way to check if an article has already been extracted
#      Approach: Cross reference titles of articles with titles previously extracted 
#      Time Complexity: Linear and managable with asyncio and docker swarm 
#      Optimization: Use internal datetime to offload cross referencing outdated articles /
#              - Time comlexity: Constant

class Main:
    """
    Sections to crawl: Tech, Business, Politics, Health/pandemic coverage 
    Scrape news articles from abc news.
    Store news articles in postgres.  
    """ 
    # Share established connection to existing database, 'db' -> Named in docker-compose.yml
    ## Uncomment line below upon integration of docker-compose.yml
    #conn = await asyncpg.connect('postgresql://postgres@localhost/db') 

    async def get_urls(self, session, section) -> list:
        """Extract article urls. Crawl to article page."""
        urls = [] 
        titles = []
        base_url = f"https://abcnews.go.com/{section}" #Format with sections
        async with session.get(base_url) as response:
            html = await response.text() 
            # print(html)
            soup = BS(html, "html.parser") 
            articles = soup.find_all('section', attrs={'class':'ContentRoll__Item'}) 
            for i in articles: #Extract urls , titles for logging  
                _article =  i.find('a', attrs={'class':'AnchorLink'})
                url = _article['href']
                title =  _article.get_text() 
                urls.append(url)
                titles.append(title) 

        async def fetch_parse():
            """Async callback to parse articles""" 
            tasks = [self.parse(session, url) for url in urls]
            result = await asyncio.gather(*tasks)
            return result 

        # Shield coroutine from ending due to raised exception; potential network/data discrepencies.
        await asyncio.shield(fetch_parse())  

    async def parse(self, session, url) -> dict:
        """
        Parse articles.
        Extract text, title, author, and date posted. 
        Transform data, drop html tags. 
        """
        async def format_date_posted() -> str:
            """
            Example date posted output: 'Date/Time Posted': 'October 6, 2021, 11:27 AM'
            Transform date_posted to postgressql TIMESTAMP scalar format for sorting 
            but keep original format for front end article view. 
            """
            # Convert month to int. 
            _months = ['January', 'Febuary', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December'] 
            _month_dict = dict(enumerate(_months))
            _date_posted = post_date_time.split() # Split into array
            _month = _date_posted[0] 
            # format month 
            _month_int = int([key for key, val in _month_dict if val == _month]) + 1 
            if _month_int[0] < 10: 
                _month_int += '0' + str(_month_int) # format: concatenate to 0 if single digit. 
            # Convert time to military time  
            if 'PM' in _date_posted[-1]:
                _time_hour = int(_date_posted[3][:2]) + 12 # Add 12 hours  
                _time = str(_time_hour) +  str(_date_posted[3][2:5]) 
            else:
                _time = _date_posted[3] 
            print(_time) # Check debug 
            # Format into TIMESTAMP scalar 
            formatted_datetime = f"{_date_posted[2]}-{_month} {_time}:00 " # seconds will default to '00'
            print(f"\n {formatted_datetime} \n") # TEMP Test output 

        article_text = [] 
        async with session.get(url) as response: 
            html = await response.text() 
            await asyncio.sleep(.25)  # Courtesy buffer 
            # Aggregate html from article pages into BeautifulSoup, 'BS' 
            soup = BS(html, "html.parser")
            # Get the Title, author, data-posted/Timestamp
            title = soup.find('h1', attrs={'class':'Article__Headline__Title'}).get_text() 
            author = soup.find('span', attrs={'class':'Byline__Author'}).get_text() 

            post_date_time = soup.find('div', attrs={'class':'Byline__Meta--publishDate'}).get_text()
                
            # Main article text content contains varying number of paragraphs.
            try:
                main_content = soup.find('section', attrs={'class':'story'}) 
                for p in main_content.find_all('p'): #Loop through all paragraphs 
                    article_text.append(p.get_text()) #Append to list 

            except AttributeError as a: # No text detected. Most likely a video and NOT article. 
                print(a, url, "No article text present.")

            await format_date_posted()  # Format date of post for sql backend
            # Prepare Load  
            _data = {"Title":title,
                    "Author":author,
                    "Date/Time Posted":post_date_time, # For frontend UI 
                    "Date Formatted": formatted_datetime # For sorting/organization
                    "Article Text":article_text}       # Comma delimited array of paragraphs. 
            
            # Async callback to load data into postgres. 
            await self.load_into_db(_data) 

    #TODO
    async def load_into_db(self, _data):
        """Insert/load into postgres docker container."""
        
        pass # Activate upon integration of docker     



    async def fetch(self):
        """
        Initialize aiohttp.ClientSession(). 
        Fetch news stories for provided section.
        """
        async def setup_tables(self, section): 
            """
            Make tables for respective sections/categories.
            Will only happen once per aggregation of data if no tables already exist.
            article text 
            """
            # conn: async connection pool...NOTE Do I need to pass in loop explicitly???
            await self.conn.execute('''
                    CREATE TABLE [IF NOT EXISTS] $section(
                        article_id serial PRIMARY KEY,
                        title VARCHAR (100) NOT NULL, 
                        author VARCHAR (100) NOT NULL,
                        date_posted VARCHAR(50) NOT NULL, 
                        formatted_datetime TIMESTAMP NOT NULL, 
                        article_text TEXT NOT NULL,  
                    )
                    ''')
            pass # Delete this pass statement after integration of dockerized applications 

        # These are the news categories of interest 
        sections = ['technology', 'business', 'politics', 'health', 'international'] 
        # Client Session pool 
        async with aiohttp.ClientSession(loop=loop) as session: # Init client session
            tasks = [self.get_urls(session, section) for section in sections]
            result = await asyncio.gather(*tasks)
            return result 

            
        
if __name__ == '__main__':
    m = Main()
    loop = asyncio.get_event_loop() 
    results = loop.run_until_complete(m.fetch()) 
