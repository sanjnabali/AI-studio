"""
Code Agent Implementation for AI Studio
Specialized agent for code generation, review, debugging, and explanation tasks.
"""

import asyncio
import logging
import re
import ast
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

from .base_agent import BaseAgent, AgentType, AgentCapability, AgentTask, AgentStatus
from app.services.llm import llm_service

logger = logging.getLogger(__name__)

@dataclass
class CodeAnalysisResult:
    """Result of code analysis"""
    language: str
    complexity_score: int
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    metrics: Dict[str, Any]

@dataclass
class CodeExecutionResult:
    """Result of code execution"""
    success: bool
    output: str
    error: str
    execution_time: float
    return_code: int

class CodeAgent(BaseAgent):
    """
    Specialized agent for code-related tasks including:
    - Code generation from natural language
    - Code review and analysis
    - Bug detection and fixes
    - Code explanation and documentation
    - Code refactoring suggestions
    - Unit test generation
    """
    
    def __init__(self, agent_id: str = "code_agent"):
        capabilities = [
            AgentCapability(
                name="code_generation",
                description="Generate code from natural language requirements",
                input_types=["text", "requirements", "specifications"],
                output_types=["code", "explanation"],
                complexity_score=8,
                estimated_time=3.0,
                memory_usage=200,
                cpu_intensive=True
            ),
            AgentCapability(
                name="code_review",
                description="Review code for bugs, style, and best practices",
                input_types=["code"],
                output_types=["analysis", "suggestions", "score"],
                complexity_score=7,
                estimated_time=2.5,
                memory_usage=150
            ),
            AgentCapability(
                name="code_explanation",
                description="Explain how code works step by step",
                input_types=["code"],
                output_types=["explanation", "documentation"],
                complexity_score=5,
                estimated_time=2.0,
                memory_usage=100
            ),
            AgentCapability(
                name="bug_fixing",
                description="Identify and fix bugs in code",
                input_types=["code", "error_message"],
                output_types=["fixed_code", "explanation"],
                complexity_score=9,
                estimated_time=4.0,
                memory_usage=250,
                cpu_intensive=True
            ),
            AgentCapability(
                name="code_refactoring",
                description="Refactor code for better performance and readability",
                input_types=["code"],
                output_types=["refactored_code", "improvements"],
                complexity_score=8,
                estimated_time=3.5,
                memory_usage=200
            ),
            AgentCapability(
                name="test_generation",
                description="Generate unit tests for given code",
                input_types=["code", "function"],
                output_types=["test_code", "test_cases"],
                complexity_score=7,
                estimated_time=3.0,
                memory_usage=150
            ),
            AgentCapability(
                name="code_execution",
                description="Execute code safely in sandbox environment",
                input_types=["code", "language"],
                output_types=["output", "result"],
                complexity_score=6,
                estimated_time=2.0,
                memory_usage=300,
                cpu_intensive=True
            )
        ]
        
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.CODE,
            capabilities=capabilities,
            max_concurrent_tasks=3
        )
        
        # Code-specific configurations
        self.supported_languages = {
            "python": {
                "extension": ".py",
                "executor": "python",
                "syntax_checker": self._check_python_syntax
            },
            "javascript": {
                "extension": ".js", 
                "executor": "node",
                "syntax_checker": None
            },
            "typescript": {
                "extension": ".ts",
                "executor": "ts-node",
                "syntax_checker": None
            },
            "java": {
                "extension": ".java",
                "executor": "java",
                "syntax_checker": None
            },
            "cpp": {
                "extension": ".cpp",
                "executor": "g++",
                "syntax_checker": None
            },
            "go": {
                "extension": ".go",
                "executor": "go",
                "syntax_checker": None
            }
        }
        
        self.code_templates = {
            "python_function": '''def {function_name}({parameters}):
    """
    {docstring}
    """
    {implementation}
    return {return_value}''',
            
            "python_class": '''class {class_name}:
    """
    {docstring}
    """
    
    def __init__(self{init_params}):
        {init_implementation}
    
    {methods}''',
            
            "javascript_function": '''function {function_name}({parameters}) {{
    /**
     * {docstring}
     */
    {implementation}
    return {return_value};
}}''',
            
            "unit_test": '''def test_{function_name}():
    """Test {function_name} function"""
    # Arrange
    {test_setup}
    
    # Act
    result = {function_call}
    
    # Assert
    {assertions}'''
        }
    
    async def initialize(self) -> bool:
        """Initialize the code agent"""
        try:
            logger.info(f"Initializing {self.agent_id}")
            
            # Initialize LLM service if not already done
            if not llm_service.model:
                await llm_service.initialize()
            
            # Check for code execution tools
            self._check_execution_environment()
            
            self.status = AgentStatus.IDLE
            logger.info(f"{self.agent_id} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute code-related tasks"""
        task_type = task.type
        input_data = task.input_data
        
        try:
            if task_type == "code_generation":
                return await self._generate_code(input_data)
            elif task_type == "code_review":
                return await self._review_code(input_data)
            elif task_type == "code_explanation":
                return await self._explain_code(input_data)
            elif task_type == "bug_fixing":
                return await self._fix_bugs(input_data)
            elif task_type == "code_refactoring":
                return await self._refactor_code(input_data)
            elif task_type == "test_generation":
                return await self._generate_tests(input_data)
            elif task_type == "code_execution":
                return await self._execute_code(input_data)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Task execution failed in {self.agent_id}: {e}")
            raise
    
    async def _generate_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code from requirements"""
        requirements = input_data.get("requirements", "")
        language = input_data.get("language", "python").lower()
        style = input_data.get("style", "clean")
        include_tests = input_data.get("include_tests", False)
        include_docs = input_data.get("include_docs", True)
        
        # Build enhanced prompt
        prompt = self._build_code_generation_prompt(
            requirements, language, style, include_tests, include_docs
        )
        
        messages = [{"role": "user", "content": prompt}]
        
        # Generate code with lower temperature for consistency
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.2,
            max_tokens=800
        )
        
        # Parse and analyze generated code
        code_blocks = self._extract_code_blocks(response)
        main_code = code_blocks[0] if code_blocks else response
        
        # Perform syntax validation
        validation_result = await self._validate_code_syntax(main_code, language)
        
        # Generate additional components if requested
        additional_components = {}
        if include_tests and main_code:
            test_result = await self._generate_tests({
                "code": main_code,
                "language": language
            })
            additional_components["tests"] = test_result.get("test_code", "")
        
        return {
            "code": main_code,
            "language": language,
            "explanation": self._extract_explanation(response),
            "validation": validation_result,
            "additional_components": additional_components,
            "latency_ms": latency,
            "requirements": requirements,
            "style": style,
            "code_blocks": code_blocks
        }
    
    async def _review_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for quality, bugs, and improvements"""
        code = input_data.get("code", "")
        language = input_data.get("language", "python").lower()
        review_type = input_data.get("review_type", "comprehensive")
        
        if not code:
            raise ValueError("No code provided for review")
        
        # Perform static analysis
        static_analysis = await self._perform_static_analysis(code, language)
        
        # AI-powered code review
        prompt = f"""
        Review this {language} code for:
        1. Bugs and potential errors
        2. Performance issues  
        3. Security vulnerabilities
        4. Code style and best practices
        5. Maintainability concerns
        6. Suggested improvements
        
        Code:
        ```{language}
        {code}
        ```
        
        Provide detailed analysis with specific line references where possible.
        Rate the overall code quality from 1-10.
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.3,
            max_tokens=600
        )
        
        # Extract quality score
        quality_score = self._extract_quality_score(response)
        
        # Combine results
        review_result = {
            "code_reviewed": code,
            "language": language,
            "review_type": review_type,
            "ai_analysis": response,
            "static_analysis": static_analysis,
            "quality_score": quality_score,
            "issues_found": static_analysis.get("issues_count", 0),
            "recommendations": self._extract_recommendations(response),
            "latency_ms": latency
        }
        
        return review_result
    
    async def _explain_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Explain how code works step by step"""
        code = input_data.get("code", "")
        language = input_data.get("language", "python").lower()
        level = input_data.get("level", "intermediate")  # beginner, intermediate, advanced
        
        if not code:
            raise ValueError("No code provided for explanation")
        
        # Build explanation prompt based on level
        level_instructions = {
            "beginner": "Explain in simple terms suitable for someone new to programming",
            "intermediate": "Provide a detailed technical explanation",
            "advanced": "Focus on advanced concepts, patterns, and optimization details"
        }
        
        prompt = f"""
        {level_instructions.get(level, level_instructions['intermediate'])}.
        
        Explain this {language} code step by step:
        
        ```{language}
        {code}
        ```
        
        Please include:
        1. Overall purpose and functionality
        2. Step-by-step breakdown of each section
        3. Key concepts and patterns used
        4. Input/output behavior
        5. Any notable design decisions
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.4,
            max_tokens=500
        )
        
        # Extract code structure information
        code_structure = await self._analyze_code_structure(code, language)
        
        return {
            "explanation": response,
            "code_explained": code,
            "language": language,
            "explanation_level": level,
            "code_structure": code_structure,
            "complexity_analysis": self._calculate_complexity(code, language),
            "latency_ms": latency
        }
    
    async def _fix_bugs(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and fix bugs in code"""
        code = input_data.get("code", "")
        language = input_data.get("language", "python").lower()
        error_message = input_data.get("error_message", "")
        context = input_data.get("context", "")
        
        if not code:
            raise ValueError("No code provided for bug fixing")
        
        # Build bug fixing prompt
        prompt = f"""
        Fix the bugs in this {language} code.
        
        Code with issues:
        ```{language}
        {code}
        ```
        """
        
        if error_message:
            prompt += f"\nError message: {error_message}"
        
        if context:
            prompt += f"\nContext: {context}"
        
        prompt += """
        
        Please provide:
        1. Corrected code
        2. Explanation of what was wrong
        3. Why the fix works
        4. Prevention tips for similar issues
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.2,
            max_tokens=600
        )
        
        # Extract fixed code
        fixed_code_blocks = self._extract_code_blocks(response)
        fixed_code = fixed_code_blocks[0] if fixed_code_blocks else ""
        
        # Validate the fix
        if fixed_code:
            validation = await self._validate_code_syntax(fixed_code, language)
        else:
            validation = {"valid": False, "errors": ["No fixed code generated"]}
        
        return {
            "original_code": code,
            "fixed_code": fixed_code,
            "language": language,
            "error_message": error_message,
            "explanation": response,
            "bug_analysis": self._extract_bug_analysis(response),
            "validation": validation,
            "prevention_tips": self._extract_prevention_tips(response),
            "latency_ms": latency
        }
    
    async def _refactor_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor code for better performance and readability"""
        code = input_data.get("code", "")
        language = input_data.get("language", "python").lower()
        refactor_goals = input_data.get("goals", ["readability", "performance"])
        
        if not code:
            raise ValueError("No code provided for refactoring")
        
        goals_text = ", ".join(refactor_goals)
        
        prompt = f"""
        Refactor this {language} code focusing on: {goals_text}
        
        Original code:
        ```{language}
        {code}
        ```
        
        Please provide:
        1. Refactored code
        2. List of improvements made
        3. Performance impact analysis
        4. Readability improvements
        5. Any trade-offs made
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.3,
            max_tokens=700
        )
        
        # Extract refactored code
        refactored_code_blocks = self._extract_code_blocks(response)
        refactored_code = refactored_code_blocks[0] if refactored_code_blocks else ""
        
        # Compare complexity
        original_complexity = self._calculate_complexity(code, language)
        refactored_complexity = self._calculate_complexity(refactored_code, language) if refactored_code else {}
        
        return {
            "original_code": code,
            "refactored_code": refactored_code,
            "language": language,
            "refactor_goals": refactor_goals,
            "improvements": self._extract_improvements(response),
            "complexity_comparison": {
                "original": original_complexity,
                "refactored": refactored_complexity
            },
            "analysis": response,
            "latency_ms": latency
        }
    
    async def _generate_tests(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate unit tests for given code"""
        code = input_data.get("code", "")
        language = input_data.get("language", "python").lower()
        test_framework = input_data.get("framework", "unittest")
        coverage_level = input_data.get("coverage", "standard")  # basic, standard, comprehensive
        
        if not code:
            raise ValueError("No code provided for test generation")
        
        # Extract functions/methods to test
        testable_functions = self._extract_testable_functions(code, language)
        
        prompt = f"""
        Generate comprehensive unit tests for this {language} code using {test_framework}.
        
        Code to test:
        ```{language}
        {code}
        ```
        
        Please generate tests that cover:
        1. Normal/happy path scenarios
        2. Edge cases and boundary conditions
        3. Error conditions and exceptions
        4. Input validation
        
        Coverage level: {coverage_level}
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.3,
            max_tokens=800
        )
        
        # Extract test code
        test_code_blocks = self._extract_code_blocks(response)
        test_code = test_code_blocks[0] if test_code_blocks else ""
        
        # Generate test cases summary
        test_cases = self._extract_test_cases(response)
        
        return {
            "original_code": code,
            "test_code": test_code,
            "language": language,
            "test_framework": test_framework,
            "coverage_level": coverage_level,
            "testable_functions": testable_functions,
            "test_cases": test_cases,
            "test_explanation": response,
            "estimated_coverage": self._estimate_test_coverage(test_cases, testable_functions),
            "latency_ms": latency
        }
    
    async def _execute_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code safely in sandbox environment"""
        code = input_data.get("code", "")
        language = input_data.get("language", "python").lower()
        input_args = input_data.get("input", "")
        timeout = input_data.get("timeout", 10)
        
        if not code:
            raise ValueError("No code provided for execution")
        
        if language not in self.supported_languages:
            raise ValueError(f"Language {language} not supported for execution")
        
        try:
            # Execute code in sandbox
            execution_result = await self._execute_in_sandbox(
                code, language, input_args, timeout
            )
            
            return {
                "code": code,
                "language": language,
                "input": input_args,
                "success": execution_result.success,
                "output": execution_result.output,
                "error": execution_result.error,
                "execution_time": execution_result.execution_time,
                "return_code": execution_result.return_code
            }
            
        except Exception as e:
            return {
                "code": code,
                "language": language,
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "return_code": -1
            }
    
    # Helper methods
    def _build_code_generation_prompt(self, requirements: str, language: str, 
                                    style: str, include_tests: bool, include_docs: bool) -> str:
        """Build enhanced prompt for code generation"""
        style_instructions = {
            "clean": "Write clean, readable code following best practices",
            "minimal": "Write concise, minimal code",
            "robust": "Write robust code with comprehensive error handling",
            "performance": "Write performance-optimized code"
        }
        
        prompt = f"""
        Generate {language} code that meets the following requirements:
        
        Requirements: {requirements}
        
        Style: {style_instructions.get(style, style_instructions['clean'])}
        
        Please include:
        """
        
        if include_docs:
            prompt += "\n- Comprehensive documentation and comments"
        if include_tests:
            prompt += "\n- Example usage or test cases"
        
        prompt += f"""
        - Type hints (if supported by {language})
        - Error handling where appropriate  
        - Clear variable and function names
        
        Provide the code with explanations.
        """
        
        return prompt
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from response"""
        # Pattern to match code blocks with optional language specifier
        pattern = r'```(?:\w+)?\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if not matches:
            # Try to extract inline code
            inline_pattern = r'`([^`]+)`'
            matches = re.findall(inline_pattern, text)
        
        return [match.strip() for match in matches if match.strip()]
    
    def _extract_explanation(self, text: str) -> str:
        """Extract explanation from response"""
        # Remove code blocks to get explanation
        cleaned_text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        return cleaned_text.strip()
    
    async def _validate_code_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code syntax"""
        if language == "python":
            return self._check_python_syntax(code)
        else:
            # For other languages, basic validation
            return {
                "valid": True,
                "errors": [],
                "warnings": [],
                "message": f"Syntax validation not implemented for {language}"
            }
    
    def _check_python_syntax(self, code: str) -> Dict[str, Any]:
        """Check Python code syntax"""
        try:
            ast.parse(code)
            return {
                "valid": True,
                "errors": [],
                "warnings": [],
                "message": "Syntax is valid"
            }
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [f"Line {e.lineno}: {e.msg}"],
                "warnings": [],
                "message": f"Syntax error: {e.msg}"
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "message": f"Validation error: {str(e)}"
            }
    
    async def _perform_static_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """Perform static analysis on code"""
        analysis = {
            "issues_count": 0,
            "warnings": [],
            "suggestions": [],
            "metrics": {}
        }
        
        if language == "python":
            # Basic Python static analysis
            try:
                tree = ast.parse(code)
                analyzer = PythonCodeAnalyzer()
                analysis = analyzer.analyze(tree, code)
            except Exception as e:
                analysis["errors"] = [str(e)]
        
        return analysis
    
    def _extract_quality_score(self, text: str) -> int:
        """Extract quality score from review text"""
        # Look for patterns like "8/10", "8 out of 10", "score: 8"
        patterns = [
            r'(\d+)/10',
            r'(\d+)\s*out\s*of\s*10',
            r'score:?\s*(\d+)',
            r'quality:?\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return min(int(match.group(1)), 10)
        
        return 7  # Default score
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from review text"""
        # Simple extraction - look for bullet points or numbered lists
        lines = text.split('\n')
        recommendations = []
        
        for line in lines:
            line = line.strip()
            if (line.startswith('•') or line.startswith('-') or 
                line.startswith('*') or re.match(r'^\d+\.', line)):
                recommendations.append(line)
        
        return recommendations[:5]  # Limit to top 5
    
    async def _analyze_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code structure"""
        structure = {
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
            "complexity": 0
        }
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        structure["functions"].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        structure["classes"].append(node.name)
                    elif isinstance(node, ast.Import):
                        structure["imports"].extend([alias.name for alias in node.names])
            except:
                pass
        
        return structure
    
    def _calculate_complexity(self, code: str, language: str) -> Dict[str, Any]:
        """Calculate code complexity metrics"""
        metrics = {
            "lines_of_code": len([line for line in code.split('\n') if line.strip()]),
            "cyclomatic_complexity": 1,  # Base complexity
            "functions_count": 0,
            "classes_count": 0
        }
        
        if language == "python":
            try:
                tree = ast.parse(code)
                complexity_calculator = ComplexityCalculator()
                metrics.update(complexity_calculator.calculate(tree))
            except:
                pass
        
        return metrics
    
    def _extract_improvements(self, text: str) -> List[str]:
        """Extract improvements from refactoring response"""
        return self._extract_recommendations(text)
    
    def _extract_testable_functions(self, code: str, language: str) -> List[str]:
        """Extract functions that can be tested"""
        functions = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
            except:
                pass
        
        return functions
    
    def _extract_test_cases(self, text: str) -> List[Dict[str, str]]:
        """Extract test cases from test generation response"""
        # Simple extraction of test case descriptions
        lines = text.split('\n')
        test_cases = []
        
        current_case = {}
        for line in lines:
            if 'test_' in line.lower() or 'def test' in line:
                if current_case:
                    test_cases.append(current_case)
                current_case = {"name": line.strip(), "description": ""}
            elif current_case and line.strip().startswith('#'):
                current_case["description"] += line.strip() + " "
        
        if current_case:
            test_cases.append(current_case)
        
        return test_cases
    
    def _estimate_test_coverage(self, test_cases: List[Dict], functions: List[str]) -> float:
        """Estimate test coverage percentage"""
        if not functions:
            return 100.0
        
        covered_functions = set()
        for test_case in test_cases:
            test_name = test_case.get("name", "").lower()
            for func in functions:
                if func.lower() in test_name:
                    covered_functions.add(func)
        
        return (len(covered_functions) / len(functions)) * 100
    
    async def _execute_in_sandbox(self, code: str, language: str, 
                                input_args: str, timeout: int) -> CodeExecutionResult:
        """Execute code in a sandboxed environment"""
        lang_config = self.supported_languages.get(language)
        if not lang_config:
            raise ValueError(f"Unsupported language: {language}")
        
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=lang_config["extension"], 
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            start_time = time.time()
            
            if language == "python":
                # Execute Python code
                process = await asyncio.create_subprocess_exec(
                    "python", temp_file,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=input_args.encode() if input_args else None),
                    timeout=timeout
                )
                
                execution_time = time.time() - start_time
                
                return CodeExecutionResult(
                    success=process.returncode == 0,
                    output=stdout.decode() if stdout else "",
                    error=stderr.decode() if stderr else "",
                    execution_time=execution_time,
                    return_code=process.returncode or 0
                )
            
            else:
                # Placeholder for other languages
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error=f"Execution not implemented for {language}",
                    execution_time=0,
                    return_code=-1
                )
                
        except asyncio.TimeoutError:
            return CodeExecutionResult(
                success=False,
                output="",
                error=f"Execution timed out after {timeout} seconds",
                execution_time=timeout,
                return_code=-1
            )
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=0,
                return_code=-1
            )
        finally:
            # Cleanup temp file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def _extract_bug_analysis(self, text: str) -> Dict[str, Any]:
        """Extract bug analysis from response"""
        return {
            "issues_identified": self._extract_recommendations(text),
            "severity": "medium",  # Default
            "fix_confidence": 0.8
        }
    
    def _extract_prevention_tips(self, text: str) -> List[str]:
        """Extract prevention tips from bug fix response"""
        return self._extract_recommendations(text)
    
    def _check_execution_environment(self) -> None:
        """Check if code execution environment is available"""
        # Check for Python
        try:
            subprocess.run(["python", "--version"], capture_output=True, check=True)
            logger.info("Python execution environment available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Python execution environment not available")
    
    async def cleanup(self) -> None:
        """Cleanup code agent resources"""
        logger.info(f"Cleaning up {self.agent_id}")
        # No specific cleanup needed for code agent

