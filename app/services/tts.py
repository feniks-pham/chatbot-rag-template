import os
import tempfile
import re
import base64
import numpy as np
from typing import List

import httpx
import aiofiles

from google import genai
from google.genai import types
from scipy.io.wavfile import write as write_wav
import wave

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TTSService:
    def __init__(self):
        self.api_url = settings.tts_api_url
        self.api_key = settings.tts_api_key
        self.model = settings.tts_model
        self.speaker_id = settings.tts_speaker_id
        self.speed = settings.tts_speed
        self.encode_type = settings.tts_encode_type
        self.max_chars = 2000  # API character limit
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks smaller than max_chars characters"""
        logger.info(f"Starting text splitting. Original text length: {len(text)} chars")
        logger.info(f"Text preview: {text[:100]}{'...' if len(text) > 100 else ''}")

        if len(text) <= self.max_chars:
            logger.info("Text is within limit, no splitting needed")
            return [text]

        # Split by sentence to avoid cutting in the middle of a sentence
        sentences = re.split(r'([.!?]+)', text)
        logger.info(f"Split into {len(sentences)} sentence parts")

        chunks = []
        current_chunk = ""
        chunk_count = 0

        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + punctuation

            logger.debug(f"Processing sentence {i//2 + 1}: '{full_sentence[:50]}{'...' if len(full_sentence) > 50 else ''}'")

            # If adding this sentence exceeds the limit
            if len(current_chunk + full_sentence) > self.max_chars:
                if current_chunk:
                    chunk_count += 1
                    logger.info(f"Chunk {chunk_count} completed: {len(current_chunk)} chars")
                    logger.debug(f"Chunk {chunk_count} content: '{current_chunk[:100]}{'...' if len(current_chunk) > 100 else ''}'")
                    chunks.append(current_chunk.strip())
                    current_chunk = full_sentence
                    logger.info(f"Started new chunk {chunk_count + 1} with sentence: {len(full_sentence)} chars")
                else:
                    # Sentence too long, must split by word
                    logger.warning(f"Sentence too long ({len(full_sentence)} chars), splitting by words")
                    words = full_sentence.split()
                    for word in words:
                        if len(current_chunk + " " + word) > self.max_chars:
                            if current_chunk:
                                chunk_count += 1
                                logger.info(f"Chunk {chunk_count} completed (word split): {len(current_chunk)} chars")
                                logger.debug(f"Chunk {chunk_count} content: '{current_chunk[:100]}{'...' if len(current_chunk) > 100 else ''}'")
                                chunks.append(current_chunk.strip())
                                current_chunk = word
                                logger.info(f"Started new chunk {chunk_count + 1} with word: '{word[:20]}{'...' if len(word) > 20 else ''}'")
                            else:
                                # Word too long, must split by character
                                logger.warning(f"Word too long ({len(word)} chars), splitting by characters")
                                chunk_count += 1
                                chunks.append(word[:self.max_chars])
                                logger.info(f"Chunk {chunk_count} created (char split): {self.max_chars} chars")
                                logger.debug(f"Chunk {chunk_count} content: '{word[:self.max_chars][:100]}{'...' if len(word[:self.max_chars]) > 100 else ''}'")
                                current_chunk = word[self.max_chars:]
                                if current_chunk:
                                    logger.info(f"Remaining characters: {len(current_chunk)}")
                        else:
                            current_chunk += (" " + word) if current_chunk else word
            else:
                current_chunk += full_sentence
                logger.debug(f"Added sentence to current chunk. Current length: {len(current_chunk)} chars")

        if current_chunk.strip():
            chunk_count += 1
            chunks.append(current_chunk.strip())
            logger.info(f"Final chunk {chunk_count} completed: {len(current_chunk)} chars")
            logger.debug(f"Final chunk content: '{current_chunk[:100]}{'...' if len(current_chunk) > 100 else ''}'")

        logger.info(f"Text splitting completed. Total chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Chunk {i}: {len(chunk)} chars")

        return chunks

    async def _generate_speech_chunk(self, text: str, chunk_index: int, total_chunks: int) -> str:
        """Generate speech for a text chunk"""
        try:
            logger.info(f"Generating speech for chunk {chunk_index}/{total_chunks} ({len(text)} chars)")
            logger.debug(f"Chunk {chunk_index} content: '{text[:100]}{'...' if len(text) > 100 else ''}'")

            payload = {
                "model": self.model,
                "input": text,
                "speaker_id": self.speaker_id,
                "speed": self.speed,
                "encode_type": self.encode_type
            }

            # Create temporary file for this chunk
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"tts_chunk_{chunk_index}_{hash(text)}.mp3")
            
            logger.debug(f"Making API request to {self.api_url} with model: {self.model}")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()

                # Save response to file
                async with aiofiles.open(temp_file, "wb") as f:
                    await f.write(response.content)
                
                file_size = len(response.content)
                logger.info(f"Generated audio chunk {chunk_index}: {temp_file} ({file_size} bytes)")
                return temp_file

        except Exception as e:
            logger.error(f"Error generating speech for chunk {chunk_index}: {e}", exc_info=True)
            raise
    
    async def _merge_audio_files(self, audio_files: List[str]) -> str:
        """Merge audio files into a single file by concatenating binary files"""
        if len(audio_files) == 1:
            logger.info("Only one audio file, no merging needed")
            return audio_files[0]
        
        try:
            logger.info(f"Starting to merge {len(audio_files)} audio files")
            
            # Create output file
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"tts_merged_{hash(str(audio_files))}.mp3")
            
            total_size = 0
            # Read and concatenate audio files
            async with aiofiles.open(output_file, "wb") as output:
                for i, audio_file in enumerate(audio_files, 1):
                    logger.info(f"Merging file {i}/{len(audio_files)}: {audio_file}")
                    async with aiofiles.open(audio_file, "rb") as input_file:
                        content = await input_file.read()
                        await output.write(content)
                        file_size = len(content)
                        total_size += file_size
                        logger.info(f"Added file {i}: {file_size} bytes")
            
            # Clean up temporary chunk files
            logger.info("Cleaning up temporary chunk files")
            for audio_file in audio_files:
                try:
                    os.remove(audio_file)
                    logger.debug(f"Removed temporary file: {audio_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {audio_file}: {e}")
            
            logger.info(f"Audio merging completed: {output_file} ({total_size} bytes)")
            return output_file
            
        except Exception as e:
            logger.error(f"Error merging audio files: {e}", exc_info=True)
            raise
    
    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech and return the path to the audio file"""
        try:
            logger.info(f"Starting TTS process for text: {len(text)} characters")
            
            # Split text into chunks
            text_chunks = self._split_text(text)
            logger.info(f"Text split into {len(text_chunks)} chunks")
            
            # Generate speech for each chunk
            audio_files = []
            for i, chunk in enumerate(text_chunks, 1):
                logger.info(f"Processing chunk {i}/{len(text_chunks)}: {len(chunk)} chars")
                audio_file = await self._generate_speech_chunk(chunk, i, len(text_chunks))
                audio_files.append(audio_file)
            
            # Merge audio files
            logger.info("Starting audio file merging")
            final_audio_file = await self._merge_audio_files(audio_files)
            
            logger.info(f"TTS process completed successfully: {final_audio_file}")
            return final_audio_file

        except Exception as e:
            logger.error(f"Error in TTS process: {e}", exc_info=True)
            raise

