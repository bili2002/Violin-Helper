import sounddevice as sd
import numpy as np
import aubio

# Parameters
samplerate = 44100  # Sampling rate for audio
buffer_size = 512   # Size of audio buffer
hop_size = 512      # Hop size for processing audio
min_pitch_change = 5  # Minimum change in pitch (Hz) to trigger output
min_duration_between_notes = 0.2  # Minimum duration between note outputs (seconds)

# Initialize aubio pitch detector
pitch_detector = aubio.pitch(
    method="default",
    buf_size=buffer_size,
    hop_size=hop_size,
    samplerate=samplerate
)
pitch_detector.set_unit("Hz")  # Set output in Hz

# Note-to-frequency mapping for standard tuning (A4 = 440 Hz)
note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
def frequency_to_note_name(frequency):
    if frequency <= 0:
        return None
    A4 = 440.0
    C0 = A4 * pow(2, -4.75)
    h = round(12 * np.log2(frequency / C0))
    octave = h // 12
    n = h % 12
    return f"{note_names[n]}{octave}"

# Variables to track last detected note
last_pitch = 0
last_note_time = 0

# Callback function for audio processing
def audio_callback(indata, frames, time, status):
    global last_pitch, last_note_time
    if status:
        print(f"Audio input status: {status}")
    # Convert audio input to mono if it's stereo
    mono_data = np.mean(indata, axis=1)
    # Detect pitch
    pitch = pitch_detector(mono_data)[0]
    # Filter out small noises and non-drastic changes
    if abs(pitch - last_pitch) >= min_pitch_change:
        current_time = time.inputBufferAdcTime
        if current_time - last_note_time >= min_duration_between_notes:
            last_pitch = pitch
            last_note_time = current_time
            # Map pitch to note
            note = frequency_to_note_name(pitch)
            if note:
                print(f"Detected Note: {note} ({pitch:.2f} Hz)")

# Start audio stream
print("Starting note detection. Press Ctrl+C to stop.")
with sd.InputStream(callback=audio_callback, channels=1, samplerate=samplerate, blocksize=buffer_size):
    try:
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        print("Note detection stopped.")
