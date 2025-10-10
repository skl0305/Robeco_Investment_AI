/**
 * 🌊 STREAMING COMPLETION HANDLER
 * Comprehensive solution for detecting streaming completion and hiding loading states
 * 
 * CRITICAL FIX: Addresses the issue where streaming HTML generation completes
 * but the loading state persists indefinitely due to missing completion signals.
 */

class StreamingCompletionHandler {
    constructor(options = {}) {
        // Configuration
        this.options = {
            // Completion detection timeouts
            inactivityTimeout: options.inactivityTimeout || 30000, // 30 seconds
            maxStreamTime: options.maxStreamTime || 300000, // 5 minutes
            chunkInactivityTimeout: options.chunkInactivityTimeout || 10000, // 10 seconds
            
            // Completion indicators
            expectedSlideCount: options.expectedSlideCount || null,
            completionKeywords: options.completionKeywords || [
                'report-footer', 'completion-marker', 'stream-complete', 'generation-finished'
            ],
            
            // Callbacks
            onCompletion: options.onCompletion || (() => {}),
            onTimeout: options.onTimeout || (() => {}),
            onError: options.onError || (() => {}),
            
            // Debug
            debug: options.debug || false
        };
        
        // State tracking
        this.isStreaming = false;
        this.startTime = null;
        this.lastChunkTime = null;
        this.chunkCount = 0;
        this.currentSlideCount = 0;
        this.accumulatedHtml = '';
        
        // Timers
        this.inactivityTimer = null;
        this.maxTimeTimer = null;
        this.chunkTimer = null;
        
        // DOM elements
        this.loadingElement = null;
        this.previewElement = null;
        
        // Event listeners
        this.completionListeners = [];
        
        this.log('Streaming Completion Handler initialized');
    }
    
    /**
     * 🎯 START STREAMING MONITORING
     * Call this when streaming begins
     */
    startMonitoring(loadingElement, previewElement) {
        this.loadingElement = loadingElement;
        this.previewElement = previewElement;
        this.isStreaming = true;
        this.startTime = Date.now();
        this.lastChunkTime = Date.now();
        this.chunkCount = 0;
        this.currentSlideCount = 0;
        this.accumulatedHtml = '';
        
        this.log('🎯 Started streaming monitoring');
        
        // Set maximum streaming time timeout
        this.maxTimeTimer = setTimeout(() => {
            this.log('⏰ Maximum streaming time reached');
            this.handleCompletion('timeout_max_time');
        }, this.options.maxStreamTime);
        
        // Set initial inactivity timeout
        this.resetInactivityTimer();
        
        return this;
    }
    
    /**
     * 📦 PROCESS STREAMING CHUNK
     * Call this for each received chunk
     */
    processChunk(chunkData) {
        if (!this.isStreaming) return;
        
        this.chunkCount++;
        this.lastChunkTime = Date.now();
        
        // Reset chunk inactivity timer
        this.resetChunkTimer();
        this.resetInactivityTimer();
        
        // Extract HTML content from chunk
        let htmlContent = '';
        if (typeof chunkData === 'string') {
            htmlContent = chunkData;
        } else if (chunkData.html_chunk) {
            htmlContent = chunkData.html_chunk;
        } else if (chunkData.content) {
            htmlContent = chunkData.content;
        }
        
        this.accumulatedHtml += htmlContent;
        
        // Update slide count if available
        if (chunkData.debug_info && chunkData.debug_info.includes('slides=')) {
            const slideMatch = chunkData.debug_info.match(/slides=(\d+)/);
            if (slideMatch) {
                this.currentSlideCount = parseInt(slideMatch[1]);
            }
        }
        
        this.log(`📦 Processed chunk ${this.chunkCount}, slides: ${this.currentSlideCount}`);
        
        // Check for completion indicators
        this.checkCompletionIndicators(htmlContent, chunkData);
    }
    
