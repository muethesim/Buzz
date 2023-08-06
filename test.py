from flask import Flask, render_template
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

url = "mongodb+srv://farhankomban99:sPG15HTXqB3Ld4RB@cluster0.g46d69s.mongodb.net/?retryWrites=true&w=majority"

app = Flask(__name__)

# collection = db['Routes']
# collection2 = db['Trips']
# collection3 = db['Buses']
# collection4 = db['Users']

# client = MongoClient(url)
# db = client['buzzzProject']

# async def fetch_data_from_mongodb():

#     collection = db['Buses']
#     data = await collection.find({})
#     dt = list(data)

#     return dt

# @app.route('/')
# async def display_data():
#     # Fetch data from MongoDB asynchronously
#     data = await fetch_data_from_mongodb()
#     print(data)
#     return render_template('aboutUs.html')

# if __name__ == '__main__':
#     # Run the application asynchronously
#     loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.gather(app.run(debug=True), loop=loop))



# lst = list(collection.find())

# dest = 'c'
# src = 'a'

# print(math.ceil((lst[0]['dist'][dest] - lst[0]['dist'][src])*2.2))

# print(type(lst[0]['dist'][dest]))

# from datetime import date, datetime

# print(date.today())
# print(datetime.now().strftime('%H:%M'))

# print("2023-01-20" < "2023-01-21")
# print("00:30"<"12:31")

# places = set()
# collection = db['Routes']
# tripCollection = db['Trips']
# lst = list(collection.find())
# for i in lst:
#     for j in i['places']:
#         places.add(j)
# place = sorted(list(places))

# print("PLACES : ",  place)
# flag = 0
# src = 'a'
# dest = 'c'
# for k, i in enumerate(lst):
#     if src in i['places'] and dest in i['places']:
#         flag = 1
#         index = k
#         break

# if flag == 1 :
#     if lst[index]['dist'][src] < lst[index]['dist'][dest]:
#         startTime = {}
#         for k, i in enumerate(lst):
#             if src in i['places'] and dest in i['places']:
#                 trp = list(tripCollection.find({ 'routeId' : i['_id'] }))
#                 for trips in trp:
#                     sttm = int(trips['start'])
#                     TotalTime = sttm + math.ceil((int(lst[index]['dist'][src]) * 1.75))
#                     startTime.update({TotalTime : trips['busId']})

#         print(startTime)

#         timeOut = {}
#         for h in startTime:
#             ttm =f"{h//60 if len(str(h//60)) > 1 else '0'+str(h//60)}:{h%60 if len(str(h%60)) > 1 else '0'+str(h%60)}"
#             timeOut.update({ttm : startTime[h]})

#         print(timeOut)

#         ticketPrice = max(math.ceil((lst[0]['dist'][dest] - lst[0]['dist'][src])*2.2), 10)
                        
#         data = {'from' : src, 'to' : dest, 'times' : timeOut, 'ticketPrice' : ticketPrice}

#         print(data)


# import json

# # String representation of a dictionary
# string_data = "{'12:30': '64a402b300929f124853777d', '15:30': '64a402b300929f124853777d'}"

# # Convert the string to a dictionary
# dictionary = eval(string_data)

# # Access and print values in the dictionary
# print(type(dictionary))


# l = {'a' : 'fd', 'b':'sefe'}
# print(list(l.values()))

# time = '13:25'

# tm = (int(time[:2])*60)+int(time[3:5])

# print(tm)

def find(lst, finder):
    for i in lst:
        if(i['a'] == finder):
            return i

hello = [{'a' : 1}, {'a' : 2}, {'a' : 3}]

print(find(hello, 2))