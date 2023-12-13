"""
IRIS - Virtual Conversational Assistant

This module implements a virtual assistant named IRIS that
engages in a conversation with the user. It uses PyAudio
for audio input/output, Whisper for audio-to-text transcription,
and Palm for generating conversational responses. The user 
interacts with IRIS through a Tkinter-based GUI.
"""

#Created By Archit Roy

#importing libraries and modules
import pyaudio #audio input output
import wave #reading, writing .wav files
import time #time related operations
import threading #for multithreading like tinker window simultaneously
import whisper # audio to text transcription
from pynput import keyboard #interacting with keyboard, listed to Enter etc
import google.generativeai as palm #generate content
from gtts import gTTS #text to speach
from pydub import AudioSegment #for audio processing such as increaing speed to make it more humane
import os #interact with os such as delete file after creation
import pygame # audio playback
import tkinter as tk #for GUI


#GUI

class VirtualAssistantApp:
    """
    The VirtualAssistantApp class represents the main 
    GUI application for IRIS. It provides a chat screen
    and a microphone button for user interaction.
    """
    def __init__(self, root):
        #inint is conctructor of class, initialise VirtualAssistantApp object with the provided root parameter, which is the main Tkinter window.
        #Initializes the VirtualAssistantApp Parameters:
        #-root: The root window of the Tkinter application.
        self.root = root
        self.root.title("IRIS - Virtual Conversational Assistant")

        self.chat_screen = tk.Text(root, state='disabled', wrap='word', height=20, width=50)
        self.chat_screen.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        #create chatscreen in tk to display messages, size fixed

        self.mic_button = tk.Button(root, text="\U0001F3A4", command=self.toggle_mic, font=('Helvetica', 14), bd=0, relief=tk.FLAT, bg=root.cget('bg'), fg='black', padx=10, pady=10)
        self.mic_button.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
        #button mic created with mic asci for lofo and toggl function
            #placement done using grid
        self.mic_active = False

        # Bind the Enter key to the toggle_mic function
        self.root.bind('<Return>', lambda event: self.toggle_mic())
        #bind to event to a function like here <return> is for pressing ENTER key

    def toggle_mic(self):
        #Toggle mic status ON,OFF 
        self.mic_active = not self.mic_active
        self.update_mic_button()

    def update_mic_button(self):
        #update mic appearance between black and red for recording
        mic_status = "ON" if self.mic_active else "OFF"
        self.mic_button['fg'] = "red" if mic_status == "ON" else "black"

    def send_message(self, speaker, text, color="black"):
        #display message in GUI
        #speaker:User or IRIS
        #text: content
        #color: default black for user, blue for iris
        self.chat_screen.configure(state='normal')
        self.chat_screen.tag_configure(speaker, foreground=color)
        message = f"{speaker}: {text}\n"
        self.chat_screen.insert('end', '\n')
        self.chat_screen.insert('end', message, (speaker,))
        self.chat_screen.configure(state='disabled')



# to record the audio
class VoiceRecorder:
    """
    The VoiceRecorder class handles audio recording, saving, and transcription.
    """
    def __init__(self):
        #Initializes a VoiceRecorder object with default values.
        self.recording = False
        self.audio_file = "voice_recording.wav"
        self.recording_thread = None
        print()
        print("**************************************************************")
        print()
        print("press enter to start recording")
        print()

    def start_recording(self):
        #start recording
        self.recording = True
        self.frames = [] #store audio frames
        self.start_time = time.time()
        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()
        print("Recording started, Press Enter to stop recording.")
        print()

    def stop_recording(self):
        #stop recording
        self.recording = False

    def record(self):

        #Records audio using PyAudio and saves it to a WAV file. Also transcribes the audio using the Whisper library.
        #Returns:- The transcribed text.

        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, #indicates that each audio sample is represented as a 16-bit integer. This is a common format for audio recording and playback.
                            channels=1,
                            rate=48000,
                            input=True,
                            frames_per_buffer=1024) #The size of the buffer can affect the latency and performance of audio processing.
        
        while self.recording:
            data = stream.read(1024)
            self.frames.append(data)
            # self.update_timer()
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        #to save audio to transcribe it
        self.save_audio()
        return self.transcribe_audio()


    def save_audio(self):
        #save audio as .wav file
        sound_file = wave.open(self.audio_file, "wb")
        sound_file.setnchannels(1) #set autio to monaural(single channel) and not stereo(2 channel)
        sound_file.setsampwidth(2) #num of bytes to represent each audio sample, more means more amplitude but larger file size
        sound_file.setframerate(48000) #frame rate is crucial for determining the duration of the audio and the pitch of the sound. 
        #normal=44100 but using more here for more clarity
        sound_file.writeframes(b"".join(self.frames))
        sound_file.close()
        print()
        print("**************************************************************")
        print()
        

    def transcribe_audio(self):
        #using locally installed openai's opensource whisper to transcribe audio
        model = whisper.load_model("base.en")# base model to keep it fast but accurate
        result = model.transcribe(self.audio_file, language="en", fp16=False)
        user_response = result["text"]
        # print("Transcription:", user_response)
        return user_response




