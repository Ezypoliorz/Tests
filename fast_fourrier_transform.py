# Uses the Numpy fast fourrier transform tool to isolate the main frequencies from a sound wave

import numpy as np
import matplotlib.pyplot as plt
import sys
import sounddevice as sd
from scipy.signal import find_peaks

sampleRate = 44100 # Sample rate, in Hertz
duration = 3 # Duration of the sound, in seconds
# Calculates the correct number of samples for the given duration
numSamples = int(sampleRate * duration)
t = np.linspace(0, duration, numSamples, endpoint = False)

noiseRatio = 0.1 # Ratio of the random noise over the defined sound, ∈ [0; 1]
if noiseRatio < 0 or noiseRatio > 1 :
    print("Variable noiseRatio must be set between 0 and 1")
    sys.exit()

frequencies = [ # [Frequency (Hz), Amplitude]
    [200, 0.25],
    [400, 0.5],
    [800, 0.25],
]

# Normalizes the amplitude between 0 and 1
totalWeight = sum(f[1] for f in frequencies)
if totalWeight > 1 :
    for frequency in frequencies :
        frequency[1] = frequency[1] / totalWeight

# Creates the signal
signalData = 0
for frequency in frequencies : 
    signalData += frequency[1] * np.sin(2 * np.pi * frequency[0] * t)

noise = np.random.normal(0, 1, len(t))
combinedSignal = signalData * (1 - noiseRatio) + noise * noiseRatio

# Computes the discrete fourrier transform
fftResult = np.fft.fft(combinedSignal)
frequencies = np.fft.fftfreq(len(t), 1 / sampleRate)

# Calculates the magnitude and keeps only the positive frequencies
magnitudeSpectrum = np.abs(fftResult)[:len(t) // 4]
positiveFrequencies = frequencies[:len(t) // 4]

# Detects peaks to allow playing individual frequencies
peaks, _ = find_peaks(magnitudeSpectrum, height = 500) # height = 500 is a threshold to ignore noise
peakFrequencies = positiveFrequencies[peaks]

def on_click(event) :
    if event.inaxes is None :
        return
    
    # Click on the Top Plot : Play the full combined signal
    if event.inaxes == ax1 :
        print("Playing combined signal...")
        sd.play(combinedSignal, sampleRate)
    
    # Click on the Bottom Plot : Play the nearest identified peak
    elif event.inaxes == ax2 :
        # Finds the frequency closest to the click
        clickedFreq = event.xdata
        closestIdx = (np.abs(peakFrequencies - clickedFreq)).argmin()
        targetFreq = peakFrequencies[closestIdx]
        
        print(f"Playing identified frequency : {targetFreq : .2f} Hz")
        # Generates a 1-second preview of that specific frequency
        previewTime = np.linspace(0, 1, sampleRate, endpoint = False)
        previewSignal = 0.5 * np.sin(2 * np.pi * targetFreq * previewTime)
        sd.play(previewSignal, sampleRate)

# Plots the graphs
fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (10, 8))
fig.canvas.mpl_connect('button_press_event', on_click)

# 1. Time Domain Plot
ax1.plot(t[:500], combinedSignal[:500])
ax1.set_title("Time Domain (Click here to play FULL sound)")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Amplitude")
ax1.grid(True)

# 2. Frequency Domain Plot
ax2.plot(positiveFrequencies, magnitudeSpectrum)
ax2.plot(peakFrequencies, magnitudeSpectrum[peaks], "x", color = "red") # Marks peaks
ax2.set_title("Frequency Domain (Click near a red X to play that frequency)")
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude")
ax2.grid(True)

plt.tight_layout()
print("Interactive mode active. Click on the plots to play sounds.")
plt.show()