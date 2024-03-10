import time
import boto3
import pymysql

def get_athena_client():
    return boto3.client('athena', region_name='us-east-2')

def get_mysql_connection():
    return pymysql.connect(
        host="localhost",
        database="smart_city",
        user="root",
        password="*********"
    )

def create_mysql_table(cursor, table_name, columns):
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    create_table_query += ", ".join(f"{col} VARCHAR(255)" for col in columns)
    create_table_query += ")"
    cursor.execute(create_table_query)

def insert_into_mysql(cursor, table_name, columns, values):
    insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(columns))})"
    cursor.execute(insert_query, values)

def get_table_list(athena_client):
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'smartcity_v3';"
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': 'smartcity_v3'},
        ResultConfiguration={'OutputLocation': 's3://spark-streaming-data-jatin/output/'}
    )
    execution_id = response['QueryExecutionId']
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=execution_id)
        status = response['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        print("Status: ", status)
        time.sleep(5)
    if status != 'SUCCEEDED':
        print("Error fetching table list")
        return []
    results = athena_client.get_query_results(QueryExecutionId=execution_id)
    table_list = [row['Data'][0]['VarCharValue'] for row in results['ResultSet']['Rows'][1:]]
    print(table_list)
    return table_list

def fetch_and_insert_data(athena_client, cursor, conn, table_name):
    query = f"SELECT * FROM {table_name};"
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': 'smartcity_v3'},
        ResultConfiguration={'OutputLocation': 's3://spark-streaming-data-jatin/output/'}
    )
    execution_id = response['QueryExecutionId']
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=execution_id)
        status = response['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        print("Status: ", status)
        time.sleep(5)
    print("Final Status: ", status)
    if status != 'SUCCEEDED':
        print(f"Error fetching data for table {table_name}")
        print("Error message:", response['QueryExecution']['Status']['StateChangeReason'])
        return

    results = athena_client.get_query_results(QueryExecutionId=execution_id)
    columns = [data['VarCharValue'] for data in results['ResultSet']['Rows'][0]['Data']]
    rows = results['ResultSet']['Rows'][1:]
    print("Columns: ", columns)
    create_mysql_table(cursor, table_name, columns)

    for row in rows:
        try:
            values = [data['VarCharValue'] for data in row['Data']]
            insert_into_mysql(cursor, table_name, columns, values)
        except Exception as e:
            print(f"Error inserting data into {table_name}: {e}")
            continue
    conn.commit()
    print(f"Data inserted successfully for table {table_name}")

def main():
    athena_client = get_athena_client()
    conn = get_mysql_connection()
    cursor = conn.cursor()

    tables = get_table_list(athena_client)
    for table in tables:
        fetch_and_insert_data(athena_client, cursor, conn, table)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
