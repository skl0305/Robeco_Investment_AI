/**
 * ROBECO ANALYSIS PERSISTENCE SYSTEM
 * Stores and retrieves analysis results for professional review
 * No mock data - real analysis storage and retrieval
 */

class RobecoAnalysisPersistence {
    constructor(sessionId = null) {
        // Use provided session ID or generate new one
        this.currentSession = sessionId || this.generateSessionId();
        this.storageKey = `robeco_analyses_${this.currentSession}`;
        this.init();
    }

    init() {
        console.log('📁 Initializing Robeco Analysis Persistence System');
        console.log('🆔 Session ID:', this.currentSession);
        
        // Clear old sessions (keep only current session)
        this.clearOldSessions();
        
        // Load existing analyses (should be empty for new session)
        this.loadExistingAnalyses();
        
        // Setup UI for analysis history
        this.setupAnalysisHistoryUI();
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    clearOldSessions() {
        // Remove all old robeco analysis sessions from localStorage
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('robeco_analyses_session_') && key !== this.storageKey) {
                keysToRemove.push(key);
            }
        }
        
        keysToRemove.forEach(key => {
            localStorage.removeItem(key);
            console.log('🗑️ Removed old session:', key);
        });
        
        if (keysToRemove.length > 0) {
            console.log(`🧹 Cleared ${keysToRemove.length} old analysis sessions`);
        }
    }

    saveAnalysis(analysisData) {
        console.log('💾 Saving analysis:', analysisData.ticker);
        
        const analyses = this.getStoredAnalyses();
        
        const analysisRecord = {
            id: `analysis_${Date.now()}`,
            sessionId: this.currentSession,
            timestamp: new Date().toISOString(),
            company: analysisData.company,
            ticker: analysisData.ticker,
            analystType: analysisData.analystType,
            objective: analysisData.objective || '',
            content: analysisData.content,
            sources: analysisData.sources || [],
            qualityScore: analysisData.qualityScore || 0.9,
            processingTime: analysisData.processingTime || 0,
            status: 'completed'
        };
        
        // Add to beginning of array (most recent first)
        analyses.unshift(analysisRecord);
        
        // Keep only last 50 analyses to manage storage
        if (analyses.length > 50) {
            analyses.splice(50);
        }
        
        // Save to localStorage with quota management
        try {
            const dataString = JSON.stringify(analyses);
            const dataSize = new Blob([dataString]).size;
            console.log(`💾 Saving ${dataSize} bytes to localStorage`);
            
            // If data is too large, reduce the number of analyses
            if (dataSize > 4.5 * 1024 * 1024) { // 4.5MB limit (localStorage is usually 5MB)
                console.warn('⚠️ Data too large, reducing to last 25 analyses');
                analyses.splice(25);
            }
            
            localStorage.setItem(this.storageKey, JSON.stringify(analyses));
        } catch (error) {
            if (error.name === 'QuotaExceededError') {
                console.error('❌ Storage quota exceeded, clearing old data and retrying...');
                
                // Emergency cleanup - keep only last 10 analyses
                analyses.splice(10);
                
                try {
                    localStorage.setItem(this.storageKey, JSON.stringify(analyses));
                    console.log('✅ Saved with reduced data after quota cleanup');
                } catch (retryError) {
                    console.error('❌ Still failed after cleanup:', retryError);
                    // Clear all stored analyses as last resort
                    localStorage.removeItem(this.storageKey);
                    analyses.splice(0, analyses.length - 1); // Keep only current analysis
                    localStorage.setItem(this.storageKey, JSON.stringify(analyses));
                }
            } else {
                throw error; // Re-throw if not quota error
            }
        }
        
        // Update UI
        this.updateAnalysisHistoryUI();
        
        console.log('✅ Analysis saved successfully');
        return analysisRecord.id;
    }

    getStoredAnalyses() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('❌ Error loading stored analyses:', error);
            return [];
        }
    }

    loadExistingAnalyses() {
        const analyses = this.getStoredAnalyses();
        console.log(`📊 Loaded ${analyses.length} existing analyses`);
        
        // Update UI if analyses exist
        if (analyses.length > 0) {
            this.updateAnalysisHistoryUI();
        }
    }

    getAnalysisById(analysisId) {
        const analyses = this.getStoredAnalyses();
        return analyses.find(analysis => analysis.id === analysisId);
    }

    getAnalysesByTicker(ticker) {
        const analyses = this.getStoredAnalyses();
        return analyses.filter(analysis => 
            analysis.ticker.toLowerCase() === ticker.toLowerCase()
        );
    }

    getSpecialistAnalysis(ticker, analystType) {
        const analyses = this.getStoredAnalyses();
        return analyses.find(analysis => 
            analysis.ticker.toLowerCase() === ticker.toLowerCase() &&
            analysis.analystType === analystType
        );
    }

    clearSpecialistAnalysis(ticker, analystType) {
        const analyses = this.getStoredAnalyses();
        const filteredAnalyses = analyses.filter(analysis => 
            !(analysis.ticker.toLowerCase() === ticker.toLowerCase() &&
              analysis.analystType === analystType)
        );
        
        localStorage.setItem(this.storageKey, JSON.stringify(filteredAnalyses));
        this.updateAnalysisHistoryUI();
        console.log(`🗑️ Cleared ${analystType} analysis for ${ticker}`);
    }

    setupAnalysisHistoryUI() {
        // Add analysis history section to sidebar
        const sidebar = document.querySelector('.workflow-nav');
        if (!sidebar) return;

        // Check if history section already exists
        if (document.getElementById('analysisHistorySection')) return;

        const historySection = document.createElement('div');
        historySection.className = 'nav-section';
        historySection.id = 'analysisHistorySection';
        historySection.innerHTML = `
            <div class="nav-section-title">Analysis History</div>
            <div id="analysisHistoryList">
                <div class="nav-item" style="opacity: 0.6; cursor: default;">
                    <i class="fas fa-clock"></i>
                    <div class="nav-item-text">No analyses yet</div>
                </div>
            </div>
            <div class="nav-item" onclick="robecoAnalysisPersistence.clearAllAnalyses()" style="color: #dc2626;">
                <i class="fas fa-trash"></i>
                <div class="nav-item-text">Clear History</div>
            </div>
        `;

        sidebar.appendChild(historySection);
    }

    updateAnalysisHistoryUI() {
        const historyList = document.getElementById('analysisHistoryList');
        if (!historyList) return;

        const analyses = this.getStoredAnalyses();
        
        if (analyses.length === 0) {
            historyList.innerHTML = `
                <div class="nav-item" style="opacity: 0.6; cursor: default;">
                    <i class="fas fa-clock"></i>
                    <div class="nav-item-text">No analyses yet</div>
                </div>
            `;
            return;
        }

        // Show last 10 analyses
        const recentAnalyses = analyses.slice(0, 10);
        
        historyList.innerHTML = recentAnalyses.map(analysis => {
            const timeAgo = this.getTimeAgo(new Date(analysis.timestamp));
            const analystIcon = this.getAnalystIcon(analysis.analystType);
            
            return `
                <div class="nav-item analysis-history-item" onclick="robecoAnalysisPersistence.loadAnalysis('${analysis.id}')" title="Click to reload analysis">
                    <i class="fas ${analystIcon}"></i>
                    <div>
                        <div class="nav-item-text">${analysis.ticker}</div>
                        <div class="nav-item-subtitle">${analysis.analystType} • ${timeAgo}</div>
                    </div>
                </div>
            `;
        }).join('');
    }

    getAnalystIcon(analystType) {
        const icons = {
            'fundamentals': 'fa-chart-bar',
            'industry': 'fa-industry', 
            'technical': 'fa-chart-line',
            'risk': 'fa-shield-alt',
            'esg': 'fa-leaf',
            'valuation': 'fa-calculator'
        };
        return icons[analystType] || 'fa-brain';
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }

    loadAnalysis(analysisId) {
        const analysis = this.getAnalysisById(analysisId);
        if (!analysis) {
            console.error('❌ Analysis not found:', analysisId);
            this.showNotification('Analysis not found', 'error');
            return;
        }

        console.log('📖 Loading analysis:', analysis.ticker, analysis.analystType);

        // Fill in project form if in setup phase
        if (document.getElementById('companyName')) {
            document.getElementById('companyName').value = analysis.company;
            document.getElementById('tickerSymbol').value = analysis.ticker;
            if (analysis.objective) {
                document.getElementById('investmentObjective').value = analysis.objective;
            }
        }

        // Navigate to specialist analysis phase
        if (typeof navigateToPhase === 'function') {
            navigateToPhase('specialist-analysis');
        }

        // Show the analysis interface
        const analysisInterface = document.getElementById('analysisInterface');
        if (analysisInterface) {
            analysisInterface.classList.add('active');
            
            // Set the title
            const titleElement = document.getElementById('analysisTitle');
            if (titleElement) {
                titleElement.textContent = `${analysis.analystType.title()} Analysis - ${analysis.ticker}`;
            }

            // Show completion state
            if (typeof updateProgress === 'function') {
                updateProgress('Analysis loaded from history', 100);
            }

            // Display the content
            const contentDiv = document.getElementById('streamingContent');
            if (contentDiv) {
                contentDiv.innerHTML = `
                    <div class="streaming-content">
                        <div style="background: var(--robeco-light-blue); padding: 12px; border-radius: 6px; margin-bottom: 16px;">
                            <strong>📖 Loaded from Analysis History</strong><br>
                            <small>Original analysis: ${new Date(analysis.timestamp).toLocaleString()}</small>
                        </div>
                        ${analysis.content}
                    </div>
                `;
            }

            // Show sources if available
            if (analysis.sources && analysis.sources.length > 0) {
                const sourcesDiv = document.getElementById('researchSources');
                const sourcesList = document.getElementById('sourcesList');
                
                if (sourcesDiv && sourcesList) {
                    sourcesDiv.style.display = 'block';
                    sourcesList.innerHTML = analysis.sources.map(source => `
                        <div class="source-item">
                            <div class="source-title">${source.title}</div>
                            <div class="source-meta">
                                <span class="credibility-score">${Math.round((source.credibility_score || 0.8) * 100)}%</span>
                                <span>${source.url || 'No URL'}</span>
                            </div>
                        </div>
                    `).join('');
                }
            }
        }

        this.showNotification(`Loaded ${analysis.analystType} analysis for ${analysis.ticker}`, 'success');
    }

    exportAnalysisHistory() {
        const analyses = this.getStoredAnalyses();
        
        const exportData = {
            export_metadata: {
                export_date: new Date().toISOString(),
                total_analyses: analyses.length,
                session_id: this.currentSession,
                robeco_workbench: 'Professional Investment Analysis History'
            },
            analyses: analyses
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
            type: 'application/json' 
        });
        
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `robeco_analysis_history_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        console.log('📥 Analysis history exported');
        this.showNotification('Analysis history exported successfully', 'success');
    }

    clearAllAnalyses() {
        if (confirm('Are you sure you want to clear all analysis history? This cannot be undone.')) {
            localStorage.removeItem(this.storageKey);
            this.updateAnalysisHistoryUI();
            console.log('🗑️ Analysis history cleared');
            this.showNotification('Analysis history cleared', 'info');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `analysis-notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#059669' : type === 'error' ? '#dc2626' : '#0ea5e9'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            font-size: 13px;
            font-weight: 500;
            max-width: 300px;
            animation: slideInRight 0.3s ease;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // Method to be called when analysis completes
    onAnalysisComplete(analysisData) {
        // Save the analysis
        const analysisId = this.saveAnalysis({
            company: analysisData.company,
            ticker: analysisData.ticker,
            analystType: analysisData.analyst_type,
            objective: analysisData.objective,
            content: document.getElementById('streamingContent')?.innerHTML || '',
            sources: analysisData.sources || [],
            qualityScore: analysisData.quality_score || 0.9,
            processingTime: analysisData.processing_time || 0
        });

        console.log('✅ Analysis saved with ID:', analysisId);
    }
}

// Global instance - will be initialized with session ID from main page
window.robecoAnalysisPersistence = null;

// Function to initialize with session ID
window.initAnalysisPersistence = function(sessionId) {
    window.robecoAnalysisPersistence = new RobecoAnalysisPersistence(sessionId);
    console.log('🔧 Analysis persistence initialized with session:', sessionId);
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .analysis-history-item:hover {
        background: rgba(0, 163, 163, 0.1) !important;
        border-left: 3px solid var(--robeco-turquoise) !important;
    }
`;
document.head.appendChild(style);

console.log('📁 Robeco Analysis Persistence System Loaded');