import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time

bucket = os.environ["DOCKER_INFLUXDB_INIT_BUCKET"]
org = os.environ["DOCKER_INFLUXDB_INIT_ORG"]
token = os.environ["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"]
url="http://app2-influxdb:8086"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

query = 'from(bucket: "edge")\
|> range(start: -1m)\
|> filter(fn: (r) => r._measurement == "dsf_ls")'

while True:
    try:
        result = query_api.query(query=query, org=org)

        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_field(), record.get_value()))
        print(results)
    except Exception as e:
        print(e)
    
    time.sleep(10)