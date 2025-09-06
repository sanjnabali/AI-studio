import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import time
import json
from datetime import datetime
from app.services.llm import llm_service
from app.services.rag_engine import RAGEngine

logger = logging.getLogger(__name__)

class AgentType(Enum):
    CODE = "code"
    TEXT = "text" 
    MULTIMODAL = "multimodal"
    RAG = "rag"
    SUMMARIZER = "summarizer"
    ANALYZER = "analyzer"

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    INITIALIZING = "initializing"

@dataclass
class AgentCapability:
    """Represents a capability an agent can perform"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    complexity_score: int = 1  # 1-10 scale

@dataclass
class AgentTask:
    """Represents a task for an agent"""
    id: str
    type: str
    input_data: Dict[str, Any]
    agent_id: Optional[str] = None
    priority: int = 1  # 1 (high) to 10 (low)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, 
                 agent_id: str, 
                 agent_type: AgentType,
                 capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = AgentStatus.INITIALIZING
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent"""
        pass
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a given task"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass
    
    def can_handle_task(self, task: AgentTask) -> bool:
        """Check if agent can handle the given task"""
        for capability in self.capabilities:
            if capability.name == task.type:
                return True
        return False
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process a task with error handling and metrics"""
        if self.status != AgentStatus.IDLE:
            raise ValueError(f"Agent {self.agent_id} is not available (status: {self.status})")
        
        self.status = AgentStatus.BUSY
        self.current_task = task
        task.started_at = datetime.now()
        start_time = time.time()
        
        try:
            logger.info(f"Agent {self.agent_id} starting task {task.id}")
            result = await self.execute_task(task)
            
            task.result = result
            task.completed_at = datetime.now()
            execution_time = time.time() - start_time
            
            # Update metrics
            self.metrics["tasks_completed"] += 1
            self.metrics["total_execution_time"] += execution_time
            self.metrics["average_execution_time"] = (
                self.metrics["total_execution_time"] / self.metrics["tasks_completed"]
            )
            
            logger.info(f"Agent {self.agent_id} completed task {task.id} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            task.error = str(e)
            task.completed_at = datetime.now()
            self.metrics["tasks_failed"] += 1
            
            logger.error(f"Agent {self.agent_id} failed task {task.id}: {e}")
            raise
        
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.task_history.append(task)
            
            # Keep only recent history
            if len(self.task_history) > 100:
                self.task_history = self.task_history[-100:]

class CodeAgent(BaseAgent):
    """Agent specialized for code generation and analysis"""
    
    def __init__(self):
        capabilities = [
            AgentCapability(
                "code_generation",
                "Generate code in various programming languages",
                ["text", "requirements"],
                ["code", "explanation"],
                complexity_score=7
            ),
            AgentCapability(
                "code_review",
                "Review and analyze code for bugs and improvements", 
                ["code"],
                ["analysis", "suggestions"],
                complexity_score=8
            ),
            AgentCapability(
                "code_explanation",
                "Explain how code works",
                ["code"],
                ["explanation"],
                complexity_score=5
            )
        ]
        super().__init__("code_agent", AgentType.CODE, capabilities)
    
    async def initialize(self) -> bool:
        """Initialize the code agent"""
        try:
            # Ensure LLM service is initialized
            if not llm_service.model:
                await llm_service.initialize()
            
            self.status = AgentStatus.IDLE
            logger.info("Code agent initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize code agent: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute code-related tasks"""
        task_type = task.type
        input_data = task.input_data
        
        if task_type == "code_generation":
            return await self._generate_code(input_data)
        elif task_type == "code_review":
            return await self._review_code(input_data)
        elif task_type == "code_explanation":
            return await self._explain_code(input_data)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def _generate_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on requirements"""
        requirements = input_data.get("requirements", "")
        language = input_data.get("language", "python")
        
        messages = [
            {
                "role": "user",
                "content": f"Write {language} code for the following requirements:\n{requirements}\n\nInclude comments and error handling."
            }
        ]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.3,  # Lower temperature for more consistent code
            max_tokens=500
        )
        
        return {
            "code": response,
            "language": language,
            "latency_ms": latency,
            "requirements": requirements
        }
    
    async def _review_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for issues and improvements"""
        code = input_data.get("code", "")
        language = input_data.get("language", "python")
        
        messages = [
            {
                "role": "user", 
                "content": f"Review this {language} code and identify:\n1. Bugs or errors\n2. Performance issues\n3. Best practice violations\n4. Suggestions for improvement\n\nCode:\n```{language}\n{code}\n```"
            }
        ]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.2,
            max_tokens=400
        )
        
        return {
            "analysis": response,
            "code_reviewed": code,
            "language": language,
            "latency_ms": latency
        }
    
    async def _explain_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Explain how code works"""
        code = input_data.get("code", "")
        language = input_data.get("language", "python")
        
        messages = [
            {
                "role": "user",
                "content": f"Explain how this {language} code works step by step:\n\n```{language}\n{code}\n```"
            }
        ]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="code",
            temperature=0.4,
            max_tokens=400
        )
        
        return {
            "explanation": response,
            "code_explained": code,
            "language": language,
            "latency_ms": latency
        }
    
    async def cleanup(self) -> None:
        """Cleanup code agent resources"""
        logger.info("Cleaning up code agent")

class TextAgent(BaseAgent):
    """Agent specialized for text processing and generation"""
    
    def __init__(self):
        capabilities = [
            AgentCapability(
                "text_generation",
                "Generate creative and informative text content",
                ["prompt", "style"],
                ["text"],
                complexity_score=6
            ),
            AgentCapability(
                "text_summarization", 
                "Summarize long texts into key points",
                ["text"],
                ["summary"],
                complexity_score=5
            ),
            AgentCapability(
                "text_analysis",
                "Analyze text for sentiment, topics, etc.",
                ["text"],
                ["analysis"],
                complexity_score=6
            )
        ]
        super().__init__("text_agent", AgentType.TEXT, capabilities)
    
    async def initialize(self) -> bool:
        """Initialize the text agent"""
        try:
            if not llm_service.model:
                await llm_service.initialize()
            
            self.status = AgentStatus.IDLE
            logger.info("Text agent initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize text agent: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute text-related tasks"""
        task_type = task.type
        input_data = task.input_data
        
        if task_type == "text_generation":
            return await self._generate_text(input_data)
        elif task_type == "text_summarization":
            return await self._summarize_text(input_data)
        elif task_type == "text_analysis":
            return await self._analyze_text(input_data)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def _generate_text(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text based on prompt and style"""
        prompt = input_data.get("prompt", "")
        style = input_data.get("style", "informative")
        max_length = input_data.get("max_length", 300)
        
        style_prompts = {
            "creative": "Write creatively with vivid imagery and engaging language.",
            "professional": "Write in a professional, formal tone.",
            "casual": "Write in a casual, conversational tone.",
            "informative": "Write informatively with clear, factual content."
        }
        
        style_instruction = style_prompts.get(style, style_prompts["informative"])
        
        messages = [
            {
                "role": "user",
                "content": f"{style_instruction}\n\nTopic: {prompt}"
            }
        ]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="creative" if style == "creative" else "general",
            temperature=0.8 if style == "creative" else 0.6,
            max_tokens=max_length
        )
        
        return {
            "generated_text": response,
            "style": style,
            "prompt": prompt,
            "latency_ms": latency
        }
    
    async def _summarize_text(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize input text"""
        text = input_data.get("text", "")
        max_summary_length = input_data.get("max_summary_length", 150)
        
        messages = [
            {
                "role": "user",
                "content": f"Summarize the following text in approximately {max_summary_length} words:\n\n{text}"
            }
        ]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="summarizer",
            temperature=0.3,
            max_tokens=max_summary_length + 50
        )
        
        return {
            "summary": response,
            "original_length": len(text.split()),
            "summary_length": len(response.split()),
            "compression_ratio": len(response.split()) / len(text.split()) if text else 0,
            "latency_ms": latency
        }
    
    async def _analyze_text(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text for various attributes"""
        text = input_data.get("text", "")
        analysis_type = input_data.get("analysis_type", "general")
        
        analysis_prompts = {
            "sentiment": "Analyze the sentiment of this text (positive, negative, neutral) and explain why:",
            "topics": "Identify the main topics and themes in this text:",
            "general": "Provide a general analysis of this text including tone, main points, and key insights:"
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
        
        messages = [
            {
                "role": "user",
                "content": f"{prompt}\n\n{text}"
            }
        ]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="analysis",
            temperature=0.4,
            max_tokens=300
        )
        
        return {
            "analysis": response,
            "analysis_type": analysis_type,
            "text_length": len(text),
            "latency_ms": latency
        }
    
    async def cleanup(self) -> None:
        """Cleanup text agent resources"""
        logger.info("Cleaning up text agent")

class RAGAgent(BaseAgent):
    """Agent specialized for RAG (Retrieval-Augmented Generation)"""
    
    def __init__(self, rag_engine: RAGEngine):
        capabilities = [
            AgentCapability(
                "rag_query",
                "Answer questions using retrieved context",
                ["question", "context"],
                ["answer", "sources"],
                complexity_score=8
            ),
            AgentCapability(
                "document_analysis",
                "Analyze documents and extract insights",
                ["documents"],
                ["insights", "summary"],
                complexity_score=7
            ),
            AgentCapability(
                "knowledge_synthesis",
                "Synthesize information from multiple sources",
                ["queries", "sources"],
                ["synthesis"],
                complexity_score=9
            )
        ]
        super().__init__("rag_agent", AgentType.RAG, capabilities)
        self.rag_engine = rag_engine
    
    async def initialize(self) -> bool:
        """Initialize the RAG agent"""
        try:
            if not llm_service.model:
                await llm_service.initialize()
            
            if not self.rag_engine.embedding_model:
                await self.rag_engine.initialize()
            
            self.status = AgentStatus.IDLE
            logger.info("RAG agent initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize RAG agent: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute RAG-related tasks"""
        task_type = task.type
        input_data = task.input_data
        
        if task_type == "rag_query":
            return await self._answer_with_rag(input_data)
        elif task_type == "document_analysis":
            return await self._analyze_documents(input_data)
        elif task_type == "knowledge_synthesis":
            return await self._synthesize_knowledge(input_data)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def _answer_with_rag(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Answer question using RAG"""
        question = input_data.get("question", "")
        max_context_length = input_data.get("max_context_length", 1500)
        
        # Retrieve relevant context
        context = await self.rag_engine.get_context_for_query(
            question, max_context_length=max_context_length
        )
        
        # Get source citations
        sources = await self.rag_engine.query(question, top_k=5)
        
        # Generate answer with context
        messages = [
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}\n\nPlease answer the question based on the provided context. If the context doesn't contain relevant information, say so."
            }
        ]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="analysis",
            temperature=0.3,
            max_tokens=400
        )
        
        return {
            "answer": response,
            "question": question,
            "context_used": context,
            "sources": [
                {
                    "content": source["content"][:200] + "...",
                    "metadata": source["metadata"],
                    "similarity": source["similarity_score"]
                }
                for source in sources
            ],
            "latency_ms": latency
        }
    
    async def _analyze_documents(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze documents for insights"""
        document_ids = input_data.get("document_ids", [])
        analysis_focus = input_data.get("focus", "general insights")
        
        # Retrieve document contents
        documents = []
        for doc_id in document_ids:
            if doc_id in self.rag_engine.documents:
                documents.append(self.rag_engine.documents[doc_id].content)
        
        if not documents:
            return {"error": "No documents found"}
        
        combined_content = "\n\n".join(documents[:5])  # Limit to 5 docs
        
        messages = [
            {
                "role": "user",
                "content": f"Analyze the following documents and provide insights focusing on: {analysis_focus}\n\nDocuments:\n{combined_content}"
            }
        ]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="analysis", 
            temperature=0.4,
            max_tokens=500
        )
        
        return {
            "analysis": response,
            "documents_analyzed": len(documents),
            "focus": analysis_focus,
            "latency_ms": latency
        }
    
    async def _synthesize_knowledge(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize knowledge from multiple queries"""
        queries = input_data.get("queries", [])
        synthesis_goal = input_data.get("goal", "comprehensive overview")
        
        all_results = []
        for query in queries:
            results = await self.rag_engine.query(query, top_k=3)
            all_results.extend(results)
        
        # Combine unique content
        unique_content = []
        seen_content = set()
        for result in all_results:
            content = result["content"]
            if content not in seen_content:
                unique_content.append(content)
                seen_content.add(content)
        
        combined_knowledge = "\n\n".join(unique_content[:10])  # Limit content
        
        messages = [
            {
                "role": "user",
                "content": f"Synthesize the following information to provide a {synthesis_goal}:\n\nQueries: {', '.join(queries)}\n\nInformation:\n{combined_knowledge}"
            }
        ]
        
        response, latency = await llm_service.chat(
            messages=messages,
            domain="analysis",
            temperature=0.5,
            max_tokens=600
        )
        
        return {
            "synthesis": response,
            "queries": queries,
            "sources_used": len(unique_content),
            "goal": synthesis_goal,
            "latency_ms": latency
        }
    
    async def cleanup(self) -> None:
        """Cleanup RAG agent resources"""
        logger.info("Cleaning up RAG agent")

class AgentOrchestrator:
    """Orchestrates multiple agents and manages task distribution"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, AgentTask] = {}
        self.task_results: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.worker_tasks: List[asyncio.Task] = []
        
    async def initialize(self):
        """Initialize the orchestrator and all agents"""
        logger.info("Initializing Agent Orchestrator...")
        
        try:
            # Initialize RAG engine
            rag_engine = RAGEngine()
            await rag_engine.initialize()
            
            # Create agents
            agents = [
                CodeAgent(),
                TextAgent(),
                RAGAgent(rag_engine)
            ]
            
            # Initialize all agents
            for agent in agents:
                success = await agent.initialize()
                if success:
                    self.agents[agent.agent_id] = agent
                    logger.info(f"Agent {agent.agent_id} initialized successfully")
                else:
                    logger.error(f"Failed to initialize agent {agent.agent_id}")
            
            # Start worker tasks
            self.is_running = True
            for i in range(3):  # 3 worker threads
                worker_task = asyncio.create_task(self._worker(f"worker_{i}"))
                self.worker_tasks.append(worker_task)
            
            logger.info(f"Agent Orchestrator initialized with {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize Agent Orchestrator: {e}")
            raise
    
    async def _worker(self, worker_id: str):
        """Worker coroutine to process tasks"""
        logger.info(f"Worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Find suitable agent
                suitable_agent = self._find_suitable_agent(task)
                if not suitable_agent:
                    task.error = "No suitable agent found"
                    self.task_results[task.id] = {"error": task.error}
                    continue
                
                # Execute task
                self.active_tasks[task.id] = task
                try:
                    result = await suitable_agent.process_task(task)
                    self.task_results[task.id] = result
                except Exception as e:
                    self.task_results[task.id] = {"error": str(e)}
                finally:
                    if task.id in self.active_tasks:
                        del self.active_tasks[task.id]
                
                # Mark task as done
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
    
    def _find_suitable_agent(self, task: AgentTask) -> Optional[BaseAgent]:
        """Find the most suitable agent for a task"""
        suitable_agents = []
        
        for agent in self.agents.values():
            if (agent.status == AgentStatus.IDLE and 
                agent.can_handle_task(task)):
                suitable_agents.append(agent)
        
        if not suitable_agents:
            return None
        
        # Return agent with best performance metrics
        return min(suitable_agents, 
                  key=lambda a: a.metrics["average_execution_time"])
    
    async def submit_task(self, 
                         task_type: str,
                         input_data: Dict[str, Any],
                         priority: int = 5,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Submit a task for processing"""
        task_id = f"task_{int(time.time() * 1000)}_{hash(str(input_data)) % 10000}"
        
        task = AgentTask(
            id=task_id,
            type=task_type,
            input_data=input_data,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Add to queue (higher priority = lower number = processed first)
        await self.task_queue.put(task)
        logger.info(f"Submitted task {task_id} of type {task_type}")
        
        return task_id
    
    async def get_task_result(self, 
                            task_id: str, 
                            timeout: float = 30.0) -> Dict[str, Any]:
        """Get result of a submitted task"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if task_id in self.task_results:
                result = self.task_results[task_id]
                # Clean up old results
                del self.task_results[task_id]
                return result
            
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")
    
    async def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        status = {}
        for agent_id, agent in self.agents.items():
            status[agent_id] = {
                "type": agent.agent_type.value,
                "status": agent.status.value,
                "current_task": agent.current_task.id if agent.current_task else None,
                "capabilities": [cap.name for cap in agent.capabilities],
                "metrics": agent.metrics,
                "recent_tasks": len(agent.task_history)
            }
        return status
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        total_tasks = sum(agent.metrics["tasks_completed"] for agent in self.agents.values())
        total_failures = sum(agent.metrics["tasks_failed"] for agent in self.agents.values())
        
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status == AgentStatus.IDLE]),
            "busy_agents": len([a for a in self.agents.values() if a.status == AgentStatus.BUSY]),
            "total_tasks_completed": total_tasks,
            "total_tasks_failed": total_failures,
            "success_rate": total_tasks / (total_tasks + total_failures) if (total_tasks + total_failures) > 0 else 0,
            "queue_size": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "pending_results": len(self.task_results)
        }
    
    async def health_check(self) -> bool:
        """Check health of orchestrator"""
        try:
            healthy_agents = sum(1 for agent in self.agents.values() 
                               if agent.status != AgentStatus.ERROR)
            return healthy_agents > 0 and self.is_running
        except:
            return False
    
    async def cleanup(self):
        """Cleanup orchestrator and all agents"""
        logger.info("Cleaning up Agent Orchestrator...")
        
        # Stop workers
        self.is_running = False
        for task in self.worker_tasks:
            task.cancel()
        
        # Cleanup all agents
        for agent in self.agents.values():
            await agent.cleanup()
        
        # Clear data structures
        self.agents.clear()
        self.active_tasks.clear()
        self.task_results.clear()
        
        logger.info("Agent Orchestrator cleanup completed")

# Global orchestrator instance
orchestrator = AgentOrchestrator()