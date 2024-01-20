# Real-Time Data Streaming Project

This project aims to design a robust and scalable real-time data-intensive application backend. The architecture of the system is designed with careful consideration given to various software components.

## Architecture Overview

The architecture of the system is as follows:

1. **Data Source**: A Python script fetches records from a time-stamped dataset continuously and in near real-time, acting as the data source for our pipeline.

2. **Data Ingestion**: A Kafka producer streams the records to a Kafka topic for high-throughput, low-latency data ingestion. ZooKeeper manages the distributed streaming platform for reliable and consistent data flow.

3. **Data Processing and Transformation**: Apache Spark consumes the Kafka topic to perform complex transformations on the data streamed from Kafka to make it ready for our Cassandra sink.

4. **Delivering Data to Frontend ML Application**: The processed data is available to the Machine Learning frontend app through Cassandra, a high-performing distributed database system.

5. **Ensuring Reliability, Scalability, and Maintainability**: The architecture uses Docker containers for each service, closely following the microservice architecture for robustness, consistent deployments, and scalability.

6. **Ensuring Data Security, Governance, and Protection**: Enhanced data security can be achieved through techniques such as authentication, encryption, activity logs, backup, and recovery, which can also provide audit trails and protection.

## Getting Started

To get started with this project, you will need to have Docker and Docker compose installed on your system.  You also need to rename the `.env.example` file to `.env` and update the environment variables in the file. Then, clone this repository and run the following command in the project directory:

```bash
docker-compose up -d
```
This will create and start the containers for the Python script, Kafka, ZooKeeper, Spark, and Cassandra.

## Usage

### Spark Streaming

We will use Spark to consume the Kafka topic and perform transformations on the data before writing it to Cassandra. To run the Spark job, run the following command in the project directory:

```bash
docker-compose exec spark-master spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1,org.apache.spark:spark-sql_2.12:3.4.1 /opt/bitnami/app/spark_streaming.py
```

### Cassandra

To access the Cassandra shell, run the following command in the project directory:

```bash
docker-compose exec cassandra cqlsh
```
You can then run CQL commands to query the data in Cassandra. For example, to see the schema of the table, run the following command in the Cassandra shell:

```bash
DESCRIBE TABLE iot_data.weather_condition_and_household_energy_consumption;
```
You can also run the following command to see the total data in the table:

```bash
SELECT COUNT(*) FROM iot_data.weather_condition_and_household_energy_consumption;
```


### Monitor Kafka and Spark
You can also monitor the data flow using Kafka’s Control Center and Spark’s Web UI. To access Kafka’s Control Center, go to http://localhost:9021. To access Spark’s Web UI, go to http://localhost:8080.


## Contact
Author: [Eric Clinton Appiah-Kubi](https://www.linkedin.com/in/ecakubi/) 