    /**
     * 🔍 CHECK COMPLETION INDICATORS
     * Multiple strategies to detect completion
     */
    checkCompletionIndicators(htmlContent, chunkData) {
        // Strategy 1: Explicit completion signals
        if (chunkData.status === 'complete' || chunkData.status === 'finished') {
            this.log('✅ Completion detected: Explicit status signal');
            this.handleCompletion('explicit_status');
            return;
        }
        
        // Strategy 2: Completion keywords in HTML
        for (const keyword of this.options.completionKeywords) {
            if (htmlContent.includes(keyword)) {
                this.log(`✅ Completion detected: Keyword "${keyword}" found`);
                this.handleCompletion('completion_keyword');
                return;
            }
        }
        
        // Strategy 3: Footer detection (common end-of-document indicator)
        if (htmlContent.includes('</footer>') || htmlContent.includes('report-footer')) {
            this.log('✅ Completion detected: Footer found');
            this.handleCompletion('footer_detected');
            return;
        }
        
        // Strategy 4: HTML document end markers
        if (htmlContent.includes('</html>') || htmlContent.includes('</body>')) {
            this.log('✅ Completion detected: Document end marker');
            this.handleCompletion('document_end');
            return;
        }
        
        // Strategy 5: Expected slide count reached
        if (this.options.expectedSlideCount && this.currentSlideCount >= this.options.expectedSlideCount) {
            this.log(`✅ Completion detected: Expected slide count reached (${this.currentSlideCount})`);
            this.handleCompletion('slide_count_reached');
            return;
        }
        
        // Strategy 6: High slide count heuristic (likely complete)
        if (this.currentSlideCount >= 10 && this.chunkCount > 250) {
            this.log(`✅ Completion detected: High slide count heuristic (${this.currentSlideCount} slides, ${this.chunkCount} chunks)`);
            this.handleCompletion('heuristic_completion');
            return;
        }
    }
    
    /**
     * ⏰ RESET TIMERS
     */
    resetInactivityTimer() {
        if (this.inactivityTimer) {
            clearTimeout(this.inactivityTimer);
        }
        
        this.inactivityTimer = setTimeout(() => {
            this.log('⏰ Inactivity timeout reached');
            this.handleCompletion('timeout_inactivity');
        }, this.options.inactivityTimeout);
    }
    
    resetChunkTimer() {
        if (this.chunkTimer) {
            clearTimeout(this.chunkTimer);
        }
        
        this.chunkTimer = setTimeout(() => {
            this.log('⏰ Chunk inactivity timeout reached');
            this.handleCompletion('timeout_chunk_inactivity');
        }, this.options.chunkInactivityTimeout);
    }
    
    /**
     * ✅ HANDLE COMPLETION
     * Unified completion handler
     */
    handleCompletion(reason) {
        if (!this.isStreaming) return;
        
        this.log(`✅ Streaming completed: ${reason}`);
        this.isStreaming = false;
        
        // Clear all timers
        this.clearTimers();
        
        // Hide loading element
        this.hideLoadingState();
        
        // Calculate statistics
        const duration = Date.now() - this.startTime;
        const stats = {
            reason,
            duration,
            chunkCount: this.chunkCount,
            slideCount: this.currentSlideCount,
            htmlLength: this.accumulatedHtml.length
        };
        
        this.log('📊 Completion stats:', stats);
        
        // Trigger completion callback
        try {
            this.options.onCompletion(stats);
        } catch (error) {
            this.log('❌ Error in completion callback:', error);
        }
        
        // Notify completion listeners
        this.notifyCompletionListeners(stats);
    }
    
    /**
     * 🚫 HIDE LOADING STATE
     * Remove loading indicators from UI
     */
    hideLoadingState() {
        try {
            // Hide main loading element
            if (this.loadingElement) {
                this.loadingElement.style.display = 'none';
                this.log('🚫 Loading element hidden');
            }
            
            // Remove loading classes
            const loadingElements = document.querySelectorAll('.loading, .generating, .spinner, [class*="load"]');
            loadingElements.forEach(element => {
                element.style.display = 'none';
                element.classList.add('hidden');
            });
            
            // Update loading text
            const loadingTexts = document.querySelectorAll('[class*="loading-"], [class*="generating-"]');
            loadingTexts.forEach(element => {
                if (element.textContent.includes('Generating') || element.textContent.includes('Loading')) {
                    element.textContent = 'Report Generated Successfully';
                }
            });
            
            // Enable preview interaction
            if (this.previewElement) {
                this.previewElement.style.pointerEvents = 'auto';
                this.previewElement.style.opacity = '1';
            }
            
            this.log('✅ Loading state hidden successfully');
            
        } catch (error) {
            this.log('❌ Error hiding loading state:', error);
        }
    }
    