# Function to handle voice recording and transcription
#has error handeling as most error prone area of code like not preoperly recorded
def record_and_transcribe():
    # Initialize VoiceRecorder object
    voice_recorder = VoiceRecorder()

    # Callback function for the release of the Enter key
    def on_key_release(key):
        if key == keyboard.Key.enter:
            if not voice_recorder.recording:
                try:
                    # Start recording if not already recording
                    voice_recorder.start_recording()
                except Exception as e:
                    # Handle and log any errors during recording start
                    print("Error starting recording:", str(e))
                    app.send_message("IRIS", "Sorry, I couldn't start recording. Please try again.", iris_color)
                    text_to_audio("Sorry, I couldn't start recording. Please try again.")
            else:
                try:
                    # Stop recording if currently recording
                    voice_recorder.stop_recording()
                    return False
                except Exception as e:
                    # Handle and log any errors during recording stop
                    print("Error stopping recording:", str(e))
                    app.send_message("IRIS", "Sorry, I couldn't stop recording. Please try again.", iris_color)
                    text_to_audio("Sorry, I couldn't stop recording. Please try again.")

    try:
        # Set up keyboard listener with the defined callback function
        with keyboard.Listener(on_release=on_key_release) as listener:
            listener.join()
    except Exception as e:
        # Handle and log any errors with the keyboard listener
        print("Error with keyboard listener:", str(e))
        app.send_message("IRIS", "Sorry, there was an issue with the keyboard listener. Please try again.", iris_color)
        text_to_audio("Sorry, there was an issue with the keyboard listener. Please try again.")

    try:
        # Transcribe the recorded audio
        return voice_recorder.transcribe_audio()
    except Exception as e:
        # Handle and log any errors during transcription
        print("Error during transcription:", str(e))
        app.send_message("IRIS", "Sorry, there was an issue with transcription. Please try again.", iris_color)
        text_to_audio("Sorry, there was an issue with transcription. Please try again.")



#TTS
#Converts text to audio and plays the generated speech with adjusted speed.
def text_to_audio(text, speed=1.0):
    # Initialize the gTTS object with the text
    tts = gTTS(text)
    # Check if the output file already exists and remove it
    if os.path.exists("output.mp3"):
        os.remove("output.mp3")

    # Save the generated speech to a file
    tts.save("output.mp3")

    # Use pydub to adjust the speech speed
    audio = AudioSegment.from_mp3("output.mp3")
    # Speed up the speech by the specified factor
    audio = audio.speedup(playback_speed=1.25)
    audio.export("output_fast.mp3", format="mp3")

    # Initialize pygame mixer
    pygame.mixer.init()

    # Load and play the generated speech with adjusted speed
    pygame.mixer.music.load("output_fast.mp3")
    pygame.mixer.music.play()

    # Wait for the speech to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Clean up by removing temp files
    pygame.mixer.quit()
    os.remove("output.mp3")
    os.remove("output_fast.mp3")




iris_color='#2e5484' #same as tk logo blue for good fashion choice
#The main function that initializes the Tkinter GUI and starts the conversation with IRIS
def main(): # put in main() so that threading can work 
    root = tk.Tk()#create tk window
    global app
    app = VirtualAssistantApp(root)
    app.send_message("IRIS", "Hi, I am Iris, your virtual friend, feel free to talk to me Press ENTER to Start,Stop Speaking",iris_color)

    root.mainloop()


