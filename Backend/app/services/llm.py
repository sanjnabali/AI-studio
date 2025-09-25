# Backend/app/services/llm.py
import asyncio
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM,
    pipeline, BertTokenizer, BertForSequenceClassification
)
import torch
from config.settings import settings
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseModel(ABC):
    def __init__(self, model_name: str, device: str = "auto"):
        self.model_name = model_name
        self.device = self._get_device(device)
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
    def _get_device(self, device: str) -> str:
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    @abstractmethod
    async def load_model(self):
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

class ChatModel(BaseModel):
    async def load_model(self):
        try:
            logger.info(f"Loading chat model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            # Add pad token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            logger.info(f"Chat model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading chat model: {str(e)}")
            # Fallback to a smaller model
            self.model_name = "microsoft/DialoGPT-small"
            await self._load_fallback_model()
    
    async def _load_fallback_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        except Exception as e:
            logger.error(f"Fallback model loading failed: {str(e)}")
            raise
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            # Default parameters
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            top_p = kwargs.get('top_p', 0.9)
            top_k = kwargs.get('top_k', 50)
            
            # Encode input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = inputs.cuda()
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=2
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove input prompt from response
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            return response if response else "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I encountered an error while processing your request. Please try again."

class CodeModel(BaseModel):
    async def load_model(self):
        try:
            logger.info(f"Loading code model: {self.model_name}")
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                tokenizer=self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device=0 if self.device == "cuda" else -1
            )
            logger.info("Code model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading code model: {str(e)}")
            # Fallback to a code generation model
            self.model_name = "microsoft/CodeGPT-small-py"
            self.pipeline = pipeline("text-generation", model=self.model_name, device=-1)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            max_tokens = kwargs.get('max_tokens', 500)
            temperature = kwargs.get('temperature', 0.3)  # Lower temp for code
            
            result = self.pipeline(
                prompt,
                max_length=len(prompt.split()) + max_tokens,
                temperature=temperature,
                do_sample=True,
                num_return_sequences=1
            )
            
            generated_text = result[0]['generated_text']
            # Remove the input prompt
            if prompt in generated_text:
                generated_text = generated_text.replace(prompt, "").strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return f"# Error generating code: {str(e)}"

class SummarizerModel(BaseModel):
    async def load_model(self):
        try:
            logger.info(f"Loading summarizer model: {self.model_name}")
            self.pipeline = pipeline(
                "summarization",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if self.device == "cuda" else -1
            )
            logger.info("Summarizer model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading summarizer: {str(e)}")
            # Fallback to a smaller summarizer
            self.model_name = "sshleifer/distilbart-cnn-12-6"
            self.pipeline = pipeline("summarization", model=self.model_name, device=-1)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            max_length = kwargs.get('max_tokens', 150)
            min_length = kwargs.get('min_tokens', 50)
            
            result = self.pipeline(
                prompt,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return result[0]['summary_text']
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"

class LLMService:
    def __init__(self):
        self.models: Dict[str, BaseModel] = {}
        self.model_configs = {
            "chat": ChatModel("microsoft/DialoGPT-medium"),
            "code": CodeModel("microsoft/CodeBERT-base"),
            "summarizer": SummarizerModel("facebook/bart-large-cnn")
        }
        self._loading_lock = asyncio.Lock()
    
    async def get_model(self, model_type: str) -> BaseModel:
        if model_type not in self.models:
            async with self._loading_lock:
                if model_type not in self.models:
                    model = self.model_configs.get(model_type)
                    if not model:
                        raise ValueError(f"Unsupported model type: {model_type}")
                    
                    await model.load_model()
                    self.models[model_type] = model
        
        return self.models[model_type]
    
    async def generate_response(self, 
                              prompt: str, 
                              model_type: str = "chat", 
                              **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            model = await self.get_model(model_type)
            response = await model.generate(prompt, **kwargs)
            
            processing_time = time.time() - start_time
            
            # Estimate token count (rough approximation)
            token_count = len(response.split()) * 1.3
            
            return {
                "response": response,
                "model_used": model.model_name,
                "processing_time": processing_time,
                "token_count": int(token_count)
            }
            
        except Exception as e:
            logger.error(f"Error in generate_response: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "model_used": "error",
                "processing_time": time.time() - start_time,
                "token_count": 0
            }
    
    async def chat_completion(self, 
                            messages: List[Dict[str, str]], 
                            model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a chat completion request with conversation history
        """
        # Build conversation context
        conversation = ""
        for msg in messages[-10:]:  # Keep last 10 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                conversation += f"User: {content}\n"
            elif role == "assistant":
                conversation += f"Assistant: {content}\n"
        
        conversation += "Assistant: "
        
        return await self.generate_response(
            conversation,
            model_type="chat",
            **model_config
        )

# Global service instance
llm_service = LLMService()