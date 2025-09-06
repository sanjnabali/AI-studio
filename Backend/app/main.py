

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
    CLIPProcessor,
    CLIPModel,
)
import torch
from PIL import Image
import io
import tempfile

app = FastAPI()

# Configurations
MODEL_NAME = "microsoft/phi-3-mini-128k-instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load main LLM (text/code generation)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
    device_map="auto"
)

# Load CLIP for vision tasks
CLIP_MODEL = "openai/clip-vit-base-patch16"
clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL)
clip_model = CLIPModel.from_pretrained(CLIP_MODEL).to(DEVICE)

# Load Whisper for speech-to-text
whisper_pipe = pipeline("automatic-speech-recognition", model="openai/whisper-tiny.en", device=0 if DEVICE=="cuda" else -1)


@app.get("/")
def root():
    return {"message": "Welcome to Multimodal AI Studio Backend!"}


@app.post("/completion")
async def completion(payload: dict):
    prompt = payload.get("prompt")
    max_new_tokens = int(payload.get("max_new_tokens", 100))
    temperature = float(payload.get("temperature", 0.6))

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt missing.")

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(DEVICE)
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
        )
    response = tokenizer.decode(output[0][input_ids.shape[-1]:], skip_special_tokens=True)
    return JSONResponse({"result": response})


@app.post("/image2text/")
async def image_to_text(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        texts = ["a photo", "a diagram", "a cat", "a person", "a landscape"]

        inputs = clip_processor(text=texts, images=image, return_tensors="pt", padding=True)
        for k in inputs:
            inputs[k] = inputs[k].to(DEVICE)

        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=-1)
        best_idx = torch.argmax(probs)

        return {
            "label": texts[best_idx],
            "confidence": probs[0][best_idx].item(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing error: {e}")


@app.post("/speech2text/")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        # Save to a temporary file for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            result = whisper_pipe(tmp.name)

        return {"transcription": result["text"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Speech-to-text error: {e}")
