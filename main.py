import requests,smtplib,emoji
from datetime import date,timedelta
import config


list_of_stocks_in_portfolio = ["TSLA","META","AMZN","AAPL","MSFT","AMD","NVDA","GOOG","PLTR","NFLX"]

company_names = {
    "TSLA":"Tesla",
    "META":"Meta",
    "AMZN":"Amazon",
    "AAPL":"Apple",
    "MSFT":"Microsoft",
    "AMD":"AMD",
    "NVDA":"Nvidia",
    "GOOG":"Google",
    "PLTR":"Palantir",
    "NFLX":"Netflix"
                 }

url= "https://www.alphavantage.co/query"
news_url = "https://newsapi.org/v2/everything"
neg_sign = emoji.emojize(":red_triangle_pointed_down:")
pos_sign =  emoji.emojize(":red_triangle_pointed_up:")

for stock in list_of_stocks_in_portfolio:
  
    
    parameters =( 
    {
        "function":"TIME_SERIES_DAILY",
        "symbol":stock,
        "outputsize":"compact",
        "apikey":config.stock_key

    }
    )
    
    raw_data = requests.get(url=url,params=parameters)
    raw_data.raise_for_status()
    compiled = raw_data.json()["Time Series (Daily)"]

    two_days_ago = date.today() - timedelta(days=2)
    two_days_ago = two_days_ago.strftime("%Y-%m-%d")
    two_days_ago_data = compiled[two_days_ago]
    two_day_close =float(two_days_ago_data["4. close"])

    yesterday = date.today() - timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")
    yesterday_data = compiled[yesterday]
    yesterday_close = float(yesterday_data["4. close"])

    difference = two_day_close - yesterday_close
    per_change =  (difference/yesterday_close) * 100 
    
    parameters_news = (
    {
    "apiKey":config.news_key,
    "q":company_names[stock],
    "searchIn":"title",
    "from":two_days_ago
    }
    )
    
    news_raw = requests.get(url=news_url, params=parameters_news)
    news_raw.raise_for_status()

    unsliced_news = news_raw.json()["articles"]
    relevant_news = unsliced_news[0:3]
    
    for story in relevant_news:
        if story["title"] == "[Removed]" or story["description"] == None :
            relevant_news[relevant_news.index(story)] = unsliced_news[5]
            
    
    recepient_email = "sheltonmutambirwa@gmail.com"
    sender_email = "t68441387@gmail.com"
    password = "kurpclhoxvlwgikq"

    if abs(per_change) >= 5:

        if per_change < 0:
            sign = neg_sign
           
        else:
            sign = pos_sign
        
      
            
        for story in relevant_news:
            

            message = ("subject:Significant Change In " + company_names[stock] + " Stock Price\n\n" + "The change was " 
                       + str(round(abs(per_change),2)) +"% " + sign + ".\n\n" + "Headline: "+ story["title"] +"\n\n" + "Brief: " + 
                       story["description"] + "\n\n" + "Read the full story here: " + story["url"])
            
            message =  message.encode()
         
            with smtplib.SMTP("smtp.gmail.com",587) as connection:
                connection.starttls()
                connection.login(sender_email,password=password)
                connection.sendmail(
                from_addr=sender_email,
                to_addrs=recepient_email,
                msg=message)



