import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import tempfile
import os
from faster_whisper import WhisperModel
import threading
import time
from datetime import datetime
import queue

class FasterWhisperTranscriber:
    def __init__(self, model_size="large-v3", sample_rate=44100):
        self.model_size = model_size
        self.sample_rate = sample_rate
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.is_recording = False
        self.audio_queue = queue.Queue()
        

        self.recordings_dir = "recordings"
        os.makedirs(self.recordings_dir, exist_ok=True)
        

        device_info = sd.query_devices(kind='input')
        self.channels = min(int(device_info['max_input_channels']), 2)
        print(f"Using {self.channels} channel{'s' if self.channels > 1 else ''} for recording")
        
    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status)
        if self.is_recording:
            self.audio_queue.put(indata.copy())
            
    def record_audio(self):
        """Record audio from the microphone."""
        
        print("\nPress Enter to start recording...")
        input()
        
        # Clear the queue
        while not self.audio_queue.empty():
            self.audio_queue.get()
        
        print("Recording... Press Enter again to stop.")
        self.is_recording = True
        

        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self.audio_callback,
            dtype=np.float32,
            blocksize=int(self.sample_rate * 0.05) 
        )
        
        def stop_recording():
            input()
            self.is_recording = False
            
        input_thread = threading.Thread(target=stop_recording)
        input_thread.daemon = True
        input_thread.start()
        

        chunks = []
        with stream:
            while self.is_recording:
                try:
                    chunks.append(self.audio_queue.get_nowait())
                except queue.Empty:
                    time.sleep(0.01)  
                    continue
            

            while not self.audio_queue.empty():
                chunks.append(self.audio_queue.get())
        
        if len(chunks) == 0:
            print("No audio recorded!")
            return None

        recording = np.vstack(chunks)
        print(f"Recording stopped. Duration: {len(recording) / self.sample_rate:.2f} seconds")
        return recording
    
    def get_recording_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.recordings_dir, f"recording_{timestamp}.wav")
    
    def save_audio(self, recording, is_temp=False):
        if recording is None or len(recording) == 0:
            return None
            
        try:

            normalized = np.int16(recording * 32767)
            
            if is_temp:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                filename = temp_file.name
            else:
                filename = self.get_recording_filename()
            
            write(filename, self.sample_rate, normalized)
            print(f"{'Temporary' if is_temp else 'Permanent'} audio file saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            if is_temp and 'temp_file' in locals() and os.path.exists(temp_file.name):
                os.remove(temp_file.name)
            return None
    
    def transcribe_audio(self, file_path):
        if file_path is None:
            return ""
            
        try:
            segments, info = self.model.transcribe(file_path, beam_size=5)
            print(f"Detected Language: {info.language} with probability {info.language_probability:.2f}")
            
            full_transcription = ""
            for segment in segments:
                print(segment.text)
                full_transcription += segment.text + " "
            

            if "/tmp" in file_path or "\\tmp" in file_path:
                os.remove(file_path)
                
            return full_transcription.strip()
        except Exception as e:
            print(f"Error during transcription: {e}")
            return ""
    
    def run(self):
        print("Welcome to the Whisper Transcriber!")
        print("This program will record your voice, save it as a WAV file, and transcribe it to text.")
        print(f"Recordings will be saved in the '{self.recordings_dir}' directory.")
        
        try:
            while True:
                recording = self.record_audio()
                if recording is not None and len(recording) > 0:
                    permanent_file = self.save_audio(recording, is_temp=False)
                    temp_file = self.save_audio(recording, is_temp=True)
                    
                    transcription = self.transcribe_audio(temp_file)
                    if transcription:
                        print("\nTranscription:", transcription)
                        print(f"Audio saved as: {permanent_file}")
                
                print("\nWould you like to record again? (y/n)")
                if input().lower() != 'y':
                    break
                    
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    transcriber = FasterWhisperTranscriber()
    transcriber.run()
            
        
            
    
                