class GeminiTTSService:
    def __init__(self):
        self.api_url = settings.gemini_tts_api_url
        self.api_key = settings.gemini_tts_api_key
        self.language_code = settings.gemini_tts_voice_language_code
        self.voice_name = settings.gemini_tts_voice_name
        self.audio_encoding = settings.gemini_tts_audio_encoding
        self.speaking_rate = settings.gemini_tts_speaking_rate
        self.pitch = settings.gemini_tts_pitch
        self.sample_rate_hertz = settings.gemini_tts_sample_rate_hertz
        self.max_chars = 5000
        self.headers = {
            "Content-Type": "application/json"
        }

    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks smaller than max_chars characters"""
        logger.info(f"Starting text splitting. Original text length: {len(text)} chars")
        logger.info(f"Text preview: {text[:100]}{'...' if len(text) > 100 else ''}")

        if len(text) <= self.max_chars:
            logger.info("Text is within limit, no splitting needed")
            return [text]

        # Split by sentence to avoid cutting in the middle of a sentence
        sentences = re.split(r'([.!?]+)', text)
        logger.info(f"Split into {len(sentences)} sentence parts")

        chunks = []
        current_chunk = ""
        chunk_count = 0

        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + punctuation

            logger.debug(f"Processing sentence {i//2 + 1}: '{full_sentence[:50]}{'...' if len(full_sentence) > 50 else ''}'")

            # If adding this sentence exceeds the limit
            if len(current_chunk + full_sentence) > self.max_chars:
                if current_chunk:
                    chunk_count += 1
                    logger.info(f"Chunk {chunk_count} completed: {len(current_chunk)} chars")
                    logger.debug(f"Chunk {chunk_count} content: '{current_chunk[:100]}{'...' if len(current_chunk) > 100 else ''}'")
                    chunks.append(current_chunk.strip())
                    current_chunk = full_sentence
                    logger.info(f"Started new chunk {chunk_count + 1} with sentence: {len(full_sentence)} chars")
                else:
                    # Sentence too long, must split by word
                    logger.warning(f"Sentence too long ({len(full_sentence)} chars), splitting by words")
                    words = full_sentence.split()
                    for word in words:
                        if len(current_chunk + " " + word) > self.max_chars:
                            if current_chunk:
                                chunk_count += 1
                                logger.info(f"Chunk {chunk_count} completed (word split): {len(current_chunk)} chars")
                                logger.debug(f"Chunk {chunk_count} content: '{current_chunk[:100]}{'...' if len(current_chunk) > 100 else ''}'")
                                chunks.append(current_chunk.strip())
                                current_chunk = word
                                logger.info(f"Started new chunk {chunk_count + 1} with word: '{word[:20]}{'...' if len(word) > 20 else ''}'")
                            else:
                                # Word too long, must split by character
                                logger.warning(f"Word too long ({len(word)} chars), splitting by characters")
                                chunk_count += 1
                                chunks.append(word[:self.max_chars])
                                logger.info(f"Chunk {chunk_count} created (char split): {self.max_chars} chars")
                                logger.debug(f"Chunk {chunk_count} content: '{word[:self.max_chars][:100]}{'...' if len(word[:self.max_chars]) > 100 else ''}'")
                                current_chunk = word[self.max_chars:]
                                if current_chunk:
                                    logger.info(f"Remaining characters: {len(current_chunk)}")
                        else:
                            current_chunk += (" " + word) if current_chunk else word
            else:
                current_chunk += full_sentence
                logger.debug(f"Added sentence to current chunk. Current length: {len(current_chunk)} chars")

        if current_chunk.strip():
            chunk_count += 1
            chunks.append(current_chunk.strip())
            logger.info(f"Final chunk {chunk_count} completed: {len(current_chunk)} chars")
            logger.debug(f"Final chunk content: '{current_chunk[:100]}{'...' if len(current_chunk) > 100 else ''}'")

        logger.info(f"Text splitting completed. Total chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Chunk {i}: {len(chunk)} chars")

        return chunks
    
    async def _generate_speech_chunk(self, text: str, chunk_index: int, total_chunks: int) -> str:
        """Generate speech for a text chunk"""
        try:
            logger.info(f"Generating speech for chunk {chunk_index}/{total_chunks} ({len(text)} chars)")
            logger.debug(f"Chunk {chunk_index} content: '{text[:100]}{'...' if len(text) > 100 else ''}'")

            payload = {
                "input": {"text": text},
                "voice": {
                    "languageCode": self.language_code,
                    "name": self.voice_name
                },
                "audioConfig": {
                    "audioEncoding": self.audio_encoding,
                    "speakingRate": self.speaking_rate,
                    "pitch": self.pitch,
                    "sampleRateHertz": self.sample_rate_hertz
                }
            }

            # Create temporary file for this chunk
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"tts_chunk_{chunk_index}_{hash(text)}.mp3")
            
            logger.debug(f"Making API request to {self.api_url} with Gemini model")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()

                audio_content = base64.b64decode(response.json()["audioContent"])

                # Save response to file
                async with aiofiles.open(temp_file, "wb") as f:
                    await f.write(audio_content)
                
                file_size = len(audio_content)
                logger.info(f"Generated audio chunk {chunk_index}: {temp_file} ({file_size} bytes)")
                return temp_file

        except Exception as e:
            logger.error(f"Error generating speech for chunk {chunk_index}: {e}", exc_info=True)
            raise

    async def _merge_audio_files(self, audio_files: List[str]) -> str:
        """Merge audio files into a single file by concatenating binary files"""
        if len(audio_files) == 1:
            logger.info("Only one audio file, no merging needed")
            return audio_files[0]
        
        try:
            logger.info(f"Starting to merge {len(audio_files)} audio files")
            
            # Create output file
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"tts_merged_{hash(str(audio_files))}.mp3")
            
            total_size = 0
            # Read and concatenate audio files
            async with aiofiles.open(output_file, "wb") as output:
                for i, audio_file in enumerate(audio_files, 1):
                    logger.info(f"Merging file {i}/{len(audio_files)}: {audio_file}")
                    async with aiofiles.open(audio_file, "rb") as input_file:
                        content = await input_file.read()
                        await output.write(content)
                        file_size = len(content)
                        total_size += file_size
                        logger.info(f"Added file {i}: {file_size} bytes")
            
            # Clean up temporary chunk files
            logger.info("Cleaning up temporary chunk files")
            for audio_file in audio_files:
                try:
                    os.remove(audio_file)
                    logger.debug(f"Removed temporary file: {audio_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {audio_file}: {e}")
            
            logger.info(f"Audio merging completed: {output_file} ({total_size} bytes)")
            return output_file
            
        except Exception as e:
            logger.error(f"Error merging audio files: {e}", exc_info=True)
            raise

    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech and return the path to the audio file"""
        try:
            logger.info(f"Starting TTS process for text: {len(text)} characters")
            
            # Split text into chunks
            text_chunks = self._split_text(text)
            logger.info(f"Text split into {len(text_chunks)} chunks")
            
            # Generate speech for each chunk
            audio_files = []
            for i, chunk in enumerate(text_chunks, 1):
                logger.info(f"Processing chunk {i}/{len(text_chunks)}: {len(chunk)} chars")
                audio_file = await self._generate_speech_chunk(chunk, i, len(text_chunks))
                audio_files.append(audio_file)
            
            # Merge audio files
            logger.info("Starting audio file merging")
            final_audio_file = await self._merge_audio_files(audio_files)
            
            logger.info(f"TTS process completed successfully: {final_audio_file}")
            return final_audio_file

        except Exception as e:
            logger.error(f"Error in TTS process: {e}", exc_info=True)
            raise

