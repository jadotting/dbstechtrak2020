from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
#from firebase import firebase
import tkinter
from tkinter import *
import sqlalchemy
#import win32api
import mysql.connector
import requests
import datetime
import random
import string

app = Flask(__name__)
app.secret_key = "hello"
#app.permanent_session_lifetime = timedelta(seconds=100)

@app.route("/", methods=["POST", "GET"])
def login():
    MAIN_URL = "https://u8fpqfk2d4.execute-api.ap-southeast-1.amazonaws.com/techtrek2020/login"

    if request.method == "POST":
        user = request.form["nm"]
        salt = generateSalt()
        password = request.form["pass"] +"!@#$#@!" + salt #password salting
        print(password)
        passwords = password.split("!@#$#@!")
        result = requests.post(MAIN_URL, headers={'x-api-key': '1elJCmVDjP45as0PT9fsEmHvP03074O8h05lQUmh'}, json={'username':user, 'password':passwords[0]}) #payload = {'username': 'corey', 'password': 'testing'}
        #result = requests.post(MAIN_URL, headers={'x-api-key': '1elJCmVDjP45as0PT9fsEmHvP03074O8h05lQUmh'}, json={'username':'Group18', 'password':'GN8lYWvsWU5YaOx'}) #payload = {'username': 'corey', 'password': 'testing'}
        number = result.status_code
        if number == 200:
            result_dict = result.json()
            if request.form["test"] == "yes":
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=5)
                session["user"] = user
                session["custID"] = result_dict["custID"]
                session["lastName"] = result_dict["lastName"]
                session["address"] = result_dict["address"]
                session["email"] = result_dict["email"]
                session["firstName"] = result_dict["firstName"]
                session["nric"] = result_dict["nric"]
                session["gender"] = result_dict["gender"]
                session["age"] = result_dict["age"]
                flash("Login successful!")
                print("i am here")
                return redirect(url_for("user"))
            else:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=5) 
                session["user"] = user
                session["custID"] = result_dict["custID"]
                session["lastName"] = result_dict["lastName"]
                session["address"] = result_dict["address"]
                session["email"] = result_dict["email"]
                session["firstName"] = result_dict["firstName"]
                session["nric"] = result_dict["nric"]
                session["gender"] = result_dict["gender"]
                session["age"] = result_dict["age"]
                flash("Login successful!")
                print("i am here1")
                return redirect(url_for("user"))
        else:
            flash(f"Error {number}", "warning")
            return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        else:
            return render_template("login.html")

def generateSalt(chars = string.ascii_uppercase + string.digits, N=10):
    return ''.join(random.choice(chars) for _ in range(N))

#956.29, 413.05, 10
@app.route("/user")
def user():
    MAIN_URL = "https://u8fpqfk2d4.execute-api.ap-southeast-1.amazonaws.com/techtrek2020/accounts/view"
    
    if "user" in session:
        user = session["user"]
        custID = session["custID"]
        result = requests.post(MAIN_URL, headers={'x-api-key': '1elJCmVDjP45as0PT9fsEmHvP03074O8h05lQUmh'}, json={'custID': custID}) #payload = {'username': 'corey', 'password': 'testing'}
        result_list = result.json()
        result_dict = result_list[0]
        accountNumber = []
        accountName = []
        availableBal = []
        linked = []
        for row in result_list:
            accountNumber.append(row['accountNumber'])
            accountName.append(row['accountName'])
            availableBal.append(row['availableBal'])
            linked.append(row['linked'])
            foo = zip(accountName, accountNumber, availableBal, linked)
        session["accountName"] = accountName
        session["availableBal"] = availableBal
        return render_template("user.html", user=user, accountDetails = foo)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info") #warning, info and error
    list = ["user", "custID", "lastName", "address", "email","firstName", "nric", "gender", "age", "accountName", "availableBal"] 
    for value in list:
        session.pop(value, None)
    return redirect(url_for("login"))

@app.route("/trf", methods=["POST", "GET"])
def trf():       
    MAIN_URL = "https://u8fpqfk2d4.execute-api.ap-southeast-1.amazonaws.com/techtrek2020/accounts/update"

    if "user" in session:
        phonenumber_custID = getPayeeIDs()
        #phonenumber_custID = {}
        if request.method == "POST":
            #form for add transaction
            user = session["user"]
            custID = session["custID"]
            countryCode = request.form["countryCode"]
            phoneNumber = request.form["phoneNumber"]
            #check payee id
            phoneNumber2 = "(+" + countryCode + ")" + phoneNumber
            phoneNumber2.replace(" ","")
            payeeID = phonenumber_custID[phoneNumber2]
            amount = request.form["amount"]
            accountType = request.form["accountType"]
            accountName = session["accountName"]
            availableBal = session["availableBal"]
            #check count bal not working :(
            #if accountType == "ca":
            #    for i in range(len(accountName)):
            #        if (accountType[i] == "Current Account"):
            #            if (availableBal[i] < amount):
            #                flash(f"Not enough money in Current Account", "error")
            #if accountType == "ma":
            #    for i in range(len(accountName)):
            #        if (accountType[i] == "Multipier Account"):
            #            if (availableBal[i] < amount):
            #                flash(f"Not enough money in Multipier Account", "error")
            #if accountType == "sa":
            #    for i in range(len(accountName)):
            #        if (accountType[i] == "Saving Account"):
            #            print(amount)
            #            print(availableBal[i])
            #            if (availableBal[i] < amount):
            #                flash(f"Not enough money in Saving Account", "error")
            expensesCat = request.form["expensesCat"]
            eGift = request.form["eGift"]
            eGiftMessage = False
            if eGift == "yes":
                eGiftMessage = True
            message = request.form["message"]
            datetime_now = datetime.datetime.today() #cannot parse to json in date format
            addTransaction(custID=custID, payeeID=payeeID, dateTime= "", amount=amount, expensesCat=expensesCat, eGift=eGiftMessage, message=message)
            result = requests.post(MAIN_URL, headers={'x-api-key': '1elJCmVDjP45as0PT9fsEmHvP03074O8h05lQUmh'}, json={'custID': custID, 'amount': amount}) #payload = {'username': 'corey', 'password': 'testing'}
            #result_list = result.text()
            number = result.status_code
            if number == 200:
                #load details
                flash(f"Success in transfer, {number}", "info") #warning, info and error
            else:
                flash(f"Error in transfer, {number}", "info") #warning, info and error
        else:
            user = session["user"]
            custID = session["custID"]
        return render_template("transfer.html")
    else:
        flash("you are not logged in!")
        return redirect(url_for("login"))

