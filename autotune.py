from pathlib import Path

import librosa
from pydub import AudioSegment
import numpy as np
import psola


audio = AudioSegment.from_file("Recording.m4a", "m4a")

audio.export("Recording.wav", format="wav")

def correct(f0):
    if np.isnan(f0):
        return np.nan
    c_minor_degrees = librosa.key_to_degrees('C:min')
    degrees = librosa.key_to_degrees('C:min')
    degrees = np.concatenate((degrees, [degrees[0] + 12 ]))

    midi_note = librosa.hz_to_midi(f0)
    degree = midi_note % 12
    closet_degree_id = np.argmin(np.abs(degrees - degree ))


def correct_pitch(f0):
    corrected_f0 = np.zeros_like(f0)
    for i in range(f0.shape[0]):
        corrected_f0[i] = corrected(f0[i])
def autotune(y,sr):
    #1.Track pitch
    frame_length = 2048 
    hop_lenght = frame_length / 4
    fmin = librosa.note_to_hz('C2')
    fmax = librosa.note_to_hz('C7')
    f0, _, _ = librosa.pyin(y,
                 frame_length= frame_length,
                 hop_length=hop_length,
                 sr=sr,
                 fmin = fmin,
                 fmax = fmax)
    #2.Calculate described pitch 
    corrected_f0 = corrected_pitch(f0)
    
    #3.Pitch shifting
    return psola.vocode(y, sample_rate=int(sr), target_pitch=corrected_f0, fmin=fmin, fmax=fmax)
def main(): 
        y, sr = librosa.load("Recording.wav", sr=None, mono=False)
        
        if y.ndim > 1:
            y = y[0, :]
            
            pitch_corrected_y = autotune(y, sr)
            
            filepath = Path("Recording.wav")
            output_filepath = filepath.parent / (filepath.stem + "_pitch_corrected.wav" + filepath.suffix)
            sf.write(str(output_filepath), pitch_corrected_y, sr)
            
            
    if __name__=='__main__':
        main()