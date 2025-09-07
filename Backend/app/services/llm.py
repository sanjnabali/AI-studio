import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import time
import logging
from typing import List, Dict, Optional, Any
from peft import PeftModel, LoraConfig, get_peft_model, TaskType
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    max_new_tokens: int = 200
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    do_sample: bool = True

class LocalLLMService:
    """Enhanced local LLM service with fine-tuning support"""
    
    def __init__(self, model_name: str = "microsoft/phi-2"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.fine_tuned_adapters = {}
        
        # Domain-specific system prompts
        self.domain_prompts = {
            "general": "You are a helpful AI assistant that provides accurate and concise responses.",
            "code": """You are an expert programmer with deep knowledge of multiple programming languages. 
Provide clean, efficient, and well-documented code. Always include explanations and best practices.""",
            "creative": """You are a creative writer with expertise in storytelling, poetry, and creative content. 
Write engaging, imaginative, and well-structured content.""",
            "analysis": """You are a data analyst and researcher. Provide clear, structured analysis with 
actionable insights. Use logical reasoning and evidence-based conclusions.""",
            "summarizer": """You are an expert at summarization. Create concise, accurate summaries that 
capture the key points and essential information.""",
            "marketing": """You are a marketing expert with knowledge of copywriting, branding, and 
customer engagement. Create compelling, persuasive content that resonates with target audiences."""
        }
    
    async def initialize(self):
        """Load tokenizer and model asynchronously"""
        if self.initialized:
            return
        logger.info(f"Initializing model '{self.model_name}' on {self.device}...")

        try:
            # Tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, trust_remote_code=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Quantization for GPU
            quantization_config = None
            if self.device == "cuda":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16
                )

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                quantization_config=quantization_config,
                trust_remote_code=True
            )
            self.initialized = True
            logger.info(f"Model loaded successfully on {self.device}.")

        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise
    
    def prepare_prompt(self, messages: List[Dict], domain: str = "general") -> str:
        """Prepare formatted prompt from messages"""
        system_prompt = self.domain_prompts.get(domain, self.domain_prompts["general"])
        
        # Build conversation history
        prompt_parts = [f"System: {system_prompt}"]
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                continue  # Already added system prompt
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    async def chat(self, 
                   messages: List[Dict], 
                   temperature: float = 0.7,
                   top_k: int = 50,
                   top_p: float = 0.9,
                   domain: str = "general",
                   max_tokens: int = 200,
                   adapter_name: Optional[str] = None) -> tuple[str, float]:
        """Generate chat response with fine-tuning support"""
        
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized. Call initialize() first.")
        
        try:
            start_time = time.time()
            
            # Switch to fine-tuned adapter if specified
            current_model = self.model
            if adapter_name and adapter_name in self.fine_tuned_adapters:
                logger.info(f"Using fine-tuned adapter: {adapter_name}")
                current_model = self.fine_tuned_adapters[adapter_name]
            
            # Prepare prompt
            prompt = self.prepare_prompt(messages, domain)
            
            # Tokenize
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncate=True, 
                max_length=1024
            )
            
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            generation_config = GenerationConfig(
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            )
            
            with torch.no_grad():
                outputs = current_model.generate(
                    **inputs,
                    max_new_tokens=generation_config.max_new_tokens,
                    temperature=generation_config.temperature,
                    top_p=generation_config.top_p,
                    top_k=generation_config.top_k,
                    repetition_penalty=generation_config.repetition_penalty,
                    do_sample=generation_config.do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response_text = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[-1]:],
                skip_special_tokens=True
            ).strip()
            
            latency = (time.time() - start_time) * 1000
            
            return response_text, latency
            
        except Exception as e:
            logger.error(f"Chat generation error: {e}")
            raise
    
    async def fine_tune_lora(self, 
                           training_data: List[Dict],
                           adapter_name: str,
                           lora_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Fine-tune the model using LoRA"""
        
        if not self.model or not self.tokenizer:
            raise ValueError("Base model not loaded")
        
        logger.info(f"Starting LoRA fine-tuning for adapter: {adapter_name}")
        
        try:
            # Default LoRA configuration
            if lora_config is None:
                lora_config = {
                    "r": 16,
                    "lora_alpha": 32,
                    "lora_dropout": 0.1,
                    "bias": "none",
                    "task_type": TaskType.CAUSAL_LM,
                    "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"]
                }
            
            # Create LoRA model
            peft_config = LoraConfig(**lora_config)
            peft_model = get_peft_model(self.model, peft_config)
            
            # Prepare training data
            train_texts = []
            for item in training_data:
                if isinstance(item, dict):
                    # Format as conversation
                    messages = item.get("messages", [])
                    domain = item.get("domain", "general")
                    text = self.prepare_prompt(messages, domain)
                    train_texts.append(text)
                else:
                    train_texts.append(str(item))
            
            # Simple training loop (in production, use proper training framework)
            peft_model.train()
            optimizer = torch.optim.AdamW(peft_model.parameters(), lr=1e-4)
            
            total_loss = 0
            num_batches = 0
            
            for text in train_texts:
                # Tokenize
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncate=True,
                    max_length=512,
                    padding=True
                )
                
                if self.device == "cuda":
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Forward pass
                outputs = peft_model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                num_batches += 1
            
            # Save the fine-tuned adapter
            self.fine_tuned_adapters[adapter_name] = peft_model
            
            avg_loss = total_loss / num_batches if num_batches > 0 else 0
            
            logger.info(f"LoRA fine-tuning completed. Average loss: {avg_loss:.4f}")
            
            return {
                "adapter_name": adapter_name,
                "status": "completed",
                "average_loss": avg_loss,
                "num_examples": len(training_data),
                "lora_config": lora_config
            }
            
        except Exception as e:
            logger.error(f"Fine-tuning error: {e}")
            raise
    
    def get_available_adapters(self) -> List[str]:
        """Get list of available fine-tuned adapters"""
        return list(self.fine_tuned_adapters.keys())
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if not self.model:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_name": self.model_name,
            "device": self.device,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "available_adapters": self.get_available_adapters(),
            "supported_domains": list(self.domain_prompts.keys()),
            "memory_usage": {
                "allocated_mb": torch.cuda.memory_allocated() / 1024**2 if torch.cuda.is_available() else 0,
                "reserved_mb": torch.cuda.memory_reserved() / 1024**2 if torch.cuda.is_available() else 0
            } if torch.cuda.is_available() else {}
        }
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up LLM service...")
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.model = None
        self.tokenizer = None
        self.fine_tuned_adapters.clear()

# Global instance
llm_service = LocalLLMService()