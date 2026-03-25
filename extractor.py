import cv2
import base64
import requests
import whisper
import os
import imageio_ffmpeg
import subprocess

# ── FFMPEG SETUP ──────────────────────────────────────
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
os.environ["FFMPEG_BINARY"] = ffmpeg_path

# ── WHISPER MODEL ─────────────────────────────────────
print("Loading Whisper model...")
whisper_model = whisper.load_model("small")
print("Whisper ready!")

# ── VISION MODELS ─────────────────────────────────────
VISION_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.2-90b-vision-preview",
    "llama-3.2-11b-vision-preview",
]

# ── PROMPTS ───────────────────────────────────────────
VISUAL_PROMPT = """Analyse this video frame using THREE semantic layers:

LAYER 1 - SURFACE: What objects, text, people, settings are visible?

LAYER 2 - SEMANTIC: What is the overall scene or activity? 
What is happening in this context?

LAYER 3 - CONCEPTUAL: What is the deeper meaning or purpose 
of what is shown? What story does this frame tell?

Be specific and concise — 2 sentences per layer."""

ACTION_PROMPT = """Analyse this video frame and identify:

ACTIONS: What physical actions are happening?
(Examples: running, jumping, cooking, explaining, writing, 
pointing, dancing, fighting, sitting, walking)

SUBJECT: Who or what is performing the action?

CONTEXT: Where is this happening and what is the purpose?

MOTION: Is there fast/slow movement, stillness, or transition?

Be specific — 1-2 sentences per section."""


# ── STAGE 1: SPEECH EXTRACTION ────────────────────────
def extract_audio(video_path, output_path="temp_audio.wav"):
    try:
        subprocess.run([
            ffmpeg_path, "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1", output_path
        ], capture_output=True, check=True)
        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        print(f"  Audio extraction error: {e}")
        return None


def extract_speech(video_path):
    """Extract and transcribe speech from video"""
    print("  Extracting speech with Whisper...")
    audio_path = extract_audio(video_path)

    if not audio_path:
        return {"transcript": "", "language": "unknown"}

    try:
        result = whisper_model.transcribe(audio_path)
        transcript = result["text"].strip()
        language   = result["language"]

        if os.path.exists(audio_path):
            os.remove(audio_path)

        print(f"  Speech extracted: {transcript[:80]}...")
        return {"transcript": transcript, "language": language}

    except Exception as e:
        print(f"  Whisper error: {e}")
        return {"transcript": "", "language": "unknown"}


# ── STAGE 2 & 3: VISUAL + ACTION EXTRACTION ───────────
def extract_frames(video_path, num_frames=5):
    """Extract evenly spaced frames"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total == 0:
        return []

    interval = max(1, total // num_frames)
    frames   = []

    for i in range(num_frames):
        pos = min(i * interval, total - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)

    cap.release()
    print(f"  Extracted {len(frames)} frames")
    return frames


def frame_to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buffer).decode('utf-8')


def query_vision_model(img_base64, prompt, groq_api_key):
    """Query Groq vision model with fallback"""
    for model in VISION_MODELS:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }],
                    "max_tokens": 300,
                    "temperature": 0.2
                },
                timeout=20
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"    Model {model} failed: {response.status_code}")
                continue
        except Exception as e:
            print(f"    Model {model} error: {e}")
            continue
    return None


def extract_visual_and_actions(video_path, groq_api_key):
    """Extract visual semantic context AND actions from video"""
    print("  Extracting visual context and actions...")
    frames = extract_frames(video_path, num_frames=5)

    if not frames:
        return {
            "visual_context": "No visual content extracted.",
            "actions": "No actions detected."
        }

    visual_analyses = []
    action_analyses = []

    for i, frame in enumerate(frames):
        print(f"  Analysing frame {i+1}/{len(frames)}...")
        img_b64 = frame_to_base64(frame)

        # Visual semantic layers
        visual = query_vision_model(img_b64, VISUAL_PROMPT, groq_api_key)
        if visual:
            visual_analyses.append(f"Frame {i+1}:\n{visual}")

        # Action detection
        action = query_vision_model(img_b64, ACTION_PROMPT, groq_api_key)
        if action:
            action_analyses.append(f"Frame {i+1}:\n{action}")

    return {
        "visual_context": "\n\n".join(visual_analyses) if visual_analyses else "No visual content detected.",
        "actions":        "\n\n".join(action_analyses) if action_analyses else "No actions detected."
    }


# ── MAIN EXTRACTOR ────────────────────────────────────
def extract_all(video_path, groq_api_key):
    """
    Full extraction pipeline:
    Speech + Visual Semantic Layers + Actions
    """
    print(f"\n── Extracting from: {video_path}")

    speech  = extract_speech(video_path)
    visuals = extract_visual_and_actions(video_path, groq_api_key)

    return {
        "transcript":     speech["transcript"],
        "language":       speech["language"],
        "visual_context": visuals["visual_context"],
        "actions":        visuals["actions"]
    }


if __name__ == "__main__":
    import sys
    GROQ_API_KEY = "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"
    if len(sys.argv) > 1:
        result = extract_all(sys.argv[1], GROQ_API_KEY)
        print("\nTranscript:", result["transcript"])
        print("\nVisual Context:", result["visual_context"][:200])
        print("\nActions:", result["actions"][:200])
    else:
        print("Usage: python extractor.py <video_path>")
