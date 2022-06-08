############################################################
############################################################

#PLEASE READ THE README FILE INCLUDED BEFORE DOING ANYTHING#
#THERE IS A LINK TO A VIDEO THAT SHOWS THE WEB APP RUNNING #
#IN CASE YOU CANNOT RUN THE WEB APP                        #

############################################################
############################################################


from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.engine.result import ResultMetaData, RowProxy
import random, string,os

app = Flask(__name__)


#connecting to db
dbConnect = ""
db = create_engine(dbConnect)

app.config['TEMPLATES_AUTO_RELOAD'] = True

app.secret_key = 'peepo'

def writeToSQL(file, sqlqueue):
    newline = '\n'
    with open(file, mode='w') as f:
        for sql in sqlqueue:
            f.write(sql + newline)

@app.route('/')
def toHomePage():
    return redirect(url_for('homepage'))

@app.route('/homepage')
def homepage():
    return render_template("index.html")

#renders webpage for booking flight
@app.route('/book', methods=['GET','POST'])
def bookFlight():
    sqlQueue = list()
    data = list()
    #showing available flights to book
    getAvailableFlights = "SELECT flight_id, flight_type, scheduled_departure, scheduled_arrival,departure_airport, arrival_airport, seats_available FROM flights ORDER BY flight_id"
    results = db.execute(getAvailableFlights)
    sqlQueue.append(getAvailableFlights)
    for i in results:
        data.append(i)
    
    if request.method == "POST":
        if request.form["submit_button"] is not None:
            #saving flight ID for later use as session var
            session['flightID'] = request.form['submit_button']
            flightid = session['flightID']
            temp = int(flightid) + 1
            flightid2 = str(temp)
            


            #checking if flight is full, t means it is full, f means it is not full
            if flightid == '1001' or flightid == '1003':
                isFull = ("SELECT CASE \n"
                            "WHEN (SELECT COUNT(*) FROM (SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_available = 0) AS a) > 0 THEN 't' \n"
                            "WHEN (SELECT COUNT(*) FROM (SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_available = 0) AS a) > 0 THEN 't' \n"
                            "ELSE 'f' END;")
            else:
                isFull = ("SELECT CASE \n"
                        "WHEN (SELECT COUNT(*) FROM (SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_available = 0) AS a) > 0 THEN 't' \n"
                        "ELSE 'f' END;")
            full = db.execute(isFull)
            sqlQueue.append(isFull)
            writeToSQL('query.sql', sqlQueue)
            answer = ""
            for rowproxy in full:
                for column, value in rowproxy.items():
                    b = value

            session['isSubmitting'] = True

            #do waitlist stuff here
            if b == 't':
                return render_template('waitlist.html')

            return redirect(url_for('info'))

    return render_template("book.html",data=data)

