"""
Voice-to-Text for Letter Creation
Converts audio recordings to text for correspondence creation
"""

import frappe
from frappe import _
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import os
import tempfile
import base64


class VoiceToTextConverter:
	"""Converts voice recordings to text"""
	
	def __init__(self):
		self.recognizer = sr.Recognizer()
		self.supported_formats = ['wav', 'mp3', 'ogg', 'flac', 'm4a']
	
	def convert_audio_to_text(self, audio_file_path, language='en-US'):
		"""
		Convert audio file to text
		
		Args:
			audio_file_path: Path to audio file
			language: Language code (e.g., 'en-US', 'ar-SA')
			
		Returns:
			str: Transcribed text
		"""
		try:
			# Convert audio to WAV if needed
			wav_path = self._convert_to_wav(audio_file_path)
			
			# Load audio file
			with sr.AudioFile(wav_path) as source:
				# Adjust for ambient noise
				self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
				
				# Record audio
				audio_data = self.recognizer.record(source)
			
			# Recognize speech
			try:
				text = self.recognizer.recognize_google(audio_data, language=language)
				return text
			except sr.UnknownValueError:
				frappe.throw(_(
					"Could not understand the audio. Please ensure: "
					"1) The audio contains clear speech, "
					"2) The correct language is selected, "
					"3) There is minimal background noise, "
					"4) The recording volume is adequate."
				))
			except sr.RequestError as e:
				frappe.throw(_("Could not request results from speech recognition service: {0}").format(str(e)))
			
		except Exception as e:
			frappe.log_error(f"Error converting audio to text: {str(e)}", "Voice to Text Error")
			frappe.throw(_("Failed to convert audio to text: {0}").format(str(e)))
		finally:
			# Clean up temporary WAV file
			if wav_path and wav_path != audio_file_path and os.path.exists(wav_path):
				os.remove(wav_path)
	
	def convert_audio_chunks(self, audio_file_path, language='en-US', chunk_duration=30):
		"""
		Convert long audio files by splitting into chunks
		
		Args:
			audio_file_path: Path to audio file
			language: Language code
			chunk_duration: Duration of each chunk in seconds
			
		Returns:
			str: Complete transcribed text
		"""
		try:
			# Load audio
			audio = AudioSegment.from_file(audio_file_path)
			
			# Calculate chunks
			chunk_length_ms = chunk_duration * 1000
			chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
			
			# Process each chunk
			full_text = []
			
			for i, chunk in enumerate(chunks):
				# Export chunk to temporary WAV file
				with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
					chunk.export(temp_wav.name, format='wav')
					temp_wav_path = temp_wav.name
				
				try:
					# Convert chunk to text
					chunk_text = self.convert_audio_to_text(temp_wav_path, language)
					full_text.append(chunk_text)
				finally:
					# Clean up temporary file
					if os.path.exists(temp_wav_path):
						os.remove(temp_wav_path)
			
			# Combine all chunks
			return ' '.join(full_text)
			
		except Exception as e:
			frappe.log_error(f"Error converting audio chunks: {str(e)}", "Voice to Text Error")
			frappe.throw(_("Failed to convert audio chunks: {0}").format(str(e)))
	
	def _convert_to_wav(self, audio_file_path):
		"""
		Convert audio file to WAV format if needed
		
		Args:
			audio_file_path: Path to audio file
			
		Returns:
			str: Path to WAV file
		"""
		# Get file extension
		file_ext = os.path.splitext(audio_file_path)[1].lower().replace('.', '')
		
		# If already WAV, return as is
		if file_ext == 'wav':
			return audio_file_path
		
		# Check if FFmpeg is available
		try:
			import subprocess
			subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
		except (FileNotFoundError, subprocess.CalledProcessError):
			frappe.throw(_(
				"FFmpeg is not installed. Please install FFmpeg to convert audio files, or upload WAV files directly. "
				"To install: sudo apt install ffmpeg"
			))
		
		# Convert to WAV
		try:
			# Try to load the audio file
			audio = AudioSegment.from_file(audio_file_path, format=file_ext)
			
			# Check if audio is valid
			if len(audio) == 0:
				frappe.throw(_("The audio file appears to be empty or corrupted. Please try recording again or upload a different file."))
			
			# Create temporary WAV file
			with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
				audio.export(temp_wav.name, format='wav')
				return temp_wav.name
				
		except Exception as e:
			error_msg = str(e).lower()
			
			# Provide specific error messages for common issues
			if 'invalid data' in error_msg or 'ebml' in error_msg or 'truncating' in error_msg:
				frappe.throw(_(
					"The audio file is corrupted or incomplete. This often happens with browser recordings. "
					"Please try: 1) Record again and wait a moment after stopping, 2) Upload a pre-recorded file instead, "
					"3) Use a different browser, or 4) Upload a WAV file directly."
				))
			elif 'no such file' in error_msg:
				frappe.throw(_("Audio file not found. Please try uploading again."))
			else:
				frappe.log_error(f"Error converting audio format: {str(e)}", "Voice to Text Error")
				frappe.throw(_(
					"Failed to convert audio format. Please try: 1) Recording again, "
					"2) Uploading a different audio file, or 3) Using WAV format. Error: {0}"
				).format(str(e)[:100]))
	
	def transcribe_with_timestamps(self, audio_file_path, language='en-US'):
		"""
		Transcribe audio with word-level timestamps (advanced feature)
		
		Args:
			audio_file_path: Path to audio file
			language: Language code
			
		Returns:
			list: List of dictionaries with word and timestamp
		"""
		# Note: This is a simplified version. For production, consider using
		# services like Google Cloud Speech-to-Text API or AWS Transcribe
		# which provide word-level timestamps
		
		try:
			text = self.convert_audio_to_text(audio_file_path, language)
			
			# Split into words
			words = text.split()
			
			# Estimate timestamps (simplified)
			# In production, use proper speech recognition API with timestamp support
			timestamps = []
			avg_word_duration = 0.5  # Average 0.5 seconds per word
			
			for i, word in enumerate(words):
				timestamps.append({
					"word": word,
					"start_time": i * avg_word_duration,
					"end_time": (i + 1) * avg_word_duration
				})
			
			return timestamps
			
		except Exception as e:
			frappe.log_error(f"Error transcribing with timestamps: {str(e)}", "Voice to Text Error")
			frappe.throw(_("Failed to transcribe with timestamps: {0}").format(str(e)))


