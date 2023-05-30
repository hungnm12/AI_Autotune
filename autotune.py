from pathlib import Path
import soundfile as sf
import librosa
from pydub import AudioSegment
import numpy as np
import psola
import scipy.signal as sig
import matplotlib.pyplot as plt
from functools import partial
import argparse
import librosa.display




def correct(f0):
    if np.isnan(f0):
        return np.nan
    c_minor_degrees = librosa.key_to_degrees('C:min')
    c_minor_degrees = np.concatenate((c_minor_degrees, [c_minor_degrees[0] + 12]))
    degrees = librosa.key_to_degrees('C:min')
    degrees = np.concatenate((degrees, [degrees[0] + 12 ]))

    midi_note = librosa.hz_to_midi(f0)
    degree = midi_note % 12
    closet_degree_id = np.argmin(np.abs(degrees - degree ))

    degree_difference = degree - c_minor_degrees[closet_degree_id]

    midi_note -= degree_difference

    return librosa.midi_to_hz(midi_note)
def correct_pitch(f0):
    corrected_f0 = np.zeros_like(f0)
    for i in range(f0.shape[0]):
        corrected_f0[i] = correct(f0[i])
    smoothed_corrected_f0 = sig.medfilt(corrected_f0, kernel_size=11)

    smoothed_corrected_f0[np.isnan(smoothed_corrected_f0)] = f0[np.isnan(smoothed_corrected_f0)]

    return smoothed_corrected_f0
def autotune(y,sr):
    #1.Track pitch
    frame_length = 2048 
    hop_length = frame_length // 4
    fmin = librosa.note_to_hz('C2')
    fmax = librosa.note_to_hz('C7')
    f0, _, _ = librosa.pyin(y,
                 frame_length= frame_length,
                 hop_length=hop_length,
                 sr=sr,
                 fmin = fmin,
                 fmax = fmax)
    #2.Calculate described pitch 
    corrected_f0 = correct_pitch(f0)
    
    #3.Pitch shifting
    return psola.vocode(y, sample_rate=int(sr), target_pitch=corrected_f0, fmin=fmin, fmax=fmax)
def main(): 
        y, sr = librosa.load("Recording.wav", sr=None, mono=False)
        
        if y.ndim > 1:
            y = y[0, :]
            
            pitch_corrected_y = autotune(y, sr)
            
            filepath = Path("Recording.wav")
            output_filepath = filepath.parent / (filepath.stem + "_pitch_corrected.wav" + filepath.suffix)
            sf.write(str(output_filepath),pitch_corrected_y, sr)
            
if __name__=='__main__':
        main()