# class GeminiTTSService:
#     def __init__(self):
#         self.model_name = "gemini-2.5-flash-preview-tts"
#         self.voice_name = "Kore"  # bạn có thể thay bằng các giọng khác
#         self.sample_rate = 24000
#         self.max_chars = 5000
#         self.client = genai.Client(
#             api_key="AIzaSyCPgEcCIDJvVbHJsOCy2XombKJS9EQk8oI"
#         )

#     def _split_text(self, text: str) -> List[str]:
#         """Split text into chunks smaller than max_chars characters"""
#         logger.info(f"Splitting text of length {len(text)}")
#         if len(text) <= self.max_chars:
#             return [text]

#         sentences = re.split(r'([.!?]+)', text)
#         chunks = []
#         current_chunk = ""

#         for i in range(0, len(sentences), 2):
#             sentence = sentences[i]
#             punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
#             full_sentence = sentence + punctuation

#             if len(current_chunk + full_sentence) > self.max_chars:
#                 chunks.append(current_chunk.strip())
#                 current_chunk = full_sentence
#             else:
#                 current_chunk += full_sentence

#         if current_chunk.strip():
#             chunks.append(current_chunk.strip())

#         logger.info(f"Split into {len(chunks)} chunks")
#         return chunks

#     def _save_audio(self, filename: str, pcm_base64: bytes):
#         # """Save raw PCM bytes into a WAV file"""
#         # with wave.open(filename, "wb") as wf:
#         #     wf.setnchannels(1)
#         #     wf.setsampwidth(2)  # 16-bit
#         #     wf.setframerate(self.sample_rate)
#         #     wf.writeframes(pcm_data)
#         """Convert PCM bytes to numpy array and save to WAV"""
#         pcm_data = base64.b64decode(pcm_base64)
    
