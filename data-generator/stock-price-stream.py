import requests
import random
import datetime
import time
import datetime
import os
import csv
import json
import yaml
import requests
from confluent_kafka import Producer, KafkaError
from dotenv import load_dotenv

# write_to
WRITE_TO = "kafka" # or "tinybird"

# Load from .env file.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

TINYBIRD_TOKEN = os.getenv("TINYBIRD_TOKEN")
TINYBIRD_URL = "https://api.tinybird.co/v0/events?name=incoming_data"
HEADERS = {"Authorization": f"Bearer {TINYBIRD_TOKEN}", "Content-Type": "application/json"}

COMPANY_INFO = './company-info.csv'

CONFLUENT_SERVER = os.getenv("CONFLUENT_SERVER")
CONFLUENT_KEY = os.getenv("CONFLUENT_KEY")
CONFLUENT_SECRET = os.getenv("CONFLUENT_SECRET")
TOPIC_NAME = os.getenv("TOPIC_NAME")

# Load "app settings" from YAML file. 
with open('./settings.yaml') as file:
    config = yaml.safe_load(file) # Includes a set of Sensor presets/overrides.  

sleep_seconds = config['sleep_seconds']

# Rather than using `While True`, here we run a given number of cycles and then stop. 
num_iterations = config['num_iterations']

# This is key... And the data velocity needs to be taken into account. 
value_max_normal_change = config['value_max_normal_change']

# Set some boundaries for the step amounts... 
step_change_max = config['step_change_max']
step_change_min = config['step_change_min']
percent_step = config['percent_step']
percent_step_trend = config['percent_step_trend']

# Does this data set have out of bounds limits. For stocks, we are setting up with those. 
# percent_out_of_bounds = config['percent_out_of_bounds']
# percent_out_of_bounds_high = config['percent_out_of_bounds_high']

class Sensor:
    def __init__(self, sensor_id):

        # print(f"Creating Sensor object." )

        self.id = sensor_id

        self.reports = []
        self.report = {}
        # self.report['timestamp'] = self.timestamp
        # self.report['price'] = self.value
    
        self.stopped = False
        self.trend = None # 'up', 'down' 
           
    def generate_new_value(self):

        value = self.value
        change = random.uniform(-value_max_normal_change,value_max_normal_change)
        
        # For some small percentage, generate a step change
        step_control = random.uniform(0,100)

        if (step_control < percent_step) or (step_control < percent_step_trend):
            # OK, we are inserting a 'step' change
            step_change = random.uniform(step_change_min, step_change_max)

            if self.trend == 'None':
                change = random.choice([-1,1]) * step_change
            elif self.trend == 'up':
                change = step_change
            elif self.trend == 'down':
                change = -step_change
            else:
                pass
           
            
        value = value + change
        self.previous_value = value

        if value < 0:
            print(f"Oops, company with ID:{self.id} has become a penny stock...")
            value = 0.01

        return value

    def generate_new_report(self):
        # print(f"Generate new sensor report based on current: {self.report}")

        # Calculate new value
        self.value = self.generate_new_value()
        # Calculate new timestamp
        
        self.timestamp = generate_timestamp()
        # Create new report
        self.report = {}
        
        self.report['timestamp'] = self.timestamp
        self.report['id'] = self.id # Need to send sensor ID. 
        self.report['symbol'] = self.symbol
        # Opportunity to adjust base name to better match domain. 
        self.report['price'] = round(self.value,2)

        self.reports.append(self.report)

        return self.report

def generate_timestamp():
    ''' UTC '''
    # Get the current datetime object in UTC 
    now = datetime.datetime.utcnow()
    # Format the datetime object in the "%Y-%m-%d %H:%M:%S.000" format
    #timestamp = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-2] # Tinybird casts as string.
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S') # Tinybird casts as DateTime.

    return timestamp

def sensor_presets(sensors, config):

    print(f"Applying Sensor presets...")

    for sensor_data in config['sensor_overrides']:
        if 'symbol' in sensor_data:
            id = find_sensor_id_by_symbol(sensors, sensor_data['symbol']) - 1
        else:
            id = sensor_data['id']  - 1
                
        trend = sensor_data['trend']
        initial_value = sensor_data['initial_value']
        outliers = sensor_data['outliers']

        sensors[id].id = id + 1
        sensors[id].trend = trend
        sensors[id].outliers = outliers
        sensors[id].value = initial_value
        sensors[id].initial_value = initial_value
        sensors[id].previous_value = initial_value
        sensors[id].reports = []
        report = {}
        report['timestamp'] = generate_timestamp()

        # For 'stock price' use case, we are broadcasting the attribute as 'price'.
        report['price'] = initial_value
        sensors[id].reports.append(report)

    return sensors

def send(events):

    #if kafka/confluent
    pass
    #if not, the Events AP!

def assemble_payload(events):
    pass
    payload = ''
    for event in events:
        json_string = json.dumps(event)
        payload += json_string + '\n'

    return payload


