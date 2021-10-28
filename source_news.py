#!/usr/bin/env python3 
import asyncio
import asyncpg 
from asyncpg.connection import Connection
import aiohttp
from bs4 import BeautifulSoup as BS 
from datetime import datetime
import time
import ujson  
import re 

#NOTE: This program needs a way to check if an article has already been extracted
#      Approach: After bulk population of database with articles, aggregate new storis via latestStories sitemap cross reference extracted article urls with prevviously extracted urls after datetime sort. 
# Docs for pyscopg can provide more information on it's async counterpart, asyncpg. (link below)
    # https://www.psycopg.org/psycopg3/docs/

class Main:
    """
    Sections to crawl: Tech, Business, Politics, Health/pandemic coverage 
    Scrape news articles from abc news.
    Store news articles in postgres.  
    """ 
    # dsn used to connect to database. NOTE: Ensure these values are defined in docker-copose.yml 
    dsn = 'postgresql://postgres:password@localhost:5432/db' 

    async def get_urls(self, session, section) -> list:
        """Extract article urls. Crawl to article page."""
        titles = []
        urls = [] 
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
            tasks = [self.parse(session, section, url) for url in urls]
            result = await asyncio.gather(*tasks)
            return result 

        # Shield coroutine from ending due to raised exception; potential network/data discrepencies.
        await asyncio.shield(fetch_parse())  

    async def parse(self, session, section, url) -> dict:
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
            # format month add one because key starts at 0.
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
            # Prepare Load, serialize to json with fast ujson
            _data = ujson.dumps({
                "Title":title,
                "Author":author,
                "Date/Time Posted":post_date_time, # For frontend UI 
                "Date Formatted": formatted_datetime # For sorting/organization
                "Article Text":article_text})       # Comma delimited array of paragraphs. 
            
            # Async callback to load data into postgres. 
            await self.load_into_db(_data, section) 

    #TODO
    async def load_into_db(self, _data, section):
        """
        Insert/load into postgres docker container.
        All data is sanitized in transformation. 
        """   
        #Init connection pool
        async with asyncpg.create_pool(dsn=self.dsn, command_timeout=90) as pool: # Pass in dsn. Drop connection if transaction exceeds 90 seconds.  
            # Use nested transaction for redundancies on failure 
            #try: 
            async with Connection.transaction():
                columns = _data.keys() # Define columns
                values =  [_data[column] for column in columns] 
                async with asyncpg.pool.Pool.aquire(pool) as con: # TODO import above
                    async for val in values: # asyncpg supports async iteration!
                        await con.executemany('INSERT  INTO TABLE %s, %s', section, _data)

        pass # Activate upon integration of docker     

    async def fetch(self):
        """
        Initialize aiohttp.ClientSession(). 
        Fetch news stories for provided section.
        """

        async def latest_articles():
            # TODO 
            """
            After initial scrape populates database,run this function every hour.
            Articles scrapped from latest stories will have the tag latest=True in database. 
            If an article has previoulsy been extracted during initial scrape, 'Is Latest' will 
            be updated to True. 
            """  
            # Sitemap page for latest stories. 
            latest_stories_url = "https://abcnews.go.com/xmlLatestStories"
            _temp_urls = []
            latest_urls = []
            async with session.get(latest_stories_url) as response:
                # Get urls for latest stories
                xml = await response.text()
                # Make soup 
                soup = BS(xml, 'html.parser')
                _urls = soup.find_all('url') 
                for url in _urls:
                    _temp_urls.append(_url.find('loc').text) # Get latest stories urls
                # Only parse the urls that have a desired section in url path.
                # TODO optmize with working re pattern 
                for url in _temp_urls:
                    for section in sections:
                        if str(section) in url:
                            latest_urls.append(url)
                # Parse urls 
                tasks = [self.parse(session, url) for url in latest_urls]     
                result = await asyncio.gather(*tasks) 
                return result

        async def setup_tables():  
            """
            Make tables for respective sections/categories.
            Will only happen once per aggregation of data if no tables already exist.
            """
            # NOTE:Using the Cursor.executemany (in function load_into_db) only excepts composite types WITHOUT CONSTRAINTS
                # So we won't introduce constraints in table creation nor will we define composite types rather the _data.keys() will be used as column names during bulk dict insertion. 
            async with Connection.transaction():  # Create savepoint on table creation. 
                async for section in sections:
                    await Connection.execute('
                            CREATE TABLE [IF NOT EXISTS] $s', section # Create a table for each section 
                            )
            pass # Delete this pass statement after integration of dockerized applications 

        # These are the news categories of interest 
        sections = ['Technology', 'Business', 'Politics', 'Health', 'International', 'US'] 
        # Client Session pool 
        async with aiohttp.ClientSession(loop=loop) as session: # Init client session
            tasks = [self.get_urls(session, section) for section in sections]
            result = await asyncio.gather(*tasks)
            return result 
            # Extract latest articles  
            while True: 
                await latest_articles() 
                print("Collected latest stories.  Running again in 30 minutes.")
                time.sleep(1800) # blocking sleep call. 

            
        
if __name__ == '__main__':
    m = Main()
    loop = asyncio.get_event_loop() 
    results = loop.run_until_complete(m.fetch()) 
