import whisper
model = whisper.load_model('large-v2')

result = model.transcribe(audio = "audios/1_Installing VS Code & How Websites Work.mp3",
                          language = "hi",
                          task = "translate")

print(result['text'])