class VoiceLetterCreator:
	"""Creates letters from voice recordings"""
	
	def __init__(self):
		self.converter = VoiceToTextConverter()
	
	def create_letter_from_voice(self, audio_file_path, doctype, language='en-US', metadata=None):
		"""
		Create a letter document from voice recording
		
		Args:
			audio_file_path: Path to audio file
			doctype: Type of letter (Incoming Letter or Outgoing Letter)
			language: Language code
			metadata: Additional metadata (dict)
			
		Returns:
			dict: Created letter document
		"""
		try:
			# Convert audio to text
			transcribed_text = self.converter.convert_audio_to_text(audio_file_path, language)
			
			# Parse text to extract subject and body
			# Simple heuristic: First sentence is subject, rest is body
			sentences = transcribed_text.split('.')
			subject = sentences[0].strip() if sentences else "Voice Letter"
			body = '. '.join(sentences[1:]).strip() if len(sentences) > 1 else transcribed_text
			
			# Create letter document
			letter = frappe.new_doc(doctype)
			letter.subject = subject[:140]  # Limit subject length
			letter.body = body
			
			# Add metadata if provided
			if metadata:
				for key, value in metadata.items():
					if hasattr(letter, key):
						setattr(letter, key, value)
			
			# Add note about voice creation
			letter.add_comment('Comment', _('This letter was created from a voice recording'))
			
			# Save letter
			letter.insert()
			frappe.db.commit()
			
			return {
				"success": True,
				"message": _("Letter created successfully from voice recording"),
				"letter_name": letter.name,
				"subject": letter.subject,
				"transcribed_text": transcribed_text
			}
			
		except Exception as e:
			frappe.log_error(f"Error creating letter from voice: {str(e)}", "Voice to Text Error")
			frappe.throw(_("Failed to create letter from voice: {0}").format(str(e)))
	
	def enhance_transcription(self, text):
		"""
		Enhance transcription with punctuation and formatting
		
		Args:
			text: Raw transcribed text
			
		Returns:
			str: Enhanced text
		"""
		# Basic enhancements
		# In production, use NLP libraries for better results
		
		# Capitalize first letter
		text = text.capitalize()
		
		# Add period at end if missing
		if not text.endswith('.'):
			text += '.'
		
		# Capitalize after periods
		sentences = text.split('. ')
		sentences = [s.capitalize() for s in sentences]
		text = '. '.join(sentences)
		
		return text


