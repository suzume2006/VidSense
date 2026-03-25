import requests

# ── RICH TRANSCRIPT GENERATOR ─────────────────────────
# Merges speech + visual + actions into one rich text
# that captures EVERYTHING that happened in the video

def generate_rich_transcript(speech, visual_context, actions, groq_api_key):
    """
    Combine speech transcript, visual semantic context,
    and action detection into one rich unified transcript.
    This transcript is then used for:
    1. Similarity comparison against ground truth
    2. Input to AI video generator
    """

    prompt = f"""You are an expert video understanding AI.

You have been given three types of analysis from a video:

SPEECH TRANSCRIPT (what was said):
{speech if speech else "No speech detected"}

VISUAL SEMANTIC CONTEXT (what was shown — 3 layers):
{visual_context}

ACTION DETECTION (what was happening physically):
{actions}

Your task is to generate a RICH UNIFIED TRANSCRIPT that:
1. Combines ALL three sources of information
2. Describes the complete video content holistically
3. Captures both verbal and non-verbal communication
4. Is written as a coherent paragraph (not bullet points)
5. Is detailed enough that someone could recreate the video from it
6. Includes what was said, what was shown, and what actions occurred

Write the rich transcript now — be thorough and specific:"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
                "temperature": 0.3
            },
            timeout=25
        )

        if response.status_code == 200:
            rich_transcript = response.json()['choices'][0]['message']['content']
            print(f"  Rich transcript generated: {rich_transcript[:100]}...")
            return rich_transcript
        else:
            print(f"  Rich transcript generation failed: {response.status_code}")
            # Fallback — just combine all three
            return f"{speech}\n\nVisual: {visual_context}\n\nActions: {actions}"

    except Exception as e:
        print(f"  Error generating rich transcript: {e}")
        return f"{speech}\n\nVisual: {visual_context}\n\nActions: {actions}"


def generate_video_prompt(rich_transcript, groq_api_key):
    """
    Convert rich transcript into a concise video generation prompt
    suitable for Runway ML / Pika Labs
    """
    prompt = f"""Based on this video description, generate a concise 
video generation prompt (max 200 words) suitable for an AI video generator like Runway ML.

VIDEO DESCRIPTION:
{rich_transcript}

The prompt should:
- Describe the visual scene clearly
- Mention key actions and movements
- Include setting, lighting, and atmosphere
- Be specific enough to recreate the video
- Start with the main subject and action

Write ONLY the video generation prompt, nothing else:"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 250,
                "temperature": 0.4
            },
            timeout=20
        )

        if response.status_code == 200:
            video_prompt = response.json()['choices'][0]['message']['content']
            print(f"  Video prompt generated: {video_prompt[:100]}...")
            return video_prompt
        else:
            return rich_transcript[:200]

    except Exception as e:
        print(f"  Error generating video prompt: {e}")
        return rich_transcript[:200]


if __name__ == "__main__":
    GROQ_API_KEY = "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"

    # Test with sample data
    speech  = "The photosynthesis process converts sunlight into energy"
    visual  = "Frame 1: Student pointing to diagram of chloroplast"
    actions = "Frame 1: Student is gesturing towards whiteboard"

    rich = generate_rich_transcript(speech, visual, actions, GROQ_API_KEY)
    print("\nRich Transcript:")
    print(rich)

    prompt = generate_video_prompt(rich, GROQ_API_KEY)
    print("\nVideo Generation Prompt:")
    print(prompt)
