"""
Utility helper functions for AI Studio Backend
"""

import os
import re
import json
import hashlib
import uuid
import time
import asyncio
import tempfile
import mimetypes
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
import logging
import subprocess
import shutil

logger = logging.getLogger(__name__)


# Text Processing Helpers
def clean_text(text: str, max_length: Optional[int] = None) -> str:
    """Clean and normalize text input"""
    if not isinstance(text, str):
        return str(text)
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip() + "..."
    
    return text


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown-style text"""
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = []
    for language, code in matches:
        code_blocks.append({
            "language": language.lower() if language else "text",
            "code": code.strip()
        })
    
    return code_blocks


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def count_tokens_approximate(text: str) -> int:
    """Approximate token count (rough estimation)"""
    # Simple approximation: 1 token ≈ 4 characters for English text
    return max(1, len(text) // 4)


def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If we're not at the end, try to break at word boundary
        if end < len(text):
            # Look for word boundary within the last 100 characters
            boundary_search = text[max(start, end - 100):end]
            last_space = boundary_search.rfind(' ')
            
            if last_space > 0:
                end = max(start, end - 100) + last_space
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


# File Helpers
def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase"""
    return Path(filename).suffix.lower()


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)


def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe"""
    if not filename or filename in ['.', '..']:
        return False
    
    # Check for dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    return not any(char in filename for char in dangerous_chars)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s\-_\.]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Remove multiple dots
    filename = re.sub(r'\.+', '.', filename)
    return filename.strip('._')


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def create_temp_file(content: bytes, suffix: str = '') -> str:
    """Create temporary file and return path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(content)
        return temp_file.name


def cleanup_temp_file(file_path: str):
    """Safely cleanup temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {file_path}: {e}")


# Hash and ID Helpers
def generate_id(prefix: str = "id") -> str:
    """Generate unique ID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}_{int(time.time())}"


def hash_content(content: Union[str, bytes]) -> str:
    """Generate hash of content"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


def hash_file(file_path: Union[str, Path]) -> str:
    """Generate hash of file content"""
    hash_obj = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


# JSON Helpers
def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"JSON parsing failed: {e}")
        return default


def safe_json_dumps(obj: Any, default: Any = None) -> str:
    """Safely serialize object to JSON"""
    try:
        return json.dumps(obj, default=str, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as e:
        logger.warning(f"JSON serialization failed: {e}")
        return json.dumps({"error": str(e)})


# Time and Date Helpers
def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"


def parse_timestamp(timestamp: str) -> Optional[datetime]:
    """Parse ISO timestamp"""
    try:
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except ValueError:
        return None


def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def is_recent(timestamp: datetime, minutes: int = 5) -> bool:
    """Check if timestamp is within recent minutes"""
    return datetime.utcnow() - timestamp < timedelta(minutes=minutes)


# System Helpers
def get_system_info() -> Dict[str, Any]:
    """Get basic system information"""
    import platform
    import psutil
    
    try:
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_usage_gb": round(shutil.disk_usage("/").free / (1024**3), 2)
        }
    except Exception as e:
        logger.warning(f"Failed to get system info: {e}")
        return {"error": str(e)}


def check_command_available(command: str) -> bool:
    """Check if command is available in system"""
    try:
        result = subprocess.run([command, "--version"], 
                               capture_output=True, 
                               timeout=5, 
                               text=True)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        return False


def get_available_languages() -> Dict[str, Dict[str, Any]]:
    """Get available programming languages for code execution"""
    languages = {}
    
    # Python
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True, timeout=5)
        languages["python"] = {
            "available": result.returncode == 0,
            "version": result.stdout.strip() if result.returncode == 0 else None,
            "command": "python"
        }
    except:
        languages["python"] = {"available": False, "version": None, "command": "python"}
    
    # Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        languages["javascript"] = {
            "available": result.returncode == 0,
            "version": result.stdout.strip() if result.returncode == 0 else None,
            "command": "node"
        }
    except:
        languages["javascript"] = {"available": False, "version": None, "command": "node"}
    
    # Bash
    try:
        result = subprocess.run(["bash", "--version"], capture_output=True, text=True, timeout=5)
        languages["bash"] = {
            "available": result.returncode == 0,
            "version": result.stdout.split('\n')[0] if result.returncode == 0 else None,
            "command": "bash"
        }
    except:
        languages["bash"] = {"available": False, "version": None, "command": "bash"}
    
    return languages


# Async Helpers
async def run_in_executor(func: Callable, *args, **kwargs) -> Any:
    """Run blocking function in thread executor"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


