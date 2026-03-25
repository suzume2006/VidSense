import json
import os
import random

# ── MSR-VTT DATASET LOADER ────────────────────────────
# After downloading from Kaggle, your folder should have:
# /msrvtt/
#   ├── train_val_videodatainfo.json
#   ├── test_videodatainfo.json
#   └── videos/
#         ├── video0.mp4
#         ├── video1.mp4
#         └── ...

def load_dataset(json_path, videos_folder, max_videos=10):
    """
    Load MSR-VTT videos and their ground truth captions.
    Returns list of {video_path, captions, video_id}
    """
    print(f"Loading MSR-VTT dataset from {json_path}...")

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Build caption lookup: video_id → list of captions
    caption_map = {}
    for sentence in data['sentences']:
        vid_id = sentence['video_id']
        if vid_id not in caption_map:
            caption_map[vid_id] = []
        caption_map[vid_id].append(sentence['caption'])

    # Build dataset list
    dataset = []
    videos = data['videos'][:max_videos]

    for video in videos:
        vid_id  = video['video_id']
        vid_file = os.path.join(videos_folder, f"{vid_id}.mp4")

        if not os.path.exists(vid_file):
            print(f"  Skipping {vid_id} — file not found")
            continue

        captions = caption_map.get(vid_id, [])
        if not captions:
            continue

        dataset.append({
            "video_id":    vid_id,
            "video_path":  vid_file,
            "captions":    captions,
            "reference":   captions[0]  # use first caption as reference
        })

    print(f"Loaded {len(dataset)} videos with captions")
    return dataset


def get_sample_video(dataset):
    """Return a random video from dataset for demo"""
    return random.choice(dataset)


if __name__ == "__main__":
    # Test loader
    dataset = load_dataset(
        json_path="msrvtt/train_val_videodatainfo.json",
        videos_folder="msrvtt/videos",
        max_videos=5
    )
    for item in dataset:
        print(f"Video: {item['video_id']}")
        print(f"Reference: {item['reference']}")
        print()
