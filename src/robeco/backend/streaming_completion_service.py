"""
🌊 STREAMING COMPLETION SERVICE
Backend service to ensure proper completion signals are sent in streaming responses
"""

import json
import time
import logging
from typing import Dict, Any, Generator, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class StreamingCompletionService:
    """
    Service to wrap streaming generators with proper completion signaling
    
    CRITICAL FIX: Ensures all streaming endpoints send explicit completion signals
    to prevent infinite loading states in the frontend.
    """
    
    @staticmethod
    def wrap_streaming_generator(
        generator: Generator,
        completion_data: Optional[Dict[str, Any]] = None,
        stream_type: str = "html_generation"
    ) -> Generator[str, None, None]:
        """
        Wrap a streaming generator to ensure proper completion signaling
        
        Args:
            generator: The original streaming generator
            completion_data: Additional data to include in completion signal
            stream_type: Type of stream for logging purposes
        
        Yields:
            Properly formatted streaming chunks with completion signal
        """
        start_time = time.time()
        chunk_count = 0
        last_chunk_data = None
        
        try:
            logger.info(f"🌊 Starting {stream_type} stream with completion wrapping")
            
            # Process all chunks from the original generator
            for chunk in generator:
                chunk_count += 1
                last_chunk_data = chunk
                
                # Ensure chunk is properly formatted
                if isinstance(chunk, dict):
                    chunk_json = json.dumps(chunk)
                    yield f"data: {chunk_json}\n\n"
                elif isinstance(chunk, str):
                    # If it's already formatted SSE, pass through
                    if chunk.startswith("data: "):
                        yield chunk
                    else:
                        # Wrap plain string in data field
                        chunk_data = {"content": chunk, "type": "content"}
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                else:
                    # Convert other types to string
                    chunk_data = {"content": str(chunk), "type": "content"}
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Log progress periodically
                if chunk_count % 50 == 0:
                    logger.debug(f"📊 {stream_type}: {chunk_count} chunks processed")
            
            # Generate completion statistics
            duration = time.time() - start_time
            stats = {
                "total_chunks": chunk_count,
                "duration_seconds": round(duration, 2),
                "chunks_per_second": round(chunk_count / duration, 2) if duration > 0 else 0,
                "stream_type": stream_type,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            # Add custom completion data if provided
            if completion_data:
                stats.update(completion_data)
            
            # Send explicit completion signal
            completion_signal = {
                "status": "complete",
                "message": f"{stream_type.replace('_', ' ').title()} completed successfully",
                "stats": stats,
                "completion_indicators": {
                    "stream_ended": True,
                    "generation_finished": True,
                    "ready_for_display": True
                }
            }
            
            logger.info(f"✅ {stream_type} completed: {chunk_count} chunks in {duration:.2f}s")
            yield f"data: {json.dumps(completion_signal)}\n\n"
            
        except Exception as e:
            # Send error signal if generation fails
            error_duration = time.time() - start_time
            error_signal = {
                "status": "error",
                "message": f"Stream error: {str(e)}",
                "error_type": type(e).__name__,
                "stats": {
                    "chunks_processed": chunk_count,
                    "duration_seconds": round(error_duration, 2),
                    "stream_type": stream_type,
                    "failed_at": datetime.utcnow().isoformat()
                }
            }
            
            logger.error(f"❌ {stream_type} failed after {chunk_count} chunks: {str(e)}")
            yield f"data: {json.dumps(error_signal)}\n\n"
            
        finally:
            # Always send final stream termination marker
            termination_signal = {
                "status": "stream_ended",
                "message": "Stream connection terminated",
                "final_stats": {
                    "total_chunks": chunk_count,
                    "stream_type": stream_type,
                    "terminated_at": datetime.utcnow().isoformat()
                }
            }
            
            yield f"data: {json.dumps(termination_signal)}\n\n"
            logger.info(f"🔚 {stream_type} stream terminated")
    
    @staticmethod
    def create_sse_response(generator: Generator, **kwargs) -> Generator[str, None, None]:
        """
        Create a Server-Sent Events response with proper headers and completion signaling
        
        Args:
            generator: The streaming generator to wrap
            **kwargs: Additional arguments for wrap_streaming_generator
        
        Returns:
            Generator yielding SSE-formatted chunks
        """
        # Send SSE headers information as first chunk (for debugging)
        headers_info = {
            "type": "stream_init",
            "message": "Server-Sent Events stream initialized",
            "timestamp": datetime.utcnow().isoformat(),
            "expected_headers": {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        }
        yield f"data: {json.dumps(headers_info)}\n\n"
        
        # Wrap the generator with completion signaling
        for chunk in StreamingCompletionService.wrap_streaming_generator(generator, **kwargs):
            yield chunk
    
    @staticmethod
    def wrap_html_generation(html_generator: Generator, project_id: str = None) -> Generator[str, None, None]:
        """
        Specific wrapper for HTML report generation streaming
        
        Args:
            html_generator: Generator yielding HTML chunks
            project_id: Project ID for logging purposes
        
        Returns:
            Generator with proper completion signaling for HTML generation
        """
        completion_data = {}
        if project_id:
            completion_data["project_id"] = project_id
        
        # Extract slide count and other metadata from chunks
        slide_count = 0
        html_length = 0
        
        def enhanced_generator():
            nonlocal slide_count, html_length
            
            for chunk in html_generator:
                # Track HTML metrics
                if isinstance(chunk, dict):
                    if chunk.get("html_chunk"):
                        html_length += len(chunk["html_chunk"])
                    if chunk.get("debug_info") and "slides=" in chunk.get("debug_info", ""):
                        import re
                        slide_match = re.search(r'slides=(\d+)', chunk["debug_info"])
                        if slide_match:
                            slide_count = int(slide_match.group(1))
                elif isinstance(chunk, str):
                    html_length += len(chunk)
                
                yield chunk
        
        # Update completion data with HTML-specific metrics
        completion_data.update({
            "final_slide_count": slide_count,
            "total_html_length": html_length,
            "generation_type": "html_report"
        })
        
        return StreamingCompletionService.wrap_streaming_generator(
            enhanced_generator(),
            completion_data=completion_data,
            stream_type="html_generation"
        )
    
    @staticmethod
    def create_timeout_checker(max_duration: int = 300) -> Generator[Dict[str, Any], None, None]:
        """
        Create a timeout checker that yields periodic status updates
        
        Args:
            max_duration: Maximum duration in seconds before timeout
        
        Yields:
            Status update chunks every 30 seconds
        """
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed >= max_duration:
                yield {
                    "status": "timeout",
                    "message": f"Stream exceeded maximum duration of {max_duration} seconds",
                    "elapsed_seconds": elapsed
                }
                break
            
            # Yield status update every 30 seconds
            if elapsed % 30 == 0 and elapsed > 0:
                yield {
                    "type": "status_update",
                    "message": f"Stream active for {elapsed:.0f} seconds",
                    "elapsed_seconds": elapsed,
                    "max_duration": max_duration,
                    "remaining_seconds": max_duration - elapsed
                }
            
            time.sleep(1)


# Decorator for easy integration with existing streaming endpoints
def ensure_completion_signal(stream_type: str = "general", **completion_kwargs):
    """
    Decorator to automatically wrap streaming endpoints with completion signaling
    
    Usage:
        @ensure_completion_signal(stream_type="html_generation")
        def my_streaming_endpoint():
            for chunk in generate_chunks():
                yield chunk
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get the original generator
            original_generator = func(*args, **kwargs)
            
            # Wrap it with completion signaling
            return StreamingCompletionService.wrap_streaming_generator(
                original_generator,
                completion_data=completion_kwargs,
                stream_type=stream_type
            )
        
        return wrapper
    return decorator


# Example usage for Flask endpoints
def create_streaming_response(generator: Generator, stream_type: str = "html_generation"):
    """
    Create a Flask streaming response with proper completion signaling
    
    Args:
        generator: The streaming generator
        stream_type: Type of stream for logging
    
    Returns:
        Flask Response object with proper SSE headers
    """
    try:
        from flask import Response
        
        wrapped_generator = StreamingCompletionService.create_sse_response(
            generator,
            stream_type=stream_type
        )
        
        return Response(
            wrapped_generator,
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
    except ImportError:
        # If Flask is not available, return raw generator
        logger.warning("Flask not available, returning raw generator")
        return StreamingCompletionService.create_sse_response(
            generator,
            stream_type=stream_type
        )