    /**
     * 🧹 CLEANUP
     */
    clearTimers() {
        if (this.inactivityTimer) {
            clearTimeout(this.inactivityTimer);
            this.inactivityTimer = null;
        }
        
        if (this.maxTimeTimer) {
            clearTimeout(this.maxTimeTimer);
            this.maxTimeTimer = null;
        }
        
        if (this.chunkTimer) {
            clearTimeout(this.chunkTimer);
            this.chunkTimer = null;
        }
    }
    
    /**
     * 🔄 MANUAL COMPLETION
     * Allow manual completion trigger
     */
    forceCompletion(reason = 'manual_trigger') {
        this.log(`🔄 Manual completion triggered: ${reason}`);
        this.handleCompletion(reason);
    }
    
    /**
     * 📢 EVENT LISTENERS
     */
    onCompletion(callback) {
        this.completionListeners.push(callback);
        return this;
    }
    
    notifyCompletionListeners(stats) {
        this.completionListeners.forEach(callback => {
            try {
                callback(stats);
            } catch (error) {
                this.log('❌ Error in completion listener:', error);
            }
        });
    }
    
    /**
     * 🐛 DEBUG LOGGING
     */
    log(message, data = null) {
        if (!this.options.debug) return;
        
        const timestamp = new Date().toISOString().substr(11, 12);
        console.log(`[${timestamp}] StreamingHandler:`, message, data || '');
    }
    
    /**
     * 📊 GET STATUS
     */
    getStatus() {
        return {
            isStreaming: this.isStreaming,
            chunkCount: this.chunkCount,
            slideCount: this.currentSlideCount,
            duration: this.startTime ? Date.now() - this.startTime : 0,
            htmlLength: this.accumulatedHtml.length
        };
    }
}

/**
 * 🌊 GLOBAL STREAMING HANDLER
 * Global instance for easy integration
 */
window.StreamingCompletionHandler = StreamingCompletionHandler;

// Create default instance
window.globalStreamingHandler = new StreamingCompletionHandler({
    debug: true,
    onCompletion: (stats) => {
        console.log('🎉 Report generation completed!', stats);
        
        // Hide any remaining loading indicators
        document.querySelectorAll('.loading, .generating, .spinner').forEach(el => {
            el.style.display = 'none';
        });
        
        // Update page title
        if (document.title.includes('Generating')) {
            document.title = document.title.replace('Generating...', 'Complete');
        }
    }
});

/**
 * 🔧 INTEGRATION HELPERS
 */
window.streamingHelpers = {
    /**
     * Quick integration for existing streaming handlers
     */
    patchExistingHandler: function(existingHandler) {
        const originalHandler = existingHandler;
        const completionHandler = window.globalStreamingHandler;
        
        return function(data) {
            // Call original handler
            if (originalHandler) {
                originalHandler(data);
            }
            
            // Process chunk for completion detection
            completionHandler.processChunk(data);
        };
    },
    
    /**
     * Auto-detect and patch streaming handlers
     */
    autoSetup: function() {
        // Look for common streaming handler patterns
        const patterns = [
            'handleReportGenerationStreaming',
            'handleStreamingData',
            'processStreamingChunk',
            'onStreamingUpdate'
        ];
        
        patterns.forEach(pattern => {
            if (window[pattern]) {
                console.log(`🔧 Patching streaming handler: ${pattern}`);
                window[pattern] = this.patchExistingHandler(window[pattern]);
            }
        });
        
        // Setup automatic monitoring for EventSource
        const originalEventSource = window.EventSource;
        window.EventSource = function(...args) {
            const eventSource = new originalEventSource(...args);
            window.globalStreamingHandler.startMonitoring(
                document.querySelector('.loading') || document.querySelector('[class*="loading"]'),
                document.querySelector('.preview') || document.querySelector('[class*="preview"]')
            );
            return eventSource;
        };
    }
};

// Auto-setup when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.streamingHelpers.autoSetup();
    });
} else {
    window.streamingHelpers.autoSetup();
}

console.log('🌊 Streaming Completion Handler loaded and ready');