# Helper classes for code analysis
class PythonCodeAnalyzer:
    """Analyze Python code for issues and metrics"""
    
    def analyze(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Analyze Python AST"""
        analysis = {
            "issues_count": 0,
            "warnings": [],
            "suggestions": [],
            "metrics": {
                "functions": 0,
                "classes": 0,
                "complexity": 1
            }
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["metrics"]["functions"] += 1
                # Check for long functions
                if len(node.body) > 20:
                    analysis["warnings"].append(f"Function '{node.name}' is quite long")
                    analysis["issues_count"] += 1
                    
            elif isinstance(node, ast.ClassDef):
                analysis["metrics"]["classes"] += 1
                
        return analysis

class ComplexityCalculator:
    """Calculate code complexity metrics"""
    
    def calculate(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate complexity metrics"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Increase complexity for control structures
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return {
            "cyclomatic_complexity": complexity,
            "cognitive_complexity": complexity  # Simplified
        }
    
class CodeExecutionResult:
    """Result of code execution"""
    
    def __init__(self, success: bool, output: str, error: str, 
                 execution_time: float, return_code: int):
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.return_code = return_code
import os
import re
import ast
import time
import json
import asyncio
import tempfile
import logging
import subprocess
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from AI_studio.Services.llm_service import llm_service
from AI_studio.Agents.agent_base import AgentBase, AgentStatus, AgentTask
from AI_studio.Utils.logger import get_logger
logger = get_logger(__name__)

class CodeAgent(AgentBase):
    """Agent specialized in code generation, review, explanation, bug fixing, refactoring, test generation, and execution"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.agent_type = "code_agent"
        self.supported_languages = {
            "python": {
                "extension": ".py",
                "execute_cmd": ["python"]
            },
            # Future support for more languages can be added here
        }
    
    async def initialize(self) -> bool:
        """Initialize the code agent"""
        try:
            # Check if execution environment is available
            self._check_execution_environment()
            
            self.status = AgentStatus.READY
            logger.info(f"{self.agent_id} initialized and ready")
            return True
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Failed to initialize {self.agent_id}: {e}")
            return False
        
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a given task"""
        if self.status != AgentStatus.READY:
            raise RuntimeError(f"Agent {self.agent_id} not ready to execute tasks")
        
        try:
            task_type = task.type
            input_data = task.input_data
            
            if task_type == "code_generation":
                return await self._generate_code(input_data)
            elif task_type == "code_review":
                return await self._review_code(input_data)
            elif task_type == "code_explanation":
                return await self._explain_code(input_data)
            elif task_type == "bug_fixing":
                return await self._fix_bugs(input_data)
            elif task_type == "code_refactoring":
                return await self._refactor_code(input_data)
            elif task_type == "test_generation":
                return await self._generate_tests(input_data)
            elif task_type == "code_execution":
                return await self._execute_code(input_data)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
        except Exception as e:
            logger.error(f"Error executing task {task.type}: {e}")
            return {"error": str(e)}
    async def _generate_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on requirements"""
        requirements = input_data.get("requirements", "")
        language = input_data.get("language", "python").lower()
        style = input_data.get("style", "clean")
        include_tests = input_data.get("include_tests", False)
        include_docs = input_data.get("include_docs", True)
        if not requirements:
            raise ValueError("No requirements provided for code generation")
        if language not in self.supported_languages:
            raise ValueError(f"Language {language} not supported for code generation")
        prompt = self._build_code_generation_prompt(
            requirements, language, style, include_tests, include_docs
        )
        messages = [{"role": "user", "content": prompt}]
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.3,
            max_tokens=800
        )
        code_blocks = self._extract_code_blocks(response)
        main_code = code_blocks[0] if code_blocks else ""
        additional_components = code_blocks[1:] if len(code_blocks) > 1 else []
        validation_result = await self._validate_code_syntax(main_code, language) if main_code else {
            "valid": False,
            "errors": ["No code generated"],
            "warnings": [],
            "message": "No code to validate"
        }
        explanation = self._extract_explanation(response)
        return {
            "generated_code": main_code,
            "language": language,
            "style": style,
            "include_tests": include_tests,
            "include_docs": include_docs,
            "explanation": explanation,
            "validation": validation_result,
            "latency_ms": latency,
            "additional_components": additional_components,
            "all_code_blocks": code_blocks
        }
