from flask import Flask, render_template, request, redirect, session, json
from pymongo import MongoClient
from bson.objectid import ObjectId
import razorpay
import math
from datetime import date, datetime


url = "mongodb+srv://farhankomban99:sPG15HTXqB3Ld4RB@cluster0.g46d69s.mongodb.net/?retryWrites=true&w=majority"
razorpayClient = razorpay.Client(auth=('rzp_test_Tum9Wc5xEZEhMb', '7RSFhkKUe4rQjxz5BMvWuSaE'))
client = MongoClient(url)
db = client['buzzzProject']

app = Flask(__name__)
app.secret_key = 'thisissomethingsecret'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        msg = ""
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        password = request.form.get("password")
        mail = request.form.get("mail")
        phoneNumber = request.form.get("phoneNumber")
        collection = db['Users']
        if(collection.find_one( { 'email' : mail } )):
            dt = { 'message' : "User Already Exists!", 'page' : "/login"}
            msg = "error"

        else : 
            newData = { 'firstName' : firstName, 'lastName' : lastName, 'password' : password, 'email' : mail, 'phoneNumber' : phoneNumber }
            collection.insert_one(newData)
            dt = { 'message' : "User Successfully Created.",  'page' : "/"}
            msg = "added"

        return render_template('register.html', message = msg)
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get("password")
        collection = db['Users']

        user = collection.find_one( { 'email' : username } )
        msg = ""
        if(user):
            if(user['password'] == password):
                session['data'] = str(user['_id'])
                return redirect('/home')

            else :
                msg = "Wrong Password! Please check your Password!"

        else : 
            msg = "No user found in this Username"
        return render_template('login.html', message = msg)
    return render_template('login.html')

@app.route('/aboutUs')
def aboutus():
    return render_template('aboutUs.html')

