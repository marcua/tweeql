#!/usr/bin/env python

from Weather.data import rows as station_rows
from Weather.data import calcDist

def get_temperatures():
    engine = create_engine(DB_URI, echo=True)
    meta = MetaData()
    meta.reflect(bind=engine)
    temperature = meta.tables['weather_meandev']
    conn = engine.connect()
    yesterday = datetime.today()-timedelta(hours=48)
    where_clause = and_(temperature_table.c.latitude != None,
                        temperature_table.c.longitude != None, 
                        temperature_table.c.temperature != None,
                        temperature_table.c.temperature > 0.0,
                        temperature_table.c.temperature < 120.0, 
                        temperature_table.c.meandevs < 2, 
                        temperature_table.c.meandevs > 0, 
                        temperature_table.c.created_at > yesterday)
    latcol = cast(temperature_table.c.latitude, Integer).label('latitude')
    longcol = cast(temperature_table.c.longitude, Integer).label('longitude')
    data_query = select([latcol, longcol, 
                         func.avg(temperature_table.c.temperature).label('temperature')],
                        where_clause).\
                       group_by(latcol, longcol)
    cursor = db_conn.execute(data_query)

    return cursor

def latlong2station(latitude, longitude):
    best,result = 99999999,[]
    for row in station_rows():
        test_point = map(float, (row[2],row[3]))
        
        distance = calcDist(latitude, longitude, test_point[0], test_point[1])
        if distance < best:
            best,result = distance,row
    station = None
    if best < MAX_DISTANCE:
        station = result[0]
    return station

def get_nws_temp(latitude, longitude):
    station_name = latlong2station(latitude, longitude)
    temperature = None
    if station_name != None:
        station = Weather.Station(station_name)
        temperature = station['temp_f']
    return temperature

def compare_temperatures(cursor):
    for row in cursor:
        tweet_temp = float(row["temperature"])
        latitude = float(row["latitude"])
        longitude = float(row["longitude"])
        nws_temp = get_nws_temp(latitude, longitude)
        print "ours: ", tweet_temp, "nws: ", nws_temp
