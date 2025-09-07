"""
Summarizer Agent Implementation for AI Studio
Specialized agent for text summarization, document analysis, and content extraction.
"""

import asyncio
import logging
import re
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import nltk
from collections import Counter

from .base_agent import BaseAgent, AgentType, AgentCapability, AgentTask, AgentStatus
from app.services.llm import llm_service

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    logger.warning("Failed to download NLTK data - some features may be limited")

@dataclass
class SummaryMetrics:
    """Metrics for summary quality"""
    original_length: int
    summary_length: int
    compression_ratio: float
    reading_time_minutes: float
    key_topics: List[str]
    sentiment: str
    readability_score: float

@dataclass
class DocumentStructure:
    """Structure analysis of document"""
    sections: List[str]
    headings: List[str]
    paragraphs: int
    sentences: int
    words: int
    main_topics: List[str]

class SummarizerAgent(BaseAgent):
    """
    Specialized agent for text summarization tasks including:
    - Extractive summarization (key sentence extraction)
    - Abstractive summarization (AI-generated summaries)
    - Multi-document summarization
    - Topic extraction and analysis
    - Document structure analysis
    - Content categorization
    - Key insights extraction
    """
    
    def __init__(self, agent_id: str = "summarizer_agent"):
        capabilities = [
            AgentCapability(
                name="extractive_summarization",
                description="Extract key sentences to create summaries",
                input_types=["text", "document"],
                output_types=["summary", "key_sentences"],
                complexity_score=5,
                estimated_time=2.0,
                memory_usage=150
            ),
            AgentCapability(
                name="abstractive_summarization", 
                description="Generate AI-written summaries of content",
                input_types=["text", "document"],
                output_types=["summary", "insights"],
                complexity_score=8,
                estimated_time=4.0,
                memory_usage=300,
                cpu_intensive=True
            ),
            AgentCapability(
                name="multi_document_summary",
                description="Summarize multiple documents together",
                input_types=["documents", "text_list"],
                output_types=["consolidated_summary", "comparative_analysis"],
                complexity_score=9,
                estimated_time=6.0,
                memory_usage=500,
                cpu_intensive=True
            ),
            AgentCapability(
                name="topic_extraction",
                description="Extract main topics and themes from text",
                input_types=["text", "document"],
                output_types=["topics", "themes", "keywords"],
                complexity_score=6,
                estimated_time=2.5,
                memory_usage=200
            ),
            AgentCapability(
                name="document_analysis",
                description="Analyze document structure and content",
                input_types=["text", "document"],
                output_types=["structure", "analysis", "metrics"],
                complexity_score=4,
                estimated_time=1.5,
                memory_usage=100
            ),
            AgentCapability(
                name="key_insights",
                description="Extract key insights and actionable items",
                input_types=["text", "document"],
                output_types=["insights", "action_items"],
                complexity_score=7,
                estimated_time=3.0,
                memory_usage=250
            ),
            AgentCapability(
                name="content_categorization",
                description="Categorize and classify content",
                input_types=["text", "document"],
                output_types=["categories", "classification"],
                complexity_score=5,
                estimated_time=2.0,
                memory_usage=150
            )
        ]
        
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.SUMMARIZER,
            capabilities=capabilities,
            max_concurrent_tasks=4
        )
        
        # Summarization configurations
        self.summary_styles = {
            "concise": {
                "max_ratio": 0.2,
                "focus": "key points only",
                "tone": "direct and brief"
            },
            "comprehensive": {
                "max_ratio": 0.4,
                "focus": "detailed coverage",
                "tone": "thorough and complete"
            },
            "executive": {
                "max_ratio": 0.15,
                "focus": "strategic insights",
                "tone": "business-oriented"
            },
            "academic": {
                "max_ratio": 0.3,
                "focus": "methodology and findings",
                "tone": "scholarly and precise"
            },
            "narrative": {
                "max_ratio": 0.35,
                "focus": "story and flow",
                "tone": "engaging and flowing"
            }
        }
        
        self.extraction_algorithms = {
            "frequency": self._frequency_based_extraction,
            "position": self._position_based_extraction,
            "tf_idf": self._tfidf_extraction,
            "hybrid": self._hybrid_extraction
        }
        
        # NLP tools initialization
        self.stop_words = set()
        self._initialize_nlp_tools()
    
    def _initialize_nlp_tools(self):
        """Initialize NLP tools and resources"""
        try:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except:
            # Fallback stop words
            self.stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could'
            }
    
    async def initialize(self) -> bool:
        """Initialize the summarizer agent"""
        try:
            logger.info(f"Initializing {self.agent_id}")
            
            # Initialize LLM service if not already done
            if not llm_service.model:
                await llm_service.initialize()
            
            self.status = AgentStatus.IDLE
            logger.info(f"{self.agent_id} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute summarization tasks"""
        task_type = task.type
        input_data = task.input_data
        
        try:
            if task_type == "extractive_summarization":
                return await self._extractive_summarize(input_data)
            elif task_type == "abstractive_summarization":
                return await self._abstractive_summarize(input_data)
            elif task_type == "multi_document_summary":
                return await self._multi_document_summarize(input_data)
            elif task_type == "topic_extraction":
                return await self._extract_topics(input_data)
            elif task_type == "document_analysis":
                return await self._analyze_document(input_data)
            elif task_type == "key_insights":
                return await self._extract_key_insights(input_data)
            elif task_type == "content_categorization":
                return await self._categorize_content(input_data)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
        except Exception as e:
            logger.error(f"Error executing task {task_type}: {e}")
            return {"error": str(e)}
    async def _extractive_summarize(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform extractive summarization"""
        text = input_data.get("text", "")
        style = input_data.get("style", "concise")
        algorithm = input_data.get("algorithm", "hybrid")
        
        if not text:
            raise ValueError("Input text is required for extractive summarization")
        
        if style not in self.summary_styles:
            raise ValueError(f"Unsupported summary style: {style}")
        
        if algorithm not in self.extraction_algorithms:
            raise ValueError(f"Unsupported extraction algorithm: {algorithm}")
        
        # Preprocess text
        sentences = nltk.sent_tokenize(text)
        total_sentences = len(sentences)
        
        # Determine number of sentences for summary
        max_ratio = self.summary_styles[style]["max_ratio"]
        num_summary_sentences = max(1, int(total_sentences * max_ratio))
        
        # Extract key sentences
        extraction_func = self.extraction_algorithms[algorithm]
        key_sentences = extraction_func(sentences, num_summary_sentences)
        
        summary = " ".join(key_sentences)
        
        # Calculate metrics
        metrics = SummaryMetrics(
            original_length=len(text.split()),
            summary_length=len(summary.split()),
            compression_ratio=len(summary.split()) / len(text.split()),
            reading_time_minutes=len(summary.split()) / 200,  # Assuming 200 WPM reading speed
            key_topics=[],  # To be filled by topic extraction if needed
            sentiment="",   # To be filled by sentiment analysis if needed
            readability_score=self._calculate_readability(summary)
        )
        
        return {
            "summary": summary,
            "key_sentences": key_sentences,
            "metrics": metrics.__dict__
        }
    async def _abstractive_summarize(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform abstractive summarization using LLM"""
        text = input_data.get("text", "")
        style = input_data.get("style", "concise")
        
        if not text:
            raise ValueError("Input text is required for abstractive summarization")
        
        if style not in self.summary_styles:
            raise ValueError(f"Unsupported summary style: {style}")
        
        # Prepare prompt for LLM
        prompt = (
            f"Summarize the following text in a {style} manner, focusing on "
            f"{self.summary_styles[style]['focus']} and using a "
            f"{self.summary_styles[style]['tone']} tone:\n\n{text}\n\nSummary:"
        )
        
        # Call LLM service
        llm_response = await llm_service.generate_text(prompt, max_tokens=300)
        summary = llm_response.get("text", "").strip()
        
        # Calculate metrics
        metrics = SummaryMetrics(
            original_length=len(text.split()),
            summary_length=len(summary.split()),
            compression_ratio=len(summary.split()) / len(text.split()),
            reading_time_minutes=len(summary.split()) / 200,  # Assuming 200 WPM reading speed
            key_topics=[],  # To be filled by topic extraction if needed
            sentiment="",   # To be filled by sentiment analysis if needed
            readability_score=self._calculate_readability(summary)
        )
        
        return {
            "summary": summary,
            "metrics": metrics.__dict__
        }
    async def _multi_document_summarize(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize multiple documents together"""
        documents = input_data.get("documents", [])
        style = input_data.get("style", "concise")
        
        if not documents or not isinstance(documents, list):
            raise ValueError("A list of documents is required for multi-document summarization")
        
        if style not in self.summary_styles:
            raise ValueError(f"Unsupported summary style: {style}")
        
        combined_text = "\n\n".join(documents)
        
        # Prepare prompt for LLM
        prompt = (
            f"Summarize the following documents in a {style} manner, focusing on "
            f"{self.summary_styles[style]['focus']} and using a "
            f"{self.summary_styles[style]['tone']} tone:\n\n{combined_text}\n\nSummary:"
        )
        
        # Call LLM service
        llm_response = await llm_service.generate_text(prompt, max_tokens=500)
        summary = llm_response.get("text", "").strip()
        
        # Calculate metrics
        metrics = SummaryMetrics(
            original_length=len(combined_text.split()),
            summary_length=len(summary.split()),
            compression_ratio=len(summary.split()) / len(combined_text.split()),
            reading_time_minutes=len(summary.split()) / 200,  # Assuming 200 WPM reading speed
            key_topics=[],  # To be filled by topic extraction if needed
            sentiment="",   # To be filled by sentiment analysis if needed
            readability_score=self._calculate_readability(summary)
        )
        
        return {
            "consolidated_summary": summary,
            "metrics": metrics.__dict__
        }
    async def _extract_topics(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract main topics and themes from text"""
        text = input_data.get("text", "")
        
        if not text:
            raise ValueError("Input text is required for topic extraction")
        
        # Tokenize and filter stop words
        words = nltk.word_tokenize(text.lower())
        filtered_words = [word for word in words if word.isalnum() and word not in self.stop_words]
        
        # Frequency analysis
        word_freq = Counter(filtered_words)
        most_common = word_freq.most_common(10)
        topics = [word for word, freq in most_common]
        
        return {
            "topics": topics,
            "themes": topics,  # For simplicity, using same as topics
            "keywords": topics
        }
    async def _analyze_document(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document structure and content"""
        text = input_data.get("text", "")
        
        if not text:
            raise ValueError("Input text is required for document analysis")
        
        sentences = nltk.sent_tokenize(text)
        words = nltk.word_tokenize(text)
        paragraphs = text.split("\n\n")
        
        # Simple heading extraction (lines in all caps or starting with numbers)
        headings = re.findall(r'^(?:[A-Z\s]{2,}|[0-9]+\..+)$', text, re.MULTILINE)
        
        # Topic extraction
        main_topics = (await self._extract_topics({"text": text}))["topics"]
        
        structure = DocumentStructure(
            sections=[para.strip() for para in paragraphs if para.strip()],
            headings=headings,
            paragraphs=len(paragraphs),
            sentences=len(sentences),
            words=len(words),
            main_topics=main_topics
        )
        
        return {
            "structure": structure.__dict__
        }
    async def _extract_key_insights(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights and actionable items"""
        text = input_data.get("text", "")
        
        if not text:
            raise ValueError("Input text is required for key insights extraction")
        
        # Prepare prompt for LLM
        prompt = (
            f"Extract key insights and actionable items from the following text:\n\n{text}\n\nInsights:"
        )
        
        # Call LLM service
        llm_response = await llm_service.generate_text(prompt, max_tokens=300)
        insights = llm_response.get("text", "").strip()
        
        return {
            "insights": insights,
            "action_items": insights  # For simplicity, using same as insights
        }
    async def _categorize_content(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize and classify content"""
        text = input_data.get("text", "")
        
        if not text:
            raise ValueError("Input text is required for content categorization")
        
        # Prepare prompt for LLM
        prompt = (
            f"Categorize the following content into appropriate categories:\n\n{text}\n\nCategories:"
        )
        
        # Call LLM service
        llm_response = await llm_service.generate_text(prompt, max_tokens=200)
        categories = llm_response.get("text", "").strip().split(",")
        categories = [cat.strip() for cat in categories if cat.strip()]
        
        return {
            "categories": categories,
            "classification": categories  # For simplicity, using same as categories
        }
    def _frequency_based_extraction(self, sentences: List[str], num_sentences: int) -> List[str]:
        """Extract sentences based on word frequency"""
        text = " ".join(sentences)
        words = nltk.word_tokenize(text.lower())
        filtered_words = [word for word in words if word.isalnum() and word not in self.stop_words]
        
        word_freq = Counter(filtered_words)
        
        sentence_scores = {}
        for sentence in sentences:
            sentence_words = nltk.word_tokenize(sentence.lower())
            score = sum(word_freq.get(word, 0) for word in sentence_words)
            sentence_scores[sentence] = score
        
        # Select top N sentences
        ranked_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
        return ranked_sentences[:num_sentences]
    def _position_based_extraction(self, sentences: List[str], num_sentences: int) -> List[str]:
        """Extract sentences based on their position in the text"""
        # Simple heuristic: first and last sentences are often important
        selected_sentences = []
        if sentences:
            selected_sentences.append(sentences[0])
        if len(sentences) > 1:
            selected_sentences.append(sentences[-1])
        # Fill remaining slots with sentences from the middle
        mid_index = len(sentences) // 2
        if len(selected_sentences) < num_sentences and mid_index < len(sentences):
            selected_sentences.append(sentences[mid_index])
        return selected_sentences[:num_sentences]
    def _tfidf_extraction(self, sentences: List[str], num_sentences: int) -> List[str]:
        """Extract sentences using TF-IDF scoring"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        if not sentences:
            return []
        
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(sentences)
        sentence_scores = tfidf_matrix.sum(axis=1).A1
        ranked_sentences = [sentences[i] for i in sentence_scores.argsort()[::-1]]
        return ranked_sentences[:num_sentences]
    def _hybrid_extraction(self, sentences: List[str], num_sentences: int) -> List[str]:
        """Hybrid extraction combining frequency and position"""
        freq_sentences = self._frequency_based_extraction(sentences, num_sentences)
        pos_sentences = self._position_based_extraction(sentences, num_sentences)
        
        # Combine and deduplicate
        combined = list(dict.fromkeys(freq_sentences + pos_sentences))
        return combined[:num_sentences]
    def _calculate_readability(self, text: str) -> float:
        """Calculate Flesch Reading Ease score"""
        sentences = nltk.sent_tokenize(text)
        words = nltk.word_tokenize(text)
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        num_sentences = len(sentences)
        num_words = len(words)
        
        if num_sentences == 0 or num_words == 0:
            return 0.0
        
        # Flesch Reading Ease formula
        reading_ease = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (syllable_count / num_words)
        return round(reading_ease, 2)
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simple heuristic)"""
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        if word and word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count = 1
        return count
# Register the agent
summarizer_agent = SummarizerAgent()

asyncio.run(summarizer_agent.initialize())
# Register the agent
summarizer_agent = SummarizerAgent()
asyncio.run(summarizer_agent.initialize())

