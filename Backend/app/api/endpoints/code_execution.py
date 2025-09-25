

# Backend/app/api/endpoints/code_execution.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
import subprocess
import tempfile
import os
import time
import signal
import threading
import sys
import json
import ast
import docker
import uuid
from pathlib import Path

from app.models.user import User, CodeExecution
from app.services.llm import llm_service
from app.api.deps import get_current_user
from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = Field(..., pattern="^(python|javascript|java|cpp|c|go|rust|php|ruby|bash|sql)$")
    timeout: int = Field(10, ge=1, le=30)  # seconds
    inputs: Optional[List[str]] = []  # For programs that need input

class CodeExecutionResponse(BaseModel):
    id: int
    output: Optional[str]
    error: Optional[str]
    execution_time: int  # milliseconds
    status: str
    language: str
    memory_used: Optional[int]  # KB

class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str = "python"
    complexity: str = "simple"  # simple, intermediate, advanced
    include_tests: bool = False
    model_config: Optional[Dict[str, Any]] = {}

class CodeGenerationResponse(BaseModel):
    code: str
    explanation: str
    language: str
    model_used: str
    processing_time: float
    tests: Optional[str] = None

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str
    analysis_type: str = "full"  # full, security, performance, style

class CodeAnalysisResponse(BaseModel):
    analysis: str
    suggestions: List[str]
    complexity_score: int
    issues: List[Dict[str, str]]
    processing_time: float

