from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
import mysql.connector
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired
from passlib.hash import sha256_crypt
from functools import wraps
import gc
from datetime import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = '70cb4bdd167f34d84a682241'


def getConnection():
    conn = mysql.connector.connect(host = 'localhost', user = '****', password = '********', database = 'HORIZONTRAVELS')
    return conn

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login_page'))
    return wrap

def basic_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'basic'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main_page'))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'admin'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main_page'))
    return wrap

@app.route('/')
@app.route('/main/')
@app.route('/home/')
def main_page():
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT cityD FROM journeys;')
    rows = cursor.fetchall()

    cursor.execute('SELECT * FROM journeys;')
    journeys = cursor.fetchall()

    cursor.close()
    conn.close()
    cities = []
    for city in rows:
        city = str(city).strip("(")
        city = str(city).strip(")")
        city = str(city).strip(",")
        city = str(city).strip("'")
        cities.append(city)
    return render_template('main.html', departurelist = cities, journeylist = journeys)

@app.route('/returncity/', methods = ['POST', 'GET'])
def ajax_returncity():
    if request.method == 'GET':
        deptcity = request.args.get('q')
        
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT cityA FROM journeys WHERE cityD = %s;', (deptcity,))
        rows = cursor.fetchall()
        total = cursor.rowcount
        cursor.close()
        conn.close()
        return jsonify(returncities = rows, size = total)

@app.route('/aboutus/')
def aboutus_page():
    return render_template('aboutUs.html')

@app.route('/help/')
def help_page():
    return render_template('help.html')

@app.route('/privacypolicy/')
def privacypolicy_page():
    return render_template('privacyPolicy.html')

#Booking system
#Journey shows booking when going through home page
@app.route('/journey/', methods = ['POST', 'GET'])
def journey_page():
    if request.method == 'POST':
        if 'username' in session and session['username'] is not None:
            username = session['username']
        else:
            username = None
        departcity = request.form['departureslist']
        arrivalcity = request.form['arrivalslist']
        outdate = request.form['outdate']
        departcityreturn = arrivalcity
        arrivalcityreturn = departcity
        returndate = request.form['returndate']
        economySeats = request.form['economySeats']
        businessSeats = request.form['businessSeats']

        if returndate == "":
            returndate = "1980-01-01"

        lookupdata = [departcity, arrivalcity, outdate, departcityreturn, arrivalcityreturn, returndate, economySeats, businessSeats]
        
        conn = getConnection()
        cursor = conn.cursor()

        if username != None:
            cursor.execute('SELECT * FROM account WHERE username = %s;', (username,))
            accountid = cursor.fetchone()
            aid = accountid[0]
        else:
            aid = "0"

        cursor.execute('DELETE FROM basket WHERE aid = %s;', (aid,))
        conn.commit()

        cursor.execute('INSERT INTO basket (aid, cityD, cityA, dateD, dateRD, seatS, seatB) VALUES (%s, %s, %s, %s, %s, %s, %s);', \
                       (aid, departcity, arrivalcity, outdate, returndate, economySeats, businessSeats))   
        conn.commit()

        cursor.execute('SELECT * FROM basket WHERE aid = %s;', (aid,))
        basket = cursor.fetchall()

        lookupdata[0] = basket[0][2]
        lookupdata[1] = basket[0][3]
        lookupdata[2] = basket[0][4]

        if basket[0][5] == "1980-01-01":
            lookupdata[3] = "NORETURN"
            lookupdata[4] = "NORETURN"
            lookupdata[5] = basket[0][5]
        else:
            lookupdata[3] = basket[0][3]
            lookupdata[4] = basket[0][2]
            lookupdata[5] = basket[0][5]

        lookupdata[6] = basket[0][6]
        lookupdata[7] = basket[0][7]

        cursor.execute('SELECT * FROM journeys WHERE cityD = %s AND cityA = %s;', (str(lookupdata[0]), str(lookupdata[1])))
        rows = cursor.fetchall()
        datarows=[]
        for row in rows:
            data = list(row)
            fare = (float(row[5]) * float(lookupdata[6])) + (float(row[5]) * 2 * float(lookupdata[7]))
        
            outdateD = datetime.strptime(str(lookupdata[2].date()), '%Y-%m-%d')
            currentDate = datetime.now()
            daysUntilD = (outdateD - currentDate).days

            if daysUntilD >= 80:
                discount = 0.8
            elif daysUntilD >= 60:
                discount = 0.9
            elif daysUntilD >= 45:
                discount = 0.95
            else:
                discount = 1

            pricetotal = float(row[5]) * discount
            fare = pricetotal * (float(lookupdata[6]) + 2 * float(lookupdata[7]))
            data.append(fare)
            datarows.append(data)

        cursor.execute('SELECT * FROM journeys WHERE cityD = %s AND cityA = %s;', (lookupdata[1], lookupdata[0]))
        rows2 = cursor.fetchall()
        datarows2=[]
        for row in rows2:
            data = list(row)
            fare = (float(row[5]) * float(lookupdata[6])) + (float(row[5]) * 2 * float(lookupdata[7]))
            
            outdateD = datetime.strptime(str(lookupdata[5].date()), '%Y-%m-%d')
            currentDate = datetime.now()
            daysUntilD = (outdateD - currentDate).days

            if daysUntilD >= 80:
                discount = 0.8
            elif daysUntilD >= 60:
                discount = 0.9
            elif daysUntilD >= 45:
                discount = 0.95
            else:
                discount = 1

            pricetotal = float(row[5]) * discount
            fare = pricetotal * (float(lookupdata[6]) + 2 * float(lookupdata[7]))
            data.append(fare)
            datarows2.append(data)

        cursor.close()
        conn.close()
        return render_template('journey.html', resultset = datarows, resultset2 = datarows2, lookupdata = lookupdata, economy = economySeats, business = businessSeats, username = aid)