def send_to_events(events):

    pass

    reports_json = assemble_payload(events)
    #reports_json = json.dumps(sensor.reports)
    response = requests.post(tinybird_url, headers=headers, data=reports_json)
    status_code = response.status_code
    
    if status_code >= 200 and status_code <= 202:
        reports = []
        sensor.reports = []
        batched_reports = 0
    else:
        print(f"Events request error: {response.status_code} : {response.reason}")  

def send_to_kafka(producer, events):
    # Looping through events and publishing to Kafka topic.

    try:
        for event in events:
            producer.produce(TOPIC_NAME, value=json.dumps(event))
            producer.flush()
        return True    
    except KafkaError as error: 
        print(f"Error sending message to Kafka: {error}")
        return False
    
def create_kafka_producer():
    # Required connection configs for Kafka producer, consumer, and admin
    config = {
        'bootstrap.servers': CONFLUENT_SERVER,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': CONFLUENT_KEY,
        'sasl.password': CONFLUENT_SECRET
    }

    return Producer(config)

def find_sensor_id_by_symbol(sensors, symbol):
    # Finds the numeric ID of a sensor in a set of sensors based on its symbol.
    
    for sensor in sensors:
        if sensor.symbol == symbol:
            return sensor.id
    return None

def generate_sensors(sensor_file, sensors):

    # Read file and parse it, setting sensor attributing. 
    # Load three-character IDs from the CSV file
    #company_ids = read_company_ids(COMPANY_INFO)

    sensors = []

    # Function to read three-character IDs from the CSV file
    sensor_id = 0
    with open(sensor_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sensor_id += 1      # OK, using a 1-index, not zero-based. 
            sensor = Sensor(sensor_id)
            sensor.symbol = row['symbol']
            sensor.name = row['name']

            sensors.append(sensor) 
    
    return sensors

def update_price(sensor, symbol, new_price):
    pass


def update_with_previous_value(sensors):
        
    try:
        # Could query Tinybird for last values, and start off from there. 
        response = requests.get(f"https://api.us-east.tinybird.co/v0/pipes/most_recent.json?token={TINYBIRD_TOKEN}")

        # Check for HTTP errors
        response.raise_for_status()

        response_json = json.loads(response.text)

        for last_value in response_json['data']:
            for sensor in sensors:
                if last_value['symbol'] == sensor.symbol:
                    sensor.value = last_value['price']
                    break
            
        return sensors
    
    except requests.exceptions.RequestException as e:
        # Handle general request errors
        print(f"Error fetching data from the Tinybird `get_lastest_events` endpoint: {e}")
        print(f"Can not update sensors with most current values, and will instead initialize with a random value.")
        print(f"Implementing the endpoint and add an Auth Token to the `.env` file to retrieve most recent values at start-up." )
        return sensors  # Return sensors without updates if errors occur
    
    except KeyError as e:
        # Handle potential key errors in JSON data
        print(f"Error parsing JSON response: {e}")
        return sensors   

    except ValueError as e:
        # Handle potential value errors (e.g., invalid sensor IDs)
        print(f"Error processing sensor data: {e}")
        return sensors 


def generate():
    
    # Create sensor objects.
    sensors = []
    reports = []
    # Create an array of objects, seeding with a auto-incrementing integer ID. 

    sensors = generate_sensors(COMPANY_INFO, sensors)

    print(f"Created {len(sensors)} sensors.")
    
    sensors = sensor_presets(sensors, config)

    sensors = update_with_previous_value(sensors)

    producer = create_kafka_producer()

    print("Starting to generate data...")

    batched_reports = 0
    # March through the configured iterations... 
    for i in range(num_iterations):
        
        for sensor in sensors:    
            # print(f"Generating new sample for sensor {sensor.id}")
    
            report = sensor.generate_new_report()
            reports.append(report)
            batched_reports = batched_reports + 1

            #if sensor.id == 1:
            #    print(f"Sensor {sensor.symbol}: {report}")

        # [] TODO - update to also send via Kafka stream. 
        if batched_reports >= len(sensors):
            print(f"Publishing {len(reports)} events to Kafka stream...")

            # TODO: Add error handling... 

            #data_published = send(reports)

            if WRITE_TO == "kafka":
                data_published = send_to_kafka(producer, reports) # Sending in ndjson string of newlined JSON objects.
            elif WRITE_TO == "events":
                data_published = send_to_events(reports) # Sending in ndjson string of newlined JSON objects.
            else:
                pass # ERROR

            
            # If all went, clear the counters for the next round. 
            if data_published:
                reports = []
                sensor.reports = []
                batched_reports = 0
            else:
                print(f"Problem sending to stream... ")
                                    
        # At end of iteration, take a rest... 
        print(f"Sleeping for {sleep_seconds} seconds...")
        time.sleep(sleep_seconds)
 
if __name__ == '__main__':
  
    generate()
