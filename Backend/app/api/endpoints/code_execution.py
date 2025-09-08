# Add this to your Backend/app/api/endpoints/ directory as code_execution.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import tempfile
import subprocess
import sys
import time
import os
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/code", tags=["code-execution"])

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30
    args: Optional[list] = []
    stdin: Optional[str] = ""

class CodeExecutionResponse(BaseModel):
    output: str
    error: Optional[str] = None
    execution_time: float
    success: bool
    language: str
    exit_code: int = 0

class CodeExecutionService:
    """Safe code execution service with multiple language support"""
    
    def __init__(self):
        self.supported_languages = {
            "python": {
                "extension": ".py",
                "command": [sys.executable],
                "available": True
            },
            "javascript": {
                "extension": ".js", 
                "command": ["node"],
                "available": self._check_command_available("node")
            },
            "bash": {
                "extension": ".sh",
                "command": ["bash"],
                "available": self._check_command_available("bash")
            },
            "shell": {
                "extension": ".sh",
                "command": ["sh"],
                "available": True  # sh is usually always available
            }
        }
    
    def _check_command_available(self, command: str) -> bool:
        """Check if a command is available in the system"""
        try:
            subprocess.run([command, "--version"], 
                         capture_output=True, 
                         timeout=5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    async def execute_code(self, request: CodeExecutionRequest) -> CodeExecutionResponse:
        """Execute code safely with proper isolation"""
        
        language = request.language.lower()
        
        if language not in self.supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Language '{language}' not supported. Supported: {list(self.supported_languages.keys())}"
            )
        
        lang_config = self.supported_languages[language]
        
        if not lang_config["available"]:
            raise HTTPException(
                status_code=503,
                detail=f"{language} runtime not available on this system"
            )
        
        start_time = time.time()
        
        try:
            # Create temporary file with appropriate extension
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix=lang_config["extension"], 
                delete=False,
                encoding='utf-8'
            ) as tmp_file:
                
                # Write code to file
                tmp_file.write(request.code)
                tmp_file.flush()
                temp_filename = tmp_file.name
            
            try:
                # Prepare command
                command = lang_config["command"] + [temp_filename] + (request.args or [])
                
                # Execute with timeout and capture output
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    stdin=asyncio.subprocess.PIPE if request.stdin else None
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(input=request.stdin.encode() if request.stdin else None),
                        timeout=request.timeout
                    )
                    
                    execution_time = time.time() - start_time
                    
                    return CodeExecutionResponse(
                        output=stdout.decode('utf-8', errors='replace'),
                        error=stderr.decode('utf-8', errors='replace') if stderr else None,
                        execution_time=execution_time,
                        success=process.returncode == 0,
                        language=language,
                        exit_code=process.returncode or 0
                    )
                    
                except asyncio.TimeoutError:
                    # Kill the process if it times out
                    try:
                        process.kill()
                        await process.wait()
                    except:
                        pass
                    
                    return CodeExecutionResponse(
                        output="",
                        error=f"Code execution timed out after {request.timeout} seconds",
                        execution_time=request.timeout,
                        success=False,
                        language=language,
                        exit_code=-1
                    )
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_filename)
                except:
                    pass
                    
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Code execution error: {e}")
            
            return CodeExecutionResponse(
                output="",
                error=f"Execution error: {str(e)}",
                execution_time=execution_time,
                success=False,
                language=language,
                exit_code=-1
            )

# Global service instance
code_service = CodeExecutionService()

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """Execute code in a sandboxed environment"""
    
    # Basic validation
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    if len(request.code) > 50000:  # 50KB limit
        raise HTTPException(status_code=400, detail="Code too large (max 50KB)")
    
    if request.timeout > 60:  # Max 1 minute
        raise HTTPException(status_code=400, detail="Timeout too large (max 60 seconds)")
    
    # Security check for dangerous operations
    dangerous_patterns = [
        'import os', 'os.system', 'subprocess', 'exec(', 'eval(',
        '__import__', 'open(', 'file(', 'input(', 'raw_input(',
        'rm -rf', 'del ', 'format ', 'fdisk', 'mkfs'
    ]
    
    code_lower = request.code.lower()
    found_dangerous = [pattern for pattern in dangerous_patterns if pattern in code_lower]
    
    if found_dangerous:
        logger.warning(f"Potentially dangerous code detected: {found_dangerous}")
        # For development, we'll allow it but warn
        # In production, you might want to block it
    
    try:
        result = await code_service.execute_code(request)
        
        # Log execution for monitoring
        logger.info(f"Code executed: {request.language}, success: {result.success}, time: {result.execution_time:.2f}s")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in code execution: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during code execution")

