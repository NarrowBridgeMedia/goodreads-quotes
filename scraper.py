import requests
from constants import *
from bs4 import BeautifulSoup, NavigableString
import sqlite3
from sqlite3 import Error
 
#Get User Input
RAW_AUTHOR_NAME = input("What is the author name?\n")
AUTHOR_NAME = RAW_AUTHOR_NAME.replace(" ", "+")
 
def quotes_by_author(AUTHOR_NAME, page_num=None):
 
    # Connect to database. 
    sqliteConnection = sqlite3.connect('quotes.db')
    cursor = sqliteConnection.cursor()
    print('Database Connection Successful')
    
    # Check that table exists. Create if doesn't exist.
    cursor.execute("CREATE TABLE IF NOT EXISTS quotebot (quote TEXT, book_title TEXT, author_name TEXT")
    sqliteConnection.commit()
    print('Quotes Table Ready')
    
    all_quotes = []
 
    # for each page
    for i in range(1, page_num+1, 1):
        try:
            page = requests.get("https://www.goodreads.com/quotes/search?commit=Search&page="+str(i)+"&q="+AUTHOR_NAME)
            soup = BeautifulSoup(page.text, 'html.parser')
            print("Reading page", i)
        except:
            print("Error finding author or connecting to goodreads.")
            break
        try:
            quote = soup.find(class_="leftContainer")
            quote_list = quote.find_all(class_="quoteDetails")
        except:
            pass
 
        # get data for each quote
        for quote in quote_list:
     
            meta_data = []
     
            # Get quote's text
            try:
                outer = quote.find(class_="quoteText")
                inner_text = [element for element in outer if isinstance(element, NavigableString)]
                inner_text = [x.replace("\n", "") for x in inner_text]
                final_quote = "\n".join(inner_text[:-4])
                meta_data.append(final_quote.strip())
            except:
                pass 
     
            # Get quote's author
            try:
                author = quote.find(class_="authorOrTitle").text
                author = author.replace(",", "")
                # author = author.replace("\n", "")
                meta_data.append(author.strip())
                # print(author)
            except:
                meta_data.append(None)
     
            # Get quote's book title
            try: 
                title = quote.find(class_="authorOrTitle")
                title = title.nextSibling.nextSibling.text
                # title = title.replace("\n", "")
                meta_data.append(title.strip())
                # print(title)
            except:
                meta_data.append(None)
     
            all_quotes.append(meta_data)
     
    for text, author, title, in all_quotes:
 
        try:
            print(text)
            print(title)
            print(author)
            print()
       
            if text is None or title is None and text == "":
                continue
            # Insert quote into table
            cursor.execute("INSERT INTO quotebot VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (text, title, author))
            sqliteConnection.commit()
            print('Quote Successfully Added')
          
        # Handle errors
        except sqlite3.Error as error:
            print('Error occured - ', error)
          
    # Close DB Connection        
    sqliteConnection.commit()
    cursor.close()
    sqliteConnection.close()
    
    print('SQLite Connection closed')

    return all_quotes
 
quotes_by_author(AUTHOR_NAME, 5)