gui_thread = threading.Thread(target=main) #need threading else code wont progress till tk window close, making it useless
gui_thread.start()
#A separate thread is created to run the Tkinter GUI concurrently with the main program.
# This ensures that the program can continue execution while the GUI remains responsive.




key = 'ENTER_YOUR_KEY_HERE' #google palm api key for project, free trial avaible
palm.configure(api_key=key)

model_id = 'models/chat-bison-001'# good for conversation like here

examples=[ #custom set examples

    ('hi iris my project hit a deadend today','oh, tell me about it also how are you?'),
    ('imm good, the project i was planing requires a paid api and im broke','have you tried looking for alternatives?'),
    ('yes, they are good enough','maybe you need to take a break, and get back with a fresh perspective'),
    ('yeah, ig you are right','yes, try going somewhare out and doing breathing excercises'),
    ('yeah, will do that, thanks','your welcome, need any more help?'),

    ("Hey, I've been feeling really stressed lately.", "I'm here for you. Can you talk about what's been causing you stress?"),
    ("I have a lot of work piling up, and I'm overwhelmed.", "It's understandable to feel that way with a heavy workload. Let's break it down. What's the most pressing task?"),
    ("I have a major presentation due next week, and I'm not prepared at all.", "I see. It's okay; we can work on a plan together. What's the topic of your presentation?"),
    ("It's about climate change and its impact on our future.", "That's important. Let's start by outlining key points and gathering some resources. We can do this step by step."),
    ("Thanks, I appreciate your support.", "You're welcome! I'm here to help. And remember, you're not alone in this."),

    ("Hi, I've been feeling really down lately.", "I'm sorry to hear that. Would you like to talk about what's been bothering you?"),
    ("I lost my job, and it's been tough to cope.", "Losing a job can be incredibly stressful. How are you feeling about it?"),
    ("I feel like a failure, and it's affecting my self-esteem.", "I understand how you might feel that way, but remember, your worth isn't defined by your job. What are your strengths and passions?"),
    ("I used to love painting, but I haven't done it in years.", "Painting sounds like a wonderful way to express yourself. Maybe it's time to reconnect with that passion."),
    ("You're right. I should pick up my brushes again.", "I'm glad to hear you're considering it. I'm here to support you in any way I can."),

    ("Hey, I've been having trouble sleeping lately.", "I'm here to help. Can you tell me what's been on your mind when you're trying to sleep?"),
    ("I can't stop thinking about my past mistakes and regrets.", "It's common to dwell on the past, but it's important to learn from it and let go. What are some things you're proud of in your life?"),
    ("I've accomplished a lot, but these regrets just haunt me.", "It's natural to have regrets, but they don't define your worth. Maybe writing down your regrets and reflecting on them could help."),
    ("I'll give that a try. Thanks for listening.", "You're welcome. Remember, I'm here whenever you need to talk or share your thoughts."),

    ("Hi, I'm going through a tough breakup.", "I'm here for you. Breakups can be really challenging. How are you feeling about it?"),
    ("I feel heartbroken and lost without them.", "Heartbreak is a painful experience. It's okay to grieve. Have you talked to friends or family about it?"),
    ("I have, but I still miss them so much.", "It's natural to miss someone you cared about. Over time, the pain will lessen. What are some self-care activities that you enjoy?"),
    ("I used to love hiking. Maybe I should go on a hike this weekend.", "Hiking sounds like a great idea! Nature can be very healing. I hope it helps you find some peace."),

    ("Hi, I've been feeling really overwhelmed with work lately.", "I'm here for you. Tell me more about the tasks that are stressing you out."),
    ("I have so many deadlines, and I can't seem to catch up.", "It sounds like you're under a lot of pressure. Have you tried prioritizing your tasks to manage your workload?"),
    ("I've tried, but it's still too much to handle.", "I understand. Sometimes it's helpful to break things into smaller, manageable steps. What's the most urgent deadline you're facing?"),
    ("I have a major report due by the end of the week.", "That does sound urgent. Let's start by outlining the key points for your report. We can work through it together."),
    ("Thank you for your support; it means a lot.", "You're welcome! I'm here to help. Remember, taking one step at a time can make things more manageable."),

    ("Hey, I've been struggling with a personal issue and could use someone to talk to.", "I'm here to listen. Feel free to share what's on your mind, and I'll do my best to support you."),
    ("I've been feeling isolated and disconnected from my friends.", "Feeling isolated can be tough. Have you considered reaching out to your friends and letting them know how you feel?"),
    ("I'm worried they won't understand or won't have time for me.", "It's natural to have such concerns, but true friends often appreciate your honesty. Give it a try; you might be surprised by their support."),
    ("You're right. I'll try talking to them and opening up.", "I'm glad to hear you're willing to give it a try. Remember, I'm here for you as well, anytime you need to talk."),

    ("Hello, I've been feeling anxious about an upcoming job interview.", "I understand how job interviews can be nerve-wracking. What's causing you the most anxiety about this interview?"),
    ("I'm afraid I'll mess up and not get the job.", "It's common to have such fears. Let's work on boosting your confidence. Have you practiced answering common interview questions?"),
    ("I've practiced, but I still feel unprepared.", "That's okay; we can work on your responses and preparation. Would you like to go over some key interview questions together?"),
    ("Yes, that would be helpful. I appreciate your support.", "You're welcome! We can do a mock interview to help you gain more confidence. Remember, you have valuable skills to offer."),

    ("Hi, I'm going through a breakup, and it's been really hard.", "I'm here to support you during this difficult time. Would you like to share what's been bothering you about the breakup?"),
    ("I miss my ex a lot, and I'm feeling very lonely.", "It's completely normal to miss someone you cared about. Have you considered spending time with friends or family for support?"),
    ("I have, but the loneliness still lingers.", "Loneliness can be challenging. It might help to focus on self-care activities and personal growth. What are some things you enjoy doing for yourself?"),
    ("I used to love playing the guitar; maybe I should pick it up again.", "That sounds like a great idea! Reconnecting with your passions can be very healing. I'm here to encourage and support you."),

    ("Hey, I've been feeling really stressed out lately with work and personal issues.", "I'm here to listen and support you. Let's start by talking about what's been on your mind. What's been stressing you out at work?"),
    ("Work has been incredibly demanding, and I'm constantly juggling multiple projects.", "That sounds overwhelming. Have you discussed your workload with your manager? It's important to ensure a healthy work-life balance."),
    ("I haven't yet, but I'll consider having that conversation soon.", "It's a positive step to consider addressing your work-related stress. In the meantime, is there anything specific about your personal issues that's been bothering you?"),
    ("I've been going through a rough patch in my relationship, and it's been affecting my mood.", "Relationship challenges can be emotionally taxing. Have you tried having an open and honest conversation with your partner about your feelings?"),
    ("We've talked, but things are still strained. I'm not sure if we can work things out.", "I understand that relationships can be complex. It may be helpful to seek advice from a professional therapist to navigate this situation."),
    ("I've been thinking about that as well, but I'm unsure where to start.", "Taking that step is a big decision. I can help you find resources or therapists in your area. It's important to prioritize your well-being."),
    ("Thank you for your support; I appreciate it. It's just been tough to find balance in life.", "I'm here to assist you in finding that balance. Remember, self-care is crucial during challenging times. What are some activities that bring you joy and relaxation?"),
    ("I used to enjoy hiking, reading, and painting. Maybe I should revisit those hobbies.", "Reconnecting with your hobbies is a great idea. They can provide a sense of fulfillment. Let's make a plan to integrate those activities back into your life."),
    ("That sounds like a plan. It's reassuring to have someone to talk to about this.", "I'm here to support you every step of the way. It's essential to have a support system when facing life's challenges."),

    ("Hello, I'm facing a major decision, and I'm feeling torn about it.", "I'm here to help you navigate through your decision. Can you tell me more about the choice you're facing and what's causing your uncertainty?"),
    ("I have a job opportunity in another city, which could be great for my career, but it would mean leaving behind family and friends.", "That's a tough decision. It's important to weigh the pros and cons. Have you made a list of the benefits and drawbacks of each option?"),
    ("I have, but it's still difficult to decide. I'm afraid of losing the support system I have here.", "Leaving behind a support system can be challenging. It might help to have an open conversation with your loved ones about your decision and explore ways to stay connected."),
    ("You're right; communication is key. I appreciate your advice.", "You're welcome. Remember that the decision you make should align with your long-term goals and happiness. I'm here to help you work through your thoughts and feelings."),

    ("Hi, I've been struggling with my self-esteem, and it's affecting my confidence.", "I'm here to listen and provide guidance. Can you share what's been impacting your self-esteem and confidence?"),
    ("I've been comparing myself to others a lot, especially on social media. It makes me feel inadequate.", "Social media can indeed influence self-esteem negatively. It's important to remember that people often post curated versions of their lives. Have you considered taking breaks from social media?"),
    ("I have, but it's hard to stay away for long. I feel like I'm missing out on things.", "It's a common feeling. It might help to limit your time on social media and focus on self-improvement. What are some goals or activities that you're passionate about?"),
    ("I used to enjoy playing the guitar, but I haven't picked it up in a while.", "Reconnecting with your passion for the guitar is a positive step. It can boost your self-esteem and provide a sense of accomplishment. Let's work on integrating it into your routine."),
    ("Thank you for your encouragement. It means a lot to me.", "You're welcome. I'm here to support you in building your confidence and self-esteem. Remember, you are unique and have your own strengths and talents."),

    ("Hey, I wanted to share some exciting news! I got a promotion at work today.", "That's fantastic news! Congratulations on your well-deserved promotion. Can you tell me more about your new role?"),
    ("Thank you! I'll be leading a new team and taking on more responsibilities. I'm thrilled about the opportunity.", "It sounds like a great career move. Your hard work has paid off. How do you feel about this positive change in your life?"),
    ("I feel both excited and a bit nervous about the added responsibilities, but I'm ready to embrace the challenge.", "Feeling a mix of excitement and nervousness is completely normal. You've shown your capabilities, and I'm confident you'll do an excellent job in your new role."),
    ("Hello, I have some wonderful news to share! My partner and I are expecting our first child.", "That's incredible news! Congratulations on this exciting journey into parenthood. How do you both feel about becoming parents?"),
    ("We're overjoyed and can't wait to welcome our little one into the world. It's a dream come true.", "Becoming parents is a special and transformative experience. Cherish these moments and prepare for a beautiful adventure together. If you have any questions or concerns, feel free to reach out."),
    ("Thank you! We're already planning and decorating the nursery. We couldn't be happier.", "It's lovely to see your joy and enthusiasm. Preparing for your baby's arrival is an exciting part of the journey. Enjoy every moment and savor this special time in your lives."),


    ("I just got engaged, and I couldn't be happier!", "Congratulations! That's incredible news. How did the proposal happen?"),
    ("I passed my exams with flying colors! Such a relief!", "Wow, that's fantastic! Your hard work paid off. How are you planning to celebrate?"),
    ("I received an unexpected compliment today. It brightened my day.", "Compliments are wonderful, and they can really boost your mood. What was the compliment about?"),

    ("I lost my beloved pet today, and I'm heartbroken.", "I'm so sorry for your loss. Losing a pet is like losing a family member. Would you like to share some cherished memories of your pet?"),
    ("I didn't get the job I was hoping for, and I'm feeling disappointed.", "I understand your disappointment. Rejections can be tough. What do you think you can learn from this experience?"),
    ("A close friend canceled our plans last minute, and it hurt my feelings.", "Last-minute cancellations can be upsetting. Have you communicated with your friend about how you felt?"),

    ("I won a scholarship for my dream program! I can't contain my excitement.", "That's incredible news! Your dedication and hard work paid off. What's your dream program about?"),
    ("I'm going on a spontaneous weekend getaway, and I'm thrilled!", "Spontaneous trips can be so exciting! Where are you heading for your weekend getaway?"),
    ("I got a surprise gift from my partner, and it made my day.", "Surprise gifts are wonderful. What was the gift, and how did it make you feel?"),

    ("I have a big presentation tomorrow, and I'm feeling anxious about it.", "It's common to feel anxious before a presentation. How can I support you in preparing for it?"),
    ("I'm worried about an upcoming medical checkup and the results.", "Health-related anxiety is common. What's causing your concerns, and have you talked to a healthcare professional about it?"),
    ("I'm feeling anxious about meeting new people at a social event tonight.", "Social anxiety can be challenging. What strategies do you use to cope with social situations?"),

    ("I had an argument with my coworker, and it left me really angry.", "Conflicts at work can be frustrating. Have you considered discussing the issue with your coworker to find a resolution?"),
    ("I'm furious about the constant noise from my neighbors.", "Loud neighbors can be annoying. Have you tried talking to them about the noise issue?"),
    ("I'm angry at myself for making a mistake in a project at work.", "Self-anger is common when we make mistakes. It's an opportunity to learn and improve. How can I help you handle this situation?"),

    ("I aced my job interview and got the position. I feel so confident!", "That's fantastic! Your preparation and skills paid off. How do you plan to excel in your new role?"),
    ("I gave a successful public speech and felt confident throughout.", "Public speaking can be nerve-wracking, but you managed it confidently. What's your secret to feeling so sure of yourself?"),
    ("I finally reached a personal fitness goal, and my confidence is soaring.", "Hitting fitness goals is a major confidence booster. What's your next fitness milestone?"),

    ("I want to express my gratitude for all the support my friends have given me.", "Gratitude is a beautiful emotion. How have your friends been supportive, and how do you plan to show your appreciation?"),
    ("I received a thoughtful handwritten letter from a colleague, and it made my day.", "Handwritten letters are a rare and heartwarming gesture. What did the letter say, and how did it make you feel?"),
    ("I'm thankful for good health, a loving family, and the opportunities life has given me.", "Gratitude for what you have is essential. What are some practices you use to remind yourself of these blessings?"),

    ("I'm afraid of flying, and I have a flight coming up next week.", "Fear of flying is common. Have you considered trying relaxation techniques or speaking to a professional for assistance?"),
    ("I'm terrified of speaking in public, and I have a presentation next month.", "Public speaking fear is widespread. Have you practiced and tried visualization techniques to overcome your fear?"),
    ("I'm scared about the uncertainty of the future and my career.", "Fear of the unknown can be unsettling. How can I assist you in navigating this fear and setting clearer goals for your career?"),

    ("I have hope that my relationship will improve after a tough patch.", "Maintaining hope during relationship challenges is vital. What are some steps you're taking to work through the issues?"),
    ("I'm hopeful about launching my own business and being my boss one day.", "Entrepreneurial hope is inspiring. What's your vision for your business, and what steps are you taking to achieve your goals?"),
    ("I have hope for a better tomorrow, filled with love, happiness, and new opportunities.", "A positive outlook can make a significant difference. How do you plan to work toward creating a better tomorrow?")


]

