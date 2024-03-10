import datetime
import os
import random
import time
import uuid
from datetime import timedelta
from datetime import datetime
from confluent_kafka import SerializingProducer
import simplejson as json
import googlemaps
from polyline import decode
from config import configuration

# Define the origin and destination
ORIGIN = 'Boston, MA'
DESTINATION = 'New York, NY'
global GMAPS

# Environment Variables for configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
VEHICLE_TOPIC = os.getenv('VEHICLE_TOPIC', 'vehicle_data')
GPS_TOPIC = os.getenv('GPS_TOPIC', 'gps_data')
TRAFFIC_TOPIC = os.getenv('TRAFFIC_TOPIC', 'traffic_data')
WEATHER_TOPIC = os.getenv('WEATHER_TOPIC', 'weather_data')
EMERGENCY_TOPIC = os.getenv('EMERGENCY_TOPIC', 'emergency_data')

random.seed(42)
start_time = datetime.now()

# def get_speed_limit(latitude, longitude):
#     result = GMAPS.speed_limits((latitude, longitude))
#     if result and 'speedLimits' in result:
#         for limit_data in result['speedLimits']:
#             if 'speedLimit' in limit_data:
#                 speed_limit = limit_data['speedLimit']
#                 return speed_limit
#     return None
def get_next_time():
    global start_time
    start_time += timedelta(seconds=random.randint(30, 60)) # update frequency
    return start_time

def generate_gps_data(device_id, timestamp, speed, vehicle_type='private'):
    return{
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'timestamp': timestamp,
        'speed': speed, # km/h
        'direction': 'North-East',
        'vehicleType': vehicle_type
    }

def generate_traffic_camera_data(device_id, timestamp, location, camera_id):
    return{
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'cameraId': camera_id,
        'location': location,
        'timestamp': timestamp,
        'snapshot': 'Base64EncodedString'
    }

def generate_weather_data(device_id, timestamp, location):
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'location': location,
        'timestamp': timestamp,
        'temperature': random.uniform(-5, 26),
        'weatherCondition': random.choice(['Sunny','Cloudy', 'Rain', 'Snow']),
        'precipitation': random.uniform(0, 25),
        'windSpeed': random.uniform(0,100),
        'humidity': random.randint(0,100 ), # percentage
        'airQualityIndex': random.uniform(0, 500) # AQL value goes here
    }

def generate_emergency_incident_data(device_id, timestamp, location, speed, speed_limit):
    incident_type = 'Police' if speed > speed_limit else random.choice(['Accident', 'Fire', 'Medical', 'None'])

    return {
        'id': str(uuid.uuid4()),  # Convert UUID to string
        'deviceId': device_id,
        'incidentId': str(uuid.uuid4()),  # Convert UUID to string
        'type': incident_type,
        'timestamp': timestamp,
        'location': location,
        'status': random.choice(['Active', 'Resolved']),
        'description': 'Description of the incident'
    }

def generate_vehicle_data(device_id,lat,long):
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'timestamp': get_next_time().isoformat(),
        'location': (lat,long),
        'speed': random.uniform(10, 70),
        'direction': 'North-East',
        'make': 'BMW',
        'model': 'C500',
        'year': 2024,
        'fuelType': 'Hybrid'
    }

def json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_data_to_kafka(producer, topic, data):
    producer.produce(
        topic,
        key=str(data['id']),
        value=json.dumps(data, default=json_serializer).encode('utf=8'),
        on_delivery=delivery_report
    )

    producer.flush()


def simulate_journey( producer, device_id):
    if not subset_route:
        print("Subset route is empty. Unable to simulate journey.")
        return

    for point in subset_route:
        try:
            speed_limit = random.uniform(35, 55)
            vehicle_data = generate_vehicle_data(device_id, point[0], point[1])
            gps_data = generate_gps_data(device_id, vehicle_data['timestamp'], vehicle_data['speed'])
            traffic_camera_data = generate_traffic_camera_data(device_id, vehicle_data['timestamp'],
                                                               vehicle_data['location'], 'Sony-Cam123')
            weather_data = generate_weather_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])
            emergency_incident_data = generate_emergency_incident_data(device_id, vehicle_data['timestamp'],
                                                                       vehicle_data['location'], vehicle_data['speed'], speed_limit)

            # print(vehicle_data)
            # print(gps_data)
            # print(traffic_camera_data)
            # print(weather_data)
            # print(emergency_incident_data)

            produce_data_to_kafka(producer, VEHICLE_TOPIC, vehicle_data)
            produce_data_to_kafka(producer, GPS_TOPIC, gps_data)
            produce_data_to_kafka(producer, TRAFFIC_TOPIC, traffic_camera_data)
            produce_data_to_kafka(producer, WEATHER_TOPIC, weather_data)
            produce_data_to_kafka(producer, EMERGENCY_TOPIC, emergency_incident_data)

            time.sleep(5)

        except Exception as e:
            print(f"Error occurred while processing point {point}: {e}")

    print(f'Vehicle has reached {DESTINATION}. Simulation ending...')


if __name__ == "__main__":
    try:
        GMAPS = googlemaps.Client(key=configuration.get("GOOGLE_API_KEY"))

        # Request directions via public transit
        directions_result = GMAPS.directions(ORIGIN, DESTINATION, mode="driving")

        # Check if directions_result is empty
        if not directions_result:
            print("Google Maps unable to fetch route. Exiting simulation.")
            exit()

        # Extract the route coordinates
        route = directions_result[0]['overview_polyline']['points']
        decoded_route = decode(route)

        # Extract a subset of points from the decoded route
        num_points = 60
        step = len(decoded_route) // num_points
        subset_route = decoded_route[::step]

        producer_config = {
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'error_cb': lambda err: print(f'Kafka error: {err}')
        }
        producer = SerializingProducer(producer_config)

        try:
            simulate_journey(producer, 'Vehicle-iamjatinmadan-123')

        except KeyboardInterrupt:
            print('Simulation ended by the user')
        except Exception as e:
            print(f'Unexpected Error occurred: {e}')

    except Exception as e:
        print(f'Error occurred while fetching route from Google Maps: {e}')