def addTransaction(custID, payeeID, dateTime, amount, expensesCat, eGift, message):
    MAIN_URL = "https://u8fpqfk2d4.execute-api.ap-southeast-1.amazonaws.com/techtrek2020/transaction/add"
    result = requests.post(MAIN_URL, headers={'x-api-key': '1elJCmVDjP45as0PT9fsEmHvP03074O8h05lQUmh'},
                           json={'custID': custID, 'payeeID': payeeID, 'dateTime': dateTime, 'amount': amount, 'expensesCat': expensesCat, 'eGift': eGift, 'message': message}) #payload = {'username': 'corey', 'password': 'testing'}
    number = result.status_code
    if number == 200:
                #load details
        print("success")
        flash(f"Success in adding transaction, {number}", "info") #warning, info and error
    else:
        print("failure")
        flash(f"Error in adding transaction, {number}", "info") #warning, info and error
        
def getPayeeIDs():
    MAIN_URL = "https://u8fpqfk2d4.execute-api.ap-southeast-1.amazonaws.com/techtrek2020/users"
    result = requests.post(MAIN_URL, headers={'x-api-key': '1elJCmVDjP45as0PT9fsEmHvP03074O8h05lQUmh'}) #payload = {'username': 'corey', 'password': 'testing'}
    result_lists = result.json()
    phonenumber_custID = {
        }
    for row in result_lists:
        custID = row["custID"]
        phoneNumber = row["phoneNumber"].replace(" ","")
        phonenumber_custID[phoneNumber] = custID
    return phonenumber_custID
    
@app.route("/th")
def th():
    if "user" in session:
        user = session["user"]
        custID = session["custID"]
        MAIN_URL = "https://u8fpqfk2d4.execute-api.ap-southeast-1.amazonaws.com/techtrek2020/transaction/view"
        result = requests.post(MAIN_URL, headers={'x-api-key': '1elJCmVDjP45as0PT9fsEmHvP03074O8h05lQUmh'}, json={'custID': custID}) #payload = {'username': 'corey', 'password': 'testing'}
        result_lists = result.json()
        print(result_lists)
        eGiftList = []
        dateTimeList = []
        custIDList = []
        expensesCatList = []
        amountList = []
        messageList = []
        payeeIDList = []
        for row in result_lists:
            eGiftList.append(row['eGift'])
            dateTimeList.append(row['dateTime'])
            custIDList.append(row['custID'])
            expensesCatList.append(row['expensesCat'])
            amountList.append(row['amount'])
            messageList.append(row['message'])
            payeeIDList.append(row['payeeID'])
            foo = zip( eGiftList, dateTimeList, custIDList, expensesCatList, amountList, messageList, payeeIDList)
        return render_template("transactionHistory.html", details = foo)
    else:
        flash("you are not logged in!")
        return redirect(url_for("login"))

@app.route("/finduser", methods=["GET", "POST"])
def finduser():
    if request.method == "POST":
        if request.form['btn_identifier'] == 'phonenumbersearch':
            countrycode = request.form["countrycode"]
            phonenumber = request.form["phonenumber"]
            phonenumber1 = "(+" + countrycode + ")" + phonenumber
            phonenumber2 = phonenumber1.replace(" ", "")
            MAIN_URL = "https://u8fpqfk2d4.execute-api.ap-southeast-1.amazonaws.com/techtrek2020/users"
            result = requests.post(MAIN_URL, headers={'x-api-key': '1elJCmVDjP45as0PT9fsEmHvP03074O8h05lQUmh'}) #payload = {'username': 'corey', 'password': 'testing'}
            result_lists = result.json()
            userfound = False
            for row in result_lists:
                matchingPhoneNumber = row["phoneNumber"].replace(" ","")
                if (phonenumber2 == matchingPhoneNumber):
                    userfound = True
                    userdetails = row
                    return render_template("finduser.html", userfound=userfound, userdetails=userdetails)         
            return render_template("finduser.html", userfound=userfound)



    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
    