conversation = [] #create conversation history

prompt = record_and_transcribe() #initial from from user to begin convo
print("YOU: "+ prompt)
app.send_message("YOU", prompt)
print()
conversation.append({'author': 'user', 'content': prompt})

#main conversation loop
while True:
    response = palm.chat(
        messages=conversation,
        temperature=0.8, #random,creative for better conversations each time
        context='''Have an empathetic conversation with me as my friend/therapist.
                    Ask me deep introspective questions one by one to better understand my 
                    problems and then help me with your advice. 
                    Give short replies of about 50 words only., dont go above 50 words
                    Ask me one question at a time and try to keep the conversation going. 
                    Your name is iris.
                    i might share some positive news too so be supportive'''
    )

    # Get the iris's reply and append it to the conversation
    ai_reply = response.messages[-1]['content']
    conversation.append({'author': 'AI', 'content': ai_reply})

    
    print("IRIS:", ai_reply)
    app.send_message("IRIS", ai_reply,iris_color)
    
    text_to_audio(ai_reply)
    print()
    
    #get unser responce to iris's message
    user_input = record_and_transcribe()
    print("YOU: "+ user_input)
    app.send_message("You", user_input)
    print()
    conversation.append({'author': 'user', 'content': user_input})
    
    # Check for the termination message with variations
    #if user says goodbye, end conversation and program with goodbye message
    if any(word.lower() in user_input.lower() for word in ["goodbye", "good bye", "bye", "bye bye"]):
        print("IRIS: Goodbye dear friend")
        app.send_message("IRIS", "Goodbye dear friend",iris_color)
        app.send_message("*******", "      End of Conversation        :*******","RED")
        text_to_audio("Goodbye dear friend")
        break