#Basket saves booking data for later use
@app.route('/basket/')
@login_required
def basket_page():
    if 'username' in session and session['username'] is not None:
        username = session['username']
        
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM account WHERE username = %s;', (username,))
        accountid = cursor.fetchone()
        aid = accountid[0]
        
        cursor.execute('SELECT * FROM basket WHERE aid = %s;', (aid,))
        basket = cursor.fetchall()

        if basket == []:
            cursor.execute('UPDATE basket SET aid = %s WHERE aid = %s;', (aid, '0'))
            conn.commit()
            
            cursor.execute('SELECT * FROM basket WHERE aid = %s;', (aid,))
            basket = cursor.fetchall()
        
        cursor.close()
        conn.close()

    else:
        aid = "0"
        
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM basket WHERE aid = %s;', (aid,))
        basket = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    lookupdata = ["", "", "", "", "", "", "", ""]

    if basket:
        lookupdata[0] = basket[0][2]
        lookupdata[1] = basket[0][3]
        lookupdata[2] = basket[0][4]

        if basket[0][5] == "1980-01-01":
            lookupdata[3] = "NORETURN"
            lookupdata[4] = "NORETURN"
            lookupdata[5] = str(basket[0][5])
        else:
            lookupdata[3] = basket[0][3]
            lookupdata[4] = basket[0][2]
            lookupdata[5] = basket[0][5]

        lookupdata[6] = basket[0][6]
        lookupdata[7] = basket[0][7]
    else:
        return redirect(url_for('main_page'))

    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM journeys WHERE cityD = %s AND cityA = %s;', (str(lookupdata[0]), str(lookupdata[1])))
    rows = cursor.fetchall()

    datarows=[]
    for row in rows:
        data = list(row)
        fare = (float(row[5]) * float(lookupdata[6])) + (float(row[5]) * 2 * float(lookupdata[7]))
    
        outdateD = datetime.strptime(str(lookupdata[2].date()), '%Y-%m-%d')
        currentDate = datetime.now()
        daysUntilD = (outdateD - currentDate).days

        if daysUntilD >= 80:
            discount = 0.8
        elif daysUntilD >= 60:
            discount = 0.9
        elif daysUntilD >= 45:
            discount = 0.95
        else:
            discount = 1

        pricetotal = float(row[5]) * discount
        fare = pricetotal * (float(lookupdata[6]) + 2 * float(lookupdata[7]))
        data.append(fare)
        datarows.append(data)

    cursor.execute('SELECT * FROM journeys WHERE cityD = %s AND cityA = %s;', (lookupdata[1], lookupdata[0]))
    rows2 = cursor.fetchall()

    datarows2=[]
    for row in rows2:
        data = list(row)
        fare = (float(row[5]) * float(lookupdata[6])) + (float(row[5]) * 2 * float(lookupdata[7]))
        
        outdateD = datetime.strptime(str(lookupdata[5].date()), '%Y-%m-%d')
        currentDate = datetime.now()
        daysUntilD = (outdateD - currentDate).days

        if daysUntilD >= 80:
            discount = 0.8
        elif daysUntilD >= 60:
            discount = 0.9
        elif daysUntilD >= 45:
            discount = 0.95
        else:
            discount = 1

        pricetotal = float(row[5]) * discount
        fare = pricetotal * (float(lookupdata[6]) + 2 * float(lookupdata[7]))
        data.append(fare)
        datarows2.append(data)

    cursor.close()
    conn.close()

    economyData = str(lookupdata[6])
    businessData = str(lookupdata[7])

    return render_template('journey.html', resultset = datarows, resultset2 = datarows2, lookupdata = lookupdata, economy = economyData, business = businessData, username = aid)

