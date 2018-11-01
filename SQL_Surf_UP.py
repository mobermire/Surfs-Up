import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date>/<end_date>/"
    )


@app.route("/api/v1.0/precipitation")
def precp():
    # Query Precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()
#     # Create a dictionary from the row data
    all_results = []
    for x in results:
        prcp_dict = {}
        prcp_dict["date"] = x.date
        prcp_dict["prcp"] = x.prcp
        all_results.append(prcp_dict)

    return jsonify(all_results)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.id, Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    d1 = dt.date(2017,8,23)
    yr_ago = d1- dt.timedelta(days=365)
    results = session.query(Measurement.id, Station.name, Measurement.tobs).\
    filter(Measurement.station == Station.station, Measurement.date >= yr_ago, Measurement.date <= d1).\
    group_by(Measurement.station).all()

    all_results = []
    for x in results:
        tobs_dict = {}
        tobs_dict["id"] = x.id  
        tobs_dict["station"] = x.station
        tobs_dict["date"] = x.date
        tobs_dict["tobs"] = x.tobs
        all_results.append(tobs_dict)

    return jsonify(all_results)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def query_dates(start_date, end_date):
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
    filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    list = []
    for x in results:
        dict = {}
        dict["Start Date"] = start_date
        dict["End Date"] = end_date
        dict["Average Temperature"] = x[0]
        dict["Highest Temperature"] = x[1]
        dict["Lowest Temperature"] = x[2]
        data_list.append(dict)
    return jsonify(list)

if __name__ == '__main__':
    app.run(debug=True)
