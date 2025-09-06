from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64
from io import BytesIO

# Example: Using Stable Diffusion from diffusers
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image

router = APIRouter(
    prefix="/image",
    tags=["image-generation"]
)

# Load your model once at startup (adjust path/model as needed)
try:
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
except Exception as e:
    pipe = None
    print(f"Failed to load Stable Diffusion pipeline: {e}")

class ImageGenRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    num_inference_steps: Optional[int] = 30
    guidance_scale: Optional[float] = 7.5
    width: Optional[int] = 512
    height: Optional[int] = 512

class ImageGenResponse(BaseModel):
    image_base64: str

@router.post("/generate", response_model=ImageGenResponse)
async def generate_image(req: ImageGenRequest):
    if pipe is None:
        raise HTTPException(status_code=503, detail="Image generation model not available.")

    try:
        result = pipe(
            prompt=req.prompt,
            negative_prompt=req.negative_prompt,
            num_inference_steps=req.num_inference_steps,
            guidance_scale=req.guidance_scale,
            width=req.width,
            height=req.height
        )
        image: Image.Image = result.images[0]

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return ImageGenResponse(image_base64=img_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")
    
@router.get("/health")
async def health_check():
    if pipe is None:
        return {"status": "unavailable"}
    return {"status": "ok"}
# Note: Ensure you have the required packages installed:
# pip install fastapi pydantic diffusers transformers torch pillow
# Also, make sure to have the appropriate model files and weights downloaded for Stable Diffusion.
# This is a basic implementation. Depending on your requirements, you might want to add more features like:
# - Caching generated images
# - Rate limiting
# - Authentication
# - Support for different image generation models
# - Error handling for specific cases
# - Logging for monitoring usage and errors
# - Environment variable configuration for model paths and settings
# - Async support if using an async-compatible model or service
# - Unit tests for the endpoint
# - Documentation for the API using OpenAPI/Swagger
# - Integration with a frontend or other services
# - GPU support and optimization for faster inference
# - Support for batch image generation
# - Customizable image formats (e.g., JPEG, PNG)
# - Input validation for prompt length, image dimensions, etc.
# - Monitoring and alerting for service health
# - Deployment considerations (e.g., Docker, Kubernetes)
