import logging
import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, DoubleType, StringType

# Set the logging level to info
logging.basicConfig(level=logging.INFO)

# Get configuration params
cassandra_contact_points = os.getenv('CASSANDRA_CONTACT_POINTS', 'kafka-broker').split(',')
cassandra_username = os.getenv('CASSANDRA_USERNAME', 'cassandra')
cassandra_password = os.getenv('CASSANDRA_PASSWORD')
cassandra_host = os.getenv('CASSANDRA_HOST', 'cassandra')
cassandra_port = os.getenv('CASSANDRA_PORT', 9042)
cassandra_keyspace = os.getenv('CASSANDRA_KEYSPACE', 'iot_data')
cassandra_table = os.getenv('CASSANDRA_TABLE', 'weather_condition_and_household_energy_consumption')
cassandra_replication_factor = os.getenv('CASSANDRA_REPLICATION_FACTOR', 1)
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
kafka_topic = os.getenv('KAFKA_TOPIC', 'weather_condition_and_household_energy_consumption')

schema = StructType([
    StructField("time", DoubleType(), False),
    StructField("use [kW]", DoubleType(), False),
    StructField("gen [kW]", DoubleType(), False),
    StructField("House overall [kW]", DoubleType(), False),
    StructField("Dishwasher [kW]", DoubleType(), False),
    StructField("Furnace 1 [kW]", DoubleType(), False),
    StructField("Furnace 2 [kW]", DoubleType(), False),
    StructField("Home office [kW]", DoubleType(), False),
    StructField("Fridge [kW]", DoubleType(), False),
    StructField("Wine cellar [kW]", DoubleType(), False),
    StructField("Garage door [kW]", DoubleType(), False),
    StructField("Kitchen 12 [kW]", DoubleType(), False),
    StructField("Kitchen 14 [kW]", DoubleType(), False),
    StructField("Kitchen 38 [kW]", DoubleType(), False),
    StructField("Barn [kW]", DoubleType(), False),
    StructField("Well [kW]", DoubleType(), False),
    StructField("Microwave [kW]", DoubleType(), False),
    StructField("Living room [kW]", DoubleType(), False),
    StructField("Solar [kW]", DoubleType(), False),
    StructField("temperature", DoubleType(), False),
    StructField("icon", StringType(), False),
    StructField("humidity", DoubleType(), False),
    StructField("visibility", DoubleType(), False),
    StructField("summary", StringType(), False),
    StructField("apparentTemperature", DoubleType(), False),
    StructField("pressure", DoubleType(), False),
    StructField("windSpeed", DoubleType(), False),
    StructField("cloudCover", StringType(), False),
    StructField("windBearing", DoubleType(), False),
    StructField("precipIntensity", DoubleType(), False),
    StructField("dewPoint", DoubleType(), False),
    StructField("precipProbability", DoubleType(), False)
])


def transform_kafka_data(df, schema):
    # Convert the 'value' field from Kafka message (which is binary) to a string
    json_df = df.selectExpr("CAST(value AS STRING)")

    # Transform the JSON strings into a DataFrame using the provided schema
    parsed_df = json_df.select(from_json(col('value'), schema).alias('data'))

    # Change the column names to make it easier to work with the data
    renamed_df = (parsed_df.select(col("data.time").alias("time"),
                                   col("data.use [kW]").alias("use_kw"),
                                   col("data.gen [kW]").alias("gen_kw"),
                                   col("data.House overall [kW]").alias("house_overall_kw"),
                                   col("data.Dishwasher [kW]").alias("dishwasher_kw"),
                                   col("data.Furnace 1 [kW]").alias("furnace1_kw"),
                                   col("data.Furnace 2 [kW]").alias("furnace2_kw"),
                                   col("data.Home office [kW]").alias("home_office_kw"),
                                   col("data.Fridge [kW]").alias("fridge_kw"),
                                   col("data.Wine cellar [kW]").alias("wine_cellar_kw"),
                                   col("data.Garage door [kW]").alias("garage_door_kw"),
                                   col("data.Kitchen 12 [kW]").alias("kitchen12_kw"),
                                   col("data.Kitchen 14 [kW]").alias("kitchen14_kw"),
                                   col("data.Kitchen 38 [kW]").alias("kitchen38_kw"),
                                   col("data.Barn [kW]").alias("barn_kw"),
                                   col("data.Well [kW]").alias("well_kw"),
                                   col("data.Microwave [kW]").alias("microwave_kw"),
                                   col("data.Living room [kW]").alias("living_room_kw"),
                                   col("data.Solar [kW]").alias("solar_kw"),
                                   col("data.temperature").alias("temperature"),
                                   col("data.icon").alias("icon"),
                                   col("data.humidity").alias("humidity"),
                                   col("data.visibility").alias("visibility"),
                                   col("data.summary").alias("summary"),
                                   col("data.apparentTemperature").alias("apparent_temperature"),
                                   col("data.pressure").alias("pressure"),
                                   col("data.windSpeed").alias("wind_speed"),
                                   col("data.cloudCover").alias("cloud_cover"),
                                   col("data.windBearing").alias("wind_bearing"),
                                   col("data.precipIntensity").alias("precip_intensity"),
                                   col("data.dewPoint").alias("dew_point"),
                                   col("data.precipProbability").alias("precip_probability")))

    # Return the renamed Dataframe
    return renamed_df