#Completes booking
@app.route ('/booking_confirm/', methods = ['POST', 'GET'])
def booking_confirm():
    if request.method == 'POST':
        username = session['username']
        
        jid = request.form['bookingchoiceD']
        if 'bookingchoiceR' in request.form:
            jidR = request.form['bookingchoiceR']
        else:
            jidR = "0000"
        cityD = request.form['cityD']
        cityA = request.form['cityA']
        dateD = request.form['dateD']
        if 'cityRD' in request.form:
            cityRD = request.form['cityRD']
        else:
            cityRD = "NORETURN"
        if 'cityRA' in request.form:
            cityRA = request.form['cityRA']
        else:
            cityRA = "NORETURN"
        if 'dateRD' in request.form:
            dateRD = request.form['dateRD']
        else:
            dateRD = "1980-01-01"
        seatS = request.form['seatS']
        if 'seatB' in request.form:
            seatB = request.form['seatB']
        else:
            seatB = "0"
        pricetotal = request.form['pricetotal']
        currentTime = datetime.now()
        bookedOn = currentTime.strftime("%Y-%m-%d %H:%M:%S")

        conn = getConnection()
        cursor = conn.cursor(buffered = True)

        cursor.execute('SELECT * FROM account WHERE username = %s;', (username,))
        accountid = cursor.fetchone()
        aid = accountid[0]

        cursor.execute('SELECT timeD FROM journeys WHERE jid = %s', (jid,))
        timeD = cursor.fetchone()
        dateD = datetime.strptime(dateD[:10], '%Y-%m-%d').date()
        timeD = datetime.strptime(timeD[0], '%H:%M').time()
        datetimeD = datetime.combine(dateD, timeD)
        datetimeDeparture = datetimeD.strftime('%Y-%m-%d %H:%M:%S')

        if dateRD != "1980-01-01":
            cursor.execute('SELECT timeD FROM journeys WHERE jid = %s', (jidR,))
            timeRD = cursor.fetchone()
            dateRD = datetime.strptime(dateRD[:10], '%Y-%m-%d').date()
            timeRD = datetime.strptime(timeRD[0], '%H:%M').time()
            datetimeRD = datetime.combine(dateRD, timeRD)
            datetimeDepartureR = datetimeRD.strftime('%Y-%m-%d %H:%M:%S')
        else:
            datetimeDepartureR = "1980-01-01 00:00:00"

        if jidR != "0000":
            pricetotal = str(float(pricetotal) * 2)

        bookingdata = [jid, jidR, cityD, cityA, datetimeDeparture, cityRD, cityRA, datetimeDepartureR, seatS, seatB, pricetotal, bookedOn]

        cursor.execute('INSERT INTO bookings (jid, jidR, aid, cityD, cityA, dateD, cityRD, cityRA, dateRD, seatS, seatB, pricetotal, bookedOn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);', \
                       (jid, jidR, aid, cityD, cityA, datetimeDeparture, cityRD, cityRA, datetimeDepartureR, seatS, seatB, pricetotal, bookedOn))
        conn.commit()
        
        cursor.execute('SELECT LAST_INSERT_ID();')
        rows = cursor.fetchone()
        bookingid = rows[0]
        bookingdata.append(bookingid)
        cursor.execute('SELECT * FROM journeys WHERE jid = %s;', (jid,))
        rows = cursor.fetchall()
        deptTime = rows[0][2]
        arrivTime = rows[0][4]
        bookingdata.append(deptTime)
        bookingdata.append(arrivTime)
        cursor.execute

        cursor.execute('DELETE FROM basket WHERE aid = %s;', (aid,))
        conn.commit()

        cursor.close()
        conn.close()
        gc.collect()
        return redirect(url_for('mytrip_page', resultset = bookingdata))

