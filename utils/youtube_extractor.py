from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional

class YoutubeExtractor:
    def __init__(self):
        self.ytt_api = YouTubeTranscriptApi()
    
    def extract_transcript(self, video_id: str) -> Optional[List[Dict]]:
        try:
            transcript = self.ytt_api.fetch(video_id,languages=['en', 'th'])
            return transcript
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    def get_text_only(self, video_id: str) -> Optional[List[str]]:
        transcript = self.extract_transcript(video_id)
        if transcript:
            return [entry.text for entry in transcript]
        return None
    
    def get_full_text(self, video_id: str) -> Optional[str]:
        text_segments = self.get_text_only(video_id)
        if text_segments:
            return ' '.join(text_segments)
        return None
    
    def print_transcript(self, video_id: str) -> None:
        transcript = self.extract_transcript(video_id)
        if transcript:
            print("--- Full Transcript ---")
            for entry in transcript:
                print(entry['text'])