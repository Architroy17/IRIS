# IRIS - Virtual Conversational Assistant

IRIS is a conversational assistant that engages in empathetic and meaningful conversations with users. It utilizes PyAudio for audio input/output, Whisper for audio-to-text transcription, and Palm for generating conversational responses. The user interacts with IRIS through a Tkinter-based GUI.

## Screenshots displaying workflow of IRIS:

User ready to record (just press enter key to begin):
![when ready to record](https://github.com/Architroy17/IRIS/assets/91129894/ab449a09-01ce-4d1d-ac12-fcdab1a29d11)

User recording (just press enter key to stop):
![while_recording](https://github.com/Architroy17/IRIS/assets/91129894/368688f3-124f-4088-a13a-cbd28f2acd62)

When user says "Goodbye" (keyword to end conversation)"
![on_saying_goodbye](https://github.com/Architroy17/IRIS/assets/91129894/830d09c3-9838-4c05-80fb-ad14f7198e5a)

Flowchart:
![image](https://github.com/Architroy17/IRIS/assets/91129894/1099e3bc-81f9-4563-ae73-98fb61eb78e4)




## Features

- **Voice Interaction**: Users can start and stop voice recording by pressing the Enter key. IRIS transcribes the recorded audio and generates responses based on the conversation context.

- **Empathetic Conversations**: IRIS is designed to have empathetic and supportive conversations. It actively listens to users' concerns, offers guidance, and provides a positive and understanding presence.

- **Customizable Conversation Flow**: IRIS uses the Palm model for conversation generation. The conversation context is updated dynamically, allowing for a more natural and context-aware dialogue.

- **Graphical User Interface (GUI)**: The Tkinter-based GUI provides a chat screen where users can see the conversation history and a microphone button to initiate voice interaction.

- **Text-to-Speech (TTS)**: IRIS converts generated responses to audio using Google Text-to-Speech (gTTS) and plays the speech with adjusted speed using Pygame.

## Getting Started

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/iris-conversational-assistant.git
    cd iris-conversational-assistant
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure the Google API key in the code:

    ```python
    key = 'YOUR_GOOGLE_API_KEY'
    palm.configure(api_key=key)
    ```

4. Run the application:

    ```bash
    python iris.py
    ```

## Example Conversations

#### User: Hi IRIS, how are you?
IRIS: Hi, I am doing great, how are you doing?

#### User: I'm good, the project i was working on is about to end soon.
IRIS: That's great, what was the project about?

#### User: It was a Virtual conversation assistant.
IRIS: oh wow, so what is left now?

#### User: Just some documentation, hey tell me, why do we need to document everything?
IRIS: Documentation is very important, it helps others and you understand the code you have written and further develop it when necessary.

#### User: Ok, what is distance between sun and earth in kilometer?
IRIS: It's about 147.28 Million kilometer.

#### User: I lost my job today.
IRIS: Losing a job can be incredibly stressful. How are you feeling about it?

#### User: Goodbye.
IRIS: Goodbye dear friend


