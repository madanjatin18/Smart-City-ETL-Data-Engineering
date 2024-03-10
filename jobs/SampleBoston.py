import math
import random
import pymysql

BOSTON_COORDINATES = { "latitude": 42.323149, "longitude": -71.060685 }
NEW_YORK_COORDINATES = { "latitude": 40.758896, "longitude": -73.985130 }

# Calculate movement increments
LATITUDE_INCREMENT = (NEW_YORK_COORDINATES['latitude'] - BOSTON_COORDINATES['latitude']) / 150
LONGITUDE_INCREMENT = (NEW_YORK_COORDINATES['longitude'] - BOSTON_COORDINATES['longitude']) / 150

# Starting location at Boston coordinates
start_location = BOSTON_COORDINATES.copy()

# Connect to MySQL database
mydb = pymysql.connect(
  host="localhost",
  user="root",
  password="***********",
  database="smart_city"
)

# Create cursor
mycursor = mydb.cursor()

sql1 = "TRUNCATE coordinates"
mycursor.execute(sql1)
mydb.commit()


def simulate_vehicle_movement():
    global start_location

    # Move towards New York with latitude and longitude increments
    start_location['latitude'] += LATITUDE_INCREMENT
    start_location['longitude'] += LONGITUDE_INCREMENT

    # Add randomness to simulate zigzag or curved movement
    zigzag_factor = random.uniform(0.1, 2.0)  # Adjust the factor to control the zigzagness
    start_location['latitude'] += zigzag_factor * random.uniform(-0.001, 0.001)
    start_location['longitude'] += zigzag_factor * random.uniform(-0.001, 0.001)

    # Introduce randomness to the direction of movement
    direction = random.uniform(0, 2 * math.pi)

    # Introduce randomness for changing direction (left or right turn)
    turn_angle = random.uniform(-math.pi / 2, math.pi / 2)  # Adjust the range for turn angle
    direction += turn_angle

    magnitude = random.uniform(0, 0.0005)  # Adjust magnitude as needed
    start_location['latitude'] += magnitude * math.cos(direction)
    start_location['longitude'] += magnitude * math.sin(direction)


    # Insert coordinates into database
    sql = f"INSERT INTO coordinates (latitude, longitude) VALUES ({start_location['latitude']},{start_location['longitude']})"
    mycursor.execute(sql)
    mydb.commit()



# Simulate vehicle movement
for _ in range(150):
    simulate_vehicle_movement()


# Close database connection
mycursor.close()
mydb.close()
