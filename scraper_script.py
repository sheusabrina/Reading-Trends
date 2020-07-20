import requests

##BEFORE BUILDING, I WANT TO JUST PULL DOWN DETAILS FOR ONE BOOK.

test_book_url = "https://www.goodreads.com/book/show/30659"
webpage_response = requests.get(test_book_url)
webpage = webpage_response.content
webpage_str = str(webpage)

open("test_book.html", "w").write(webpage_str)

### NOTES

#SCRAPER MUST:
    #IDENTIFY CORRECT BOOK URL
    #CREATE LIST OF REVIEW URLS
    #PULL REVIEW DATA
        #rating
        #date
    #MIGHT MAKE SENSE TO HAVE BOOK SCRAPER AND URL SCRAPER BE SEPERATE

#To Do List
	#install Beautiful Soup
	#make sure to learn about user agent strings
	#make sure to learn about randomized sleep statements
	#makes sure that code saves file so that you only have to run this once.

#NOTES ON BOOK PAGES:
    #URL STRUCTURE for book pages: https://www.goodreads.com/book/show/30659
        #the number in the URL is the book ID
        #goodreads API can convert from IBSN
    ##PAGE Details:
        #Each book page has a div id = "bookReviews"
        #under that, there is a div class = "friendReviews elementListBrown"
        #one of its leafs is class = "review" and that has a two links below it.
        #the first link is to the review URL, and that URL contains "review"
        #the second link is to the reviewer, and that URL does not contain review
        #next page of reviews is under class = next_page
        #by default, reviews have filters for language and sort order and rating.
        #Can you only see 300 reviews for each view?
    ##VISUAL Observation
        #Each review has a "see review" button that leads to a unique URL, these are by author (ie https://www.goodreads.com/review/show/125098945?book_show_action=true&from_review_page=1)

#NOTES ON REVIEW PAGES:
    #URL Structure for review pages: https://www.goodreads.com/review/show/2668957860
    #Rating is under class = value-title
    #Date is under class = right-dtreviewed
