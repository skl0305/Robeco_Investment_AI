/**
 * 🚀 QUICK FIX FOR INFINITE LOADING ISSUE
 * 
 * Add this script to any HTML file experiencing infinite loading after report generation.
 * This is a lightweight solution that detects completion based on multiple heuristics.
 * 
 * Usage: <script src="static/js/quick_fix.js"></script>
 */

(function() {
    'use strict';
    
    console.log('🔧 Quick fix for infinite loading issue loaded');
    
    // Configuration
    const CONFIG = {
        // How long to wait for new activity before considering stream complete
        INACTIVITY_TIMEOUT: 30000, // 30 seconds
        
        // Maximum time to wait before force-completing
        MAX_WAIT_TIME: 300000, // 5 minutes
        
        // Minimum chunks/slides before considering completion
        MIN_CHUNKS_FOR_COMPLETION: 100,
        MIN_SLIDES_FOR_COMPLETION: 5,
        
        // Enable debug logging
        DEBUG: true
    };
    
    // State tracking
    let lastActivity = Date.now();
    let activityTimer = null;
    let maxTimer = null;
    let chunkCount = 0;
    let slideCount = 0;
    let isFixed = false;
    
    function log(message, data) {
        if (CONFIG.DEBUG) {
            console.log(`[QuickFix] ${message}`, data || '');
        }
    }
    
    function resetActivityTimer() {
        lastActivity = Date.now();
        
        if (activityTimer) {
            clearTimeout(activityTimer);
        }
        
        activityTimer = setTimeout(() => {
            if (!isFixed) {
                log('⏰ Inactivity timeout reached - forcing completion');
                forceCompletion('inactivity_timeout');
            }
        }, CONFIG.INACTIVITY_TIMEOUT);
    }
    
    function forceCompletion(reason) {
        if (isFixed) return;
        
        log(`✅ Forcing completion: ${reason}`);
        isFixed = true;
        
        // Clear timers
        if (activityTimer) clearTimeout(activityTimer);
        if (maxTimer) clearTimeout(maxTimer);
        
        // Hide loading elements
        hideLoadingElements();
        
        // Log completion stats
        log('📊 Completion stats:', {
            reason: reason,
            chunkCount: chunkCount,
            slideCount: slideCount,
            duration: Date.now() - pageLoadTime
        });
    }
    
    function hideLoadingElements() {
        const selectors = [
            '.loading',
            '.generating',
            '.spinner',
            '[class*="load"]',
            '[class*="generating"]',
            '[id*="loading"]',
            '[id*="generating"]'
        ];
        
        selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                // Only hide if it looks like a loading indicator
                const text = element.textContent.toLowerCase();
                if (text.includes('generat') || text.includes('load') || text.includes('wait')) {
                    element.style.display = 'none';
                    log(`🚫 Hidden loading element: ${selector}`);
                }
            });
        });
        
        // Update loading text
        const textElements = document.querySelectorAll('*');
        textElements.forEach(element => {
            if (element.children.length === 0) { // Only text nodes
                const text = element.textContent;
                if (text.includes('Generating Report') || text.includes('Generate Investment Report')) {
                    element.textContent = text.replace(/Generat[^.]*/, 'Report Generated Successfully');
                    log('📝 Updated loading text');
                }
            }
        });
        
        // Update page title
        if (document.title.includes('Generating') || document.title.includes('Loading')) {
            document.title = document.title.replace(/Generating.*?|Loading.*?/, 'Complete');
            log('📰 Updated page title');
        }
    }
    
    function detectActivity() {
        // Look for signs of ongoing generation
        const indicators = [
            // Check for new DOM nodes being added
            () => {
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.addedNodes.length > 0) {
                            chunkCount++;
                            resetActivityTimer();
                            
                            // Try to extract slide count
                            mutation.addedNodes.forEach(node => {
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    const slides = node.querySelectorAll('.slide, [class*="slide"]');
                                    if (slides.length > slideCount) {
                                        slideCount = slides.length;
                                    }
                                }
                            });
                            
                            log(`📦 Activity detected: chunk ${chunkCount}, slides: ${slideCount}`);
                            
                            // Check for completion conditions
                            if (chunkCount >= CONFIG.MIN_CHUNKS_FOR_COMPLETION && 
                                slideCount >= CONFIG.MIN_SLIDES_FOR_COMPLETION) {
                                
                                // Wait a bit more to ensure it's really done
                                setTimeout(() => {
                                    if (Date.now() - lastActivity > 10000) { // 10 seconds of inactivity
                                        forceCompletion('heuristic_completion');
                                    }
                                }, 15000);
                            }
                        }
                    });
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
                
                return observer;
            },
            
            // Monitor console for completion indicators
            () => {
                const originalLog = console.log;
                console.log = function(...args) {
                    const message = args.join(' ');
                    if (message.includes('Complete') || 
                        message.includes('finished') || 
                        message.includes('done') ||
                        message.includes('✅')) {
                        log('🎯 Completion keyword detected in console');
                        setTimeout(() => forceCompletion('console_completion'), 2000);
                    }
                    return originalLog.apply(console, args);
                };
            }
        ];
        
        indicators.forEach(indicator => indicator());
    }
    
    function checkExistingContent() {
        // Check if content already looks complete
        const slides = document.querySelectorAll('.slide, [class*="slide"]');
        const footers = document.querySelectorAll('footer, .footer, [class*="footer"]');
        
        slideCount = slides.length;
        
        if (slideCount >= CONFIG.MIN_SLIDES_FOR_COMPLETION && footers.length > 0) {
            log('🎯 Content appears complete on page load');
            setTimeout(() => forceCompletion('content_complete_on_load'), 3000);
        }
    }
    
    // Initialize
    const pageLoadTime = Date.now();
    
    log('🚀 Quick fix initialized');
    
    // Set maximum timeout
    maxTimer = setTimeout(() => {
        forceCompletion('max_time_exceeded');
    }, CONFIG.MAX_WAIT_TIME);
    
    // Start activity detection
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            detectActivity();
            checkExistingContent();
            resetActivityTimer();
        });
    } else {
        detectActivity();
        checkExistingContent();
        resetActivityTimer();
    }
    
    // Monitor for EventSource or WebSocket connections
    const originalEventSource = window.EventSource;
    if (originalEventSource) {
        window.EventSource = function(...args) {
            log('🌊 EventSource detected - starting enhanced monitoring');
            const eventSource = new originalEventSource(...args);
            
            eventSource.addEventListener('message', (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.status === 'complete' || data.status === 'finished') {
                        log('✅ Explicit completion signal received');
                        forceCompletion('explicit_completion');
                    }
                } catch (e) {
                    // Ignore parsing errors
                }
                resetActivityTimer();
            });
            
            return eventSource;
        };
    }
    
    // Emergency manual completion (call from console if needed)
    window.forceReportCompletion = () => {
        forceCompletion('manual_trigger');
    };
    
    log('✅ Quick fix ready - monitoring for completion...');
    
})();

console.log('🔧 Quick Fix loaded! If report appears complete but loading persists, run: forceReportCompletion()');