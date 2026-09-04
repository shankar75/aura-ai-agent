"""
AI Agent - Streamlit Web App version (with built-in web search)

Setup:
    pip install streamlit anthropic
    export ANTHROPIC_API_KEY=your_key_here

Run:
    streamlit run app.py

This opens a chat interface in your browser at http://localhost:8501
"""

import streamlit as st
import anthropic
import time
from openai import OpenAI
from runwayml import RunwayML

MODEL = "claude-sonnet-4-6"

openai_client = OpenAI()  # reads OPENAI_API_KEY from env
runway_client = RunwayML()  # reads RUNWAYML_API_SECRET from env

TOOLS = [
    {
        "type": "web_search_20250305",
        "name": "web_search"
    },
    {
        "name": "generate_image",
        "description": "Generate an image from a text description using DALL-E 3. Use this whenever the user asks you to create, draw, or generate an image or picture.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "A detailed description of the image to generate"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "generate_video",
        "description": "Generate a short video from a text description using Runway. Use this whenever the user asks you to create or generate a video or animation. Video generation takes 1-2 minutes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "A detailed description of the video to generate"
                }
            },
            "required": ["prompt"]
        }
    }
]


def generate_image(prompt):
    """Calls DALL-E 3 and returns the image URL."""
    result = openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1
    )
    return result.data[0].url


def generate_video(prompt, status_callback=None):
    """
    Calls Runway's text-to-video API and polls until the video is ready.
    Returns the video URL. status_callback (optional) is called with progress updates.
    """
    task = runway_client.text_to_video.create(
        model="gen4_turbo",
        prompt_text=prompt,
        ratio="1280:720",
        duration=5
    )

    task_id = task.id

    # Poll until done (video generation is not instant)
    while True:
        time.sleep(5)
        status = runway_client.tasks.retrieve(id=task_id)

        if status_callback:
            status_callback(status.status)

        if status.status == "SUCCEEDED":
            return status.output[0]
        elif status.status == "FAILED":
            raise RuntimeError(f"Video generation failed: {status.failure_reason}")
        # else: still RUNNING or PENDING, keep polling

st.set_page_config(page_title="AI Agent", page_icon="🤖")
st.title("🤖 AI Agent")
st.caption("Chat with an AI that can search the web for current info.")

# Set up the Anthropic client
client = anthropic.Anthropic()

# Keep chat history across reruns (Streamlit reruns the script on every interaction)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["display_text"])
            for url in msg.get("image_urls", []):
                st.image(url)
            for url in msg.get("video_urls", []):
                st.video(url)

# Chat input box at the bottom
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Show user's message immediately
    with st.chat_message("user"):
        st.write(user_input)

    # Add to history (API format)
    api_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    api_history.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                tools=TOOLS,
                messages=api_history
            )

            image_urls = []
            video_urls = []

            # Loop in case the model calls a tool (e.g. generate_image, generate_video)
            while response.stop_reason == "tool_use":
                api_history.append({"role": "assistant", "content": response.content})

                tool_use = next(b for b in response.content if b.type == "tool_use")

                if tool_use.name == "generate_image":
                    with st.spinner("Generating image..."):
                        image_url = generate_image(tool_use.input["prompt"])
                        image_urls.append(image_url)
                        tool_result = f"Image generated successfully: {image_url}"
                elif tool_use.name == "generate_video":
                    status_box = st.empty()
                    def update_status(s):
                        status_box.info(f"Generating video... ({s.lower()})")
                    try:
                        video_url = generate_video(tool_use.input["prompt"], status_callback=update_status)
                        video_urls.append(video_url)
                        tool_result = f"Video generated successfully: {video_url}"
                    except RuntimeError as e:
                        tool_result = f"Video generation failed: {e}"
                    status_box.empty()
                else:
                    tool_result = "Unknown tool"

                api_history.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": tool_result
                    }]
                })

                response = client.messages.create(
                    model=MODEL,
                    max_tokens=1024,
                    tools=TOOLS,
                    messages=api_history
                )

            answer_text = ""
            for block in response.content:
                if block.type == "text":
                    answer_text += block.text

        st.write(answer_text)
        for url in image_urls:
            st.image(url)
        for url in video_urls:
            st.video(url)

    # Save both turns to session history
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({
        "role": "assistant",
        "content": response.content,   # full content for API context
        "display_text": answer_text,   # just the text for display
        "image_urls": image_urls,      # images generated this turn
        "video_urls": video_urls       # videos generated this turn
    })