#Standard user account and mytrip features
@app.route('/account/')
@login_required
@basic_required
def account_page():
    return render_template('account.html', account = session['username'])

#Mytrip page
@app.route('/mytrip/')
@login_required
@basic_required
def mytrip_page():
    username = session['username']
    
    conn = getConnection()
    cursor = conn.cursor(buffered = True)
    cursor.execute("SELECT * FROM account WHERE username = %s;", (username,))
    accountid = cursor.fetchone()
    aid = accountid[0]

    cursor.execute("SELECT * FROM bookings WHERE aid = %s;", (aid,))
    rows = cursor.fetchall()
    bookingdata = []
    for row in rows:
        data = list(row)
        bookingdata.append(data)
    cursor.execute
    cursor.close()
    conn.close()
    return render_template('myTrip.html', resultset = bookingdata)

#Cancelling trips, calculates how much to refund customer
@app.route('/trip_cancel/', methods = ['POST', 'GET'])
@login_required
@basic_required
def trip_cancel():
    if request.method == 'POST':
        bid = request.form['delete']
        dateD = request.form['dateD']
        totalprice = request.form['totalprice']

        currentDate = datetime.now()
        outdateD = datetime.strptime(dateD, '%Y-%m-%d %H:%M:%S')
        daysUntilD = (outdateD - currentDate).days

        if daysUntilD >= 60:
            refundPercent = 1
        elif daysUntilD >= 30:
            refundPercent = 0.5
        else:
            refundPercent = 0

        refund = float(totalprice) * refundPercent
        print(refund)

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute("SELECT * FROM bookings WHERE bid = %s;", (bid,))
        cursor.fetchone()
        cursor.execute("DELETE FROM bookings WHERE bid = %s;", (bid,))
        conn.commit()
        cursor.close()
        conn.close()
        gc.collect()

        return render_template('cancelTrip.html', refund = int(refund))

#Shows cancelling confirmation
@app.route('/canceltrip/', methods = ['POST', 'GET'])
@login_required
@basic_required
def canceltrip_page():
    return render_template('cancelTrip.html')

