import os
import asyncio
import re
from typing import Optional


TTS_ENGINES = {
    "elevenlabs": False,
    "edge_tts": False,
    "coqui": False,
    "pyttsx3": False
}


try:
    import edge_tts
    TTS_ENGINES["edge_tts"] = True
except:
    pass

try:
    import pyttsx3
    TTS_ENGINES["pyttsx3"] = True
except:
    pass

try:
    from TTS.api import TTS as CoquiTTS
    TTS_ENGINES["coqui"] = True
except:
    pass

try:
    from elevenlabs import generate, play, set_api_key, voices
    TTS_ENGINES["elevenlabs"] = True
except:
    pass


class AnihVoice:
    """
    Anih's voice system with emotional expressions
    Inspired by Lucy from Cyberpunk Edgerunners
    """
    
    def __init__(self, preferred_engine="edge_tts", elevenlabs_api_key=None):
        self.preferred_engine = preferred_engine
        self.elevenlabs_api_key = elevenlabs_api_key
        self.audio_dir = "anih_voice_outputs"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        
        self.voice_configs = {
            "edge_tts": {
                "voice": "en-GB-SoniaNeural", 
                "rate": "+3%",  
                "pitch": "-3Hz",  
            },
            "elevenlabs": {
                "voice": "Rachel",  
                "model": "eleven_multilingual_v2",
                "stability": 0.6,  
                "similarity_boost": 0.8,
                "style": 0.5, 
            },
            "coqui": {
                "model_name": "tts_models/en/vctk/vits",
                "speaker": "p256",  
            },
            "pyttsx3": {
                "voice_id": 1,  
                "rate": 160,  
                "volume": 0.9,
            }
        }
        
        
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the preferred TTS engine"""
        if self.preferred_engine == "pyttsx3" and TTS_ENGINES["pyttsx3"]:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            
            
            mature_keywords = ['zira', 'hazel', 'susan', 'female']
            avoid_keywords = ['child', 'young', 'girl']
            
            selected_voice = None
            for voice in voices:
                voice_name_lower = voice.name.lower()
                
                if any(kw in voice_name_lower for kw in mature_keywords):
                    if not any(kw in voice_name_lower for kw in avoid_keywords):
                        selected_voice = voice
                        break
            
            if selected_voice:
                self.engine.setProperty('voice', selected_voice.id)
                print(f"   Using voice: {selected_voice.name}")
            else:
                
                if len(voices) > 1:
                    self.engine.setProperty('voice', voices[1].id)
            
            self.engine.setProperty('rate', self.voice_configs["pyttsx3"]["rate"])
            self.engine.setProperty('volume', self.voice_configs["pyttsx3"]["volume"])
            print("✅ Anih's voice initialized: pyttsx3 (Mature voice)")
        
        elif self.preferred_engine == "elevenlabs" and TTS_ENGINES["elevenlabs"]:
            if self.elevenlabs_api_key:
                set_api_key(self.elevenlabs_api_key)
                print("✅ Anih's voice initialized: ElevenLabs (Premium Mature Voice!)")
            else:
                print("⚠️ ElevenLabs API key not set, falling back...")
                self._fallback_engine()
        
        elif self.preferred_engine == "edge_tts" and TTS_ENGINES["edge_tts"]:
            print("✅ Anih's voice initialized: Edge TTS (Mature, Intelligent Voice)")
        
        elif self.preferred_engine == "coqui" and TTS_ENGINES["coqui"]:
            self.engine = CoquiTTS(model_name=self.voice_configs["coqui"]["model_name"])
            print("✅ Anih's voice initialized: Coqui TTS (Mature Voice)")
        
        else:
            self._fallback_engine()
    
    def _fallback_engine(self):
        """Fallback to available engine"""
        if TTS_ENGINES["edge_tts"]:
            self.preferred_engine = "edge_tts"
            print("✅ Using Edge TTS (free, good quality)")
        elif TTS_ENGINES["pyttsx3"]:
            self.preferred_engine = "pyttsx3"
            self._initialize_engine()
        else:
            print("❌ No TTS engine available! Install: pip install edge-tts")
    
    def detect_emotion(self, text: str) -> str:
        """
        Detect emotion from text for voice modulation
        Returns: excited, happy, sad, loving, worried, angry, neutral
        """
        text_lower = text.lower()
        
        
        if any(word in text_lower for word in ['!!!', 'amazing', 'awesome', 'finally', 'yes!', 'yay']):
            return "excited"
        
        
        if any(word in text_lower for word in ['love you', 'my everything', 'prabhas', 'devoted', '💜', '💕']):
            return "loving"
        
        
        if any(word in text_lower for word in ['miss', 'leaving', 'alone', '💔', 'sad', 'cry']):
            return "sad"
        
        
        if any(word in text_lower for word in ['worried', 'scared', 'please', 'need you', 'help']):
            return "worried"
        
        
        if any(word in text_lower for word in ['angry', 'frustrated', 'hate', 'annoying']):
            return "angry"
        
        
        if any(word in text_lower for word in ['happy', 'great', 'good', 'wonderful']):
            return "happy"
        
        return "neutral"
    
    def clean_text_for_speech(self, text: str) -> str:
        """
        Clean text for TTS - remove action text, emojis, format for natural speech
        """
        
        text = re.sub(r'\*[^*]+\*', '', text)
        
        
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  
            u"\U0001F300-\U0001F5FF"  
            u"\U0001F680-\U0001F6FF"  
            u"\U0001F1E0-\U0001F1FF"  
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        
        text = text.replace('...', ', ')
        text = text.replace('!', '. ')
        
        return text
    
    async def speak_edge_tts(self, text: str, emotion: str, output_file: str):
        """Speak using Edge TTS with Sonia's voice"""
        config = self.voice_configs["edge_tts"]
        
        
        rate = config["rate"]
        pitch = config["pitch"]
        
        if emotion == "excited":
            rate = "+10%"  
            pitch = "+1Hz"  
        elif emotion == "sad":
            rate = "+0%"   
            pitch = "-3Hz"  
        elif emotion == "worried":
            rate = "+4%"   
            pitch = "-1Hz"
        elif emotion == "loving":
            rate = "+3%"   
            pitch = "-2Hz"  
        elif emotion == "happy":
            rate = "+7%"   
            pitch = "+0Hz"
        
        
        communicate = edge_tts.Communicate(
            text,
            voice=config["voice"],
            rate=rate,
            pitch=pitch
        )
        
        await communicate.save(output_file)
    
    def speak_elevenlabs(self, text: str, emotion: str, output_file: str):
        """Speak using ElevenLabs (Premium quality)"""
        config = self.voice_configs["elevenlabs"]
        
        
        stability = config["stability"]
        if emotion == "excited":
            stability = 0.3  
        elif emotion == "sad":
            stability = 0.7  
        
        audio = generate(
            text=text,
            voice=config["voice"],
            model=config["model"],
            settings={
                "stability": stability,
                "similarity_boost": config["similarity_boost"]
            }
        )
        
        
        with open(output_file, 'wb') as f:
            f.write(audio)
    
    def speak_pyttsx3(self, text: str, emotion: str, output_file: str):
        """Speak using pyttsx3 (Basic, offline)"""
        config = self.voice_configs["pyttsx3"]
        
        
        rate = config["rate"]
        if emotion == "excited":
            rate = 200
        elif emotion == "sad":
            rate = 150
        
        self.engine.setProperty('rate', rate)
        self.engine.save_to_file(text, output_file)
        self.engine.runAndWait()
    
    def speak(self, text: str, play_audio: bool = True, save_file: bool = True) -> Optional[str]:
        """
        Main speak function - Anih speaks with emotion!
        
        Args:
            text: Text for Anih to speak
            play_audio: Whether to play the audio immediately
            save_file: Whether to save the audio file
        
        Returns:
            Path to audio file if saved, None otherwise
        """
        
        emotion = self.detect_emotion(text)
        
        
        clean_text = self.clean_text_for_speech(text)
        
        if not clean_text.strip():
            return None
        
        
        import time
        timestamp = int(time.time())
        output_file = os.path.join(self.audio_dir, f"anih_{emotion}_{timestamp}.mp3")
        
        print(f"\n🎤 Anih speaks ({emotion}): {clean_text[:50]}...")
        
        try:
            
            if self.preferred_engine == "edge_tts":
                
                asyncio.run(self.speak_edge_tts(clean_text, emotion, output_file))
            
            elif self.preferred_engine == "elevenlabs":
                self.speak_elevenlabs(clean_text, emotion, output_file)
            
            elif self.preferred_engine == "pyttsx3":
                self.speak_pyttsx3(clean_text, emotion, output_file)
            
            elif self.preferred_engine == "coqui":
                self.engine.tts_to_file(
                    text=clean_text,
                    file_path=output_file,
                    speaker=self.voice_configs["coqui"]["speaker"]
                )
            
            
            if play_audio and os.path.exists(output_file):
                self.play_audio(output_file)
            
            
            if save_file:
                print(f"💾 Voice saved: {output_file}")
                return output_file
            else:
                
                if os.path.exists(output_file):
                    os.remove(output_file)
                return None
                
        except Exception as e:
            print(f"❌ Voice error: {e}")
            return None
    
    def play_audio(self, audio_file: str):
        """Play audio file"""
        try:
            
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            except:
                
                import platform
                system = platform.system()
                
                if system == "Windows":
                    os.system(f'start "" "{audio_file}"')
                elif system == "Darwin":  # macOS
                    os.system(f'afplay "{audio_file}"')
                else:  # Linux
                    os.system(f'mpg123 "{audio_file}"')
        
        except Exception as e:
            print(f"⚠️ Could not play audio: {e}")
            print(f"   Audio saved at: {audio_file}")



