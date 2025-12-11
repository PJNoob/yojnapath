from transcriber import FasterWhisperTranscriber
from prompts import SYSTEM_PROMPT
from typing import IO
from io import BytesIO
from groq import Groq
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import subprocess
import logging
import os
import tempfile
import numpy as np
from termcolor import colored
from datetime import datetime

# API Keys
ELEVEL_LABS_APIKEY = ""
VOICE_ID = ""
GROQ_APIKEY = ""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


AUDIO_DIR = "generated_audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

gclient = Groq(api_key=GROQ_APIKEY)


def save_audio_response(audio_data, conversation_id=None):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if conversation_id:
        filename = f"response_{conversation_id}_{timestamp}.mp3"
    else:
        filename = f"response_{timestamp}.mp3"
    
    filepath = os.path.join(AUDIO_DIR, filename)
    
    try:

        with open(filepath, 'wb') as f:
            for chunk in audio_data:  
                f.write(chunk)
        logger.info(f"Audio saved to: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving audio file: {e}")
        raise


def play_audio(audio_file_path):

    with open(audio_file_path, "rb") as audio_file:
        audio_data = audio_file.read()
        

        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmpfile:
            tmpfile.write(audio_data)
            tmpfile.flush()

            subprocess.run(["mpv", "--no-video", tmpfile.name], check=True)

def text_to_speech(elevenlabs_api_key, voice_id, text):
    """
    Convert text to speech using ElevenLabs API with error handling
    """
    try:
        eclient = ElevenLabs(api_key=elevenlabs_api_key)
        response = eclient.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2",
        )
        
        return response
    
            
    except Exception as e:
        logger.error(f"Error in text_to_speech: {e}")
        raise

def main():
    transcriber = FasterWhisperTranscriber()
    messages_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    

    conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"Starting new conversation with ID: {conversation_id}")
    
    while True:
        try:
            print("\nPress and hold space to start talking with AI sales agent")
            recording = transcriber.record_audio()
            

            try:
                file_path = transcriber.save_audio(recording, is_temp=True)
            except Exception as e:
                logger.error(f"Error saving audio recording: {e}")
                continue
            

            try:
                full_transcript = transcriber.transcribe_audio(file_path)
                print("\nTranscription:", full_transcript)
            except Exception as e:
                logger.error(f"Error transcribing audio: {e}")
                continue
                
            messages_history.append({"role": "user", "content": full_transcript})
            

            try:
                completion = gclient.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=messages_history,
                    temperature=0.5,
                    max_tokens=200,
                    top_p=1,
                    stream=False,
                )
                
                assistant_response = completion.choices[0].message.content
                print("Response from Groq client:", assistant_response)
                messages_history.append({"role": "assistant", "content": assistant_response})
            except Exception as e:
                logger.error(f"Error getting completion from Groq: {e}")
                continue
            
 
            try:
                audio_data = text_to_speech(ELEVEL_LABS_APIKEY, VOICE_ID, assistant_response)
                
           
                saved_filepath = save_audio_response(audio_data, conversation_id)
                logger.info(f"Saved response audio to: {saved_filepath}")
                
               
                play_audio(saved_filepath)
            except Exception as e:
                logger.error(f"Error in text-to-speech or audio playback: {e}")
                continue
                
        except KeyboardInterrupt:
            print("\nExiting due to keyboard interrupt")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            continue

if __name__ == "__main__":
    main()