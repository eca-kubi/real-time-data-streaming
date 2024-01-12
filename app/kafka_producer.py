import random
import time
import json
import os
import logging
from data_generator import get_dataset
from confluent_kafka import Producer

# Set the logging level to info
logging.basicConfig(level=logging.INFO)

# get the absolute path of the directory where the script is located
dir_path = os.path.dirname(os.path.realpath(__file__))

# get the absolute path of the parent directory of dir_path (the root folder)
project_root_path = os.path.dirname(dir_path)

# create the absolute path to the data directory
data_dir_path = os.path.join(project_root_path, 'data')

def push_records_to_kafka_producer():
    # Get kafka configurations from environment variables
    boostrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
    topic = os.environ.get('KAFKA_TOPIC', 'weather_condition_and_household_energy_consumption')
    # Initialize kafka producer
    producer = Producer({'bootstrap.servers': boostrap_servers})
    #  Get the dataset
    data = get_dataset(f'{data_dir_path}/iot_dataset.csv')
    if data is not None:
        # Fetch records at random from the dataset
        try:
            while True:
                rand_index = random.randint(0, data.shape[0] - 1)
                record = data.iloc[rand_index]
                time.sleep(5)  # Simulate near real-time delivery of record
                if record is not None:
                    # Convert record from series to bytes-like object because kafka will not accept a series object
                    bytes_like_obj = (json.dumps(record.to_dict())).encode()
                    # Push to kafka producer
                    producer.produce(topic, value=bytes_like_obj)
                    producer.flush()
        except Exception as e:
            logging.error(f'An error occurred in push_records_to_kafka_producer: {e}')

    else:
        logging.info(f'No dataset was found, hence, we can not push to kafka produce')


if __name__ == '__main__':
    push_records_to_kafka_producer()
