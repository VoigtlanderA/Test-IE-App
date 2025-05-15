import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time
import pandas as pd
import scipy

bucket = "edge"
org = "novelis"
token = "edgeadmintoken"
url="http://localhost:8086"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

query = 'from(bucket: "edge")\
  |> range(start: -1m)\
  |> filter(fn: (r) => r["_measurement"] == "dsf_ls")\
  |> pivot(rowKey: ["_time"], columnKey: ["drive_name", "do_num", "param_id", "param_index"], valueColumn: "_value")'

result = query_api.query_data_frame(query=query, org=org)
for df in result:
    print(type(df))
    print(df.columns)
    print(df.head())