@app.route('/info',methods=['GET','POST'])
def info():
    sqlQueue = list()
    try:
        if 'isSubmitting' in session:
            if request.method == "POST":
                if request.form["submit_info"] == "submit":

                    session['name'] = request.form['name']
                    session['email'] = request.form['email']
                    session['phonenumber'] = request.form['phonenumber']
                    session['payment'] = request.form['payment']
                    session['fareCondition'] = request.form['fc']
                    session['currency'] = request.form['currency']
                    session['discount'] = request.form['discount']
                    session['rideStatus'] = request.form['status']
                    flightid = session.get('flightID')
                    info = list()
                    info2 = list()

                    
                    #insert user info to database using transactions and create ticket number and booking number.
                    bookRef = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                    bookRef = "B" + bookRef
                    ticketNum = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                    ticketNum = "T" + ticketNum
                    passengerid = ''.join(random.choice("123456789")for _ in range(9))
                    boardingid = ''.join(random.choice("123456789")for _ in range(11))
                    paymentid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
                    info.extend([session['name'],flightid,bookRef,ticketNum])

                    #For second ticket since the flight is indirect
                    bookRef2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                    bookRef2 = "B" + bookRef2
                    ticketNum2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                    ticketNum2 = "T" + ticketNum2
                    passengerid2 = ''.join(random.choice("123456789")for _ in range(9))
                    boardingid2 = ''.join(random.choice("123456789")for _ in range(11))
                    paymentid2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
                    temp = int(flightid) + 1
                    flightid2 = str(temp)
                    info2.extend([session['name'],flightid2,bookRef2,ticketNum2])

                    #sql queries to insert user data and beginning transaction
                    db.execute("BEGIN TRANSACTION;\n")
                    sqlQueue.append("BEGIN TRANSACTION;")
                    insertBookingsSql = ""
                    insertTicketFlightsSql = ""
                    insertPaymentSql = ""

                    #checking fare condition, currency and discount for pricing to insert into tables that require these fields
                    if flightid == '1001' or flightid == '1003':
                        if session['fareCondition'] == "business" and session['currency'] == "USD" and session['discount'] == "no":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'430.00');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','no','400.00','USD','"+session['payment']+"','30.00' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            

                            insertBookingsSql2 = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef2+"',CURRENT_TIMESTAMP,'430.00');")
                            insertTicketFlightsSql2 = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum2+"','"+flightid2+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql2 = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid2+"','"+bookRef2+"','no','400.00','USD','"+session['payment']+"','30.00' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "business" and session['currency'] == "USD" and session['discount'] == "yes":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'387.00');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','yes','360.00','USD','"+session['payment']+"','27.00' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            

                            insertBookingsSql2 = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef2+"',CURRENT_TIMESTAMP,'387.00');")
                            insertTicketFlightsSql2 = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum2+"','"+flightid2+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql2 = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid2+"','"+bookRef2+"','yes','360.00','USD','"+session['payment']+"','27.00' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "business" and session['currency'] == "CAD" and session['discount'] == "no":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'537.30');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','no','519.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")

                            insertBookingsSql2 = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef2+"',CURRENT_TIMESTAMP,'537.30');")
                            insertTicketFlightsSql2 = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum2+"','"+flightid2+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql2 = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid2+"','"+bookRef2+"','no','519.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "business" and session['currency'] == "CAD" and session['discount'] == "yes":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'486.30');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','yes','468.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")

                            insertBookingsSql2 = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef2+"',CURRENT_TIMESTAMP,'486.30');")
                            insertTicketFlightsSql2 = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum2+"','"+flightid2+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql2 = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid2+"','"+bookRef2+"','yes','468.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "economy" and session['currency'] == "USD" and session['discount'] == "no":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'268.75');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','no','250.00','USD','"+session['payment']+"','18.75' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")

                            insertBookingsSql2 = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef2+"',CURRENT_TIMESTAMP,'268.75');")
                            insertTicketFlightsSql2 = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum2+"','"+flightid2+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql2 = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid2+"','"+bookRef2+"','no','250.00','USD','"+session['payment']+"','18.75' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "economy" and session['currency'] == "USD" and session['discount'] == "yes":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'241.88');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','yes','225.00','USD','"+session['payment']+"','16.88' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")

                            insertBookingsSql2 = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef2+"',CURRENT_TIMESTAMP,'241.88');")
                            insertTicketFlightsSql2 = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum2+"','"+flightid2+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql2 = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid2+"','"+bookRef2+"','yes','225.00','USD','"+session['payment']+"','16.88' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "economy" and session['currency'] == "CAD" and session['discount'] == "no":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'343.30');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','no','325.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")

                            insertBookingsSql2 = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef2+"',CURRENT_TIMESTAMP,'343.30');")
                            insertTicketFlightsSql2 = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum2+"','"+flightid2+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql2 = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid2+"','"+bookRef2+"','no','325.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "economy" and session['currency'] == "CAD" and session['discount'] == "yes":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'310.30');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','yes','292.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")

                            insertBookingsSql2 = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef2+"',CURRENT_TIMESTAMP,'310.30');")
                            insertTicketFlightsSql2 = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum2+"','"+flightid2+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql2 = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid2+"','"+bookRef2+"','yes','292.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)
                        
                        insertTicketSql = ("INSERT INTO ticket(ticket_no,book_ref,passenger_id,passenger_name,email,phone) \n"
                                                "SELECT '"+ticketNum+"','"+bookRef+"','"+passengerid+"','"+session['name']+"','"+session['email']+"','"+session['phonenumber']+"' \n"
                                                "WHERE EXISTS\n"
                                                "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                        
                        insertTicketSql2 = ("INSERT INTO ticket(ticket_no,book_ref,passenger_id,passenger_name,email,phone) \n"
                                                "SELECT '"+ticketNum2+"','"+bookRef2+"','"+passengerid2+"','"+session['name']+"','"+session['email']+"','"+session['phonenumber']+"' \n"
                                                "WHERE EXISTS\n"
                                                "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")

                        sqlQueue.append(insertTicketSql)
                        #adds 1 to seats booked and subtracts one from seats available in flights table
                        updateSeatsSql = ("UPDATE flights \n"
                                        "SET seats_booked = seats_booked + 1, seats_available = seats_available - 1 \n"
                                        "WHERE seats_booked < 50 AND flight_id = "+flightid+";")
                        
                        updateSeatsSql2 = ("UPDATE flights \n"
                                        "SET seats_booked = seats_booked + 1, seats_available = seats_available - 1 \n"
                                        "WHERE seats_booked < 50 AND flight_id = "+flightid2+";")
                        sqlQueue.append(updateSeatsSql)
                        #dictionary for effecient inserting
                        boardingAndArrivalInfo = {
                            "1001": "A2,2020-12-20 00:45:00,2020-12-20 05:55:00,B12,4",
                            "1002": "B12,2020-12-20 06:25:00,2020-12-20 08:55:00,C9,5",
                            "1003": "A13,2021-01-16 00:25:00,2021-01-16 03:55:00,D11,1",
                            "1004": "D11,2021-01-16 04:25:00,2021-01-16 08:55:00,A4,2",
                            "1005": "C1,2020-12-23 00:45:00,2020-12-23 06:55:00,D12,6",
                            "1006": "D3,2020-12-26 23:45:00,2020-12-27 05:55:00,A5,8",
                            "1007": "D13,2020-12-27 03:45:00,2020-12-27 05:55:00,E1,9",
                            "1008": "A7,2021-01-12 22:45:00,2021-01-13 00:55:00,C7,3",
                            "1009": "E14,2021-01-16 19:25:00,2021-01-16 23:55:00,E1,7",
                            "1010": "C5,2021-01-24 05:45:00,2021-01-24 07:55:00,A14,10"
                        }
                        temp = boardingAndArrivalInfo.get(flightid).split(',')
                        temp2 = boardingAndArrivalInfo.get(flightid2).split(',')

                        #insert into boarding and arrival 
                        insertBoarding = ("INSERT INTO boarding(boarding_id,ticket_no,riding_status,gate,boarding_time) \n"
                                            "SELECT '"+boardingid+"','"+ticketNum+"','"+session['rideStatus']+"','"+temp[0]+"','"+temp[1]+"' \n"
                                            "WHERE EXISTS \n"
                                            "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")


                        insertBoarding2 = ("INSERT INTO boarding(boarding_id,ticket_no,riding_status,gate,boarding_time) \n"
                                            "SELECT '"+boardingid2+"','"+ticketNum2+"','"+session['rideStatus']+"','"+temp2[0]+"','"+temp2[1]+"' \n"
                                            "WHERE EXISTS \n"
                                            "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                        sqlQueue.append(insertBoarding)

                        insertArrival = ("INSERT INTO arrival(boarding_id,arrival_time,arrival_gate,baggage_claim) \n"
                                        "SELECT '"+boardingid+"','"+temp[2]+"','"+temp[3]+"','"+temp[4]+"' \n"
                                        "WHERE EXISTS \n"
                                        "(SELECT * FROM flights WHERE flight_id = '"+flightid+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")

                        insertArrival2 = ("INSERT INTO arrival(boarding_id,arrival_time,arrival_gate,baggage_claim) \n"
                                        "SELECT '"+boardingid2+"','"+temp2[2]+"','"+temp2[3]+"','"+temp2[4]+"' \n"
                                        "WHERE EXISTS \n"
                                        "(SELECT * FROM flights WHERE flight_id = '"+flightid2+"' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                        sqlQueue.append(insertArrival)
                        db.execute(insertBookingsSql+insertTicketSql+insertPaymentSql+insertTicketFlightsSql+updateSeatsSql+insertBoarding+insertArrival)
                        db.execute(insertBookingsSql2+insertTicketSql2+insertPaymentSql2+insertTicketFlightsSql2+updateSeatsSql2+insertBoarding2+insertArrival2+"COMMIT;")
                        sqlQueue.append('COMMIT;\n')
                        queryInfo = ("SELECT total_amount FROM bookings WHERE book_ref = '" +bookRef+"';\n")
                        r = db.execute(queryInfo)
                        for i in r:
                            info.append(i[0])
                        writeToSQL('transaction.sql', sqlQueue)
                        t = list()
                        t.append(queryInfo)
                        writeToSQL('query.sql', t)

                        return render_template("booking_info.html",info = info,ticketNum2 = ticketNum2)

                    else:
                        if session['fareCondition'] == "business" and session['currency'] == "USD" and session['discount'] == "no":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'430.00');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','no','400.00','USD','"+session['payment']+"','30.00' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "business" and session['currency'] == "USD" and session['discount'] == "yes":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'387.00');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','yes','360.00','USD','"+session['payment']+"','27.00' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "business" and session['currency'] == "CAD" and session['discount'] == "no":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'537.30');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','no','519.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "business" and session['currency'] == "CAD" and session['discount'] == "yes":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'486.30');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','business' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','yes','468.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "economy" and session['currency'] == "USD" and session['discount'] == "no":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'268.75');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','no','250.00','USD','"+session['payment']+"','18.75' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "economy" and session['currency'] == "USD" and session['discount'] == "yes":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'241.88');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','yes','225.00','USD','"+session['payment']+"','16.88' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "economy" and session['currency'] == "CAD" and session['discount'] == "no":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'343.30');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','no','325.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)

                        elif session['fareCondition'] == "economy" and session['currency'] == "CAD" and session['discount'] == "yes":
                            insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'310.30');")
                            insertTicketFlightsSql = ("INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) \n"
                                                    "SELECT '"+ticketNum+"','"+flightid+"','economy' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            insertPaymentSql = ("INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) \n"
                                                    "SELECT '"+paymentid+"','"+bookRef+"','yes','292.00','CAD','"+session['payment']+"','18.30' \n"
                                                    "WHERE EXISTS \n"
                                                    "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                            sqlQueue.append(insertBookingsSql)
                            sqlQueue.append(insertTicketFlightsSql)
                            sqlQueue.append(insertPaymentSql)
                        
                        insertTicketSql = ("INSERT INTO ticket(ticket_no,book_ref,passenger_id,passenger_name,email,phone) \n"
                                                "SELECT '"+ticketNum+"','"+bookRef+"','"+passengerid+"','"+session['name']+"','"+session['email']+"','"+session['phonenumber']+"' \n"
                                                "WHERE EXISTS\n"
                                                "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                        sqlQueue.append(insertTicketSql)
                        #adds 1 to seats booked and subtracts one from seats available in flights table
                        updateSeatsSql = ("UPDATE flights \n"
                                        "SET seats_booked = seats_booked + 1, seats_available = seats_available - 1 \n"
                                        "WHERE seats_booked < 50 AND flight_id = "+flightid+";")
                        sqlQueue.append(updateSeatsSql)
                        #dictionary for effecient inserting
                        boardingAndArrivalInfo = {
                            "1001": "A2,2020-12-10 00:45:00,2020-12-10 05:55:00,B12,4",
                            "1002": "B12,2020-12-10 06:25:00,2020-12-10 08:55:00,C9,5",
                            "1003": "A13,2021-01-16 00:25:00,2021-01-16 03:55:00,D11,1",
                            "1004": "D11,2021-01-16 04:25:00,2021-01-16 08:55:00,A4,2",
                            "1005": "C1,2020-12-13 00:45:00,2020-12-13 06:55:00,D12,6",
                            "1006": "D3,2020-12-26 23:45:00,2020-12-27 05:55:00,A5,8",
                            "1007": "D13,2020-12-07 03:45:00,2020-12-07 05:55:00,E1,9",
                            "1008": "A7,2021-01-12 22:45:00,2021-01-13 00:55:00,C7,3",
                            "1009": "E14,2021-01-16 19:25:00,2021-01-16 23:55:00,E1,7",
                            "1010": "C5,2021-01-24 05:45:00,2021-01-24 07:55:00,A14,10"
                        }
                        temp = boardingAndArrivalInfo.get(flightid).split(',')

                        #insert into boarding and arrival 
                        insertBoarding = ("INSERT INTO boarding(boarding_id,ticket_no,riding_status,gate,boarding_time) \n"
                                            "SELECT '"+boardingid+"','"+ticketNum+"','"+session['rideStatus']+"','"+temp[0]+"','"+temp[1]+"' \n"
                                            "WHERE EXISTS \n"
                                            "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                        sqlQueue.append(insertBoarding)
                        insertArrival = ("INSERT INTO arrival(boarding_id,arrival_time,arrival_gate,baggage_claim) \n"
                                        "SELECT '"+boardingid+"','"+temp[2]+"','"+temp[3]+"','"+temp[4]+"' \n"
                                        "WHERE EXISTS \n"
                                        "(SELECT * FROM flights WHERE flight_id = "+flightid+" AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);")
                        sqlQueue.append(insertArrival)
                        db.execute(insertBookingsSql+insertTicketSql+insertPaymentSql+insertTicketFlightsSql+updateSeatsSql+insertBoarding+insertArrival+"COMMIT;")
                        sqlQueue.append('COMMIT;\n')
                        queryInfo = ("SELECT total_amount FROM bookings WHERE book_ref = '" +bookRef+"';\n")
                        r = db.execute(queryInfo)
                        for i in r:
                            info.append(i[0])
                        writeToSQL('transaction.sql', sqlQueue)
                        t = list()
                        t.append(queryInfo)
                        writeToSQL('query.sql', t)
                        return render_template("booking_info.html",info = info)
            
            return render_template("type_info.html")

        return redirect(url_for('returnToHome'))
    except:
        return redirect(url_for('returnToHome'))


@app.route('/returnToHome')
def returnToHome():
    #pop session variables
    session.pop('isSubmitting',None)
    #writeToSQL('flight_sql.sql')
    return redirect(url_for('homepage'))


#renders webpage for finding flight info
@app.route('/findFlight',methods=['GET','POST'])
def findFlight():
    session.pop('isSubmitting',None)
    return render_template("findFlight.html")

@app.route('/searchResults', methods=['GET','POST'])
def searchResults():
    sqlQueue = list()
    session.pop('isSubmitting',None)
    
    try:
        if request.method == 'POST':    
            if request.form['search'] == "search":
                
                message = ""
                #perform sql queries here for users to search info based on ticket number
                ticketNo = request.form['ticket']
                data1 = list()
                data2 = list()
                data3 = list()

                search1Sql = ("SELECT ticket_no, passenger_name, email, phone, amount_due FROM ticket \n"
                        "JOIN bookings b ON ticket.book_ref = b.book_ref \n"
                        "JOIN payment p ON b.book_ref = p.book_ref \n"
                        "WHERE ticket_no = '"+ticketNo+"';")
                result1 = db.execute(search1Sql)
                sqlQueue.append(search1Sql)
                for i in result1:
                    data1.append(i)
                
                search2Sql = ("SELECT ticket_no,f.flight_id, flight_type, scheduled_departure, scheduled_arrival, departure_airport, arrival_airport, movie, meal FROM ticket_flights \n"
                        "join flights f on ticket_flights.flight_id = f.flight_id \n"
                        "where ticket_no = '"+ticketNo+"';")
                result2 = db.execute(search2Sql)
                sqlQueue.append(search2Sql)
                for i in result2:
                    data2.append(i)
                
                search3Sql = ("select ticket_no,a.boarding_id, gate, boarding_time, arrival_time, arrival_gate, baggage_claim from boarding \n"
                        "join arrival a on boarding.boarding_id = a.boarding_id \n"
                        "WHERE ticket_no = '"+ticketNo+"';")
                result3 = db.execute(search3Sql)
                sqlQueue.append(search3Sql)
                writeToSQL('query.sql', sqlQueue)
                for i in result3:
                    data3.append(i)

                #if ticket does not exist then pass a error message to render in html    
                if len(data1) == 0:
                    message = "ticket does not exist try again!"
                    return render_template('findFlight.html',message=message)

                return render_template('searchResult.html',data1=data1, data2 = data2, data3=data3)
    except:
        message = "There was an error"
        return render_template('findFlight.html',message=message)

@app.route('/clerk', methods=['GET','POST'])
def clerk():
    try:
        if request.method == 'POST': 
            if request.form['clerk'] == "clerk":
                    clerkSql = ("SELECT waitlist_number,passenger_name,email \n"
                                "FROM waitlist;")
                    
                    data = list()
                    result = db.execute(clerkSql)
                    for i in result:
                        data.append(i)
                    return render_template('clerk.html',data=data)
    except:
        message = "There was an error"
        return render_template('findFlight.html',message=message)

    

@app.route('/waitlist', methods=['GET','POST'])
def waitlist():
    sqlQueue = list()
    try:
        if 'isSubmitting' in session:
            if request.method == "POST":
                    if request.form["submit_waitlist"] == "submit":
                        
                        #getting info from waitlist form
                        name = request.form['name']
                        email = request.form['email']
                        bookRef = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                        bookRef = "B" + bookRef
                        boardingid = ''.join(random.choice("123456789")for _ in range(11))

                        #inserting into waitlist table and booking table
                        insertBookingsSql = ("INSERT INTO bookings(book_ref,book_date,total_amount) \n"
                                            "VALUES('"+bookRef+"',CURRENT_TIMESTAMP,'00.00');")
                        insertWaitlistSql = ("INSERT INTO waitlist(book_ref,passenger_name,email) \n"
                                            "VALUES('"+bookRef+"','"+name+"','"+email+"');")
                        db.execute("BEGIN TRANSACTION; \n"
                                    + insertBookingsSql +"\n"+ insertWaitlistSql + "; \n COMMIT;")
                        sqlQueue.append("BEGIN TRANSACTION; \n" + insertBookingsSql +"\n"+ insertWaitlistSql + "; \n COMMIT;")
                        writeToSQL('transaction.sql', sqlQueue)
                        return redirect(url_for('returnToHome'))
    except:
        return redirect(url_for('returnToHome'))

@app.route('/reset', methods=['GET','POST'])
def reset():
    if request.method == "POST":
        file = open('db.sql')
        query = text(file.read())
        db.execute(query)
        return redirect(url_for('returnToHome'))
    return render_template('resetDB.html')

if __name__ == "__main__":
    app.run(debug=True)