
import base64
import json
from typing import Dict, List, Any
import os

import requests
import streamlit as st
import streamlit.components.v1 as components

from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

def create_session() -> Any | None:
    """Create a new chat session"""
    try:
        response = requests.post(f"{API_BASE_URL}/v1/session")
        response.raise_for_status()
        return response.json()["id"]
    except Exception as e:
        st.error(f"Failed to create session: {e}")
        return None

def send_message_stream(session_id: str, query: str):
    """Send message to streaming chat API"""
    try:
        payload = {
            "session_id": session_id,
            "query": query
        }
        
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/stream", 
            json=payload, 
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                        yield data
                    except json.JSONDecodeError:
                        continue
                        
    except Exception as e:
        st.error(f"Failed to send streaming message: {e}")
        yield {"type": "error", "error": str(e)}

def send_message(session_id: str, query: str) -> Any | None:
    """Send message to chat API (non-streaming fallback)"""
    try:
        payload = {
            "session_id": session_id,
            "query": query
        }
        response = requests.post(f"{API_BASE_URL}/v1/chat", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to send message: {e}")
        return None

def get_chat_history(session_id: str) -> List[Dict]:
    """Get chat history for a session"""
    try:
        response = requests.get(f"{API_BASE_URL}/v1/chat/history/{session_id}")
        response.raise_for_status()
        return response.json()["history"]
    except Exception as e:
        st.error(f"Failed to get chat history: {e}")
        return []

def text_to_speech(text: str) -> str | None:
    """Convert text to speech using TTS API and return base64 encoded audio data"""
    try:
        tts_choice = st.session_state.get("tts_provider", "Zalo")
        tts_endpoint = "/v1/tts-zalo" if tts_choice == "Zalo" else "/v1/tts-gemini"

        response = requests.post(
            f"{API_BASE_URL}{tts_endpoint}",
            json={"text": text}
        )
        response.raise_for_status()
        # Convert binary audio data to base64
        audio_base64 = base64.b64encode(response.content).decode('utf-8')
        return audio_base64
    except Exception as e:
        st.error(f"Lỗi chuyển văn bản thành giọng nói: {e}")
        return None

def create_audio_player_html(audio_base64: str, button_key: str) -> str:
    """Create HTML for hidden audio player with custom play button"""
    return f"""
        <div style="display: none">
            <audio id="tts-audio-{button_key}" type="audio/mp3" src="data:audio/mp3;base64,{audio_base64}"></audio>
        </div>
        <script>
            const audio = document.getElementById('tts-audio-{button_key}');
            audio.play().catch(e => console.error('Error playing audio:', e));
        </script>
    """

def play_audio(content: str, button_key: str) -> None:
    """Handle audio playback with caching"""    
    # If this is a button click, schedule the audio and rerun
    if st.session_state.current_audio is None:
        st.session_state.current_audio = (content, button_key)
        st.rerun()
    
    # If we have scheduled audio, play it
    if st.session_state.current_audio:
        content, button_key = st.session_state.current_audio
        st.session_state.current_audio = None  # Clear the scheduled audio
        
        # # Try to get from cache first
        # audio_base64 = st.session_state.audio_cache.get(content)
        
        # # If not in cache, generate new audio
        # if not audio_base64:
        #     audio_base64 = text_to_speech(content)
        #     if audio_base64:
        #         # Cache the audio
        #         st.session_state.audio_cache[content] = audio_base64
        audio_base64 = text_to_speech(content)
        
        # Play audio if available
        if audio_base64:
            components.html(create_audio_player_html(audio_base64, button_key), height=0)

def main():
    # Initialize audio states
    if "audio_cache" not in st.session_state:
        st.session_state.audio_cache = {}
    if "current_audio" not in st.session_state:
        st.session_state.current_audio = None

    st.set_page_config(
        page_title="Trung Nguyen Legend Cafe Chatbot",
        page_icon="☕",
        layout="wide"
    )
    
    # Check for scheduled audio playback
    if st.session_state.current_audio:
        content, button_key = st.session_state.current_audio
        play_audio(content, button_key)
    
    st.title("☕ Trung Nguyen Legend Cafe Chatbot")
    st.markdown("Hỏi tôi về thiền cafe, cà phê triết đạo, địa chỉ trải nghiệm thiền cafe, và sản phẩm của Trung Nguyên Legend!")
    
    # Initialize session
    if "session_id" not in st.session_state:
        st.session_state.session_id = create_session()
        st.session_state.messages = []
    
    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        # Display the message
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                cols = st.columns([0.95, 0.05])
                with cols[0]:
                    intent = message.get("intent", "")
                    if intent == "triet_dao":
                        st.markdown(message["content"])
                        st.video("https://www.youtube.com/watch?v=sDAzSEXb1MA")
                    else:
                        st.markdown(message["content"])
                with cols[1]:
                    button_key = f"speak_history_{idx}"
                    if st.button("🔊", key=button_key, help="Click để nghe"):
                        play_audio(message["content"], button_key)
            else:
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Check if streaming is enabled
        use_streaming = st.session_state.get("use_streaming", True)
        
        # Send message to API
        with st.chat_message("assistant"):
            if use_streaming:
                # Use streaming response
                response_placeholder = st.empty()
                intent_placeholder = st.empty()
                loading_placeholder = st.empty()
                
                full_response = ""
                current_intent = ""
                loading_placeholder.markdown("⌛ *Đang suy nghĩ...*")
                
                try:
                    for chunk in send_message_stream(st.session_state.session_id, prompt):
                        if chunk["type"] == "intent":
                            current_intent = chunk["intent"]
                        elif chunk["type"] == "content":
                            # Clear loading on first content chunk
                            if loading_placeholder:
                                loading_placeholder.empty()
                                loading_placeholder = None
                            full_response += chunk["content"]
                            response_placeholder.write(full_response + "▌")  # Add cursor
                        elif chunk["type"] == "done":
                            # Add assistant response to chat history first
                            if full_response:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": full_response,
                                    "intent": current_intent
                                })
                                # Force a rerun to ensure everything is properly rendered
                                st.rerun()
                            break
                        elif chunk["type"] == "error":
                            # Make sure to clear loading if we haven't received any content yet
                            if loading_placeholder:
                                loading_placeholder.empty()
                            st.error(f"Lỗi: {chunk['error']}")
                            break
                    
                except Exception as e:
                    st.error(f"Lỗi streaming: {e}")
                    # Fallback to non-streaming
                    st.info("Đang thử lại với phương thức thông thường...")
                    use_streaming = False
            
            if not use_streaming:
                # Use regular response
                with st.spinner("Đang suy nghĩ..."):
                    response = send_message(st.session_state.session_id, prompt)
                    
                    if response:
                        # Add response to chat history and rerun
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response["response"],
                            "intent": response["intent"]
                        })
                        st.rerun()
                    else:
                        st.error("Không thể nhận được phản hồi từ chatbot")
    
    # Sidebar with information
    with st.sidebar:
        st.header("Thông tin")
        st.markdown("""
        **Chatbot này có thể trả lời về:**
        - 🧘 Thiền cafe và triết lý Trung Nguyên
        - 📍 Địa chỉ trải nghiệm thiền cà phê
        - 📞 Số điện thoại và cách đặt vé
        - ☕ Sản phẩm và giá cả
        
        """)
        # Choose TTS provider (default is Zalo)

        if "tts_provider" not in st.session_state:
            st.session_state.tts_provider = "Zalo"

        selected = st.selectbox(
            "Chọn TTS Provider",
            options=["Zalo", "Gemini"],
            index=["Zalo", "Gemini"].index(st.session_state.tts_provider)  
        )

        if selected != st.session_state.tts_provider:
            st.session_state.tts_provider = selected
        st.write("Provider đang chọn: ", st.session_state.tts_provider)
        
        # Toggle streaming mode
        use_streaming = st.checkbox("Sử dụng Streaming", value=True)
        st.session_state.use_streaming = use_streaming
        
        if st.button("Tạo phiên mới"):
            st.session_state.session_id = create_session()
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**Session ID:** `{st.session_state.session_id}`")

if __name__ == "__main__":
    main()