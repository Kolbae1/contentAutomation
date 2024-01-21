# Import everything
from dotenv import load_dotenv
import random
import os
import openai
from gtts import gTTS
from moviepy.editor import *
import moviepy.video.fx.crop as crop_vid
import requests
load_dotenv()


class TextToSpeech: 
    
    API_KEY = os.environ["ELEVEN_LABS_API"]

    def __init__(self) -> None:
        self.url = "https://api.elevenlabs.io/v1/text-to-speech/onwK4e9ZLuTAKqWW03F9"
        self.chunk_size = 1024
        
    def set_voice(self, voice_value:str) -> None: 
        self.url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_value

    def set_chunk_size(self, chunk:int) -> None: 
        self.chunk_size = chunk

    def export_text_to_mp3(self, text: str) -> None:
        headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": f"{self.API_KEY}"
        }

        data = {
        "text": f"{text}",
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
            }
        }

        response = requests.post(self.url, json=data, headers=headers)
        with open('audio/output.mp3', 'wb') as f:
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    f.write(chunk)


        
TextToSpeech().export_text_to_mp3("Hello I am a test")




class AiContent: 

    def __init__(self) -> None:
        pass

    title = input("\nEnter the name of the video >  ")

    option = input('Do you want AI to generate content? (yes/no) >  ')

    if option == 'yes':
        # Generate content using OpenAI API
        theme = input("\nEnter the theme of the video >  ")

        ### MAKE .env FILE AND SAVE YOUR API KEY ###
        openai.api_key = os.environ["OPENAI_API"]
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Generate content on - \"{theme}\"",
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        print(response.choices[0].text)

        yes_no = input('\nIs this fine? (yes/no) >  ')
        if yes_no == 'yes':
            content = response.choices[0].text
        else:
            content = input('\nEnter >  ')
    else:
        content = input('\nEnter the content of the video >  ')

    # Create the directory
    if os.path.exists('generated') == False:
        os.mkdir('generated')

    # Generate speech for the video
    speech = gTTS(text=content, lang='en', tld='ca', slow=False)
    speech.save("generated/speech.mp3")

    gp = random.choice(["1", "2"])
    start_point = random.randint(1, 480)
    audio_clip = AudioFileClip("generated/speech.mp3")

    if (audio_clip.duration + 1.3 > 58):
        print('\nSpeech too long!\n' + str(audio_clip.duration) + ' seconds\n' + str(audio_clip.duration + 1.3) + ' total')
        exit()

    print('\n')








### VIDEO EDITING ###

# Trim a random part of minecraft gameplay and slap audio on it
video_clip = VideoFileClip("gameplay/gameplay_" + gp + ".mp4").subclip(start_point, start_point + audio_clip.duration + 1.3)
final_clip = video_clip.set_audio(audio_clip)

# Resize the video to 9:16 ratio
w, h = final_clip.size
target_ratio = 1080 / 1920
current_ratio = w / h

if current_ratio > target_ratio:
    # The video is wider than the desired aspect ratio, crop the width
    new_width = int(h * target_ratio)
    x_center = w / 2
    y_center = h / 2
    final_clip = crop_vid.crop(final_clip, width=new_width, height=h, x_center=x_center, y_center=y_center)
else:
    # The video is taller than the desired aspect ratio, crop the height
    new_height = int(w / target_ratio)
    x_center = w / 2
    y_center = h / 2
    final_clip = crop_vid.crop(final_clip, width=w, height=new_height, x_center=x_center, y_center=y_center)

# Write the final video
final_clip.write_videofile("generated/" + title + ".mp4", codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)