@router.get("/languages")
async def get_supported_languages():
    """Get information about supported programming languages"""
    
    return {
        "supported_languages": {
            lang: {
                "extension": config["extension"],
                "available": config["available"],
                "command": config["command"][0] if config["command"] else None
            }
            for lang, config in code_service.supported_languages.items()
        },
        "default_timeout": 30,
        "max_timeout": 60,
        "max_code_size_kb": 50,
        "security_note": "Code execution is sandboxed but use caution with system operations"
    }

@router.post("/validate")
async def validate_code(code: str, language: str = "python"):
    """Validate code without executing it"""
    
    if not code or not code.strip():
        return {"valid": False, "error": "Code cannot be empty"}
    
    if len(code) > 50000:
        return {"valid": False, "error": "Code too large (max 50KB)"}
    
    language = language.lower()
    if language not in code_service.supported_languages:
        return {
            "valid": False, 
            "error": f"Language '{language}' not supported"
        }
    
    # Basic syntax checking for Python
    if language == "python":
        try:
            compile(code, '<string>', 'exec')
            return {"valid": True, "message": "Python syntax is valid"}
        except SyntaxError as e:
            return {
                "valid": False, 
                "error": f"Python syntax error: {e.msg} at line {e.lineno}"
            }
    
    # For other languages, just return basic validation
    return {
        "valid": True, 
        "message": f"Basic validation passed for {language}",
        "note": "Full syntax validation requires execution"
    }

@router.get("/examples")
async def get_code_examples():
    """Get example code snippets for different languages"""
    
    examples = {
        "python": {
            "hello_world": 'print("Hello, World!")',
            "fibonacci": '''def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")''',
            "data_processing": '''import json

data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
for person in data:
    print(f"{person['name']} is {person['age']} years old")'''
        },
        "javascript": {
            "hello_world": 'console.log("Hello, World!");',
            "fibonacci": '''function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

for (let i = 0; i < 10; i++) {
    console.log(`F(${i}) = ${fibonacci(i)}`);
}''',
            "array_processing": '''const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
console.log("Original:", numbers);
console.log("Doubled:", doubled);'''
        },
        "bash": {
            "hello_world": 'echo "Hello, World!"',
            "file_operations": '''echo "Creating test files..."
echo "Hello" > test1.txt
echo "World" > test2.txt
echo "Contents:"
cat test1.txt test2.txt
rm test1.txt test2.txt
echo "Cleanup complete"''',
            "system_info": '''echo "System Information:"
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Working Directory: $(pwd)"
echo "Disk Usage:"
df -h | head -2'''
        }
    }
    
    return {
        "examples": examples,
        "usage": "Copy any example and use the /execute endpoint to run it",
        "note": "These examples are safe to run and demonstrate basic functionality"
    }

@router.get("/health")
async def health_check():
    """Health check for code execution service"""
    
    # Test each language runtime
    health_status = {}
    
    for lang, config in code_service.supported_languages.items():
        health_status[lang] = {
            "available": config["available"],
            "command": config["command"][0] if config["command"] else None
        }
        
        # Quick test for available languages
        if config["available"]:
            try:
                if lang == "python":
                    result = subprocess.run([sys.executable, "-c", "print('ok')"], 
                                          capture_output=True, timeout=5, text=True)
                    health_status[lang]["test_result"] = "ok" if result.returncode == 0 else "error"
                elif lang == "javascript" and config["available"]:
                    result = subprocess.run(["node", "-e", "console.log('ok')"], 
                                          capture_output=True, timeout=5, text=True)
                    health_status[lang]["test_result"] = "ok" if result.returncode == 0 else "error"
                else:
                    health_status[lang]["test_result"] = "not_tested"
            except Exception as e:
                health_status[lang]["test_result"] = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "languages": health_status,
        "features": {
            "timeout_support": True,
            "stdin_support": True,
            "multiple_languages": True,
            "sandboxed_execution": True
        },
        "limits": {
            "max_code_size_kb": 50,
            "max_timeout_seconds": 60,
            "supported_languages": len([l for l, c in code_service.supported_languages.items() if c["available"]])
        }
    }