"""
Base Agent Implementation for AI Studio
Provides the foundational agent architecture with task management, metrics, and health monitoring.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import time
import json
from datetime import datetime
import uuid
import psutil
import threading
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of agents available in the system"""
    CODE = "code"
    TEXT = "text" 
    MULTIMODAL = "multimodal"
    RAG = "rag"
    SUMMARIZER = "summarizer"
    ANALYZER = "analyzer"
    VOICE = "voice"
    IMAGE = "image"

class AgentStatus(Enum):
    """Status of an agent"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    INITIALIZING = "initializing"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

@dataclass
class AgentCapability:
    """Represents a capability an agent can perform"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    complexity_score: int = 1  # 1-10 scale
    estimated_time: float = 1.0  # seconds
    memory_usage: int = 100  # MB
    cpu_intensive: bool = False
    requires_gpu: bool = False

@dataclass
class AgentTask:
    """Represents a task for an agent"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    agent_id: Optional[str] = None
    priority: int = TaskPriority.NORMAL.value
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 300  # seconds
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            "id": self.id,
            "type": self.type,
            "input_data": self.input_data,
            "agent_id": self.agent_id,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
            "retry_count": self.retry_count
        }

class BaseAgent(ABC):
    """
    Base class for all agents in the AI Studio system.
    Provides common functionality for task management, metrics, health monitoring.
    """
    
    def __init__(self, 
                 agent_id: str, 
                 agent_type: AgentType,
                 capabilities: List[AgentCapability],
                 max_concurrent_tasks: int = 1,
                 health_check_interval: int = 60):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = AgentStatus.INITIALIZING
        self.max_concurrent_tasks = max_concurrent_tasks
        self.health_check_interval = health_check_interval
        
        # Task management
        self.current_tasks: Dict[str, AgentTask] = {}
        self.task_history: List[AgentTask] = []
        self.task_queue = asyncio.Queue()
        self._task_lock = asyncio.Lock()
        
        # Metrics and monitoring
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_rejected": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0,
            "success_rate": 1.0,
            "memory_usage_mb": 0.0,
            "cpu_usage_percent": 0.0,
            "uptime_seconds": 0.0,
            "last_activity": datetime.now()
        }
        
        # Internal state
        self.start_time = time.time()
        self._last_health_check = time.time()
        self._shutdown_event = asyncio.Event()
        self._background_tasks: List[asyncio.Task] = []
        self._initialized = False
        
        # Performance optimization
        self._capability_map = {cap.name: cap for cap in capabilities}
        self._resource_monitor = ResourceMonitor()
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a given task - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources - must be implemented by subclasses"""
        pass
    
    async def start(self) -> bool:
        """Start the agent and background services"""
        try:
            logger.info(f"Starting agent {self.agent_id}")
            
            # Initialize the agent
            if not await self.initialize():
                logger.error(f"Failed to initialize agent {self.agent_id}")
                self.status = AgentStatus.ERROR
                return False
            
            # Start background tasks
            self._background_tasks.append(
                asyncio.create_task(self._health_monitor())
            )
            self._background_tasks.append(
                asyncio.create_task(self._metrics_updater())
            )
            
            self.status = AgentStatus.IDLE
            self._initialized = True
            logger.info(f"Agent {self.agent_id} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting agent {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def stop(self) -> None:
        """Stop the agent and cleanup resources"""
        logger.info(f"Stopping agent {self.agent_id}")
        
        self._shutdown_event.set()
        self.status = AgentStatus.OFFLINE
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for current tasks to complete (with timeout)
        if self.current_tasks:
            try:
                await asyncio.wait_for(
                    self._wait_for_tasks_completion(), 
                    timeout=30
                )
            except asyncio.TimeoutError:
                logger.warning(f"Agent {self.agent_id} tasks did not complete in time")
        
        # Cleanup resources
        await self.cleanup()
        logger.info(f"Agent {self.agent_id} stopped")
    
    def can_handle_task(self, task: AgentTask) -> bool:
        """Check if agent can handle the given task"""
        if not self._initialized or self.status != AgentStatus.IDLE:
            return False
        
        # Check capability
        if task.type not in self._capability_map:
            return False
        
        # Check capacity
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            return False
        
        # Check resources
        capability = self._capability_map[task.type]
        if capability.requires_gpu and not self._has_gpu():
            return False
        
        return True
    
    def get_capability_score(self, task_type: str) -> int:
        """Get agent's capability score for a task type"""
        capability = self._capability_map.get(task_type)
        if capability:
            # Adjust score based on current load
            load_factor = len(self.current_tasks) / max(self.max_concurrent_tasks, 1)
            adjusted_score = capability.complexity_score * (1 - load_factor * 0.3)
            return int(adjusted_score)
        return 0
    
    async def submit_task(self, task: AgentTask) -> str:
        """Submit a task to the agent"""
        if not self.can_handle_task(task):
            self.metrics["tasks_rejected"] += 1
            raise ValueError(f"Agent {self.agent_id} cannot handle task {task.type}")
        
        task.agent_id = self.agent_id
        await self.task_queue.put(task)
        
        # Process task immediately if we're idle
        if self.status == AgentStatus.IDLE:
            asyncio.create_task(self._process_next_task())
        
        return task.id
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process a task with full error handling and metrics"""
        async with self._task_lock:
            if len(self.current_tasks) >= self.max_concurrent_tasks:
                raise ValueError(f"Agent {self.agent_id} at max capacity")
            
            self.current_tasks[task.id] = task
        
        task.started_at = datetime.now()
        self.status = AgentStatus.BUSY
        start_time = time.time()
        
        try:
            logger.info(f"Agent {self.agent_id} starting task {task.id} ({task.type})")
            
            # Set timeout for task execution
            result = await asyncio.wait_for(
                self.execute_task(task),
                timeout=task.timeout
            )
            
            task.result = result
            task.completed_at = datetime.now()
            execution_time = time.time() - start_time
            
            # Update metrics
            await self._update_success_metrics(execution_time)
            
            # Execute callback if provided
            if task.callback:
                try:
                    await task.callback(task)
                except Exception as e:
                    logger.warning(f"Task callback failed: {e}")
            
            logger.info(f"Agent {self.agent_id} completed task {task.id} in {execution_time:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Task {task.id} timed out after {task.timeout}s"
            task.error = error_msg
            task.completed_at = datetime.now()
            await self._update_error_metrics()
            logger.error(f"Agent {self.agent_id}: {error_msg}")
            raise TimeoutError(error_msg)
            
        except Exception as e:
            error_msg = f"Task {task.id} failed: {str(e)}"
            task.error = error_msg
            task.completed_at = datetime.now()
            await self._update_error_metrics()
            logger.error(f"Agent {self.agent_id}: {error_msg}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                logger.info(f"Retrying task {task.id} (attempt {task.retry_count})")
                await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                return await self.process_task(task)
            
            raise
        
        finally:
            # Cleanup
            async with self._task_lock:
                self.current_tasks.pop(task.id, None)
            
            self._add_to_history(task)
            
            # Update status
            if not self.current_tasks:
                self.status = AgentStatus.IDLE
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        await self._update_resource_metrics()
        
        return {
            "agent_id": self.agent_id,
            "type": self.agent_type.value,
            "status": self.status.value,
            "capabilities": [cap.name for cap in self.capabilities],
            "current_tasks": len(self.current_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "queue_size": self.task_queue.qsize(),
            "metrics": self.metrics.copy(),
            "uptime": time.time() - self.start_time,
            "last_health_check": self._last_health_check,
            "resource_usage": self._resource_monitor.get_usage()
        }
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            self._last_health_check = time.time()
            
            # Check if agent is responsive
            if self.status == AgentStatus.ERROR:
                return False
            
            # Check resource usage
            memory_usage = self._resource_monitor.get_memory_usage()
            if memory_usage > 90:  # 90% memory usage threshold
                logger.warning(f"Agent {self.agent_id} high memory usage: {memory_usage}%")
            
            # Check if tasks are stuck
            stuck_tasks = [
                task for task in self.current_tasks.values()
                if task.started_at and 
                (datetime.now() - task.started_at).seconds > task.timeout
            ]
            
            if stuck_tasks:
                logger.warning(f"Agent {self.agent_id} has {len(stuck_tasks)} stuck tasks")
                for task in stuck_tasks:
                    task.error = "Task stuck - health check timeout"
                    await self._cleanup_stuck_task(task)
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for agent {self.agent_id}: {e}")
            return False
    
    # Private methods
    async def _process_next_task(self) -> None:
        """Process the next task in queue"""
        try:
            task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
            await self.process_task(task)
        except asyncio.TimeoutError:
            pass  # No tasks in queue
        except Exception as e:
            logger.error(f"Error processing task in agent {self.agent_id}: {e}")
    
    async def _health_monitor(self) -> None:
        """Background health monitoring"""
        while not self._shutdown_event.is_set():
            try:
                await self.health_check()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitor error for agent {self.agent_id}: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _metrics_updater(self) -> None:
        """Background metrics updating"""
        while not self._shutdown_event.is_set():
            try:
                await self._update_resource_metrics()
                self.metrics["uptime_seconds"] = time.time() - self.start_time
                self.metrics["last_activity"] = datetime.now()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Metrics updater error for agent {self.agent_id}: {e}")
                await asyncio.sleep(60)
    
    async def _update_success_metrics(self, execution_time: float) -> None:
        """Update metrics after successful task completion"""
        self.metrics["tasks_completed"] += 1
        self.metrics["total_execution_time"] += execution_time
        
        # Calculate running average
        total_tasks = self.metrics["tasks_completed"]
        self.metrics["average_execution_time"] = (
            self.metrics["total_execution_time"] / total_tasks
        )
        
        # Update success rate
        total_attempted = total_tasks + self.metrics["tasks_failed"]
        self.metrics["success_rate"] = total_tasks / max(total_attempted, 1)
    
    async def _update_error_metrics(self) -> None:
        """Update metrics after task failure"""
        self.metrics["tasks_failed"] += 1
        
        # Update success rate
        total_tasks = self.metrics["tasks_completed"]
        total_attempted = total_tasks + self.metrics["tasks_failed"]
        self.metrics["success_rate"] = total_tasks / max(total_attempted, 1)
    
    async def _update_resource_metrics(self) -> None:
        """Update resource usage metrics"""
        usage = self._resource_monitor.get_usage()
        self.metrics["memory_usage_mb"] = usage["memory_mb"]
        self.metrics["cpu_usage_percent"] = usage["cpu_percent"]
    
    def _add_to_history(self, task: AgentTask) -> None:
        """Add task to history with cleanup"""
        self.task_history.append(task)
        
        # Keep only recent history (last 1000 tasks)
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-1000:]
    
    async def _cleanup_stuck_task(self, task: AgentTask) -> None:
        """Clean up a stuck task"""
        async with self._task_lock:
            self.current_tasks.pop(task.id, None)
        self._add_to_history(task)
        self.metrics["tasks_failed"] += 1
    
    async def _wait_for_tasks_completion(self) -> None:
        """Wait for all current tasks to complete"""
        while self.current_tasks:
            await asyncio.sleep(1)
    
    def _has_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

class ResourceMonitor:
    """Monitor system resource usage"""
    
    def __init__(self):
        self._process = psutil.Process()
    
    def get_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        try:
            memory_info = self._process.memory_info()
            cpu_percent = self._process.cpu_percent()
            
            return {
                "memory_mb": memory_info.rss / 1024 / 1024,
                "cpu_percent": cpu_percent,
                "memory_percent": self._process.memory_percent()
            }
        except Exception as e:
            logger.warning(f"Error getting resource usage: {e}")
            return {"memory_mb": 0, "cpu_percent": 0, "memory_percent": 0}
    
    def get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            return self._process.memory_percent()
        except:
            return 0.0