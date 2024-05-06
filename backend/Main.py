from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
#import mysql.connector
import pandas
#import ApiBuild
from flask_cors import CORS
import numpy
import json
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


from flask import Flask, request, jsonify




# connection = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     passwd="thatpwd",
#     database='stock_sentiment'
# )
#
# cursor = connection.cursor()
#
# query = "SELECT id, title, content FROM articles"
# cursor.execute(query)
#
# articles = cursor.fetchall()
def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [word for word in tokens if word not in stopwords.words('english')]

    return ' '.join(tokens)

#INCLUDE NUMPY SOMEWHERE


#filter words and stuff

finviz_url = 'https://finviz.com/quote.ashx?t='



#biggest problem was with CORS, it wouldn't work, sso I had to install new package, flask-cors on pip3
#got CORS error, and error with not being able to access the server (127.00 vs localhost:5000)
#Rest API
app = Flask(__name__)
CORS(app)



@app.route("/<ticker>")
def stock_get(ticker):
    url = finviz_url + ticker

    req = Request(url=url, headers={'user-agent': 'my-app'})
    response = urlopen(req)

    html = BeautifulSoup(response, 'html.parser')
    news_table = html.find(id='news-table')

    data = news_table
    data_rows = data.findAll('tr')
    parsed_data = []

    for row in news_table.findAll('tr'):
        title = preprocess_text(row.a.get_text())
        original = row.a.get_text()
        link = row.a.get('href')
        stripped = row.td.text.strip()
        date_data = stripped.split(' ')
        author = row.span.get_text()
        if len(date_data) == 1:
            time = date_data[0]
        else:

            date = date_data[0]
            time = date_data[1]

        parsed_data.append([ticker, date, time, title, link, author, original])
    #2d array of objects
    df = pandas.DataFrame(parsed_data, columns=['Ticker', 'Date', 'Time', 'Title', 'Link', 'Author', 'Original'])
    vader = SentimentIntensityAnalyzer()

    f = lambda title: vader.polarity_scores(title)['compound']

    # new column for compound sentiment
    # apply vader to title
    df['compound'] = df['Title'].apply(f)

    # get average sentiment of stock
    #improve by only adding sentiment (-1, 0, 1) for stock, and see if positive or negative and get that as sentiment

    sum = 0
    total = 0
    for x in df['compound']:
        total += 1
        sum += x


    average = sum / total

    sentiment = "Neutral"

    if (average < 0):
        sentiment = "Negative"
    elif (average > 0):
        sentiment = "Positive"
    #could also evaluate sentiment here instead of in react
    arr1 = df['compound']

    arr2 = df['Original']
    arr3 = df['Link']
    arr4 = df['Author']

    news_arr = []
    sentiment_arr = []
    links_arr = []
    author_arr = []

    for x in arr2:
        news_arr.append(x)

    for x in arr1:

        sentiment_arr.append(x)

    for x in arr3:
        links_arr.append(x)
    for x in arr4:
        author_arr.append(x [1:-1])


    combined = []
    index = 0
    for x in news_arr:

        arr_temp = [news_arr[index], sentiment_arr[index], links_arr[index], author_arr[index]]
        combined.append(arr_temp)
        index += 1



    stock = {
        "sentiment": sentiment,
        "news": combined

    }




    return stock


@app.route("/")
def home():
    return "This is the landing page"
if __name__ == "__main__":
    app.run()




#adding sentiment together, getting overall (average) sentiment



# cursor.close()
# connection.close()








