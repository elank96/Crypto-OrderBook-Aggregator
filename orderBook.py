import requests

def main():
    tenBTC = input("Do you want 10 BTC, Y or N? ")
    quantity = 0
    if tenBTC == "Y":
        quantity = 10.0
    else:
        quantity = float(input("Please enter the BTC quantity of your order: "))
        if quantity <= 0.0:
            quantity = float(input("Please choose a BTC quantity greater than 0: "))

    print(orderBookAggregator(quantity))

"""
Parameter -> quantity: the number of BTC in the order
Return -> A two-key dictionary containing the Ask and Bid price for 10 BTC across
the aggregated order books of Coinbase, Gemini, and Kraken. 
"""
def orderBookAggregator(quantity):
    asks = []
    bids = []

    coinbaseAsks, coinbaseBids = fetchCBOrderBook(quantity) #fetch Coinbase order book
    krakenAsks, krakenBids = fetchKrakenOrderBook(quantity) #fetch Kraken order book
    geminiAsks, geminiBids = fetchGeminiOrderBook(quantity) #fetch Gemini order book

    #merge all asks into 1 common data structure
    asks += coinbaseAsks
    asks += krakenAsks
    asks += geminiAsks
    
    #merge all bids into 1 common data structure
    bids += coinbaseBids
    bids += krakenBids
    bids += geminiBids

    asks.sort(key=lambda x: float(x[0])) #sort asks by lowest to highest price
    askPrice = responseParser(asks, quantity) #Parses Order and calculates Price to Buy 10 BTC

    bids.sort(key=lambda x: float(x[0]), reverse = True) #sort bids by highest to lowest price
    bidPrice = responseParser(bids, quantity) #Parses Order and calculates Price to Sell 10 BTC

    return {"Ask": askPrice, "Bid": bidPrice} 

"""
Parameter -> quantity: the number of BTC in the order
Return -> A List of all ask and bid orders from the Coinbase order book.
"asks" and "bids" are nested lists.

This function fetches the order book from Coinbase API and separates the
bids and asks from each other.
"""
def fetchCBOrderBook(quantity):
    url = 'https://api.pro.coinbase.com/products/BTC-USD/book?level=2'
    response = get(url) #GET Request to Coinbase API
    return [response["asks"], response["bids"]]

"""
Parameter -> quantity: the number of BTC in the order
Return -> A List of all ask and bid orders from the Gemini order book.
"asks" and "bids" are nested lists.

This function fetches the order book from Gemini API and separates the
bids and asks from each other.
"""
def fetchGeminiOrderBook(quantity):
    url = 'https://api.gemini.com/v1/book/BTCUSD'
    response = get(url) #GET Request to Gemini API

    bids = response["bids"]
    asks = response["asks"]
    return [geminiOrderBookFlattener(asks), geminiOrderBookFlattener(bids)] #reformats Gemini order book data in a nested list format just like Coinbase and Kraken

"""
Parameter -> quantity: the number of BTC in the order
Return -> A List of all ask and bid orders from the Kraken order book.
"asks" and "bids" are nested lists.

This function fetches the order book from Kraken API and separates the
bids and asks from each other.
"""
def fetchKrakenOrderBook(quantity):
    url = 'https://api.kraken.com/0/public/Depth?pair=XBTUSD'
    response = get(url) #GET Request to Kraken API
    return [response["result"]["XXBTZUSD"]["asks"], response["result"]["XXBTZUSD"]["bids"]]

"""
Parameter -> url: API Url to be called
Return -> response.json(): a JSON object of order data
"""
def get(url):
    response = requests.get(url)
    return response.json()

"""
Parameter -> response: a JSON object of ask or bid order book data
Return -> price: a float value representing the ask or bid price of 10 BTC

This function receives order book data and cumulatively sums the price of BTC
per order until over 10 BTC have been added. The total price of all summed
BTC orders are then divided by the number of BTC orders parsed to calculate
the price for 10 BTC. Parsing must be done by list index.
"""
def responseParser(response, quantity):
    totalPrice = 0.0
    orderQuantity = 0.0
    ordersAdded = 0

    for order in range(len(response)):
        if orderQuantity >= quantity: #if at least the inputted quantity BTC have been summed, stop parsing
            break
        totalPrice += float(response[order][0]) #working sum of BTC price per order
        orderQuantity += float(response[order][1]) #working sum of BTC being added which is <= 10.0
        ordersAdded += 1 #number of orders added

    price = float(totalPrice) / ordersAdded #calculate price of specified quantity of BTC by dividing the sum of all order prices parsed by the number of orders parsed
    return price

"""
Parameter -> response: ask or bid order book data where orders are structured 
as a list of dictionary entries.
Return -> orderBook: a list containing lists of orders

This function receives and parses either asks or bids from the Gemini order book and 
writes said data into a nested list in order to structure it in an identical manner to
Coinbase's (and Kraken's) order book .   
"""
def geminiOrderBookFlattener(response):
    orderBook = []

    for orderDict in response:
        orderBook.append([orderDict["price"], orderDict["amount"], orderDict["timestamp"]])
    return orderBook
   
main()