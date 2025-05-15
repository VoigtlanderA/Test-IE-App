from fft_test import *
from get_fp_measurement import *

drive_name = "G001-N408"
do_num = 2
param_id = 69
param_index = 0

job_id = get_last_jobId(drive_name, do_num, param_id, param_index)
job_seq = get_last_jobSeq(drive_name, do_num, param_id, param_index, job_id)
measurement_df = get_measurement_df(drive_name, do_num, param_id, param_index, job_id, job_seq)

signal = measurement_df["_value"].to_numpy()

ts = measurement_df.loc[0]["_time"].strftime("%Y-%m-%dT%H:%M:%S")

#fft_img(signal, f"{drive_name}_{do_num}_{param_id}_{param_index}_{ts}")
fft_denoise_plot(signal, 2)