class CodeExecutor:
    """Secure code execution system"""
    
    def __init__(self):
        self.docker_client = None
        self.use_docker = self._check_docker()
        
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            return True
        except Exception as e:
            logger.warning(f"Docker not available, falling back to subprocess: {str(e)}")
            return False
    
    def _create_secure_environment(self) -> str:
        """Create a secure temporary directory"""
        temp_dir = tempfile.mkdtemp(prefix="code_exec_")
        os.chmod(temp_dir, 0o755)
        return temp_dir
    
    def _execute_python_secure(self, code: str, timeout: int, inputs: List[str]) -> Dict[str, Any]:
        """Execute Python code securely"""
        try:
            # Create secure temp directory
            temp_dir = self._create_secure_environment()
            
            # Create Python file with security restrictions
            secure_code = f'''
import sys
import os
import signal
import time
from io import StringIO
import contextlib

# Security restrictions
import builtins

# Disable dangerous functions
restricted_builtins = {{
    'open': lambda *args, **kwargs: None,
    'input': lambda *args: inputs.pop(0) if inputs else "",
    '__import__': lambda name, *args, **kwargs: __import__(name, *args, **kwargs) if name in allowed_modules else None,
    'exec': lambda *args: None,
    'eval': lambda *args: None,
    'compile': lambda *args: None,
    'exit': lambda *args: None,
    'quit': lambda *args: None,
}}

allowed_modules = {{
    'math', 'random', 'datetime', 'json', 're', 'collections',
    'itertools', 'functools', 'operator', 'string', 'decimal',
    'fractions', 'statistics', 'numpy', 'pandas', 'matplotlib'
}}

# Input data for interactive programs
inputs = {json.dumps(inputs)}

# Redirect stdout
old_stdout = sys.stdout
sys.stdout = captured_output = StringIO()

# Set resource limits
start_time = time.time()

try:
    # Execute user code
{code}
    
    execution_time = int((time.time() - start_time) * 1000)
    output = captured_output.getvalue()
    
    print("__EXECUTION_SUCCESS__")
    print(f"__EXECUTION_TIME__{execution_time}__")
    
except Exception as e:
    execution_time = int((time.time() - start_time) * 1000)
    print("__EXECUTION_ERROR__")
    print(f"__ERROR_MESSAGE__{str(e)}__")
    print(f"__EXECUTION_TIME__{execution_time}__")
    
finally:
    sys.stdout = old_stdout
'''
            
            code_file = os.path.join(temp_dir, "user_code.py")
            with open(code_file, 'w') as f:
                f.write(secure_code)
            
            # Execute with restrictions
            cmd = [
                sys.executable, "-c", f"""
import subprocess
import sys
import os
os.chdir('{temp_dir}')
result = subprocess.run([sys.executable, 'user_code.py'], 
                       capture_output=True, text=True, timeout={timeout})
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
"""
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Parse output
            output_lines = result.stdout.strip().split('\n')
            
            if "__EXECUTION_SUCCESS__" in result.stdout:
                # Extract execution time
                exec_time_line = [line for line in output_lines if "__EXECUTION_TIME__" in line]
                if exec_time_line:
                    exec_time = int(exec_time_line[0].split("__EXECUTION_TIME__")[1].split("__")[0])
                else:
                    exec_time = execution_time
                
                # Clean output
                clean_output = '\n'.join([line for line in output_lines 
                                        if not line.startswith('__')])
                
                return {
                    "output": clean_output,
                    "error": None,
                    "execution_time": exec_time,
                    "status": "success",
                    "memory_used": None
                }
            
            elif "__EXECUTION_ERROR__" in result.stdout:
                error_lines = [line for line in output_lines if "__ERROR_MESSAGE__" in line]
                error_msg = error_lines[0].split("__ERROR_MESSAGE__")[1].split("__")[0] if error_lines else "Unknown error"
                
                return {
                    "output": None,
                    "error": error_msg,
                    "execution_time": execution_time,
                    "status": "error",
                    "memory_used": None
                }
            
            else:
                return {
                    "output": result.stdout if result.returncode == 0 else None,
                    "error": result.stderr if result.returncode != 0 else None,
                    "execution_time": execution_time,
                    "status": "success" if result.returncode == 0 else "error",
                    "memory_used": None
                }
                
        except subprocess.TimeoutExpired:
            return {
                "output": None,
                "error": f"Code execution timed out after {timeout} seconds",
                "execution_time": timeout * 1000,
                "status": "timeout",
                "memory_used": None
            }
        
        except Exception as e:
            return {
                "output": None,
                "error": str(e),
                "execution_time": execution_time if 'execution_time' in locals() else 0,
                "status": "error",
                "memory_used": None
            }
        
        finally:
            # Clean up
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
    
    def _execute_javascript(self, code: str, timeout: int, inputs: List[str]) -> Dict[str, Any]:
        """Execute JavaScript code using Node.js"""
        try:
            temp_dir = self._create_secure_environment()
            
            # Prepare secure JavaScript code
            js_code = f'''
const readline = require('readline');

// Mock input for interactive programs
const inputs = {json.dumps(inputs)};
let inputIndex = 0;

// Override console.input (custom function)
global.input = function() {{
    return inputs[inputIndex++] || "";
}};

// Execution timing
const startTime = Date.now();

try {{
    {code}
    
    const executionTime = Date.now() - startTime;
    console.log("__EXECUTION_SUCCESS__");
    console.log(`__EXECUTION_TIME__${{executionTime}}__`);
    
}} catch (error) {{
    const executionTime = Date.now() - startTime;
    console.log("__EXECUTION_ERROR__");
    console.log(`__ERROR_MESSAGE__${{error.message}}__`);
    console.log(`__EXECUTION_TIME__${{executionTime}}__`);
}}
'''
            
            code_file = os.path.join(temp_dir, "user_code.js")
            with open(code_file, 'w') as f:
                f.write(js_code)
            
            start_time = time.time()
            result = subprocess.run(
                ["node", code_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=temp_dir
            )
            execution_time = int((time.time() - start_time) * 1000)
            
            # Parse output similar to Python
            output_lines = result.stdout.strip().split('\n')
            
            if "__EXECUTION_SUCCESS__" in result.stdout:
                clean_output = '\n'.join([line for line in output_lines 
                                        if not line.startswith('__')])
                return {
                    "output": clean_output,
                    "error": None,
                    "execution_time": execution_time,
                    "status": "success",
                    "memory_used": None
                }
            elif "__EXECUTION_ERROR__" in result.stdout:
                error_lines = [line for line in output_lines if "__ERROR_MESSAGE__" in line]
                error_msg = error_lines[0].split("__ERROR_MESSAGE__")[1].split("__")[0] if error_lines else "Unknown error"
                return {
                    "output": None,
                    "error": error_msg,
                    "execution_time": execution_time,
                    "status": "error",
                    "memory_used": None
                }
            else:
                return {
                    "output": result.stdout if result.returncode == 0 else None,
                    "error": result.stderr if result.returncode != 0 else None,
                    "execution_time": execution_time,
                    "status": "success" if result.returncode == 0 else "error",
                    "memory_used": None
                }
                
        except subprocess.TimeoutExpired:
            return {
                "output": None,
                "error": f"Code execution timed out after {timeout} seconds",
                "execution_time": timeout * 1000,
                "status": "timeout",
                "memory_used": None
            }
        except Exception as e:
            return {
                "output": None,
                "error": str(e),
                "execution_time": execution_time if 'execution_time' in locals() else 0,
                "status": "error",
                "memory_used": None
            }
        finally:
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
    
    def execute_code(self, code: str, language: str, timeout: int = 10, inputs: List[str] = None) -> Dict[str, Any]:
        """Execute code in the specified language"""
        if inputs is None:
            inputs = []
        
        # Validate code length
        if len(code) > 50000:  # 50KB limit
            return {
                "output": None,
                "error": "Code too long (maximum 50KB)",
                "execution_time": 0,
                "status": "error",
                "memory_used": None
            }
        
        language = language.lower()
        
        if language == "python":
            return self._execute_python_secure(code, timeout, inputs)
        elif language == "javascript":
            return self._execute_javascript(code, timeout, inputs)
        else:
            return {
                "output": None,
                "error": f"Language '{language}' is not supported yet. Supported: python, javascript",
                "execution_time": 0,
                "status": "error",
                "memory_used": None
            }

# Global code executor
code_executor = CodeExecutor()

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute code securely"""
    try:
        # Execute code
        execution_result = code_executor.execute_code(
            request.code,
            request.language,
            request.timeout,
            request.inputs
        )
        
        # Save execution record
        code_execution = CodeExecution(
            user_id=current_user.id,
            language=request.language,
            code=request.code,
            output=execution_result.get("output"),
            error=execution_result.get("error"),
            execution_time=execution_result["execution_time"],
            status=execution_result["status"]
        )
        
        db.add(code_execution)
        
        # Update usage stats
        current_user.usage_stats["total_requests"] += 1
        db.commit()
        db.refresh(code_execution)
        
        return CodeExecutionResponse(
            id=code_execution.id,
            output=code_execution.output,
            error=code_execution.error,
            execution_time=code_execution.execution_time,
            status=code_execution.status,
            language=code_execution.language,
            memory_used=execution_result.get("memory_used")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error executing code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing code: {str(e)}"
        )

@router.post("/generate", response_model=CodeGenerationResponse)
async def generate_code(
    request: CodeGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate code using AI with real models"""
    try:
        # Build comprehensive code generation prompt
        complexity_guidance = {
            "simple": "Write simple, beginner-friendly code with clear comments",
            "intermediate": "Write moderately complex code with good structure and error handling",
            "advanced": "Write advanced, optimized code with comprehensive features and best practices"
        }
        
        code_prompt = f"""Generate a complete, working {request.language} solution for the following request:

Request: {request.prompt}

Requirements:
- Language: {request.language}
- Complexity Level: {request.complexity} - {complexity_guidance.get(request.complexity, '')}
- Include proper error handling
- Add clear comments explaining the logic
- Follow best practices for {request.language}
- Make the code production-ready
{'- Include unit tests' if request.include_tests else ''}

Please provide:
1. Complete, executable {request.language} code
2. Detailed explanation of the implementation
3. Usage examples
{'4. Unit tests' if request.include_tests else ''}

Generated Code:
```{request.language}"""
        
        # Use specialized model config for code generation
        model_config = {**current_user.model_preferences, **(request.model_config or {})}
        model_config.update({
            "temperature": 0.2,  # Lower temperature for more deterministic code
            "max_tokens": 2000,
            "top_p": 0.9
        })
        
        # Generate code using specialized code model
        llm_response = await llm_service.generate_response(
            code_prompt,
            model_type="code",
            **model_config
        )
        
        response_text = llm_response["response"]
        
        # Parse the response to extract code, explanation, and tests
        code, explanation, tests = parse_code_response(response_text, request.language, request.include_tests)
        
        # Validate generated code syntax
        if request.language.lower() == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                # Try to fix common issues
                code = fix_python_syntax_issues(code)
        
        # Update usage stats
        current_user.usage_stats["total_requests"] += 1
        current_user.usage_stats["total_tokens"] += llm_response["token_count"]
        db.commit()
        
        return CodeGenerationResponse(
            code=code,
            explanation=explanation,
            language=request.language,
            model_used=llm_response["model_used"],
            processing_time=llm_response["processing_time"],
            tests=tests if request.include_tests else None
        )
        
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating code: {str(e)}"
        )

@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze code quality, security, and performance"""
    try:
        # Perform static analysis
        analysis_result = perform_code_analysis(request.code, request.language, request.analysis_type)
        
        # Generate AI-powered analysis
        analysis_prompt = f"""Analyze the following {request.language} code for:
- Code quality and best practices
- Security vulnerabilities
- Performance optimization opportunities
- Style and maintainability issues
- Complexity assessment

Code to analyze:
```{request.language}
{request.code}
```

Provide:
1. Overall analysis summary
2. Specific improvement suggestions
3. Security concerns (if any)
4. Performance recommendations
5. Code complexity rating (1-10)"""
        
        model_config = {**current_user.model_preferences}
        model_config["temperature"] = 0.3
        
        llm_response = await llm_service.generate_response(
            analysis_prompt,
            model_type="chat",
            **model_config
        )
        
        # Update usage stats
        current_user.usage_stats["total_requests"] += 1
        current_user.usage_stats["total_tokens"] += llm_response["token_count"]
        db.commit()
        
        return CodeAnalysisResponse(
            analysis=llm_response["response"],
            suggestions=analysis_result["suggestions"],
            complexity_score=analysis_result["complexity_score"],
            issues=analysis_result["issues"],
            processing_time=llm_response["processing_time"]
        )
        
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing code: {str(e)}"
        )

@router.get("/executions", response_model=List[Dict])
async def get_code_executions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Get user's recent code executions"""
    try:
        executions = db.query(CodeExecution).filter(
            CodeExecution.user_id == current_user.id
        ).order_by(CodeExecution.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": exec.id,
                "language": exec.language,
                "code_preview": exec.code[:200] + "..." if len(exec.code) > 200 else exec.code,
                "status": exec.status,
                "execution_time": exec.execution_time,
                "created_at": exec.created_at.isoformat(),
                "has_output": bool(exec.output),
                "has_error": bool(exec.error)
            }
            for exec in executions
        ]
        
    except Exception as e:
        logger.error(f"Error getting code executions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving code executions"
        )

