import os
from pathlib import Path
import httpx
import librosa
import numpy as np
import openai
import requests
import soundfile as sf
from string import Template
import gpt
from openai import OpenAI, NotFoundError
import json
import ffmpeg
import re
from pydub import AudioSegment


FINAL_AUDIO_START = 'merged_'
TEMPLATE_OPENING = 'Welcome to the audiobook experience of $title $subtitle, by $author. This audiobook is brought to life by the engaging narration of $narrator. Sit back, relax and enjoy the reading.'
TEMPLATE_CLOSING = 'This is the End of the audiobook $title $subtitle.'
PROCESSED_AUDIO_START = 'processed_'
BITRATE = '192k'


def sanitize_filename(filename):

    return re.sub(r'[\\/*?:"<>|]', "", filename)

def change_pitch(audio, pitch_factor):
    samples = np.array(audio.get_array_of_samples())
    samples = np.interp(np.arange(0, len(samples), pitch_factor),
                        np.arange(0, len(samples)),
                        samples)
    return audio._spawn(samples.astype(np.int16))

class ChapterProduction:
    def __init__(self, name, chapter_path, processed_chapter_path ,audio_format='flac', content=''):
        self.name = name
        self.content = ''
        self.chapter_path = Path(chapter_path)
        self.processed_path = Path(processed_chapter_path)
        self.verify_directory()
        self.audio_files_paths = []
        self.processed_audio_files_paths = []
        self.audio_file = None
        self.content = content
        self.audio_format = audio_format
        self.load_files_in_folder_to_list()
        
    def to_dict(self):
        return {
            'name': self.name,
            'content': self.content
        }
        
    def __repr__(self):
        return f'Chapter({self.name}, {self.content})'

    def load_files_in_folder_to_list(self):
        for file in os.listdir(self.chapter_path):
            if not file.endswith(self.audio_format):
                continue
            if file.startswith(FINAL_AUDIO_START):
                self.audio_file = Path(self.chapter_path) / file
                continue
            if file.endswith(self.audio_format):
                self.audio_files_paths.append(Path(self.chapter_path) / file)
        
        #sort list alphabetically
        self.audio_files_paths.sort()
    def verify_directory(self):
        if not self.chapter_path.exists():
            os.makedirs(self.chapter_path)
            print(f"Directory '{self.chapter_path}' created.")
        if not self.processed_path.exists():
            os.makedirs(self.processed_path)
            print(f"Directory '{self.processed_path}' created.")

    def audio_file_in_list(self, audio_file): 
        if audio_file in self.audio_files_paths:
            return True
        return False
        
    def add_audio_file(self, audio_file):
        #check if file exists
        if not Path(audio_file).exists():
            raise FileNotFoundError(f"File '{audio_file}' not found.")
        
        #check if the file path is already in the list
        if self.audio_file_in_list(audio_file):
            raise FileExistsError(f"File '{audio_file}' already exists in the list.")
        self.audio_files_paths.append(audio_file)

    def process_audio_file(self, audio_file, output_path, desired_avg_db=-37, pitch=1):
        audio, sample_rate = librosa.load(audio_file, sr=44100) 

        S = librosa.stft(audio)
        db = librosa.amplitude_to_db(np.abs(S))
        avg_db = np.mean(db)
        gain_factor = librosa.db_to_amplitude(desired_avg_db - avg_db)
        adjusted_audio = audio * gain_factor
        random_string = np.random.randint(0, 1000000)
        tmp_output_filename_wav = self.chapter_path / f"{random_string}.wav" 
        sf.write(tmp_output_filename_wav, adjusted_audio, sample_rate)
        if pitch != 1:
            sound = AudioSegment.from_file(tmp_output_filename_wav, format="wav")
            change_pitch(sound, pitch).export(tmp_output_filename_wav, format="wav")

        (
            ffmpeg
            .input(tmp_output_filename_wav)
            .output(str(output_path), audio_bitrate=BITRATE)
            .run(overwrite_output=True)
        )
        os.remove(tmp_output_filename_wav)

    def process_audio_files(self, output_dir=None, desired_avg_db=-37, pitch=1):
        if not self.audio_files_paths:
            raise ValueError(f"No audio file found for chapter {self.name}")
        for i, audio_file in enumerate(self.audio_files_paths):
            formted_name = self.name.replace(' ', '_')
            formted_name = sanitize_filename(formted_name)
            output_file_name = f"processed_{formted_name}_{i}.mp3"
            if output_dir:
                output_path = output_dir / output_file_name
            else:
                output_path = self.processed_path / output_file_name
            self.process_audio_file(audio_file, output_path, desired_avg_db, pitch)
            self.processed_audio_files_paths.append(output_path)

    def join_audio_files(self):
        audio_signals = []
        if not self.audio_files_paths:
            raise ValueError(f"No audio files found in {self.chapter_path}")
        
        for file in self.audio_files_paths:
            signal, sr = librosa.load(file, sr=None)  # Cargar con la tasa de muestreo original
            audio_signals.append(signal)

        concatenated_signal = np.concatenate(audio_signals)
        formated_name = self.name.replace(' ', '_')
        formated_name = sanitize_filename(formated_name)
        speech_file_path = self.chapter_path / f"{FINAL_AUDIO_START}{formated_name}.{self.audio_format}"
        sf.write(speech_file_path, concatenated_signal, sr)
        self.audio_file = speech_file_path

    def join_processed_audio_files(self, output_path=None, start_with='', merged_audio_format='mp3'):
        audio_signals = []
        if not self.audio_files_paths:
            raise ValueError(f"No audio files found in {self.chapter_path}")
            return
        
        for file in self.processed_audio_files_paths:
            signal, sr = librosa.load(file, sr=None)  # Cargar con la tasa de muestreo original
            audio_signals.append(signal)

        concatenated_signal = np.concatenate(audio_signals)
        formted_name = self.name.replace(' ', '_')
        formted_name = sanitize_filename(formted_name)
        if not output_path:
            speech_file_path = self.processed_path / f"{FINAL_AUDIO_START}{formted_name}.{merged_audio_format}"
        else:
            speech_file_path = output_path / f"{start_with}_{formted_name}.{merged_audio_format}"
        sf.write(speech_file_path, concatenated_signal, sr)
        self.audio_file = speech_file_path

    def export_content_to_txt_file(self):
        formted_name = self.name.replace(' ', '_')
        formted_name = sanitize_filename(formted_name)
        txt_file_path = self.chapter_path / f"{formted_name}.txt"
        with open(txt_file_path, 'w') as f:
            f.write(self.content)
        return txt_file_path

