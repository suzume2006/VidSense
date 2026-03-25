import cv2
import numpy as np
import requests
import base64
from sentence_transformers import SentenceTransformer, util
from rouge_score import rouge_scorer as rs

# ── SBERT MODEL ───────────────────────────────────────
print("Loading SBERT model...")
sbert = SentenceTransformer("all-MiniLM-L6-v2")
print("SBERT ready!")

GROQ_API_KEY = "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"


# ── TEXT SIMILARITY ───────────────────────────────────
def compute_text_similarity(generated_transcript, ground_truth):
    """
    Compare generated rich transcript vs MSR-VTT ground truth caption
    using SBERT cosine similarity + ROUGE-L
    """
    if not generated_transcript or not ground_truth:
        return {"text_score": 0, "rouge_score": 0, "combined_text": 0}

    # SBERT cosine similarity
    t_embed = sbert.encode(generated_transcript, convert_to_tensor=True)
    r_embed = sbert.encode(ground_truth,         convert_to_tensor=True)
    cosine  = round(util.cos_sim(t_embed, r_embed).item() * 100, 1)

    # ROUGE-L
    scorer     = rs.RougeScorer(['rougeL'], use_stemmer=True)
    rouge      = scorer.score(ground_truth, generated_transcript)
    rouge_score = round(rouge['rougeL'].fmeasure * 100, 1)

    combined = round((0.7 * cosine) + (0.3 * rouge_score), 1)

    return {
        "text_score":    cosine,
        "rouge_score":   rouge_score,
        "combined_text": combined
    }


# ── FRAME EXTRACTION ──────────────────────────────────
def extract_frames_for_comparison(video_path, num_frames=10):
    """Extract frames for visual comparison"""
    cap    = cv2.VideoCapture(video_path)
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []

    if total == 0:
        cap.release()
        return frames

    interval = max(1, total // num_frames)

    for i in range(num_frames):
        pos = min(i * interval, total - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ret, frame = cap.read()
        if ret:
            # Resize for consistency
            frame = cv2.resize(frame, (224, 224))
            frames.append(frame)

    cap.release()
    return frames


# ── FRAME SIMILARITY (Histogram) ──────────────────────
def compute_frame_similarity(frames1, frames2):
    """
    Compare two sets of frames using color histogram similarity.
    Returns average similarity score 0-100.
    """
    if not frames1 or not frames2:
        return 0

    scores = []
    min_frames = min(len(frames1), len(frames2))

    for i in range(min_frames):
        f1 = cv2.cvtColor(frames1[i], cv2.COLOR_BGR2HSV)
        f2 = cv2.cvtColor(frames2[i], cv2.COLOR_BGR2HSV)

        hist1 = cv2.calcHist([f1], [0, 1], None, [50, 60], [0, 180, 0, 256])
        hist2 = cv2.calcHist([f2], [0, 1], None, [50, 60], [0, 180, 0, 256])

        cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        scores.append(max(0, score))

    return round(np.mean(scores) * 100, 1) if scores else 0


# ── CLIP-STYLE SEMANTIC COMPARISON ────────────────────
def compute_semantic_frame_similarity(original_frames, generated_frames, groq_api_key):
    """
    Use Groq Vision to describe both videos and compare descriptions
    semantically — acts as a CLIP-style comparison.
    """
    def describe_frames(frames, label):
        if not frames:
            return ""
        descriptions = []
        for i, frame in enumerate(frames[:3]):  # Use first 3 frames
            _, buffer = cv2.imencode('.jpg', frame)
            img_b64   = base64.b64encode(buffer).decode()

            for model in ["meta-llama/llama-4-scout-17b-16e-instruct",
                          "llama-3.2-11b-vision-preview"]:
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
                                            "url": f"data:image/jpeg;base64,{img_b64}"
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": "Describe this video frame in 2 sentences. What is happening? What is visible?"
                                    }
                                ]
                            }],
                            "max_tokens": 100
                        },
                        timeout=15
                    )
                    if response.status_code == 200:
                        descriptions.append(
                            response.json()['choices'][0]['message']['content']
                        )
                        break
                except Exception:
                    continue

        return " ".join(descriptions)

    print("  Generating semantic descriptions for comparison...")
    orig_desc = describe_frames(original_frames, "original")
    gen_desc  = describe_frames(generated_frames, "generated")

    if not orig_desc or not gen_desc:
        return 0

    # Compare descriptions with SBERT
    e1 = sbert.encode(orig_desc, convert_to_tensor=True)
    e2 = sbert.encode(gen_desc,  convert_to_tensor=True)

    return round(util.cos_sim(e1, e2).item() * 100, 1)


# ── MAIN COMPARATOR ───────────────────────────────────
def compare_videos(
    original_video_path,
    generated_video_path,
    generated_transcript,
    ground_truth_caption,
    groq_api_key
):
    """
    Full comparison pipeline:
    1. Text similarity — rich transcript vs ground truth
    2. Frame histogram similarity — original vs generated video
    3. Semantic frame similarity — CLIP-style description comparison
    4. Final weighted score
    """
    print("\n── Comparing original vs generated video...")

    # ── 1. Text Similarity ────────────────────────────
    print("  Computing text similarity...")
    text_scores = compute_text_similarity(generated_transcript, ground_truth_caption)

    # ── 2. Frame Similarity ───────────────────────────
    frame_score = 0
    semantic_frame_score = 0

    if generated_video_path and generated_video_path != "SKIPPED":
        print("  Extracting frames for visual comparison...")
        orig_frames = extract_frames_for_comparison(original_video_path)
        gen_frames  = extract_frames_for_comparison(generated_video_path)

        print("  Computing frame histogram similarity...")
        frame_score = compute_frame_similarity(orig_frames, gen_frames)

        print("  Computing semantic frame similarity...")
        semantic_frame_score = compute_semantic_frame_similarity(
            orig_frames, gen_frames, groq_api_key
        )
    else:
        print("  Skipping video comparison — no generated video")

    # ── 3. Final Weighted Score ───────────────────────
    if generated_video_path and generated_video_path != "SKIPPED":
        # Full score with video comparison
        final_score = round(
            (0.4 * text_scores["combined_text"]) +
            (0.3 * semantic_frame_score) +
            (0.3 * frame_score),
            1
        )
    else:
        # Text only score
        final_score = text_scores["combined_text"]

    # ── 4. Label ──────────────────────────────────────
    if final_score >= 80:   label = "🏆 Excellent — System fully understood the video"
    elif final_score >= 60: label = "✅ Good — Strong understanding with minor gaps"
    elif final_score >= 40: label = "⚠️  Partial — Moderate understanding detected"
    else:                   label = "❌ Poor — System struggled to understand video"

    return {
        "final_score":          final_score,
        "label":                label,
        "text_similarity":      text_scores["combined_text"],
        "sbert_score":          text_scores["text_score"],
        "rouge_score":          text_scores["rouge_score"],
        "frame_histogram":      frame_score,
        "semantic_frame_score": semantic_frame_score,
        "ground_truth":         ground_truth_caption,
        "generated_transcript": generated_transcript[:200] + "..."
    }


if __name__ == "__main__":
    # Test text similarity
    gt      = "A person is cooking pasta in a kitchen"
    gen     = "A chef is preparing spaghetti on the stove in a home kitchen, stirring the pot"
    scores  = compute_text_similarity(gen, gt)
    print(f"Text similarity: {scores}")