@frappe.whitelist()
def convert_audio_to_text_api(file_url, language='en-US'):
	"""
	API to convert audio file to text
	
	Args:
		file_url: URL of audio file
		language: Language code
		
	Returns:
		dict: Transcribed text
	"""
	try:
		# Get file from URL
		file_doc = frappe.get_doc("File", {"file_url": file_url})
		file_path = file_doc.get_full_path()
		
		# Convert to text
		converter = VoiceToTextConverter()
		text = converter.convert_audio_to_text(file_path, language)
		
		return {
			"success": True,
			"message": _("Audio converted successfully"),
			"text": text,
			"language": language
		}
		
	except Exception as e:
		frappe.log_error(f"Error in audio conversion API: {str(e)}", "Voice to Text Error")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def create_letter_from_voice_api(file_url, doctype, language='en-US', metadata=None):
	"""
	API to create letter from voice recording
	
	Args:
		file_url: URL of audio file
		doctype: Type of letter
		language: Language code
		metadata: Additional metadata (JSON string)
		
	Returns:
		dict: Created letter details
	"""
	try:
		# Get file from URL
		file_doc = frappe.get_doc("File", {"file_url": file_url})
		file_path = file_doc.get_full_path()
		
		# Parse metadata if provided
		import json
		meta = json.loads(metadata) if metadata else {}
		
		# Create letter
		creator = VoiceLetterCreator()
		result = creator.create_letter_from_voice(file_path, doctype, language, meta)
		
		return result
		
	except Exception as e:
		frappe.log_error(f"Error in create letter from voice API: {str(e)}", "Voice to Text Error")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def transcribe_with_timestamps_api(file_url, language='en-US'):
	"""
	API to transcribe audio with timestamps
	
	Args:
		file_url: URL of audio file
		language: Language code
		
	Returns:
		dict: Transcription with timestamps
	"""
	try:
		# Get file from URL
		file_doc = frappe.get_doc("File", {"file_url": file_url})
		file_path = file_doc.get_full_path()
		
		# Transcribe with timestamps
		converter = VoiceToTextConverter()
		timestamps = converter.transcribe_with_timestamps(file_path, language)
		
		return {
			"success": True,
			"message": _("Audio transcribed successfully"),
			"timestamps": timestamps,
			"language": language
		}
		
	except Exception as e:
		frappe.log_error(f"Error in transcribe with timestamps API: {str(e)}", "Voice to Text Error")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def get_supported_languages():
	"""
	Get list of supported languages for voice recognition
	
	Returns:
		dict: Supported languages
	"""
	languages = {
		"en-US": "English (US)",
		"en-GB": "English (UK)",
		"ar-SA": "Arabic (Saudi Arabia)",
		"ar-EG": "Arabic (Egypt)",
		"fr-FR": "French",
		"de-DE": "German",
		"es-ES": "Spanish",
		"it-IT": "Italian",
		"pt-BR": "Portuguese (Brazil)",
		"ru-RU": "Russian",
		"zh-CN": "Chinese (Simplified)",
		"ja-JP": "Japanese",
		"ko-KR": "Korean"
	}
	
	return {
		"success": True,
		"languages": languages
	}