#Modifying trips, updates prices based on booking in advance
@app.route('/trip_modify/', methods = ['POST', 'GET'])
@login_required
@basic_required
def trip_modify():
    if request.method == 'POST':
        bid = request.form['modify']
        jid = request.form['jid']
        cityD = request.form['cityD']
        cityA = request.form['cityA']
        dateD = request.form['dateDeparture']
        jidR = request.form['jidR']
        cityRD = request.form['cityRD']
        cityRA = request.form['cityRA']
        dateRD = request.form['dateDepartureReturn']
        seatS = request.form['seatEconomy']
        seatB = request.form['seatBusiness']

        if dateRD == "":
            dateRD = "1980-01-01"
            cityRD = "NORETURN"
            cityRA = "NORETURN"
        else:
            cityRD = cityA
            cityRA = cityD

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute('SELECT price FROM journeys WHERE jid = %s;', (jid,))
        priceStandard = cursor.fetchone()[0]
        priceStandard = float(priceStandard)

        outdateD = datetime.strptime(dateD, '%Y-%m-%d')
        currentDate = datetime.now()
        daysUntilD = (outdateD - currentDate).days

        if daysUntilD >= 80:
            discount = 0.8
        elif daysUntilD >= 60:
            discount = 0.9
        elif daysUntilD >= 45:
            discount = 0.95
        else:
            discount = 1

        pricetotal = ((int(seatS) * int(priceStandard)) + (int(seatB) * 2 * int(priceStandard))) * discount

        cursor.execute('SELECT timeD FROM journeys WHERE jid = %s;', (jid,))
        timeD = cursor.fetchone()[0]
        dateD = dateD + " " + timeD

        if dateRD != "1980-01-01":
            cursor.execute('SELECT jid FROM journeys WHERE cityD = %s AND cityA = %s;', (cityA, cityD,))
            jidR = cursor.fetchone()

            if jidR:
                jidR = jidR[0]

                cursor.execute('SELECT timeD FROM journeys WHERE jid = %s;', (jidR,))
                timeRD = cursor.fetchone()[0]
                dateRD = dateRD + " " + timeRD
                pricetotal = pricetotal * 2
            else:
                dateRD = "1980-01-01"
                cityRD = "NORETURN"
                cityRA = "NORETURN"
                flash(f'Return trip is not possible for this journey')

        cursor.execute('UPDATE bookings SET dateD = %s, cityRD = %s, cityRA = %s, dateRD = %s, seatS = %s, seatB = %s, pricetotal = %s WHERE bid = %s;', (dateD, cityRD, cityRA, dateRD, seatS, seatB, pricetotal, bid))
        conn.commit()
        cursor.close()
        conn.close()
        gc.collect()

        return redirect(url_for('mytrip_page'))

#Admin account and its various features
@app.route('/admin/')
@login_required
@admin_required
def admin_page():
    return render_template('accountAdmin.html', account = session['username'])

@app.route('/adminjourney/')
@login_required
@admin_required
def admin_journey():
    conn = getConnection()
    cursor = conn.cursor(buffered = True)
    cursor.execute('SELECT * FROM journeys;')
    journeys = cursor.fetchall()
    cursor.execute
    cursor.close()
    conn.close()

    return render_template('adminJourney.html', journeys = journeys)

#Adding new journey options
@app.route('/journey_add/', methods = ['POST', 'GET'])
@login_required
@admin_required
def journey_add():
    if request.method == 'POST':
        cityD = request.form['cityD']
        timeD = request.form['timeD']
        cityA = request.form['cityA']
        timeA = request.form['timeA']
        price = request.form['price']

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        sql_statement = "INSERT INTO journeys (cityD, timeD, cityA, timeA, price) VALUES (%s, %s, %s, %s, %s)"
        args = (cityD, timeD, cityA, timeA, price)
        cursor.execute(sql_statement, args)
        conn.commit()
        cursor.close()
        conn.close()
        gc.collect()

        return redirect(url_for('admin_journey'))

