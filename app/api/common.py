from flask_restx import reqparse

headers_parser = reqparse.RequestParser()
headers_parser.add_argument(
    "X-SITE",
    type=str,
    location="headers",
    required=False,
    help="The url to filter by. Must be a Websdepadel based site. e.g. `ialesport.com`",
)
headers_parser.add_argument(
    "X-GEOLOCATION",
    type=str,
    location="headers",
    required=False,
    help="The geolocation to filter by. Must be a string with the format *lat,lon,radius_km*. e.g. `39.566059,-0.545158,10`",
)