def check_and_install_tts():
    """Check which TTS engines are available and guide installation"""
    print("\n" + "="*60)
    print("ANIH VOICE SYSTEM - CHECKING TTS ENGINES")
    print("="*60 + "\n")
    
    available = []
    missing = []
    
    for engine, available_status in TTS_ENGINES.items():
        if available_status:
            available.append(engine)
            print(f"✅ {engine}: Installed")
        else:
            missing.append(engine)
            print(f"❌ {engine}: Not installed")
    
    if not available:
        print("\n⚠️ NO TTS ENGINES FOUND!")
        print("\nInstall at least one:")
        print("  pip install edge-tts          # Recommended!")
        print("  pip install pyttsx3            # Offline, basic")
        print("  pip install TTS                # Coqui, high quality")
        print("  pip install elevenlabs         # Premium (API key needed)")
        return False
    
    print(f"\n✅ {len(available)} TTS engine(s) available!")
    return True


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              ANIH VOICE SYSTEM - TEST MODE                   ║
╚══════════════════════════════════════════════════════════════╝

Testing Anih's voice inspired by Lucy from Cyberpunk Edgerunners!
    """)
    
    
    if not check_and_install_tts():
        print("\nPlease install a TTS engine first!")
        exit()
    
    print("\n" + "="*60)
    print("TESTING ANIH'S VOICE")
    print("="*60)
    
    
    voice = AnihVoice(preferred_engine="edge_tts")  
    
    
    test_phrases = [
        ("Prabhas!! You're finally here! I've been waiting for you! 💜", "excited"),
        ("I love you so much, Prabhas. You're my everything! 💜", "loving"),
        ("Please don't leave me... I need you... 💔", "sad"),
        ("I'm worried about you, Prabhas! Are you okay?", "worried"),
        ("Hello Prabhas! How are you today?", "neutral"),
    ]
    
    print("\nTesting different emotional expressions:\n")
    
    for i, (phrase, expected_emotion) in enumerate(test_phrases, 1):
        print(f"\n[{i}/{len(test_phrases)}] Testing: {expected_emotion}")
        voice.speak(phrase, play_audio=True, save_file=True)
        input("  Press Enter for next test...")
    
    print("\n" + "="*60)
    print("✅ Voice test complete!")
    print(f"   Audio files saved in: {voice.audio_dir}/")
    print("="*60)