@app.route('/forgotPassword')
def forgotPassword():
    return render_template('forgotPassword.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    id = ObjectId(session['data'])
    collection = db['Users']
    data = collection.find_one({ '_id' : id })
    return render_template('profile.html', data = data)

@app.route('/changePassword')
def changePassword():
    id = ObjectId(session['data'])
    collection = db['Users']
    data = collection.find_one({ '_id' : id })
    return render_template('changePassword.html', data = data)

@app.route('/buses')
def buses():
    collection = db['Buses']
    collection2 = db['Routes']
    dt = collection.find()
    busData = []
    for i in dt:
        rt = collection2.find_one( { '_id' : i['start'] } )
        busData.append({ 'number' : i['busNumber'], 'name' : i['busName'], 'from' : rt['start'], 'to' : rt['end'] })
    return render_template('buses.html', data = busData)

@app.route('/routeMap')
def routeMap():
    return render_template('routeMap.html')


@app.route('/bookTicket', methods = ['GET', 'POST'])
def bookTicket():
    places = set()
    collection = db['Routes']
    tripCollection = db['Trips']
    lst = list(collection.find())
    for i in lst:
        for j in i['places']:
            places.add(j)
    place = sorted(list(places))
    
    if request.method == 'POST':
        flag = 0
        src = request.form.get('from')
        dest = request.form.get('to')
        for k, i in enumerate(lst):
            if src in i['places'] and dest in i['places']:
                flag = 1
                index = k
                break
        
        if flag == 1 :
            if lst[index]['dist'][src] < lst[index]['dist'][dest]:
                startTime = {}
                for k, i in enumerate(lst):
                    if src in i['places'] and dest in i['places']:
                        trp = list(tripCollection.find({ 'routeId' : str(i['_id']) }))
                        print("Here", trp)
                        for trips in trp:
                            sttm = int(trips['start'])
                            TotalTime = sttm + math.ceil((int(lst[index]['dist'][src]) * 1.75))
                            startTime.update({TotalTime : str(trips['busId'])})

                timeOut = {}
                for h in startTime:
                    ttm =f"{h//60 if len(str(h//60)) > 1 else '0'+str(h//60)}:{h%60 if len(str(h%60)) > 1 else '0'+str(h%60)}"
                    timeOut.update({ttm : startTime[h]})

                for k, i in enumerate(lst):
                    if src in i['places'] and dest in i['places']:
                        ticketPrice = max(math.ceil((lst[k]['dist'][dest] - lst[k]['dist'][src])*2.2), 10)
                        break
                        
                data = {'from' : src, 'to' : dest, 'times' : timeOut, 'ticketPrice' : ticketPrice}
                print(data)
                return f'''
                            <h1>Redirecting...</h1>
                            <form id="redirectForm" action="/ticket" method="POST">
                                <input type="hidden" name="data" value='{json.dumps(data)}'>
                            </form>
                            <script>
                                document.getElementById('redirectForm').submit();
                            </script>
                            '''             
        return render_template('bookTicket.html', place = place, message = "No bus Foung in this Route")
    return render_template('bookTicket.html', place = place)

@app.route('/transactions')
def transactions():
    collection = db['Orders']
    realData = []
    data = collection.find({ 'userId' : ObjectId(session["data"]) }).sort('date',1)
    
    for x in data:
        if x['date'] > str(date.today()):
            realData.append(x)

        elif x['date'] == str(date.today()):
            if x['time'] > str(datetime.now().strftime('%H:%M')):
                realData.append(x)


    return render_template('transactions.html', data = realData)

@app.route('/travelled')
def travelled():
    from datetime import date, datetime
    collection = db['Orders']
    realData = []
    data = collection.find({ 'userId' : ObjectId(session["data"]) }).sort('date',1)
    for x in data:
        if x['date'] < str(date.today()):
            realData.append(x)

        elif x['date'] == str(date.today()):
            if x['time'] < str(datetime.now().strftime('%H:%M')):
                realData.append(x)

    return render_template('travelled.html', data = realData)

@app.route('/cancel')
def cancel():
    collection = db['CancelledTicket']
    data = collection.find({ 'userId' : ObjectId(session["data"]) }).sort('date',1)
    return render_template('cancel.html', data = data)

@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

@app.route('/payment', methods = ['GET', 'POST'])
def payment():
    src = request.form.get('source')
    dest = request.form.get('destination')
    time = request.form.get('time')
    busIdData = request.form.get('busId')
    busIdData2 = eval(busIdData)
    busId = busIdData2[time]
    date = request.form.get('date')
    amt = int(request.form.get('priceData'))
    people = request.form.get('quantity')
    data = { "amount": amt*100, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = razorpayClient.order.create(data=data)
    otherDatas = {'src' : src, 'dest': dest, 'time' : time, 'date' : date, 'amt' : amt, 'people' : people, 'busId' : busId}
    return render_template('payment.html', payment=payment, otherDatas = otherDatas)

@app.route('/ticket', methods = ['GET', 'POST'])
def ticket():
    rc_data = json.loads(request.form.get('data'))
    dt = [{"src" : rc_data['from'], "dest" : rc_data['to'], "price" : rc_data['ticketPrice'], 'times' : rc_data['times']}]
    return render_template('ticket.html', data = dt)

@app.route('/profileEdited', methods = ['GET', 'POST'])
def profileEdited():
    id = ObjectId(session['data'])
    collection = db['Users']
    dt = request.form.to_dict()
    stripped_data = {k: v.strip() for k, v in dt.items()}
    collection.update_one( { '_id' : id }, { '$set' : stripped_data } )
    return redirect('/home')

@app.route('/changePasswordAction', methods = ['GET', 'POST'])
def changePasswordAction():
    password = request.form.get("pass1")
    data = { 'password' : password }
    id = ObjectId(session['data'])
    collection = db['Users']
    collection.update_one( { '_id' : id }, { '$set' : data } )
    return redirect('/home')

@app.route('/bookingDone', methods = ['POST'])
def bookingDone():
    data = json.loads(request.form.get('data'))
    collection = db['Buses']
    busDetails = collection.find_one({ '_id' : ObjectId(data['busId']) })
    data['busName'] = busDetails['busName']
    data['busNumber'] = busDetails['busNumber']
    data['userId'] = ObjectId(session['data'])
    data['check'] = "unchecked"
    collection2 = db['Orders']
    newData = collection2.insert_one(data)
    passData = newData.inserted_id
    return redirect(f'/{passData}/Orders/printTicket')

@app.route('/<id>/cancelTicket', methods = ['GET','POST'])
def delete(id):
    collection = db['Orders']
    collection2 = db['CancelledTicket']
    changeData = collection.find_one({ '_id' : ObjectId(id) })
    collection.delete_one({ '_id' : ObjectId(id) })
    collection2.insert_one(changeData)
    return redirect('/transactions')

@app.route('/logout')
def logout():
    session["data"] = None
    return redirect('/')

@app.route('/<id>/<dbname>/printTicket', methods = ['POST', 'GET'])
def printTicket(id, dbname):
    collection = db[dbname]
    data = collection.find_one({ '_id' : ObjectId(id.strip()) })
    return render_template('ticketPrint.html', data = data)

@app.route('/tst', methods = ['POST', 'GET'])
def tst():
    return render_template('scannerTest.html')


# =======================================ADMIN=============================================

@app.route('/admin')
def admin():
    return render_template('./adminPages/adminLogin.html')

@app.route('/adminLogin', methods = ['POST', 'GET'])
def adminLogin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get("password")
        collection = db['Admin']

        admin = collection.find_one( { 'username' : username } )
        msg = ""
        if(admin):
            if(admin['password'] == password):
                session['data'] = str(admin['_id'])
                return redirect('/adminHome')

            else :
                msg = "Wrong Password! Please check your Password!"

        else : 
            msg = "No user found in this Username"
        return render_template('./adminPages/AdminLogin.html', message = msg)
    return render_template('./adminPages/AdminLogin.html')

@app.route('/adminHome')
def adminHome():
    return render_template('./adminPages/adminHome.html')

@app.route('/adminUser')
def adminUser():
    return render_template('./adminPages/adminUser.html')

@app.route('/changeAdminPassword')
def changeAdminPassword():
    return render_template('./adminPages/changeAdminPassword.html')

@app.route('/changingRoute', methods = ['GET', 'POST'])
def changingRoute():
    collection = db['Routes']
    data = list(collection.find())
    for i in data:
        i['_id'] = str(i['_id'])
    
    if request.method == 'POST':
        id = request.form.get('rtId2')
        fromData = request.form.get('rtFrom')
        nameData = request.form.get('rtName')
        toData = request.form.get('rtTo')
        places = request.form.getlist('text_field1')
        distances = request.form.getlist('text_field2')
        dist = {}
        for i, value in enumerate(places):
            dist[value] = int(distances[i])
        newData = { 'start' : fromData, 'end': toData, 'places' : places, 'dist' : dist, 'name': nameData}
        collection.update_one({ '_id' : ObjectId(id) }, { '$set' : newData })
        return redirect('/changingRoute')
    return render_template('./adminPages/editRoute.html', data = data)

@app.route('/changeAdminPasswordAction', methods = ['POST'])
def changeAdminPasswordAction():
    newPass = request.form.get("pass1")
    collection = db['Admin']
    collection.update_one({ '_id' : ObjectId(session['data']) }, { '$set' : { 'password' : newPass } })
    return redirect('/adminHome')

@app.route('/changeConductorPasswordAction', methods = ['POST'])
def changeConductorPasswordAction():
    newPass = request.form.get("pass1")
    collection = db['Conductors']
    collection.update_one({ '_id' : ObjectId(session['data']) }, { '$set' : { 'password' : newPass } })
    return redirect('/conductorHome')

@app.route('/<id>/deleteRoute', methods = ['POST', 'GET'])
def deleteRoute(id):
    collection = db['Routes']
    collectionBus = db['Buses']
    collectionTrip = db['Trips']
    newId = ObjectId(id.strip())
    busData = collectionBus.find_one({ 'start' : newId })
    tripData = collectionTrip.find_one({ 'routeId' : newId })
    if busData or tripData:
        return f'''
                            <form id="redirectForm" action="/changingRoute">
                            </form>
                            <script>
                                alert("The Route Data is feeded in Trips Or in Buses. Cannot Be Deleted.")
                                document.getElementById('redirectForm').submit();
                            </script>
                            '''       
    else:
        collection.delete_one({ '_id' : newId })
    return redirect('/changingRoute')

@app.route('/addingRoute', methods = ['GET', 'POST'])
def addingRoute():
    if request.method == 'POST':
        collection = db['Routes']
        fromData = request.form.get('rtFrom')
        nameData = request.form.get('rtName')
        toData = request.form.get('rtTo')
        places = request.form.getlist('text_field1')
        distances = request.form.getlist('text_field2')
        dist = {}
        for i, value in enumerate(places):
            dist[value] = int(distances[i])
        newData = { 'start' : fromData, 'end': toData, 'places' : places, 'dist' : dist, 'name': nameData}
        collection.insert_one(newData)
        return render_template('./adminPages/addRoute.html', message = "Added Successfully.")
    return render_template('./adminPages/addRoute.html')

@app.route('/changingBus', methods = ['GET', 'POST'])
def changingBus():
    collection = db['Buses']
    collection2 = db['Routes']
    routesObtain = collection2.find()
    routesData = []
    for i in routesObtain:
        routesData.append({ '_id' : str(i['_id']),  'places' : str(i['start'] + ' To ' + i['end'])})
    dataObtained = collection.find()
    data = list(dataObtained)
    for i in data:
        i.pop('trips')
        i['start'] = str(i['start'])
        i['_id'] = str(i['_id'])
    if request.method == 'POST':
        newId = request.form.get('busId2')
        newName = request.form.get('busName')
        newNumber = request.form.get('busNumber')
        newRoute = request.form.get('busRoute')
        newData = { 'busName' : newName, 'busNumber' : newNumber, 'start':ObjectId(newRoute) }
        collection.update_one({ '_id' : ObjectId(newId) }, { '$set' : newData })
        return redirect('/changingBus')
    return render_template('./adminPages/editBuses.html', data = data, routesData = routesData)

@app.route('/addBuses', methods= ['GET', 'POST'])
def addBuses():
    collection2 = db['Routes']
    routesObtain = collection2.find()
    routesData = []
    for i in routesObtain:
        routesData.append({ '_id' : str(i['_id']),  'places' : str(i['start'] + ' To ' + i['end'])})
    if request.method == 'POST':
        collection = db['Buses']
        newName = request.form.get('busName')
        newNumber = request.form.get('busNumber')
        newRoute = request.form.get('busRoute')
        newData = {'busName' : newName, 'busNumber' : newNumber, 'start' : ObjectId(newRoute), 'trips' : []}
        collection.insert_one(newData)
        return render_template('./adminPages/addBuses.html', routesData = routesData, message = "Data Added Successfully")
    return render_template('./adminPages/addBuses.html', routesData = routesData)

def find(lst, finder):
    for i in lst:
        if(i['_id'] == ObjectId(finder)):
            return i

@app.route('/editTrips', methods = ['GET', 'POST'])
def editTrips():
    collection = db['Trips']
    collection2 = db['Buses']
    collection3 = db['Routes']
    allRoute = list(collection3.find())
    allBus = list(collection2.find())
    dtObtained = collection.find()
    busDataFullObtained = collection2.find()
    busDataFull = list(busDataFullObtained)
    for i in busDataFull:
        i['_id'] = str(i['_id'])

    routeDataFullObtained = collection3.find()
    routeDataFull = list(routeDataFullObtained)
    for i in routeDataFull:
        i['_id'] = str(i['_id'])
    
    data = []
    for i in dtObtained:
        h = i['start']
        ttm =f"{h//60 if len(str(h//60)) > 1 else '0'+str(h//60)}:{h%60 if len(str(h%60)) > 1 else '0'+str(h%60)}"
        busDataNew = find(allBus, i['busId'])
        routeDataNew = find(allRoute, i['routeId'])
        print(routeDataNew)
        if busDataNew:
            temp = {'_id' : str(i['_id']), 'start' : ttm, 'busName' : busDataNew['busName'], 'busId' : str(busDataNew['_id']), 'routeId' : str(i['routeId']), 'route' : f"{routeDataNew['start']} To {routeDataNew['start']}"}
            data.append(temp)
    return render_template('./adminPages/editTrips.html', data = data, busData = busDataFull, routeData = routeDataFull)

@app.route('/addTrips', methods = ['GET', 'POST'])
def addTrips():
    collection = db['Trips']
    collection2 = db['Buses']
    collection3 = db['Routes']
    busDataFullObtained = collection2.find()
    busDataFull = list(busDataFullObtained)
    for i in busDataFull:
        i['_id'] = str(i['_id'])

    routeDataFullObtained = collection3.find()
    routeDataFull = list(routeDataFullObtained)
    for i in routeDataFull:
        i['_id'] = str(i['_id'])

    if request.method == 'POST':
        busName = request.form.get('busName')
        busRoute = request.form.get('busRoute')
        startTime = request.form.get('startTime')
        hr = (int(startTime[:2])*60)+int(startTime[3:5])
        newData = {'start' : hr, 'routeId' : busRoute, 'busId' : busName}
        collection.insert_one(newData)
        print(busName, busRoute, startTime)
        return render_template('./adminPages/addTrips.html', busData = busDataFull, routeData =routeDataFull, message = "Data Entered SuccessFully")
    return render_template('./adminPages/addTrips.html', busData = busDataFull, routeData =routeDataFull)

@app.route('/<id>/deleteBuses', methods = ['POST', 'GET'])
def deleteBuses(id):
    collectionBus = db['Buses']
    collectionTrip = db['Trips']
    newIdStr = id.strip()
    newId = ObjectId(newIdStr)
    tripData = collectionTrip.find_one({ 'busId' : newIdStr })
    if tripData:
        return f'''
                            <form id="redirectForm" action="/changingBus">
                            </form>
                            <script>
                                alert("The Route Data is feeded in Trips. Cannot Be Deleted.")
                                document.getElementById('redirectForm').submit();
                            </script>
                            '''       
    else:
        collectionBus.delete_one({ '_id' : newId })
    return redirect('/changingBus')

@app.route('/<id>/deleteTrips', methods = ['POST', 'GET'])
def deleteTrips(id):
    collectionTrip = db['Trips']
    newId = ObjectId(id.strip())
    collectionTrip.delete_one({ '_id' : newId })
    return redirect('/editTrips')

@app.route('/addConductors', methods= ['GET', 'POST'])
def addCondudtors():
    collection2 = db['Buses']
    busObtain = collection2.find()
    busData = []
    for i in busObtain:
        busData.append({ '_id' : str(i['_id']), 'busName' : i['busName']})
    if request.method == 'POST':
        collection = db['Conductors']
        newName = request.form.get('conductorName')
        newUserName = request.form.get('conductorUsername')
        newPassword = request.form.get('conductorPassword')
        newBus = request.form.get('bus')
        newData = {'name' : newName, 'username' : newUserName, 'password' : newPassword, 'busId':newBus}
        collection.insert_one(newData)
        return render_template('./adminPages/conductorAdd.html', routesData = busData, message = "Data Added Successfully")
    return render_template('./adminPages/conductorAdd.html', busData = busData)

@app.route('/editConductor', methods = ['GET', 'POST'])
def editConductor():
    collection = db['Conductors']
    collectionBus = db['Buses']
    busObtain = collectionBus.find()
    busData = []
    for i in busObtain:
        busData.append({ '_id' : str(i['_id']),  'busName' : i['busName']})

    dataObtained = collection.find()
    data = list(dataObtained)
    for i in data:
        if i['busId'] == 'None':
            i['busName'] = 'None'
        else:
            i['busName'] = collectionBus.find_one({'_id' : ObjectId(i['busId'])})['busName']
        i['_id'] = str(i['_id'])
        i.pop('password')

    if request.method == 'POST':
        newId = request.form.get('conductorId2')
        newName = request.form.get('Name')
        newusername = request.form.get('username')
        newBus = request.form.get('Bus')
        newData = { 'name' : newName, 'username' : newusername, 'busId':newBus }
        collection.update_one({ '_id' : ObjectId(newId) }, { '$set' : newData })
        return redirect('/editConductor')
    return render_template('./adminPages/conductorEdit.html', data = data, busData = busData)

@app.route('/<id>/deleteConductor', methods = ['POST', 'GET'])
def deleteConductor(id):
    collection = db['Conductors']
    newId = ObjectId(id.strip())
    collection.delete_one({ '_id' : newId })
    return redirect('/editConductor')

@app.route('/orders', methods = ['GET', 'POST'])
def orders():
    collection = db['Orders']
    collectionUser = db['Users']
    orderData = collection.find()
    orderDataNew = []
    for i in orderData:
        i['_id'] = str(i['_id'])
        userData = collectionUser.find_one({'_id':i['userId']})
        i['user'] = userData['firstName'] + " " + userData['lastName']
        orderDataNew.append(i)
    return render_template('./adminPages/ordersView.html', data=orderDataNew)

@app.route('/ordersToday', methods = ['GET', 'POST'])
def ordersToday():
    collection = db['Orders']
    collectionUser = db['Users']
    orderData = collection.find({'date' : str(date.today())})
    orderDataNew = []
    for i in orderData:
        i['_id'] = str(i['_id'])
        userData = collectionUser.find_one({'_id':i['userId']})
        i['user'] = userData['firstName'] + " " + userData['lastName']
        orderDataNew.append(i)
    return render_template('./adminPages/ordersViewToday.html', data=orderDataNew)

@app.route('/conductorLogin', methods = ['GET', 'POST'])
def conductorLogin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get("password")
        collection = db['Conductors']

        user = collection.find_one( { 'username' : username } )
        msg = ""
        if(user):
            if(user['password'] == password):
                session['data'] = str(user['_id'])
                return redirect('/conductorHome')

            else :
                msg = "Wrong Password! Please check your Password!"

        else : 
            msg = "No user found in this Username"
        return render_template('./adminPages/conductorLogin.html', message = msg)
    return render_template('./adminPages/conductorLogin.html')

@app.route('/conductorHome', methods = ['GET', 'POST'])
def conductorHome():
    return render_template('./adminPages/conductorHome.html')

@app.route('/changeConductorPassword')
def changeConductorPassword():
    return render_template('./adminPages/conductorPasswordChange.html')

# ===============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8080', ssl_context = ("cert.pem", "key.pem"))