#         # Nếu độ dài không chia hết cho 2 -> dữ liệu không hợp lệ
#         if len(pcm_data) % 2 != 0:
#             pcm_data = pcm_data[:-1]  # hoặc raise Exception nếu bạn muốn nghiêm ngặt

#         audio_np = np.frombuffer(pcm_data, dtype=np.int16)
#         write_wav(filename, self.sample_rate, audio_np)

#     async def _generate_speech_chunk(self, text: str, index: int) -> str:
#         logger.info(f"Generating audio for chunk {index}: {text[:60]}...")

#         response = self.client.models.generate_content(
#             contents=text,
#             model=self.model_name,
#             config=types.GenerateContentConfig(
#                 response_modalities=["AUDIO"],
#                 speech_config=types.SpeechConfig(
#                     voice_config=types.VoiceConfig(
#                         prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self.voice_name)
#                     )
#                 )
#             ),
#         )

#         audio_data = response.candidates[0].content.parts[0].inline_data.data
#         raw_pcm = base64.b64decode(audio_data)
#         print("First 50 decoded bytes:", raw_pcm[:50])
#         temp_dir = tempfile.gettempdir()
#         output_path = os.path.join(temp_dir, f"gemini_tts_chunk_{index}.wav")
#         self._save_audio(output_path, raw_pcm)

#         logger.info(f"Saved audio chunk to {output_path}")
#         return output_path

#     async def _merge_audio_files(self, audio_files: List[str]) -> str:
#         if len(audio_files) == 1:
#             return audio_files[0]

#         logger.info(f"Merging {len(audio_files)} audio files...")

#         temp_dir = tempfile.gettempdir()
#         output_path = os.path.join(temp_dir, "gemini_tts_merged.wav")

#         async with aiofiles.open(output_path, "wb") as outfile:
#             for path in audio_files:
#                 async with aiofiles.open(path, "rb") as infile:
#                     content = await infile.read()
#                     await outfile.write(content)

#         for path in audio_files:
#             try:
#                 os.remove(path)
#             except:
#                 pass

#         logger.info(f"Merged audio saved to {output_path}")
#         return output_path

#     async def text_to_speech(self, text: str) -> str:
#         logger.info("Starting text-to-speech process...")
#         chunks = self._split_text(text)
#         audio_paths = []

#         for i, chunk in enumerate(chunks, start=1):
#             path = await self._generate_speech_chunk(chunk, i)
#             audio_paths.append(path)

#         final_path = await self._merge_audio_files(audio_paths)
#         logger.info(f"TTS completed: {final_path}")
#         return final_path