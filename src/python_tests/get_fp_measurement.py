import pandas as pd
import influxdb_client
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

warnings.simplefilter("ignore", MissingPivotFunction)

token = "edgeadmintoken"
bucket = "edge"
org = "novelis"

client = influxdb_client.InfluxDBClient("http://10.163.176.202:38086", token, org=org)
query_api = client.query_api()

def get_last_jobId(drive_name: str, do_num: int, param_id: int, param_index: int) -> str:
    last_jobId_query = f'''
        import "influxdata/influxdb/schema"

        schema.tagValues(
            bucket: "edge",
            tag: "jobId",
            predicate: (r) => r._measurement == "simatic1" and r["drive_name"] == \"{drive_name}\" and r["do_num"] == \"{do_num}\" and r["param_id"] == \"{param_id}\"
        )
        |> last()'''
    try:
        job_id = query_api.query(last_jobId_query, org).to_values(columns=["_value"])[0][0]
        return job_id
    except Exception as e:
        print(e)

def get_last_jobSeq(drive_name: str, do_num: int, param_id: int, param_index: int, job_id: str) -> int:
    last_jobSeq_query = f'''
        import "influxdata/influxdb/schema"

        schema.tagValues(
            bucket: "edge",
            tag: "jobSeq",
            predicate: (r) => r._measurement == "simatic1" and r["drive_name"] == \"{drive_name}\" and r["do_num"] == \"{do_num}\" and r["param_id"] == \"{param_id}\" and r["jobId"] == \"{job_id}\"
        )
        |> last()'''
    try:
        job_seq = query_api.query(last_jobSeq_query, org).to_values(columns=["_value"])[0][0]
        return int(job_seq)
    except Exception as e:
        print(e)

def get_measurement_df(drive_name: str, do_num: int, param_id: int, param_index: int, job_id: str, job_seq: int) -> pd.DataFrame | list[pd.DataFrame]:
    fp_measurement_query = f'''
        from(bucket: "edge")
        |> range(start: -2d)
        |> filter(fn: (r) => r["_measurement"] == "simatic1")
        |> filter(fn: (r) => r["_field"] == "val")
        |> filter(fn: (r) => r["drive_name"] == \"{drive_name}\")
        |> filter(fn: (r) => r["do_num"] == \"{do_num}\")
        |> filter(fn: (r) => r["param_id"] == \"{param_id}\")
        |> filter(fn: (r) => r["param_index"] == \"{param_index}\")
        |> filter(fn: (r) => r["jobId"] == \"{job_id}\")
        |> filter(fn: (r) => r["jobSeq"] == \"{job_seq}\")
        |> keep(columns: ["_time", "_value", "cycletimeMs"])'''
    try:
        fp_measurement_df = query_api.query_data_frame(fp_measurement_query, org, use_extension_dtypes=True)
        return fp_measurement_df
    except Exception as e:
        print(e)
        
def measurement_df_to_csv(measurement_df: pd.DataFrame, file_path: str) -> None:
    measurement_df = measurement_df.drop(["result", "table"], axis=1)
    measurement_df["_time"] = measurement_df["_time"].dt.tz_localize(None)
    measurement_df.to_csv("./fp_measurement.csv")

def get_slip(drive_name: str, do_num: int, time: str | None = None) -> float:
    stop_time = "now()"
    if time:
        stop_time = time
    start_time = "-1m"
    
    query = '''
        from(bucket: "edge")
        |> range(start: {start_time}, stop: {stop_time})
        |> filter(fn: (r) => r["_measurement"] == "dsf_ls")
        |> filter(fn: (r) => r["_field"] == "val")
        |> filter(fn: (r) => r["drive_name"] == \"{drive_name}\")
        |> filter(fn: (r) => r["do_num"] == \"{do_num}\")
        |> filter(fn: (r) => r["param_id"] == \"{param_id}\")
        |> filter(fn: (r) => r["param_index"] == \"{param_index}\")
        |> last()'''
    
    try:
        # get set rpm value
        response1 = query_api.query(query.format(start_time=start_time, stop_time=stop_time, drive_name=drive_name, do_num=do_num, param_id=62, param_index=0), org)
        rpm_set = response1[0].records[0]["_value"]
        # get actual rpm value
        response2 = query_api.query(query.format(start_time=start_time, stop_time=stop_time, drive_name=drive_name, do_num=do_num, param_id=63, param_index=0), org)
        rpm_act = response2[0].records[0]["_value"]
        # calculate slip
        s = (rpm_set - rpm_act) / rpm_set
        
        return s
    except Exception as e:
        print(e)
        return -1
        
if __name__ == "__main__":
    get_slip("G001-N408", 2)