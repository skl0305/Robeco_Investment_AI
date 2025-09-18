"""
Robeco Bulk File Upload and Analysis System
Integrates with Google Gemini API for document analysis and feeds summaries to analysts
"""

import os
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import aiofiles
import hashlib
from pathlib import Path
try:
    import google.generativeai as genai
except ImportError:
    # Fallback to alternative import
    try:
        from google import genai
    except ImportError:
        genai = None
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

@dataclass
class FileAnalysisResult:
    """Represents the analysis result of a single file"""
    filename: str
    file_type: str
    file_size: int
    analysis_summary: str
    key_insights: List[str]
    financial_metrics: Dict[str, Any]
    risk_factors: List[str]
    upload_timestamp: datetime
    gemini_file_id: Optional[str] = None
    processing_time: float = 0.0
    confidence_score: float = 0.0

@dataclass
class BulkAnalysisSession:
    """Represents a bulk file analysis session"""
    session_id: str
    company_ticker: str
    upload_timestamp: datetime
    total_files: int
    processed_files: int = 0
    file_results: List[FileAnalysisResult] = field(default_factory=list)
    consolidated_summary: str = ""
    status: str = "processing"  # processing, completed, failed
    error_message: Optional[str] = None

class BulkFileProcessor:
    """
    Handles bulk file upload, processing with Google Gemini API, 
    and integration with existing Robeco analysts
    """
    
    def __init__(self, gemini_api_key: str = None):
        # Use the same API key system as other agents
        try:
            from .api_key.gemini_api_key import get_intelligent_api_key
            self.get_api_key = get_intelligent_api_key
            # get_intelligent_api_key returns (api_key, metadata) or None
            api_key_result = self.get_api_key(agent_type='bulk_processor')
            if api_key_result:
                # Safely extract API key from result
                if isinstance(api_key_result, tuple) and len(api_key_result) > 0:
                    self.gemini_api_key = api_key_result[0]  # Extract the API key from tuple
                elif isinstance(api_key_result, str):
                    self.gemini_api_key = api_key_result  # Direct string (compatibility)
                else:
                    logger.error("❌ Invalid API key format returned")
                    self.gemini_api_key = None
            else:
                logger.error("❌ No API key available from intelligent system")
                self.gemini_api_key = None
            logger.info(f"✅ Bulk processor initialized with intelligent API key system")
        except Exception as e:
            logger.warning(f"Failed to import intelligent API key system: {e}")
            # Fallback to environment variable
            self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
            self.get_api_key = None
        
        self.model = None
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info(f"✅ Gemini model initialized for bulk processing")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini model: {e}")
                self.model = None
        
        # Storage directories
        self.upload_dir = Path("/tmp/robeco_uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # Supported file types (based on Gemini API capabilities)
        self.supported_extensions = {
            '.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx', '.xls',
            '.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif',
            '.mp4', '.mov', '.avi', '.mkv', '.wmv'
        }
        
        # Active sessions storage
        self.active_sessions: Dict[str, BulkAnalysisSession] = {}
    
    def generate_session_id(self, company_ticker: str) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{company_ticker}_{timestamp}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"
    
    async def validate_files(self, files: List[UploadFile]) -> Dict[str, Any]:
        """Validate uploaded files against Gemini API constraints"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "total_size": 0,
            "file_count": len(files)
        }
        
        # Check file count (Gemini limit: 10 files per request)
        if len(files) > 10:
            validation_result["errors"].append(f"Too many files: {len(files)}. Maximum 10 files per batch.")
            validation_result["valid"] = False
        
        total_size = 0
        for file in files:
            # Check file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in self.supported_extensions:
                validation_result["warnings"].append(f"Unsupported file type: {file.filename}")
            
            # Estimate file size (Gemini limit: 100MB per file)
            if hasattr(file, 'size') and file.size:
                if file.size > 100 * 1024 * 1024:  # 100MB
                    validation_result["errors"].append(f"File too large: {file.filename} ({file.size/1024/1024:.1f}MB)")
                    validation_result["valid"] = False
                total_size += file.size
        
        validation_result["total_size"] = total_size
        return validation_result
    
    async def save_uploaded_files(self, files: List[UploadFile], session_id: str) -> List[str]:
        """Save uploaded files to temporary storage"""
        session_dir = self.upload_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        saved_paths = []
        for file in files:
            file_path = session_dir / file.filename
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            saved_paths.append(str(file_path))
            await file.seek(0)  # Reset file pointer
        
        return saved_paths
    
    async def upload_files_to_gemini(self, file_paths: List[str]) -> List[str]:
        """Upload files to Gemini API using the same retry pattern as other services"""
        gemini_file_ids = []
        from .api_key.gemini_api_key import get_intelligent_api_key
        
        for file_path in file_paths:
            max_retries = 20  # Use more retries to match other services
            logger.info(f"📁 Uploading file: {Path(file_path).name}")
            
            for attempt in range(max_retries):
                try:
                    # Get API key using SAME pattern as template_report_generator
                    key_result = get_intelligent_api_key(agent_type="bulk_upload", attempt=attempt, force_attempt=True)
                    if not key_result:
                        logger.error("❌ No API key available for file upload")
                        break
                    
                    api_key, key_info = key_result  # EXACT same unpacking
                    logger.info(f"📁 Upload attempt {attempt+1} using API key: {api_key[:8]}...{api_key[-4:]}")
                    
                    # Configure API key for upload (required for genai.upload_file)
                    genai.configure(api_key=api_key)
                    
                    # Upload file to Gemini
                    uploaded_file = genai.upload_file(path=file_path, display_name=Path(file_path).name)
                    gemini_file_ids.append(uploaded_file.name)
                    logger.info(f"✅ Uploaded {Path(file_path).name} to Gemini: {uploaded_file.name}")
                    
                    # Wait for processing (Gemini requirement)
                    while uploaded_file.state.name == "PROCESSING":
                        await asyncio.sleep(0.5)
                        uploaded_file = genai.get_file(uploaded_file.name)
                    
                    break  # Success, move to next file
                    
                except Exception as e:
                    error_message = str(e)
                    logger.warning(f"⚠️ Upload attempt {attempt + 1} failed for {file_path}: {error_message[:200]}...")
                    
                    # Suspend API key if it's clearly suspended
                    if "PERMISSION_DENIED" in error_message or "CONSUMER_SUSPENDED" in error_message:
                        # Extract API key from error message and suspend it
                        import re
                        key_match = re.search(r'key=([A-Za-z0-9_-]+)', error_message)
                        if key_match and self.get_api_key:
                            suspended_key = key_match.group(1)
                            try:
                                logger.info(f"🔄 API key failed (pure rotation will retry): {suspended_key[:8]}...{suspended_key[-4:]}")
                            except Exception as suspend_error:
                                logger.error(f"❌ Failed to suspend API key: {suspend_error}")
                    
                    if attempt == max_retries - 1:
                        error_detail = f"Failed to upload {Path(file_path).name} after {max_retries} attempts: {error_message}"
                        logger.error(f"❌ {error_detail}")
                        # Reset suspended keys as a last resort and try once more with fresh API key pool
                        if self.get_api_key:
                            try:
                                from .api_key.gemini_api_key import reset_suspended_keys
                                reset_suspended_keys()
                                logger.info("🔄 Reset suspended keys for bulk upload - will try again shortly")
                                raise Exception(f"Upload failed after retries: {error_detail}")
                            except Exception:
                                pass
                        raise Exception(f"File upload failed: {error_detail}")
                    await asyncio.sleep(2)  # Longer pause before retry for suspended keys
        
        return gemini_file_ids
    
    async def analyze_files_with_gemini_streaming(self, gemini_file_ids: List[str], company_ticker: str, websocket=None) -> Dict[str, Any]:
        """Analyze uploaded files using Gemini API following the same pattern as template_report_generator"""
        
        # Default error response to ensure we never return None
        default_error_response = {
            "analysis": "",
            "success": False,
            "error": "Unknown error occurred",
            "processed_files": 0
        }
        
        # OBJECTIVE FACT EXTRACTION - No analysis, just truth delivery
        analysis_prompt = f"""
Extract facts from documents for {company_ticker}. Be objective and unbiased. Report what the documents actually say, not your analysis.

For each document:

## Document: [filename]

**Executive Summary**
[2-3 sentences summarizing what this document is about and its main content]

**Key Takeaways** 
• [What the document states as main points]
• [Management statements or analyst conclusions as written]
• [Key findings or recommendations mentioned]
• [Important developments or changes reported]
• [Strategic initiatives or plans outlined]
• [Risks or challenges identified in the document]
• [Opportunities or catalysts mentioned]

**Data Points**
• [All financial numbers, percentages, dates mentioned]
• [Revenue figures, growth rates, margins as stated]
• [Earnings, guidance, forecasts, targets provided]
• [Valuation metrics, ratios, price targets given]
• [Market share, competitive data, industry metrics]
• [Operational metrics, user numbers, efficiency ratios]
• [Balance sheet items, debt levels, cash positions]

**Investment Implications**
• [What the document says about investment outlook]
• [Recommendations or ratings if provided]
• [Risk factors mentioned in the document]
• [Catalysts or events highlighted]
• [Timeline or milestones identified]

---

After all documents:

## Overall Summary

**Executive Summary**
[Factual overview of what all documents covered]

**Key Takeaways**
• [Main themes across all documents]
• [Consistent messages or findings]
• [Conflicting views if any exist]
• [Important developments revealed]

**Combined Data Points**  
• [All key numbers and metrics from documents]
• [Financial trends shown across sources]
• [Valuation ranges or targets mentioned]

**Investment Implications**
• [Investment outlook based on document content]
• [Risk factors identified across sources]
• [Opportunities or catalysts highlighted]
• [Recommendations or ratings provided]

Focus: Report facts objectively. Extract everything. Use bullet points extensively. No personal analysis - just deliver what the documents actually say.
        """
        
        try:
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "bulk_analysis_status",
                    "data": {"message": "Initializing Gemini AI analysis...", "progress": 30}
                }))
            
            # Get file objects with error handling
            if not gemini_file_ids:
                raise Exception("No Gemini file IDs available for analysis")
            
            files = []
            for file_id in gemini_file_ids:
                if not file_id:
                    logger.error(f"❌ Invalid file_id: {file_id}")
                    continue
                try:
                    file_obj = genai.get_file(file_id)
                    if file_obj:
                        files.append(file_obj)
                        logger.info(f"✅ Retrieved file object for: {file_id}")
                    else:
                        logger.error(f"❌ Failed to retrieve file object for: {file_id}")
                except Exception as e:
                    logger.error(f"❌ Error retrieving file {file_id}: {e}")
                    continue
            
            if not files:
                error_msg = f"No valid file objects retrieved for analysis. Attempted to retrieve {len(gemini_file_ids)} file IDs"
                logger.error(f"❌ {error_msg}")
                logger.error(f"❌ File IDs were: {gemini_file_ids}")
                if websocket:
                    await websocket.send_text(json.dumps({
                        "type": "bulk_analysis_error",
                        "data": {"error": error_msg}
                    }))
                return {
                    **default_error_response,
                    "error": error_msg
                }
            
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "bulk_analysis_status", 
                    "data": {"message": f"Starting AI analysis of {len(files)} documents...", "progress": 40}
                }))
            
            # Use the SAME retry pattern as template_report_generator.py
            from .api_key.gemini_api_key import get_intelligent_api_key
            
            max_retries = 100  # Try many keys until we find a working one
            for attempt in range(max_retries):
                try:
                    # Get API key with force_attempt to start with primary key (SAME as template_report_generator)
                    key_result = get_intelligent_api_key(agent_type="bulk_analysis", attempt=attempt, force_attempt=True)
                    if not key_result:
                        raise Exception("No API key available for bulk analysis")
                    
                    api_key, key_info = key_result  # EXACT same unpacking as template_report_generator
                    logger.info(f"📊 Bulk analysis attempt {attempt+1} using API key: {api_key[:8]}...{api_key[-4:]}")
                    
                    # Configure API key and use the model that works (like in __init__)
                    try:
                        genai.configure(api_key=api_key)
                        # Use the same pattern as in __init__ that works
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        logger.info(f"✅ Configured Gemini model for bulk analysis")
                    except Exception as config_error:
                        logger.error(f"⚠️ Model configuration failed on attempt {attempt+1}: {config_error}")
                        continue  # Try next API key
                    
                    # Send analysis started message
                    if websocket:
                        await websocket.send_text(json.dumps({
                            "type": "bulk_analysis_started", 
                            "data": {
                                "message": "🤖 AI is analyzing your documents...",
                                "company_ticker": company_ticker,
                                "file_count": len(files)
                            }
                        }))
                    
                    # Generate analysis using standard model (proven to work)
                    logger.info(f"📊 Starting Gemini analysis with {len(files)} files")
                    
                    try:
                        # Use the same generation pattern as the working __init__ method
                        response = model.generate_content(
                            [analysis_prompt] + files,
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.05,  # Lower for more focused analysis
                                top_p=0.9,         # Higher for more comprehensive coverage
                                max_output_tokens=200000  # 4x increase for ultra-comprehensive analysis
                            )
                        )
                        
                        if not response:
                            raise Exception("Gemini returned empty response")
                        
                        # Extract response text with fallback methods
                        response_text = None
                        if hasattr(response, 'text') and response.text:
                            response_text = response.text
                        elif hasattr(response, 'candidates') and response.candidates:
                            try:
                                response_text = response.candidates[0].content.parts[0].text
                            except (AttributeError, IndexError):
                                pass
                        
                        if not response_text:
                            raise Exception("No text content found in Gemini response")
                        
                        logger.info(f"✅ Gemini analysis completed: {len(response_text)} characters")
                        
                        # Send streaming simulation for better UX
                        if websocket:
                            chunk_size = max(100, len(response_text) // 10)  # 10 chunks minimum
                            for i in range(0, len(response_text), chunk_size):
                                chunk = response_text[i:i+chunk_size]
                                await websocket.send_text(json.dumps({
                                    "type": "bulk_analysis_chunk",
                                    "data": {
                                        "content_chunk": chunk,
                                        "chunk_id": (i // chunk_size) + 1,
                                        "progress": min(50 + (i / len(response_text)) * 45, 95)
                                    }
                                }))
                                await asyncio.sleep(0.1)  # Small delay for streaming effect
                        
                        # Analysis successful - return immediately
                        return {
                            "analysis": response_text,
                            "success": True,
                            "processed_files": len(files),
                            "streaming": False
                        }
                        
                    except Exception as generation_error:
                        error_msg = f"Gemini generation failed: {generation_error}"
                        logger.warning(f"⚠️ Generation error on attempt {attempt+1}: {error_msg}")
                        continue  # Try next API key
                    
                except Exception as e:
                    logger.warning(f"⚠️ Bulk analysis attempt {attempt+1} failed: {e}")
                    
                    # Check if we should continue retrying
                    if attempt < max_retries - 1:
                        continue  # Try next API key
                    else:
                        # All retries exhausted
                        error_msg = f"Bulk analysis failed after {max_retries} attempts: {e}"
                        logger.error(f"❌ {error_msg}")
                        if websocket:
                            await websocket.send_text(json.dumps({
                                "type": "bulk_analysis_error",
                                "data": {"error": error_msg}
                            }))
                        return {
                            **default_error_response,
                            "error": error_msg
                        }
            
            # This should never be reached due to max_retries, but just in case
            error_msg = "Unable to complete bulk analysis with any available API key"
            logger.error(f"❌ {error_msg}")
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "bulk_analysis_error", 
                    "data": {"error": error_msg}
                }))
            return {
                **default_error_response,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"Gemini analysis system error: {e}"
            logger.error(f"❌ {error_msg}")
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "bulk_analysis_error",
                    "data": {"error": error_msg}
                }))
            return {
                **default_error_response,
                "error": error_msg
            }
    
    async def process_analysis_results(self, analysis_text: str, files: List[UploadFile]) -> List[FileAnalysisResult]:
        """Process Gemini analysis results into structured format"""
        file_results = []
        
        try:
            # Try to parse JSON response from Gemini
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                json_text = analysis_text[json_start:json_end].strip()
                analysis_data = json.loads(json_text)
            else:
                # Fallback: create structured results from text
                analysis_data = {"documents": []}
        
        except json.JSONDecodeError:
            # Fallback parsing if JSON fails
            analysis_data = {"documents": []}
        
        # Create FileAnalysisResult objects
        for i, file in enumerate(files):
            file_result = FileAnalysisResult(
                filename=file.filename,
                file_type=Path(file.filename).suffix,
                file_size=getattr(file, 'size', 0),
                analysis_summary=analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text,
                key_insights=[],
                financial_metrics={},
                risk_factors=[],
                upload_timestamp=datetime.now()
            )
            
            # Extract specific insights if JSON parsing worked
            if analysis_data.get("documents") and i < len(analysis_data["documents"]):
                doc_data = analysis_data["documents"][i]
                file_result.key_insights = doc_data.get("key_insights", [])
                file_result.financial_metrics = doc_data.get("financial_metrics", {})
                file_result.risk_factors = doc_data.get("risk_factors", [])
                file_result.confidence_score = doc_data.get("confidence_score", 0.0)
            
            file_results.append(file_result)
        
        return file_results
    
    async def start_bulk_analysis(self, files: List[UploadFile], company_ticker: str, websocket=None) -> str:
        """
        Start bulk file analysis process
        Returns session_id for tracking progress
        """
        start_time = datetime.now()
        session_id = self.generate_session_id(company_ticker)
        
        # Create analysis session
        session = BulkAnalysisSession(
            session_id=session_id,
            company_ticker=company_ticker,
            upload_timestamp=start_time,
            total_files=len(files)
        )
        
        self.active_sessions[session_id] = session
        
        try:
            # Validate files
            validation = await self.validate_files(files)
            if not validation["valid"]:
                session.status = "failed"
                session.error_message = "; ".join(validation["errors"])
                return session_id
            
            # Save files temporarily
            file_paths = await self.save_uploaded_files(files, session_id)
            
            # Upload to Gemini API
            gemini_file_ids = await self.upload_files_to_gemini(file_paths)
            
            # Analyze with Gemini (with streaming)
            analysis_result = await self.analyze_files_with_gemini_streaming(gemini_file_ids, company_ticker, websocket)
            
            # Check if analysis_result is None or invalid
            if analysis_result is None:
                session.status = "failed"
                session.error_message = "Analysis failed: No result returned from Gemini"
            elif analysis_result.get("success", False):
                # Process results
                file_results = await self.process_analysis_results(analysis_result["analysis"], files)
                session.file_results = file_results
                session.consolidated_summary = analysis_result["analysis"]
                session.processed_files = len(files)
                session.status = "completed"
            else:
                session.status = "failed"
                session.error_message = analysis_result.get("error", "Unknown error")
            
            # Cleanup temporary files
            await self.cleanup_session_files(session_id)
            
        except Exception as e:
            logger.error(f"❌ Bulk analysis failed for session {session_id}: {e}")
            session.status = "failed"
            session.error_message = str(e)
        
        return session_id
    
    async def get_session_status(self, session_id: str) -> Optional[BulkAnalysisSession]:
        """Get analysis session status"""
        return self.active_sessions.get(session_id)
    
    async def cleanup_session_files(self, session_id: str):
        """Clean up temporary files for a session"""
        try:
            session_dir = self.upload_dir / session_id
            if session_dir.exists():
                import shutil
                shutil.rmtree(session_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup session {session_id}: {e}")
    
    def get_file_summary_for_analysts(self, session_id: str) -> Dict[str, Any]:
        """
        Get consolidated file analysis summary formatted for existing analysts
        This will be fed to the 12 analyst agents as additional context
        """
        session = self.active_sessions.get(session_id)
        if not session or session.status != "completed":
            return {}
        
        # Format for analyst consumption
        analyst_summary = {
            "session_info": {
                "company_ticker": session.company_ticker,
                "analysis_date": session.upload_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "total_documents": session.total_files
            },
            "consolidated_insights": {
                "key_findings": [],
                "financial_highlights": {},
                "risk_assessment": [],
                "investment_implications": []
            },
            "document_summaries": []
        }
        
        # Extract key insights from all files
        all_insights = []
        all_risks = []
        financial_data = {}
        
        for file_result in session.file_results:
            all_insights.extend(file_result.key_insights)
            all_risks.extend(file_result.risk_factors)
            financial_data.update(file_result.financial_metrics)
            
            analyst_summary["document_summaries"].append({
                "filename": file_result.filename,
                "summary": file_result.analysis_summary,
                "confidence": file_result.confidence_score
            })
        
        analyst_summary["consolidated_insights"]["key_findings"] = list(set(all_insights))
        analyst_summary["consolidated_insights"]["financial_highlights"] = financial_data
        analyst_summary["consolidated_insights"]["risk_assessment"] = list(set(all_risks))
        
        # Add consolidated summary
        analyst_summary["full_analysis"] = session.consolidated_summary
        
        return analyst_summary

# Global processor instance
bulk_processor = BulkFileProcessor()