class BookProduction:
    def __init__(self, title, subtitle, author, narrator , output_path, audio_format='flac', description='', chapters=[], load_opening=True):
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.narrator = narrator
        name_formatted = title.replace(' ', '_')
        name_formatted = sanitize_filename(name_formatted)
        processed_audio_folder_name = f"{PROCESSED_AUDIO_START}{name_formatted}"
        self.output_path = Path(output_path) / name_formatted
        self.processed_path = Path(output_path) / processed_audio_folder_name
        self.verify_directory()
        self.audio_format = audio_format
        self.chapters = []
        if load_opening:
            self.load_opening()
        self.description = description
        if chapters:
            for chapter in chapters:
                self.add_chapter(chapter.name, chapter.content)
        
    def verify_directory(self):
        if not self.output_path.exists():
            os.makedirs(self.output_path)
            print(f"Directory '{self.output_path}' created.")
        if not self.processed_path.exists():
            os.makedirs(self.processed_path)
            print(f"Directory '{self.processed_path}' created.")
        

    def load_opening(self):
        subtitle = f" - {self.subtitle}" if self.subtitle else ''
        data_to_replace = {
            "title": self.title,
            "subtitle": subtitle,
            "author": self.author,
            "narrator": self.narrator
        }
        templ = Template(TEMPLATE_OPENING)
        content = templ.substitute(data_to_replace)
        self.add_chapter('Opening', content, include_name_in_content=False)

    def load_closing(self, add_retail=True):
        subtitle = f" - {self.subtitle}" if self.subtitle else ''
        data_to_replace = {
            "title": self.title,
            "subtitle": subtitle,
            "author": self.author
        }
        templ = Template(TEMPLATE_CLOSING)
        content = templ.substitute(data_to_replace)
        self.add_chapter('Closing', content, include_name_in_content=False)
        if self.description and add_retail:
            self.add_chapter('Retail', self.description, include_name_in_content=False)
        

    def add_chapter(self, name, content, include_name_in_content=False):
        last_index = len(self.chapters)
        name_formatted = name.replace(' ', '_')
        if include_name_in_content:
            chapter_intro = f"Chapter {last_index} {name}."
            content = f"{chapter_intro} \n\n. {content}"
        name_formatted = f"{last_index}_{name_formatted}"
        name_formatted = sanitize_filename(name_formatted)
        chapter_path = self.output_path / name_formatted
        processed_chapter_path = self.processed_path / name_formatted
        new_chapter = ChapterProduction(name, chapter_path=chapter_path, processed_chapter_path= processed_chapter_path, content=content)
        self.chapters.append(new_chapter)

    def generate_voices(self, model="text-to-speech", voice="alloy", api_key=None):
        client = OpenAI(api_key=api_key)

        # Iterar sobre cada capítulo
        for chapter in self.chapters:
            # Verificar y crear la carpeta del capítulo si no existe
            chapter_folder = chapter.chapter_path
            print(chapter.chapter_path)
            print(chapter.name)
            if not chapter_folder.exists():
                os.makedirs(chapter_folder)
                print(f"Directory '{chapter_folder}' created.")
            
            # Convertir el capítulo a formato dict y luego a JSON
            chapter_data = chapter.to_dict()
            chapters_data = json.dumps(chapter_data)
            
            # Definir la ruta completa del archivo de audio
            audio_output_path = chapter_folder / f"{chapter.name}.mp3"
            
            # Intentar la solicitud con manejo de errores
            try:
                response = client.audio.speech.create(model=model, voice=voice, input=chapters_data)
                response.stream_to_file(str(audio_output_path))  # Convertir Path a str para usarlo con OpenAI
                chapter.add_audio_file(audio_output_path)
                print(f"Audio saved to '{audio_output_path}'")
            except Exception as e:
                print(f"Error occurred while generating audio for {chapter.name}: {e}")




    def join_chapters_fragments(self, join_processed=True, merged_audio_format='mp3'):
        for i, chapter in enumerate(self.chapters):
            chapter.join_audio_files()
            if join_processed:
                chapter.join_processed_audio_files(self.processed_path, start_with=f"{i}", merged_audio_format=merged_audio_format)
        

    def process_audio_files(self, desired_avg_db=-37, pitch=1, merged_audio_format='mp3'):
        for i, chapter in enumerate(self.chapters):
            # Añadir un print para verificar qué capítulos están siendo procesados
            print(f"Processing chapter: {chapter.name}")
            try:
                chapter.process_audio_files(desired_avg_db=desired_avg_db, pitch=pitch)
            except ValueError as e:
                print(f"Error processing chapter {chapter.name}: {e}")
        
        self.join_chapters_fragments(merged_audio_format=merged_audio_format)
            
    def export_content_to_txt_files(self):
        for chapter in self.chapters:
            chapter.export_content_to_txt_file()
    