#Modifying existing journeys
@app.route('/journey_mod/', methods = ['POST', 'GET'])
@login_required
@admin_required
def journey_mod():
    if request.method == 'POST':
        jid = request.form['modify']
        cityD = request.form['cityDeparture']
        timeD = request.form['timeDeparture']
        cityA = request.form['cityArrival']
        timeA = request.form['timeArrival']
        price = request.form['priceStandard']

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute('SELECT * FROM journeys WHERE jid = %s;', (jid,))
        cursor.fetchone()
        sql_statement = "UPDATE journeys SET cityD = %s, timeD = %s, cityA = %s, timeA = %s, price = %s WHERE jid = %s;"
        args = (cityD, timeD, cityA, timeA, price, jid)
        cursor.execute(sql_statement, args)
        conn.commit()
        cursor.close()
        conn.close()
        gc.collect()

        return redirect(url_for('admin_journey'))

#Deleting existing journeys
@app.route('/journey_rem/', methods = ['POST', 'GET'])
@login_required
@admin_required
def journey_rem():
    if request.method == 'POST':
        jid = request.form['delete']

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute('SELECT * FROM journeys WHERE jid = %s;', (jid,))
        cursor.fetchone()
        cursor.execute("DELETE FROM journeys WHERE jid = %s;", (jid,))
        conn.commit()
        cursor.close()
        conn.close()
        gc.collect()

        return redirect(url_for('admin_journey'))

@app.route('/adminaccounts')
@login_required
@admin_required
def admin_accounts():
    conn = getConnection()
    cursor = conn.cursor(buffered = True)
    cursor.execute('SELECT * FROM account;')
    accounts = cursor.fetchall()
    cursor.execute
    cursor.close()
    conn.close()
    return render_template('adminAccounts.html', accounts = accounts)

#Adding new user accounts, similar to registration, hashes password
@app.route('/account_add/', methods = ['POST', 'GET'])
@login_required
@admin_required
def account_add():
    if request.method == 'POST':
        username = request.form['username']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        password = request.form['password']

        conn = getConnection()
        cursor = conn.cursor(buffered = True)

        salt = datetime.now()
        password = sha256_crypt.hash(str(password) + str(salt))

        Verify_Query = "SELECT * FROM account WHERE username = %s;"
        cursor.execute(Verify_Query,(username,))
        cursor.fetchall()
        if cursor.rowcount > 0:
            flash(f'User name already taken, please choose another')
        else:
            sql_statement = "INSERT INTO account (username, firstName, lastName, email, password_hash, password_salt) VALUES (%s, %s, %s, %s, %s, %s)"
            args = (username, firstName, lastName, email, password, str(salt))
            cursor.execute(sql_statement, args)
            conn.commit()
            cursor.close()
            conn.close()
            gc.collect()

        return redirect(url_for('admin_accounts'))

#Modifying existing user accounts
@app.route('/account_mod/', methods = ['POST', 'GET'])
@login_required
@admin_required
def account_mod():
    if request.method == 'POST':
        aid = request.form['modify']
        username = request.form['username']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute('SELECT * FROM account WHERE aid = %s;', (aid,))
        cursor.fetchone()
        sql_statement = "UPDATE account SET username = %s, firstName = %s, lastName = %s, email = %s WHERE aid = %s;"
        args = (username, firstName, lastName, email, aid)
        cursor.execute(sql_statement, args)
        conn.commit()
        cursor.close()
        conn.close()
        gc.collect()

        return redirect(url_for('admin_accounts'))

#Deleting existing user accounts
@app.route('/account_rem/', methods = ['POST', 'GET'])
@login_required
@admin_required
def account_rem():
    if request.method == 'POST':
        aid = request.form['delete']

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute('SELECT * FROM account WHERE aid = %s;', (aid,))
        cursor.fetchone()
        cursor.execute("DELETE FROM account WHERE aid = %s;", (aid,))
        conn.commit()
        cursor.close()
        conn.close()
        gc.collect()

        return redirect(url_for('admin_accounts'))