async def timeout_after(seconds: float, coro):
    """Run coroutine with timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {seconds} seconds")
        raise


def async_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Async retry decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator


# Validation Helpers
def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Basic URL validation"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_json_schema(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """Validate JSON data against required fields"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            missing_fields.append(f"{field} (empty)")
    
    return len(missing_fields) == 0, missing_fields


# Performance Helpers
def measure_time(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} took {elapsed:.3f}s")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} took {elapsed:.3f}s")
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


class PerformanceMonitor:
    """Performance monitoring utility"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a performance metric"""
        timestamp = time.time()
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            "value": value,
            "timestamp": timestamp,
            "tags": tags or {}
        })
        
        # Keep only last 1000 entries per metric
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metric_stats(self, name: str, minutes: int = 60) -> Dict[str, float]:
        """Get statistics for a metric over the last N minutes"""
        if name not in self.metrics:
            return {}
        
        cutoff_time = time.time() - (minutes * 60)
        recent_values = [
            entry["value"] for entry in self.metrics[name]
            if entry["timestamp"] > cutoff_time
        ]
        
        if not recent_values:
            return {}
        
        return {
            "count": len(recent_values),
            "avg": sum(recent_values) / len(recent_values),
            "min": min(recent_values),
            "max": max(recent_values),
            "latest": recent_values[-1]
        }


# Global performance monitor
perf_monitor = PerformanceMonitor()


# Caching Helpers
class SimpleCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.ttl_cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check TTL
        if key in self.ttl_cache:
            if time.time() > self.ttl_cache[key]:
                del self.cache[key]
                del self.ttl_cache[key]
                return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        self.cache[key] = value
        
        if ttl is None:
            ttl = self.default_ttl
        
        if ttl > 0:
            self.ttl_cache[key] = time.time() + ttl
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        deleted = False
        
        if key in self.cache:
            del self.cache[key]
            deleted = True
        
        if key in self.ttl_cache:
            del self.ttl_cache[key]
        
        return deleted
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.ttl_cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        current_time = time.time()
        expired_keys = [
            key for key, expires_at in self.ttl_cache.items()
            if current_time > expires_at
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "total_keys": len(self.cache),
            "expired_keys": self.cleanup_expired(),
            "active_keys": len(self.cache)
        }


# Global cache instance
cache = SimpleCache()


