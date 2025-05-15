import influxdb_client
from influxdb_client import WriteOptions
import paho.mqtt.client as mqtt

from datetime import datetime
from datetime import timezone
import logging
import json
import os
import re

from tags import tags_from_payload

logger = logging.getLogger(__name__)
logger.setLevel("WARNING")
logging.basicConfig(format="%(asctime)s %(levelname)s  %(processName)s:%(pathname)s:%(lineno)d  %(message)s", style="%", datefmt="%Y-%m-%dT%H:%M:%S.%fZ")

bucket = os.environ["DOCKER_INFLUXDB_INIT_BUCKET"]
org = os.environ["DOCKER_INFLUXDB_INIT_ORG"]
token = os.environ["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"]
url = "http://app2-influxdb:8086"

influx_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = influx_client.write_api(write_options=WriteOptions(
    batch_size=1000,
    flush_interval=10_000,
    jitter_interval=0,
    retry_interval=5000,
    max_retries = 5,
    max_retry_delay = 125000,
    max_retry_time = 180000,
    exponential_base = 2,
    max_close_wait = 300000
))



def on_connect(client, userdata, flags, reason_code, properties):
    logger.info("Connected with result code %s", reason_code)
    client.subscribe("ie/d/j/simatic/v1/dsf_ls/dp/r/+/default", qos=0)
    client.subscribe("ie/d/j/simatic/v1/sinamics1/dp/r/+/default", qos=0)
    
################################################### Drive Connector Low Speed Message ###############################################################
def on_dsf_ls(client, userdata, msg):
    logger.info("dsf_ls message received")
    global write_api
    global bucket
    global org
    payload = json.loads(msg.payload)
    drive_name =  msg.topic.split("/")[8]
    
    for val in payload["vals"]:
        id_tags = re.search("DO#(?P<do_num>[0-9]*)_(?P<param_id>[0-9]*)\\[(?P<param_index>[0-9]*)\\]", val["id"])
        tags_dict = dict(id_tags.groupdict())
        tags_dict["drive_name"] = drive_name
        p = {
            "measurement": "dsf_ls",
            "tags": tags_dict,
            "fields": {"val": float(val["val"])},
            "time": datetime.fromisoformat(val["ts"])
        }
        write_api.write(bucket, org, p)
    return

################################################### Drive Connector High Speed Message ###############################################################
def on_sinamics1(client, userdata, msg):
    logger.info("sinamics1 message received")
    global write_api
    global bucket
    global org
    payload = json.loads(msg.payload)
    ts = payload["timestamp"]
    cycletime_ms = payload["cycletimeMs"]
    msg_tags = tags_from_payload(payload, ["variables"])
    msg_tags["drive_name"] = msg.topic.split("/")[8]
    
    for variable in payload["variables"]:
        id_tags = re.search("DO#(?P<do_num>[0-9]*)_(?P<param_id>[0-9]*)\\[(?P<param_index>[0-9]*)\\]", variable["varName"])
        tags_dict = dict(id_tags.groupdict())
        tags_dict.update(msg_tags)
        n = 0
        for measurement in variable["measurements"]:
            p = {
                "measurement": "simatic1",
                "tags": tags_dict,
                "fields": {"val": float(measurement)},
                "time": datetime.fromtimestamp((ts + n * cycletime_ms) / 1000.0, timezone.utc)
            }
            write_api.write(bucket, org, p)
            
            n += 1
            
    return
    
def on_message(client, userdata, msg):
    topic = msg.topic.split("/")
    match topic[5]:
        case "dsf_ls":
            on_dsf_ls(client, userdata, msg)
        case "sinamics1":
            on_sinamics1(client, userdata, msg)
        case _:
            print(f"No action defined for topic: {msg.topic}")
    


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set("edge", "edge")
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("ie-databus", 1883)

mqttc.loop_forever()