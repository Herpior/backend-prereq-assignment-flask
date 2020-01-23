from flask import Flask
from flask import request
from flask import Response
from waitress import serve
import math
import json

app = Flask(__name__)

with open('restaurants.json', 'r') as myfile:
    data = myfile.read()
restaurants = json.loads(data)['restaurants']


@app.route('/restaurants/search')
def search():
    max_dist = 3

    args = request.args
    if not args:
        return Response('{"ok":"false", "error":"no query string"}', mimetype='application/json')
    q = args.get("q")
    lat_str = args.get("lat")
    lon_str = args.get("lon")
    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except ValueError:
        return Response('{"ok":"false", "error":"bad location data"}', mimetype='application/json')
    except TypeError:
        return Response('{"ok":"false", "error":"missing location data"}', mimetype='application/json')

    near = [rest for rest in restaurants if distance(lon, lat, *rest['location']) < max_dist]
    near_matched = [rest for rest in near if matches(q, rest)]
    res = json.dumps({'restaurants':near_matched})

    return Response(res, mimetype='application/json')

#transforms latitude and longitude to 3d coordinates on unit sphere
def latlon2xyz(lon, lat):
    return math.cos(lon)*math.sin(lat), math.sin(lon)*math.sin(lat), math.cos(lat)

def distance(lon1, lat1, lon2, lat2):
    x1, y1, z1 = latlon2xyz(lon1*math.pi/180, lat1*math.pi/180)
    x2, y2, z2 = latlon2xyz(lon2*math.pi/180, lat2*math.pi/180)
    dot = x1*x2 + y1*y2 + z1*z2
    angle = math.acos(dot)
    r = 6371
    print(angle*r)
    return angle*r

def matches(q, restaurant):
    # return all restaurants if no query
    if q is None or len(q) == 0:
        return True
    # return all restaurants with query in the name or description,
    # or if it's one of the tags
    return  q in restaurant['description'] or \
            q in restaurant['name'] or \
            q in restaurant['tags']


if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0')
    serve(app, host="0.0.0.0", port=8080)