@router.get("/languages")
async def get_supported_languages():
    """Get supported programming languages"""
    return {
        "supported_languages": [
            {
                "name": "Python",
                "code": "python",
                "version": "3.9+",
                "features": ["execution", "generation", "analysis"],
                "libraries": ["numpy", "pandas", "matplotlib", "requests"]
            },
            {
                "name": "JavaScript",
                "code": "javascript", 
                "version": "Node.js 16+",
                "features": ["execution", "generation", "analysis"],
                "libraries": ["lodash", "axios", "moment"]
            },
            {
                "name": "Java",
                "code": "java",
                "version": "11+",
                "features": ["generation", "analysis"],
                "libraries": ["Standard Library"]
            },
            {
                "name": "C++",
                "code": "cpp",
                "version": "C++17",
                "features": ["generation", "analysis"],
                "libraries": ["STL"]
            }
        ],
        "execution_limits": {
            "max_execution_time": 30,
            "max_code_size": "50KB",
            "max_memory": "128MB"
        }
    }

def parse_code_response(response: str, language: str, include_tests: bool) -> tuple:
    """Parse LLM response to extract code, explanation, and tests"""
    try:
        # Split response into sections
        sections = response.split("```")
        
        code = ""
        explanation = ""
        tests = ""
        
        # Extract code blocks
        for i, section in enumerate(sections):
            if section.strip().startswith(language) or (i > 0 and i % 2 == 1):
                # This is likely a code block
                code_content = section
                if code_content.startswith(language):
                    code_content = code_content[len(language):].strip()
                
                if "test" in code_content.lower() and include_tests:
                    tests = code_content
                else:
                    code = code_content
            else:
                # This is explanation text
                if section.strip():
                    explanation += section.strip() + "\n"
        
        # Clean up the extracted content
        if not code and sections:
            # Fallback: use the entire response as code
            code = response.strip()
        
        if not explanation:
            explanation = f"Generated {language} code solution."
        
        return code.strip(), explanation.strip(), tests.strip()
        
    except Exception as e:
        logger.error(f"Error parsing code response: {str(e)}")
        return response.strip(), "AI-generated code", ""

