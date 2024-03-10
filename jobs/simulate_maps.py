import googlemaps
# Decode the polyline and extract the coordinates
from polyline import decode
import pymysql

# Replace 'YOUR_API_KEY' with your actual Google Maps API key
gmaps = googlemaps.Client(key='AIzaSyD0_bWNzGcOjt8CnJnCcf7WTyPAA6PzR10')


# Connect to MySQL database
mydb = pymysql.connect(
  host="localhost",
  user="root",
  password="Taurus@18051998",
  database="smart_city"
)

# Create cursor
mycursor = mydb.cursor()

sql1 = "TRUNCATE coordinates"
mycursor.execute(sql1)
mydb.commit()
# Define the origin and destination
origin = 'Boston, MA'
destination = 'New York, NY'

# Request directions via public transit
directions_result = gmaps.directions(origin, destination, mode="driving")

# Extract the route coordinates
route = directions_result[0]['overview_polyline']['points']



decoded_route = decode(route)

# Extract a subset of points from the decoded route
num_points = 60
step = len(decoded_route) // num_points

subset_route = decoded_route[::step]

print (subset_route[0][0])
# Insert coordinates into database
for point in subset_route:
    sql = f"INSERT INTO coordinates (latitude, longitude) VALUES ({point[0]}, {point[1]})"
    mycursor.execute(sql)

# Commit changes to the database
mydb.commit()

# Close cursor and connection
mycursor.close()
mydb.close()