# Response Helpers
def create_response(
    success: bool = True,
    data: Any = None,
    message: str = "",
    error_code: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized API response"""
    response = {
        "success": success,
        "timestamp": get_timestamp()
    }
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    if not success and error_code:
        response["error_code"] = error_code
    
    if metadata:
        response["metadata"] = metadata
    
    return response


def paginate_data(
    data: List[Any], 
    page: int = 1, 
    page_size: int = 20
) -> Dict[str, Any]:
    """Paginate data and return with metadata"""
    total = len(data)
    total_pages = (total + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        "items": data[start_idx:end_idx],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }


# Logging Helpers
def setup_logging(
    level: str = "INFO",
    format_str: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """Setup logging configuration"""
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[
            logging.StreamHandler(),
            *([] if log_file is None else [logging.FileHandler(log_file)])
        ]
    )


def log_request(request_data: Dict[str, Any]) -> None:
    """Log API request details"""
    logger.info("API Request", extra={
        "event_type": "api_request",
        "request_data": request_data
    })


def log_response(response_data: Dict[str, Any], latency_ms: float) -> None:
    """Log API response details"""
    logger.info("API Response", extra={
        "event_type": "api_response", 
        "response_data": response_data,
        "latency_ms": latency_ms
    })


# Security Helpers
def mask_sensitive_data(data: Dict[str, Any], sensitive_keys: List[str]) -> Dict[str, Any]:
    """Mask sensitive data in dictionaries"""
    masked_data = data.copy()
    
    for key in sensitive_keys:
        if key in masked_data:
            if isinstance(masked_data[key], str) and len(masked_data[key]) > 0:
                masked_data[key] = "*" * min(len(masked_data[key]), 8)
            else:
                masked_data[key] = "[MASKED]"
    
    return masked_data


def generate_api_key(prefix: str = "sk", length: int = 32) -> str:
    """Generate API key"""
    import secrets
    return f"{prefix}-{secrets.token_urlsafe(length)}"


# Data Processing Helpers
def flatten_dict(d: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """Flatten nested dictionary"""
    def _flatten(obj, parent_key="", sep=separator):
        items = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(_flatten(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
        return dict(items)
    
    return _flatten(d)


def group_by_key(items: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group list of dictionaries by key"""
    groups = {}
    for item in items:
        group_key = item.get(key, "unknown")
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    return groups


def deduplicate_list(items: List[Any], key_func: Optional[Callable] = None) -> List[Any]:
    """Remove duplicates from list"""
    if key_func is None:
        return list(dict.fromkeys(items))
    
    seen = set()
    result = []
    
    for item in items:
        key = key_func(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    
    return result


# Model Helpers
def format_model_info(model_name: str, model_size: Optional[int] = None) -> Dict[str, Any]:
    """Format model information"""
    return {
        "name": model_name,
        "size_mb": model_size,
        "status": "loaded" if model_size else "unknown",
        "type": "language_model"
    }


def estimate_model_memory(model_name: str) -> int:
    """Estimate model memory usage in MB"""
    size_estimates = {
        "gpt2": 500,
        "microsoft/phi-2": 2800,
        "meta-llama/Llama-2-7b": 14000,
        "meta-llama/Llama-2-13b": 26000,
        "openai/whisper-tiny": 39,
        "openai/whisper-base": 74,
        "openai/whisper-small": 244,
        "runwayml/stable-diffusion-v1-5": 3400
    }
    
    # Default estimate based on name patterns
    model_lower = model_name.lower()
    if "tiny" in model_lower:
        return 100
    elif "small" in model_lower:
        return 500
    elif "base" in model_lower:
        return 1000
    elif "large" in model_lower:
        return 5000
    
    return size_estimates.get(model_name, 1000)


# Code Analysis Helpers
def extract_imports_from_code(code: str, language: str = "python") -> List[str]:
    """Extract import statements from code"""
    imports = []
    
    if language.lower() == "python":
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
    
    elif language.lower() == "javascript":
        # Extract require() and import statements
        require_pattern = r'require\(["\']([^"\']+)["\']\)'
        import_pattern = r'import.*from\s+["\']([^"\']+)["\']'
        
        imports.extend(re.findall(require_pattern, code))
        imports.extend(re.findall(import_pattern, code))
    
    return imports


def count_lines_of_code(code: str) -> Dict[str, int]:
    """Count lines of code statistics"""
    lines = code.split('\n')
    
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith('#') or line.strip().startswith('//'))
    code_lines = total_lines - blank_lines - comment_lines
    
    return {
        "total": total_lines,
        "code": code_lines,
        "blank": blank_lines,
        "comments": comment_lines
    }


# Export all helper functions
__all__ = [
    # Text processing
    "clean_text", "extract_code_blocks", "truncate_text", "count_tokens_approximate", 
    "split_text_into_chunks",
    
    # File helpers
    "get_file_extension", "get_file_size_mb", "is_safe_filename", "sanitize_filename",
    "get_mime_type", "create_temp_file", "cleanup_temp_file",
    
    # Hash and ID
    "generate_id", "hash_content", "hash_file",
    
    # JSON helpers
    "safe_json_loads", "safe_json_dumps",
    
    # Time helpers
    "get_timestamp", "parse_timestamp", "format_duration", "is_recent",
    
    # System helpers
    "get_system_info", "check_command_available", "get_available_languages",
    
    # Async helpers
    "run_in_executor", "timeout_after", "async_retry",
    
    # Validation
    "is_valid_email", "is_valid_url", "validate_json_schema",
    
    # Performance
    "measure_time", "PerformanceMonitor", "perf_monitor",
    
    # Caching
    "SimpleCache", "cache",
    
    # Response helpers
    "create_response", "paginate_data",
    
    # Logging
    "setup_logging", "log_request", "log_response",
    
    # Security
    "mask_sensitive_data", "generate_api_key",
    
    # Data processing
    "flatten_dict", "group_by_key", "deduplicate_list",
    
    # Model helpers
    "format_model_info", "estimate_model_memory",
    
    # Code analysis
    "extract_imports_from_code", "count_lines_of_code"
]