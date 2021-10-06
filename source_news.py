#!/usr/bin/env python3 

import asyncio
import aiohttp
from bs4 import BeautifulSoup as BS 

class Main:
    """
    Sections to crawl: Tech, Business, Politics, Health/pandemic coverage 
    Store in MySQL database.
    """ 
    async def get_urls(self, session, section):
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

        await asyncio.shield(fetch_parse()) # Shield coroutine from ending due to raised exception; potential network/data discrepencies. 

    async def parse(self, session, url):
        """
        Extract article text, title, keywords, and date posted 
        Output to sql db. 
        """
        article_text = [] 
        async with session.get(url) as response: 
            html = await response.text() 
            await asyncio.sleep(3) #Sleep
            soup = BS(html, "html.parser")
            # Get the Title, author, data-posted/Timestamp
            title = soup.find('h1', attrs={'class':'Article__Headline__Title'}) 
            author = soup.find('span', attrs={'class':'Byline__Author'})
            try:
                author = author.get_text()
            except AttributeError as a:
                print(a, url)
                #await asyncio.sleep(1)

            post_date_time = soup.find('div', attrs={'class':'Byline__Meta--publishDate'})
            try:
                post_date_time = post_date_time.get_text() 
            except AttributeError as a: # Debug 
                print(a, url)
                #await asyncio.sleep(1) 
                
            # Main article content contains var num of paragraphs 
            try:
                main_content = soup.find('section', attrs={'class':'story'}) 
                for p in main_content.find_all('p'): #Loop through all paragraphs 
                    article_text.append(p.get_text()) #Append to list 
                # Prep for data storage
                data = {"Title":title,
                        "Author":author,
                        "Date/Time Posted":post_date_time,
                        "Article Text":article_text}
                print(data) # Test output 

            except AttributeError as a: # No text detected.  
                print(a, url, "No article text present.")


    async def fetch(self):
        """
        Initialize aiohttp.ClientSession(). 
        Fetch news stories for provided section.
        """
        # These are the news categories of interest 
        sections = ['technology', 'business', 'politics', 'health', 'international'] 

        async with aiohttp.ClientSession(loop=loop) as session: # Init client session
            tasks = [self.get_urls(session, section) for section in sections]
            result = await asyncio.gather(*tasks)
            return result 
            
        
if __name__ == '__main__':
    m = Main()
    loop = asyncio.get_event_loop() 
    results = loop.run_until_complete(m.fetch()) 
