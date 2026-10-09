# VidSense

A Python pipeline that tries to *understand* a video. You give it a video file, and it figures out what is being said, what is shown, and what is happening, then checks how well that description matches a reference caption.

## What it does

The pipeline runs in six steps:

1. **Speech:** turns the spoken audio into text (Whisper).
2. **Visual context:** looks at frames from the video and describes what is on screen (Groq vision model).
3. **Actions:** detects what people or objects are doing (Groq vision model).
4. **Rich transcript:** combines speech, visuals and actions into one detailed description (Groq LLaMA).
5. **Reference caption:** uses the caption you provide, or writes a short one automatically from the rich transcript.
6. **Similarity score:** compares the generated description with the reference caption (SBERT + ROUGE-L) and gives a final score and a label.

## Files

| File | What it is for |
|---|---|
| `pipeline.py` | Runs the whole 6-step pipeline |
| `extractor.py` | Gets speech, visuals and actions from the video |
| `transcript.py` | Builds the rich transcript and video prompt |
| `comparator.py` | Computes the similarity score |
| `videogen.py` | Video generation helper |
| `dataset.py` | Dataset helper |
| `app.py` | App entry point |
| `requirements.txt` | Python packages needed |

## How to run it

```bash
pip install -r requirements.txt
```

Set your Groq API key as an environment variable (never write it inside the code):

```bash
# Windows PowerShell
$env:GROQ_API_KEY = "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"

# Mac / Linux
export GROQ_API_KEY="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"
```

Then run the pipeline on a video:

```bash
python pipeline.py your_video.mp4
```

It prints the speech, the rich transcript, the reference caption, the final score and a label.

## Notes

- You need a free Groq account to get an API key.
- Results depend on the quality of the video and audio.
- This is a student project and still a work in progress.

## What I'd like to add

- Example videos and sample output in this README
- Clear instructions for `app.py`
- More ways to test how accurate the scoring is