@app.route('/adminreports/')
@login_required
@admin_required
def admin_reports():
    conn = getConnection()
    cursor = conn.cursor(buffered = True)
    cursor.execute('SELECT * FROM bookings;')
    bookings = cursor.fetchall()
    
    cursor.execute('SELECT * FROM journeys;')
    journeys = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('adminReports.html', bookingslist = bookings, journeylist = journeys)

#Reports for all journeys within specified timeframe
@app.route('/report_com/', methods = ['POST', 'GET'])
@login_required
@admin_required
def report_com():
    if request.method == 'POST':
        bookingsFrom = datetime.strptime(request.form['bookingsFromCom'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        bookingsTo = datetime.strptime(request.form['bookingsToCom'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute('SELECT * FROM bookings WHERE bookedOn BETWEEN %s AND %s;', (bookingsFrom, bookingsTo,))
        reportData = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('adminReportsGen.html', reportData = reportData)

#Reports for specific journey within specified timeframe
@app.route('/report_ind/', methods = ['POST', 'GET'])
@login_required
@admin_required
def report_ind():
    if request.method == 'POST':
        jid = request.form['reportIDInd']
        print(jid)
        bookingsFrom = datetime.strptime(request.form['bookingsFromInd'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        bookingsTo = datetime.strptime(request.form['bookingsToInd'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute('SELECT * FROM bookings WHERE jid = %s AND bookedOn BETWEEN %s AND %s;', (jid, bookingsFrom, bookingsTo,))
        reportData = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('adminReportsGen.html', reportData = reportData)

#Top customer within specified timeframe
@app.route('/report_cust/', methods = ['POST', 'GET'])
@login_required
@admin_required
def report_cust():
    if request.method == 'POST':
        bookingsFrom = datetime.strptime(request.form['bookingsFromTop'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        bookingsTo = datetime.strptime(request.form['bookingsToTop'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute('SELECT aid, SUM(pricetotal) AS totalspent FROM bookings WHERE bookedOn BETWEEN %s AND %s GROUP BY aid ORDER BY totalspent DESC LIMIT 1;', (bookingsFrom, bookingsTo,))
        aid = cursor.fetchone()
        cursor.close()
        conn.close()

        return render_template('adminReportsGen.html', aid = aid)

#Top customer per journey within specified timeframe
@app.route('/report_custind/', methods = ['POST', 'GET'])
@login_required
@admin_required
def report_custind():
    if request.method == 'POST':
        jid = request.form['reportIDTopInd']
        bookingsFrom = datetime.strptime(request.form['bookingsFromTopInd'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        bookingsTo = datetime.strptime(request.form['bookingsToTopInd'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

        conn = getConnection()
        cursor = conn.cursor(buffered = True)
        cursor.execute('SELECT aid, SUM(pricetotal) AS totalspent FROM bookings WHERE jid = %s AND bookedOn BETWEEN %s AND %s GROUP BY aid ORDER BY totalspent DESC LIMIT 1;', (jid, bookingsFrom, bookingsTo,))
        aid = cursor.fetchone()
        cursor.close()
        conn.close()

        return render_template('adminReportsGen.html', aid = aid)

#Showing generated reports
@app.route('/report_gen/', methods = ['POST', 'GET'])
@login_required
@admin_required
def report_gen():
    return render_template('adminReportsGen.html')

#Account system
#Registration
class RegisterForm(FlaskForm):

    email = StringField(validators = [Email(), DataRequired()])
    username = StringField(validators = [Length(max = 20), DataRequired()])
    firstName = StringField(validators = [Length(max = 50), DataRequired()])
    lastName = StringField(validators = [Length(max = 50), DataRequired()])
    password = PasswordField(validators = [Length(min = 8), DataRequired()])
    passwordRepeat = PasswordField(validators = [EqualTo('password'), DataRequired()])
    submit = SubmitField(label = 'Register')

@app.route('/register/', methods = ['POST', 'GET'])
def register_page():
    form = RegisterForm()
    try:
        if request.method == "POST":
            email = form.email.data
            username = form.username.data
            firstName = form.firstName.data
            lastName = form.lastName.data
            password = form.password.data

            if form.validate_on_submit():
                conn = getConnection()
                cursor = conn.cursor()
                
                salt = datetime.now()
                password = sha256_crypt.hash(str(password) + str(salt))
                Verify_Query = "SELECT * FROM account WHERE username = %s;"
                cursor.execute(Verify_Query,(username,))
                cursor.fetchall()
                if cursor.rowcount > 0:
                    flash(f'User name already taken, please choose another')
                else:
                    sql_statement = "INSERT INTO account (email, username, firstName, lastName, password_hash, password_salt) VALUES (%s, %s, %s, %s, %s, %s)"
                    args = (email, username, firstName, lastName, password, str(salt))
                    cursor.execute(sql_statement, args)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    gc.collect()
                    
                    session['logged_in'] = True
                    session['username'] = username
                    session['usertype'] = 'basic'
                    return redirect(url_for('main_page', form = form))
        
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'Error creating account: {err_msg}')
        return render_template('register.html', form = form)
    
    except:
        return render_template('register.html', form = form)
    
    return render_template('register.html', form = form)

#Login
class LoginForm(FlaskForm):
    
    username = StringField(validators = [Length(max = 20), DataRequired()])
    password = PasswordField(validators = [Length(min = 8), DataRequired()])
    submit = SubmitField(label = 'Login')

@app.route('/login/', methods = ['POST', 'GET'])
def login_page():
    form = LoginForm()
    try:
        if request.method == "POST":
                username = form.username.data
                password = form.password.data
                
                if form.validate_on_submit():
                    conn = getConnection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT password_hash, password_salt, usertype FROM account WHERE username = %s;", (username,))
                    data = cursor.fetchone()

                    if cursor.rowcount < 1:
                        flash(f'Account does not exist, please register')
                    else:
                        if sha256_crypt.verify(password + data[1], str(data[0])):
                            session['logged_in'] = True
                            session['username'] = form.username.data
                            session['usertype'] = str(data[2])
                            return redirect(url_for('main_page', username = username, usertype = session['usertype']))
                        else:
                            flash(f'Invalid username or password')
                        
                        gc.collect()
                        return render_template("login.html", form = form)
            
                if form.errors != {}:
                    for err_msg in form.errors.values():
                        flash(f'Error creating account: {err_msg}')
                return render_template("login.html", form = form)
    
    except:
        flash(f'Account does not exist, please register')
        return render_template("login.html", form = form)
    
    return render_template("login.html", form = form)

#Change password
class ChangePasswordForm(FlaskForm):
    password = PasswordField(label = 'New Password', validators = [Length(min = 8), DataRequired()])
    passwordRepeat = PasswordField(label = 'Repeat New Password',validators = [EqualTo('password'), DataRequired()])
    submit = SubmitField(label = 'Change Password')

@app.route('/changepwd/', methods = ['POST', 'GET'])
@login_required
def changepwd():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        username = session['username']
        password = form.password.data
        
        conn = getConnection()
        cursor = conn.cursor()
    
        salt = datetime.now()
        password = sha256_crypt.hash(str(password) + str(salt))
    
        cursor.execute("SELECT password_hash FROM account WHERE username = %s;", (username,))                                                
        cursor.fetchone()
    
        sql_statement = "UPDATE account SET password_hash = %s, password_salt = %s WHERE username = %s;"
        args = (password, str(salt), username)
        cursor.execute(sql_statement, args)
        
        conn.commit()
        cursor.close()
        conn.close()
        gc.collect()
    
        return redirect(url_for('main_page', form = form))
    return render_template('changePWD.html', form = form)

#Logout
@app.route("/logout/")
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('main_page'))


if __name__ == '__main__':
    app.run(port = 5090, debug = True)