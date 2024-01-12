import pandas as pd
import asyncio
import random
import os
import logging

# Set the logging level to info
logging.basicConfig(level=logging.INFO)

# get the absolute path of the directory where the script is located
dir_path = os.path.dirname(os.path.realpath(__file__))

# get the absolute path of the parent directory of dir_path (the root folder)
project_root_path = os.path.dirname(dir_path)

# create the absolute path to the data directory
data_dir_path = os.path.join(project_root_path, 'data')

async def fetch_random_record(data):
    while True:
        try:
            rand_index = random.randint(0, data.shape[0] - 1)
            record = data.iloc[rand_index]
            await asyncio.sleep(5)
            yield record
        except asyncio.CancelledError:
            print("Task was cancelled.")
            logging.info("Task was cancelled")
            break  # Exit the loop
        except Exception as e:
            logging.error(f"An error occurred in fetch_random_record: {e}")
            yield None
            break


async def print_records(data):
    try:
        async for record in fetch_random_record(data):
            logging.info(str(record.to_dict()))
    except Exception as e:
        logging.error(f'An error occurred in print_records: {e}')


def get_dataset(filepath=None):
    filepath = filepath if filepath is not None else f'{data_dir_path}/iot_dataset.csv'
    if os.path.exists(filepath):
        try:
            # Specify data types for columns
            col_types = {
                27: str  # Column 27 has mixed data type hence needs to be explicitly specified
            }

            # Read and return the dataset
            return pd.read_csv(filepath, dtype=col_types)
        except pd.errors.ParserError as e:
            logging.error(f"An error occurred in get_dateset. Failed to read {filepath}: {e}")
            return None
    else:
        logging.error(f"An error occurred in get_dateset: {filepath} does not exist")
        return None


if __name__ == '__main__':
    data = get_dataset()
    if data is None:
        logging.info(f"No dataset was found")
    else:
        try:
            asyncio.run(print_records(data))
        except KeyboardInterrupt:
            print("Program was cancelled by user.")
