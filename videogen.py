import requests
import time
import os

RUNWAY_API_KEY = "key_77a2384fcd4c64b1c568fa5804821dd7df53fab2cdbd313b0f005375de93d7dd4bb7da0c2f4dfd341f4e1247956cb176653006c1deb0e969ab32cf36f3a4ed26"


def generate_video_from_text(text_prompt, runway_api_key=None, duration=5):
    api_key = runway_api_key or RUNWAY_API_KEY
    print(f"  Prompt: {text_prompt[:120]}...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06"
    }

    # Correct duration per model based on API error messages
    attempts = [
        {"model": "gen4.5",      "ratio": "1280:720",  "duration": 5},
        {"model": "gen4.5",      "ratio": "1280:720",  "duration": 10},
        {"model": "veo3.1_fast", "ratio": "1280:720",  "duration": 4},
        {"model": "veo3.1_fast", "ratio": "1920:1080", "duration": 4},
        {"model": "veo3.1",      "ratio": "1280:720",  "duration": 4},
        {"model": "veo3",        "ratio": "1280:720",  "duration": 8},
        {"model": "veo3",        "ratio": "1920:1080", "duration": 8},
    ]

    task_id = None
    for a in attempts:
        try:
            payload = {
                "promptText": text_prompt[:500],
                "model":      a["model"],
                "duration":   a["duration"],
                "ratio":      a["ratio"]
            }
            print(f"\n  Trying {a['model']} ratio={a['ratio']} duration={a['duration']}...")
            r = requests.post(
                "https://api.dev.runwayml.com/v1/text_to_video",
                headers=headers, json=payload, timeout=30
            )
            print(f"  Status: {r.status_code} | {r.text[:200]}")

            if r.status_code in [200, 201]:
                task_id = r.json().get("id")
                if task_id:
                    print(f"  SUCCESS with {a['model']}! Task: {task_id}")
                    break
        except Exception as e:
            print(f"  Error: {e}")

    if not task_id:
        print("\n  Runway API video generation not available — skipping")
        return None

    # Poll for completion
    print("\n  Waiting for video", end="", flush=True)
    for _ in range(40):
        time.sleep(10)
        print(".", end="", flush=True)
        try:
            poll      = requests.get(
                f"https://api.dev.runwayml.com/v1/tasks/{task_id}",
                headers=headers, timeout=15
            )
            poll_data = poll.json()
            status    = poll_data.get("status", "")
            if status == "SUCCEEDED":
                print(" Done!")
                outputs = poll_data.get("output", [])
                return download_video(outputs[0], task_id) if outputs else None
            elif status == "FAILED":
                print(f"\n  FAILED: {poll_data.get('failure','unknown')}")
                return None
        except Exception as e:
            print(f"\n  Poll error: {e}")

    print("\n  Timed out")
    return None


def download_video(video_url, task_id, output_folder="generated_videos"):
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{task_id}.mp4")
    try:
        r = requests.get(video_url, timeout=120)
        if r.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(r.content)
            print(f"  Saved: {output_path}")
            return output_path
        return None
    except Exception as e:
        print(f"  Download error: {e}")
        return None


if __name__ == "__main__":
    result = generate_video_from_text(
        "A person standing and explaining a concept with hand gestures",
    )
    print(f"\nFinal Result: {result}")