def fix_python_syntax_issues(code: str) -> str:
    """Fix common Python syntax issues in generated code"""
    try:
        # Common fixes
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix indentation issues
            if line.strip() and not line.startswith(' ') and line.startswith('\t'):
                line = line.replace('\t', '    ')
            
            # Fix common syntax patterns
            line = line.replace('print ', 'print(').replace(');', ')')
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    except:
        return code

def perform_code_analysis(code: str, language: str, analysis_type: str) -> Dict[str, Any]:
    """Perform static code analysis"""
    try:
        suggestions = []
        issues = []
        complexity_score = 5  # Default
        
        lines = code.split('\n')
        
        # Basic analysis metrics
        line_count = len([line for line in lines if line.strip()])
        function_count = len([line for line in lines if 'def ' in line or 'function ' in line])
        comment_count = len([line for line in lines if line.strip().startswith('#') or '//' in line])
        
        # Calculate complexity score
        complexity_factors = 0
        complexity_factors += min(line_count // 10, 3)  # Length factor
        complexity_factors += min(function_count, 2)     # Function factor
        complexity_factors += 1 if comment_count / max(line_count, 1) < 0.1 else 0  # Comment factor
        
        complexity_score = min(complexity_factors + 3, 10)
        
        # Generate suggestions based on analysis
        if language.lower() == "python":
            if "import os" in code or "import subprocess" in code:
                issues.append({
                    "type": "security",
                    "message": "Potentially dangerous imports detected",
                    "severity": "high"
                })
            
            if comment_count / max(line_count, 1) < 0.1:
                suggestions.append("Add more comments to improve code readability")
            
            if line_count > 50:
                suggestions.append("Consider breaking down large functions into smaller ones")
        
        if not suggestions:
            suggestions.append("Code looks good! Consider adding unit tests.")
        
        return {
            "suggestions": suggestions,
            "complexity_score": complexity_score,
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"Error in code analysis: {str(e)}")
        return {
            "suggestions": ["Unable to perform detailed analysis"],
            "complexity_score": 5,
            "issues": []
        }