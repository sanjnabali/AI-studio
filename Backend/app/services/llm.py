from gpt4all import GPT4All
import time

# System prompts for different domains
DOMAIN_PROMPTS = {
    "general": "You are a helpful AI assistant.",
    "code": "You are an expert Python programmer. Provide clear, runnable code.",
    "marketing": "You are a creative marketing expert. Provide concise suggestions.",
    "summarizer": "You summarize text clearly and concisely."
}

class LocalLLMService:
    def __init__(self, model_path="backend/models/ggml-gpt4all-j-v1.3-groovy.bin"):
        """
        model_path: path to local GPT4All model
        """
        self.model = GPT4All(model_path)

    def chat(self, messages, temperature=0.7, top_k=40, top_p=0.95, domain="general", max_tokens=200):
        """
        messages: list of dicts [{"role":..., "content":...}]
        """
        start_time = time.time()
        system_prompt = DOMAIN_PROMPTS.get(domain, DOMAIN_PROMPTS["general"])
        prompt = f"System: {system_prompt}\n"
        for m in messages:
            prompt += f"{m['role'].capitalize()}: {m['content']}\n"
        prompt += "Assistant: "

        output = self.model.generate(
            prompt,
            temp=temperature,
            top_k=top_k,
            top_p=top_p,
            max_tokens=max_tokens
        )

        latency = (time.time() - start_time) * 1000
        return output.strip(), latency
