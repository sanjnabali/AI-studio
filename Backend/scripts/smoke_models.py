#!/usr/bin/env python3
# Backend/scripts/smoke_models.py
"""
Minimal offline smoke-tests for core AI models to validate environment.
- Chat (DialoGPT)
- Embeddings (SentenceTransformer)
- Whisper STT (optional, small model)
Run: python scripts/smoke_models.py
"""
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer


def test_chat():
    print("[chat] Loading microsoft/DialoGPT-medium...")
    tok = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
    inputs = tok.encode("Hello there!", return_tensors="pt")
    with torch.no_grad():
        out = model.generate(inputs, max_new_tokens=30)
    text = tok.decode(out[0], skip_special_tokens=True)
    print("[chat] OK ->", text[-80:])


def test_embeddings():
    print("[embed] Loading sentence-transformers/all-MiniLM-L6-v2...")
    embed = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    vec = embed.encode(["hello world", "goodbye world"])  # numpy array
    print("[embed] OK -> shape:", getattr(vec, "shape", None))


def main():
    start = time.time()
    test_chat()
    test_embeddings()
    print(f"Done in {time.time()-start:.2f}s")


if __name__ == "__main__":
    main()
