import speech_recognition as sr
import requests
import urllib.parse
import subprocess
import os

def get_filename_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename:
        filename = 'downloaded_audio'
    return filename

def download_and_convert_audio(url):
    try:
        original_filename = get_filename_from_url(url)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(original_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Audio converted to WAV: {original_filename}")
        output_file = "converted.wav"
        try:
            command = [
                "ffmpeg",
                "-i", original_filename,  # Input file
                "-ar", "16000",  # Set sample rate to 16 kHz
                "-ac", "1",  # Set audio channels to mono
                "-c:a", "pcm_s16le",  # Set audio codec to PCM 16-bit little endian
                output_file  # Output file
            ]
            subprocess.run(command, check=True)
            print(f"Audio successfully converted to {output_file}")
            os.remove(original_filename)
        except subprocess.CalledProcessError as e:
            print(f"Error during audio conversion: {e}")
        except FileNotFoundError:
            print("FFmpeg is not installed or not found in PATH.")
        return output_file

    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

def transcribe_audio(filename):
    AUDIO_FILE = download_and_convert_audio(filename)
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)

    origin_text = "Sorry, I don't understand."
    try:
        transcribe_text = r.recognize_google(audio, language="vi-VN")
        os.remove(AUDIO_FILE)
        return transcribe_text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    os.remove(AUDIO_FILE)
    return origin_text