# noinspection SqlNoDataSourceInspection,SqlDialectInspection
def prepare_cassandra_db():
    try:
        auth_provider = PlainTextAuthProvider(username=cassandra_username, password=cassandra_password)
        cluster = Cluster(contact_points=cassandra_contact_points, auth_provider=auth_provider)
        session = cluster.connect()

        session.execute("""
        CREATE KEYSPACE IF NOT EXISTS {} WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : {} }}
        """.format(cassandra_keyspace, int(cassandra_replication_factor)))

        session.execute("""
        CREATE TABLE IF NOT EXISTS %s.%s (
            time double PRIMARY KEY,
            use_kw double,
            gen_kw double,
            house_overall_kw double,
            dishwasher_kw double,
            furnace1_kw double,
            furnace2_kw double,
            home_office_kw double,
            fridge_kw double,
            wine_cellar_kw double,
            garage_door_kw double,
            kitchen12_kw double,
            kitchen14_kw double,
            kitchen38_kw double,
            barn_kw double,
            well_kw double,
            microwave_kw double,
            living_room_kw double,
            solar_kw double,
            temperature double,
            icon text,
            humidity double,
            visibility double,
            summary text,
            apparent_temperature double,
            pressure double,
            wind_speed double,
            cloud_cover text,
            wind_bearing double,
            precip_intensity double,
            dew_point double,
            precip_probability double
        )
        """, (cassandra_keyspace, cassandra_table))

        logging.info(f"Keyspace {cassandra_keyspace} and table {cassandra_table} ready for data ingestion.")
        session.shutdown()
        cluster.shutdown()
    except Exception as e:
        logging.error(f"Error occurred while connecting to Cassandra: {e}")


def create_spark_cassandra_connection():
    s_conn = None
    try:
        active_session = SparkSession.getActiveSession()
        s_conn = active_session if active_session else SparkSession.builder \
            .appName('IoT Data Processor') \
            .config('spark.jars', '/opt/bitnami/spark/jars/spark-cassandra-connector_2.12-3.4.1.jar, /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.4.1.jar') \
            .config('spark.cassandra.connection.host', cassandra_host) \
            .config('spark.cassandra.connection.port', cassandra_port) \
            .getOrCreate()
        s_conn.sparkContext.setLogLevel("WARN")
        logging.info("Spark connection created successfully!")
    except Exception as e:
        logging.error(f"Couldn't create the spark session due to exception {e}")
        if s_conn is not None:
            s_conn.stop()
    return s_conn


def read_kafka_stream_into_spark_df(spark_conn):
    spark_df = None
    try:
        spark_df = spark_conn.readStream \
            .format('kafka') \
            .option('kafka.bootstrap.servers', bootstrap_servers) \
            .option('subscribe', kafka_topic) \
            .option('startingOffsets', 'earliest') \
            .load()
        logging.info("kafka dataframe created successfully")
    except Exception as e:
        logging.error(f"Failed to create Kafka DataFrame due to exception {e}")
    return spark_df


def create_stream_and_write_to_cassandra(spark_conn):
    # Create the Kafka DataFrame
    spark_df = read_kafka_stream_into_spark_df(spark_conn)

    if spark_df is None:
        logging.error("Kafka DataFrame is empty. Exiting...")
        return
    
    # Perform transformations
    df_transformed = transform_kafka_data(spark_df, schema)

    # Write the DataFrame to Cassandra in every trigger batch
    df_transformed.writeStream \
        .format("org.apache.spark.sql.cassandra") \
        .option("checkpointLocation", "/tmp/checkpoint") \
        .options(table=cassandra_table, keyspace=cassandra_keyspace) \
        .outputMode("update") \
        .start()


if __name__ == '__main__':
    # Start the stream and await termination
    spark_conn = create_spark_cassandra_connection()  # Assuming this function creates/connects to a SparkSession
    # Prepare Cassandra DB
    prepare_cassandra_db()
    create_stream_and_write_to_cassandra(spark_conn)
    spark_conn.streams.awaitAnyTermination()
