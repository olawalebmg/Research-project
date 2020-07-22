from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponse
import sys
sys.path.append("..")
from .route_details import stops_latlng, find_stop,latlng
import requests
import json
import requests
from pyleapcard import *

from data_analytics import linear_regression_weather
from data_analytics import get_direction
from data_analytics import db_interface

sys.path.append("..")


# showing how data can be added to a html page
posts = [
    {
        'from': 'Charlestown',
        'to': 'Limekiln Avenue',
        'time': '10:40'
    },
    {
        'route': 'Route 39',
        'from': 'Burlington Road',
        'to': 'Ongar',
        'time': '07:00'
    }
]


# create home function to handle traffic from journeyplanner app
# return what we want the user to see when they are sent to this route


# request arg has to be here
def home(request):
    # context is a dictionary. the keys will be accessible from within the home.html template
    context = {
        'posts': posts
    }
    # context is given as argument. This passes that data into the home template
    # posts variable will now be accessible from within home.html
    return render(request, 'journeyplanner/home.html', context) # render still returns a HttpResponse


def about(request):
    # can also pass dictionary in directly as arg
    return render(request, 'journeyplanner/about.html', {'title': 'About'})


# Create your views here.


def routeplanner(request):
    # can also pass dictionary in directly as arg
    return render(request, 'journeyplanner/routeplanner.html')


def allroutes(request):
    # can also pass dictionary in directly as arg
    return render(request, 'journeyplanner/allroutes.html')


def leap(request):
    # can also pass dictionary in directly as arg
    return render(request, 'journeyplanner/leap.html')


def disruptions(request):
    # can also pass dictionary in directly as arg
    return render(request, 'journeyplanner/disruptions.html')


def tourist(request):
    # can also pass dictionary in directly as arg
    return render(request, 'journeyplanner/tourist.html')


def realtime(request):
    # can also pass dictionary in directly as arg
    return render(request, 'journeyplanner/realtime.html')


@csrf_exempt
def prediction(request):
    if request.method == "POST":
        route= request.POST["route"]
        origin= request.POST["origin"]
        destination = request.POST["destination"]
        date = request.POST["date"]
        time = request.POST["time"]
        direction=request.POST["direction"]

        result = linear_regression_weather.generate_prediction(route, origin, destination, date, time, direction)
        print("Users estimated journey in minutes (from views.py)", result)
    return HttpResponse(result)


@csrf_exempt
def planner(request):
    if request.method == "POST":
        data = json.loads(request.POST["data"])

        prediction = [] # list to store the calculated predictions
      
        buses = len(data)
        route = data["route_number"]
        date = request.POST["date"]
        time = request.POST["time"]

        # direction = 2
        route_number = route.upper()

        # departure stops lat and lng
        departure=data["departure_latlng"]
        x=departure.split(",")
        departure_lat = float(x[0])
        departure_lng = float(x[1])

        # arrival stops lat and lng
        arrival=data["arrival_latlng"]
        y=arrival.split(",")
        arrival_lat = float(y[0])
        arrival_lng = float(y[1])

        route_number = route.upper()
        # getting the suggested route file 
        route_list = stops_latlng(route_number)

        # getting the origin and destination stop number using the vincenty formular
        origin=find_stop(route_list,(departure_lat,departure_lng))
        arrival=find_stop(route_list,(arrival_lat,arrival_lng))
        direction = get_direction.get_direction_from_stops(route, origin, arrival)
        #use the maachine learning module to calculate prediction 

        calculation=linear_regression_weather.generate_prediction(route_number, origin, arrival, date, time, direction)

        # adding the calculated value to the list that will be sent back
        prediction.append(calculation)
           
        print("prediction (from views.py)", calculation)

    return HttpResponse(calculation)
    

@csrf_exempt
def find_latlng(request):
    if request.method == "POST":
        route = request.POST["route"]
        stop_id = request.POST["stop"]
        route_number = route.upper()

        # getting the suggested route file 
        route_list = stops_latlng(route_number)
        result = latlng(route_list, str(stop_id))

        print(result)
        
    return HttpResponse(json.dumps(result))


@csrf_exempt
def list_latlng(request):
    if request.method == "POST":
        route = request.POST["route"]
        route_number = route.upper()

        # getting the suggested route file 
        route_list = stops_latlng(route_number)
    return HttpResponse(json.dumps(route_list))


@csrf_exempt
def real_time(request):
    if request.method == "POST":
        stop_number = request.POST["stopnumber"]
        url = "https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid={}&format=json".format(stop_number)
        r = requests.get(url=url)

        data = r.json()
        print(data)

    return HttpResponse(json.dumps(data))


# csrf exemption is only temporary while running on local machine!!!
@csrf_exempt
def leap_login(request):

    if request.method == "POST":
        user = request.POST["user"]
        password = request.POST["passwd"]

        leap_session = LeapSession()

        # attempt to login to www.leapcard.ie with supplied credentials
        # return error if credentials are incorrect
        try:
            leap_session.try_login(user, password)

        except Exception as e:
            print(e)
            return e

        # request the www.leapcard.ie account overview
        overview = leap_session.get_card_overview()
        stats = {"cardNumber": overview.card_num, "cardBalance": overview.balance, "cardName": overview.card_label,
                 "cardType": overview.card_type, "cardExpiry": overview.expiry_date}

        # convert stats to json format & return to user
        return HttpResponse(json.dumps(stats))


