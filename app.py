#import dependencies
import datetime as dt
import numpy as np
import pandas as pd 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#set up database engine to access SQLite
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect the database in classes
Base = automap_base()

#reflect tables into SQLalchemy
Base.prepare(engine, reflect=True)

#create a variable for each class to reference later
Measurement = Base.classes.measurement 
Station = Base.classes.measurement 

#create session link from Python to database
session = Session(engine)

#create flask app
app = Flask(__name__)

#define welcome root
@app.route('/')

#use f strings to display precipitation, stations, tobs, and temp routes
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

#build seperate precipitation route
@app.route("/api/v1.0/precipitation")

#create precip function
def precipitation():
    #find the date a year from august 23,2018
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#build seperate stations route
@app.route("/api/v1.0/stations")

#create station function
def stations():
    results = session.query(Station.station.distinct()).all()
    #unravel results into a one-dimensional array np.ravel()
    #convert unraveled array into a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#build seperate tobs route 
@app.route("/api/v1.0/tobs")

#create tobs function
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #query primary station for all temps last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#create starting route for stats page
@app.route("/api/v1.0/temp/<start>")
#create ending route for stats page
@app.route("/api/v1.0/temp/<start>/<end>")

#add start and end parameters to function and set to none
def stats(start=None, end=None):
    #create a list to get min, max and avg temperature
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    #determine the starting and ending date with if-not statement
    #query database using the list
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


