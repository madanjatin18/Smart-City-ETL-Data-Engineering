# Smart-City-ETL-Data-Engineering

## **Project Summary**
This project aims to track details from one point (BOSTON) to another point (NEW YORK) by generating data for specific topics using Apache Kafka. The generated data includes information related to emergencies, GPS coordinates, traffic conditions, vehicle details, and weather updates.


**Journey Simulation System:**
Developed a dynamic journey simulation system using the Google Maps API.
Fetched real-time route for accurate simulations.

**Kafka Integration and Real-Time Data:**
Configured a Kafka producer to send real-time data, including GPS, traffic camera, weather, and emergency incident data.
Ensured seamless data flow for analysis and visualization.

**Efficient Data Processing with Spark:**
Leveraged Apache Spark for efficient data processing and partitioning.
Optimized system performance and resource utilization.


**AWS Data Pipeline Infrastructure:**
Designed a resilient data pipeline on AWS S3, Glue, and Athena.
Facilitated seamless data storage, extraction, and analytical operations.


Technology Used: 
* Docker Desktop
* Programming Language - Python
* Apache Kafka
* Apache Spark
* Amazon Web Services (AWS)
* S3
* Glue
* Crawler
* Athena
* MySQL
* Tableau


## Getting Started
### Architecture
![](Refenrence%20Screenshots/System%20Architecture.png)

### Kafka Topics
- "emergency_data"
- "gps_data"
- "traffic_data"
- "vehicle_data"
- "weather_data"

### Data Generation
- Data for the specified topics is generated at each timestamp.
- The data is encapsulated into JSON objects and sent to a Kafka producer.


### Data Processing
- Kafka partitions and distributes the data based on topics.
- Apache Zookeeper manages the coordination between producers and consumers.


### Data Processing with Spark
- Utilizes Apache Spark for data processing.
- Two Spark workers are employed to process the data.

![](Refenrence%20Screenshots/Data_Generation.png)

### Storage
- Processed data is stored in an S3 bucket.

![](Refenrence%20Screenshots/S3_bucket_data.png)

### Data Pipeline
- Crawlers are used to extract data from S3 and feed it into AWS Glue.

![](Refenrence%20Screenshots/Glue_Data.png)

### Data Cleaning For Visualization
- Python scripts are utilized to scrape data from Athena.

- Data is then cleaned and converted into a MySQL table
![](Refenrence%20Screenshots/MySQL_Data.png)

### Visualization
- Tableau Dashboard
![](Refenrence%20Screenshots/Tableau_Visualisation.png)

### Commands
- Bucket Policy
```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::smart-city-streaming-data-aditsvet/*"
        }
    ]
}
```
- Delete/List topics from Kafka
```bash 
kafka-topics --delete --topic emergency_data --bootstrap-server broker:29092
kafka-topics --delete --topic gps_data --bootstrap-server broker:29092
kafka-topics --delete --topic weather_data --bootstrap-server broker:29092
kafka-topics --delete --topic traffic_data --bootstrap-server broker:29092
kafka-topics --delete --topic vehicle_data --bootstrap-server broker:29092
kafka-topics --list --bootstrap-server broker:29092
```
- Docker execution command
```bash
docker exec -it smart-city-realtime-spark-master-1 spark-submit \
--master spark://spark-master:7077 \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.6,\
com.amazonaws:aws-java-sdk:1.11.469 \
jobs/spark-city.py
```
- How to exclude folder not to get crawled
```bash
_spark_metadata
_spark_metadata/**
**/_spark_metadata
**spark_metadata**
```

## References
1. Video tutorial - https://www.youtube.com/watch?v=Vv_fvwF41_0

