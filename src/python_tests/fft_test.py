import pandas as pd
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks, find_peaks_cwt, welch
import matplotlib.pyplot as plt
import numpy as np

def fft_img(signal: np.ndarray, cycle_time_ms: int, img_name: str = "test") -> None:
    n = signal.size
    dt = cycle_time_ms / 1000.0


    rf = np.fft.rfft(signal, norm="forward")
    freq = np.fft.rfftfreq(n, dt)

    mag_rf = 10 * np.log10(np.abs(rf))

    p_ind, _ = find_peaks(mag_rf, height=-25, prominence=4, distance=10)

    plt.figure(figsize=(15,10))

    plt.plot(freq, mag_rf)
    plt.vlines(freq[p_ind], ymin=np.min(mag_rf), ymax=np.max(mag_rf), colors="lightgreen", linewidths=1)
    plt.grid(visible=True)

    plt.savefig(f"./fft_images/{img_name}.png", bbox_inches='tight')
    
def fft_denoise_plot(signal: np.ndarray, cycle_time_ms: int) -> None:
    n = signal.size
    dt = cycle_time_ms / 1000.0
    f = 1000 / cycle_time_ms
    
    f_welch, pxx = welch(signal, f, return_onesided=True, nperseg=1024)
    p_ind, _ = find_peaks(pxx, height=10e-5)
    
    pxx_mag = 10 * np.log10(np.abs(pxx))
    p_ind_mag, _ = find_peaks(pxx_mag, height=np.median(pxx_mag), prominence=3)

    plt.figure(figsize=(15,10))

    plt.subplot(2,1,1)
    plt.semilogy(f_welch, pxx)
    plt.vlines(f_welch[p_ind], ymin=np.min(pxx), ymax=np.max(pxx), colors="lightgreen")
    plt.grid(visible=True)
    
    plt.subplot(2,1,2)
    plt.hlines([np.median(pxx_mag), np.mean(pxx_mag)], xmin=np.min(f_welch), xmax=np.max(f_welch), colors="lightblue")
    plt.plot(f_welch, pxx_mag)
    plt.vlines(f_welch[p_ind_mag], ymin=np.min(pxx_mag), ymax=np.max(pxx_mag), colors="lightgreen")
    plt.grid(visible=True)

    plt.show()