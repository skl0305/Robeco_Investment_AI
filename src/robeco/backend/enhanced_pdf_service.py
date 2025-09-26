import os
import tempfile
import subprocess
import base64
import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedPdfService:
    """
    Enhanced PDF generation service using custom A4 format (1620x2291px)
    Matches DAKIN.html dimensions for proper Robeco report formatting
    """
    
    # CUSTOM A4 SETTINGS (MATCHING DAKIN.HTML FORMAT)
    A4_LANDSCAPE_SETTINGS = {
        'width_mm': 426,     # Custom width calculated from 1620px at 96 DPI (1620/96*25.4)
        'height_mm': 603,    # Custom height calculated from 2291px at 96 DPI (2291/96*25.4)
        'dpi': 96,           # Standard web DPI (not print quality)
        'width_px': 1620,    # Match DAKIN.html format
        'height_px': 2291,   # Match DAKIN.html format
    }
    
    # CONTENT SCALING (MATCHING DAKIN.HTML DIMENSIONS)
    CONTENT_16_9_SETTINGS = {
        'aspect_ratio': 1620/2291,         # 0.707:1 (portrait format from DAKIN.html)
        'fit_width': 1620,                 # Use full custom width
        'fit_height': 2291,                # Use full custom height
        'vertical_margin': 0,              # No margin needed - exact fit
    }
    
    # BACKWARD COMPATIBILITY
    DEFAULT_FRONTEND_SETTINGS = {
        'widthPx': CONTENT_16_9_SETTINGS['fit_width'],
        'heightPx': CONTENT_16_9_SETTINGS['fit_height'], 
        'bottomMarginPx': 0,
        'page_size': 'A4',
        'orientation': 'landscape',
        'quality': 'high'
    }
    
    @staticmethod
    def generate_pdf_from_html(html_content, project_id=None, settings=None):
        """
        Generate PDF from HTML using custom A4 format (1620x2291px) and return PDF binary data
        Matches DAKIN.html dimensions for proper Robeco report formatting
        """
        start_time = time.time()
        logger.info(f"🚀 Starting PDF generation from HTML")
        logger.info(f"📋 Project ID: {project_id}")
        logger.info(f"📝 HTML content length: {len(html_content) if html_content else 0} characters")
        logger.info(f"⚙️ Settings: {settings}")
        
        # Use custom format settings regardless of input settings
        a4_settings = EnhancedPdfService.A4_LANDSCAPE_SETTINGS
        content_settings = EnhancedPdfService.CONTENT_16_9_SETTINGS
        
        logger.info(f"🔧 Custom format settings: {a4_settings}")
        logger.info(f"📐 Content settings: {content_settings}")
        
        # Create temporary HTML file with custom-optimized CSS
        logger.info("📄 Creating optimized HTML file...")
        temp_html_path = EnhancedPdfService._create_a4_optimized_html(
            html_content, content_settings, a4_settings
        )
        temp_pdf_path = tempfile.mktemp(suffix='.pdf')
        logger.info(f"📁 Temp HTML: {temp_html_path}")
        logger.info(f"📁 Temp PDF: {temp_pdf_path}")
        
        pdf_generated = False
        
        try:
            # Only use Puppeteer generation
            logger.info("🚀 Calling Puppeteer generation...")
            pdf_generated, method_used = EnhancedPdfService._generate_with_a4_puppeteer(
                temp_html_path, temp_pdf_path, a4_settings
            )
            
            logger.info(f"📊 Puppeteer result: success={pdf_generated}, method={method_used}")
            
            if not pdf_generated:
                logger.error("❌ Puppeteer PDF generation failed - raising exception")
                raise Exception("Puppeteer PDF generation failed")
            
            # Read PDF data and return as bytes
            logger.info("📖 Reading generated PDF...")
            with open(temp_pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            
            total_time = time.time() - start_time
            logger.info(f"✅ PDF generation complete!")
            logger.info(f"📊 Final PDF size: {len(pdf_data)} bytes")
            logger.info(f"⏱️ Total generation time: {total_time:.2f} seconds")
            logger.info(f"🛠️ Method used: {method_used}")
            return pdf_data
            
        finally:
            # Clean up temporary files
            logger.info("🗑️ Cleaning up temporary files...")
            try:
                if os.path.exists(temp_html_path):
                    os.unlink(temp_html_path)
                    logger.info(f"🗑️ Removed temp HTML: {temp_html_path}")
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
                    logger.info(f"🗑️ Removed temp PDF: {temp_pdf_path}")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Cleanup error: {cleanup_error}")
                pass
    
    @staticmethod
    def _create_a4_optimized_html(html_content, content_settings, a4_settings):
        """
        Create HTML optimized for custom format printing (1620x2291px)
        Matches DAKIN.html dimensions for proper Robeco report formatting
        """
        
        # Custom format and content dimensions
        a4_width = a4_settings['width_px']      # 1620px
        a4_height = a4_settings['height_px']    # 2291px
        content_width = content_settings['fit_width']   # 1620px (full custom width)
        content_height = content_settings['fit_height'] # 2291px (full custom height)
        vertical_margin = content_settings['vertical_margin'] # 0px (exact fit)
        
        # CUSTOM CSS: Preserve original slide styling with custom dimensions (1620x2291px)
        a4_optimized_css = f"""
        <style>
        @media print {{
            @page {{
                size: {content_width}px {content_height}px;
                margin: 0;
            }}
            
            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                width: 100% !important;
                height: 100% !important;
            }}
            
            .slide-container {{
                width: {content_width}px !important;
                height: {content_height}px !important;
                margin: 0 !important;
                padding: 0 !important;
                page-break-after: always;
                page-break-inside: avoid;
                break-after: page;
                break-inside: avoid;
            }}
            
            .slide-container:last-child {{
                page-break-after: avoid;
                break-after: avoid;
            }}
        }}
        
        /* Preserve all original styling - no modifications to slide content */
        * {{
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            color-adjust: exact !important;
        }}
        
        /* 隐藏滚动条 */
        .slide, .slide * {{
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }}
        
        .slide::-webkit-scrollbar,
        .slide *::-webkit-scrollbar {{
            display: none !important;
        }}
        </style>
        """
        
        # Wrap content with A4 page structure
        if '<head>' in html_content:
            # Insert CSS after <head> tag
            html_with_css = html_content.replace('<head>', f'<head>{a4_optimized_css}')
        elif '<html>' in html_content:
            # Insert CSS after <html> tag
            html_with_css = html_content.replace('<html>', f'<html><head>{a4_optimized_css}</head>')
        else:
            # Wrap content with proper HTML structure and A4 page container
            html_with_css = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {a4_optimized_css}
</head>
<body>
    <div class="a4-page">
        {html_content}
    </div>
</body>
</html>"""
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        temp_file.write(html_with_css)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def _generate_with_a4_puppeteer(html_path, pdf_path, a4_settings):
        """
        Generate PDF using Puppeteer with custom format (1620x2291px) - DEBUG VERSION
        Uses custom dimensions matching DAKIN.html format with comprehensive logging
        """
        start_time = time.time()
        logger.info(f"🔧 Starting Puppeteer PDF generation")
        logger.info(f"📁 HTML input: {html_path}")
        logger.info(f"📄 PDF output: {pdf_path}")
        logger.info(f"📐 A4 settings: {a4_settings}")
        
        try:
            # Get the project root directory for puppeteer require
            # This file is in src/robeco/backend/, so go up 3 levels to get to the root
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            logger.info(f"🗂️ Project root directory: {backend_dir}")
            
            # Check if HTML file exists and get stats
            if os.path.exists(html_path):
                html_stats = os.stat(html_path)
                logger.info(f"✅ HTML file verified: {html_stats.st_size} bytes")
            else:
                logger.error(f"❌ HTML file missing: {html_path}")
                return False, None
            
            # ULTRA SIMPLIFIED A4 Landscape Puppeteer script - EXTENDED TIMEOUT WITH DEBUG
            # Try multiple ways to find puppeteer for server compatibility
            puppeteer_script = f"""
// EXTENDED TIMEOUT VERSION FOR PPT CONVERSION WITH COMPREHENSIVE DEBUG
const path = require('path');
const fs = require('fs');

// Debug timing
const startTime = Date.now();
function logWithTime(message) {{
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`[+${{elapsed}}s] ${{message}}`);
}}

// Try multiple paths to find puppeteer (server-compatible)
let puppeteer;
logWithTime('🔍 Looking for Puppeteer module...');
try {{
    // Method 1: Try relative path from current working directory
    puppeteer = require('puppeteer');
    logWithTime('✅ Found Puppeteer via require("puppeteer")');
}} catch (e1) {{
    try {{
        // Method 2: Try local node_modules
        puppeteer = require('./node_modules/puppeteer');
        logWithTime('✅ Found Puppeteer via "./node_modules/puppeteer"');
    }} catch (e2) {{
        try {{
            // Method 3: Try absolute path
            puppeteer = require('{os.path.join(backend_dir, 'node_modules', 'puppeteer')}');
            logWithTime('✅ Found Puppeteer via absolute path');
        }} catch (e3) {{
            console.error('❌ Cannot find puppeteer module:');
            console.error('  Method 1:', e1.message);
            console.error('  Method 2:', e2.message);  
            console.error('  Method 3:', e3.message);
            process.exit(1);
        }}
    }}
}}

(async () => {{
    try {{
        // Debug file check
        logWithTime(`📁 Checking HTML file: {html_path}`);
        if (fs.existsSync('{html_path}')) {{
            const stats = fs.statSync('{html_path}');
            logWithTime(`✅ HTML file exists, size: ${{stats.size}} bytes`);
        }} else {{
            throw new Error('HTML file does not exist');
        }}
        
        logWithTime('🚀 Launching browser...');
        const browser = await puppeteer.launch({{
            headless: true,
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--disable-features=VizDisplayCompositor',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--run-all-compositor-stages-before-draw',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
        }});
        logWithTime('✅ Browser launched successfully');
        
        logWithTime('📄 Creating new page...');
        const page = await browser.newPage();
        
        // Set extended timeouts for PPT conversion
        page.setDefaultTimeout(120000);  // 120 seconds (2 minutes)
        page.setDefaultNavigationTimeout(120000);  // 120 seconds
        logWithTime('⏱️ Set page timeouts to 120 seconds');
        
        // Monitor console messages from the page
        page.on('console', msg => {{
            logWithTime(`🖥️ Page console [${{msg.type()}}]: ${{msg.text()}}`);
        }});
        
        // Monitor page errors
        page.on('error', err => {{
            logWithTime(`❌ Page error: ${{err.message}}`);
        }});
        
        page.on('pageerror', err => {{
            logWithTime(`❌ Page script error: ${{err.message}}`);
        }});
        
        logWithTime('📄 Loading HTML file...');
        const response = await page.goto('file://{html_path}', {{ 
            timeout: 120000,  // 120 seconds timeout
            waitUntil: 'networkidle2'  // Wait until no network activity for 500ms
        }});
        
        logWithTime(`✅ HTML loaded, status: ${{response?.status() || 'unknown'}}`);
        
        // Check page dimensions and content
        const dimensions = await page.evaluate(() => {{
            return {{
                width: document.documentElement.scrollWidth,
                height: document.documentElement.scrollHeight,
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                slideCount: document.querySelectorAll('.slide, .slide-container').length
            }};
        }});
        
        logWithTime(`📐 Page dimensions: ${{dimensions.width}}x${{dimensions.height}}, viewport: ${{dimensions.innerWidth}}x${{dimensions.innerHeight}}, slides: ${{dimensions.slideCount}}`);
        
        logWithTime('⏳ Waiting for rendering (5 seconds)...');
        await new Promise(resolve => setTimeout(resolve, 5000));  // 5 seconds wait for rendering
        
        logWithTime('📋 Generating PDF...');
        await page.pdf({{
            path: '{pdf_path}',
            width: '{a4_settings['width_px']}px',
            height: '{a4_settings['height_px']}px', 
            margin: {{ top: '0', right: '0', bottom: '0', left: '0' }},
            printBackground: true,
            timeout: 120000  // 120 seconds timeout
        }});
        
        // Check generated PDF
        if (fs.existsSync('{pdf_path}')) {{
            const pdfStats = fs.statSync('{pdf_path}');
            logWithTime(`✅ PDF generated successfully, size: ${{pdfStats.size}} bytes`);
        }} else {{
            throw new Error('PDF file was not created');
        }}
        
        await browser.close();
        logWithTime('🏁 Browser closed, PDF generation complete');
    }} catch (error) {{
        logWithTime(`❌ Error during PDF generation: ${{error.message}}`);
        logWithTime(`❌ Error stack: ${{error.stack}}`);
        throw error;
    }}
}})().catch(err => {{
    console.error('❌ Final error:', err.message);
    console.error('❌ Stack trace:', err.stack);
    process.exit(1);
}});
"""
            
            temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8')
            temp_script.write(puppeteer_script)
            temp_script.close()
            logger.info(f"📝 Created Puppeteer script: {temp_script.name}")
            
            # Use the project root directory where node_modules exists
            # backend_dir is already calculated above
            node_modules_path = os.path.join(backend_dir, 'node_modules')
            logger.info(f"📦 Node modules path: {node_modules_path}")
            logger.info(f"📦 Node modules exists: {os.path.exists(node_modules_path)}")
            
            # Set environment variables to help Node.js find puppeteer and Chrome
            env = os.environ.copy()
            env['NODE_PATH'] = node_modules_path
            env['PUPPETEER_CACHE_DIR'] = os.path.join(backend_dir, '.cache', 'puppeteer')
            
            logger.info("🚀 Starting Node.js subprocess...")
            subprocess_start = time.time()
            
            result = subprocess.run(
                ['node', temp_script.name], 
                capture_output=True, 
                text=True, 
                timeout=150,  # 150 seconds total timeout (2.5 minutes) for PPT conversion
                cwd=backend_dir,
                env=env
            )
            
            subprocess_time = time.time() - subprocess_start
            logger.info(f"⏱️ Subprocess completed in {subprocess_time:.2f} seconds")
            logger.info(f"📤 Return code: {result.returncode}")
            
            if result.stdout:
                logger.info(f"📄 Stdout: {result.stdout}")
            if result.stderr:
                logger.warning(f"⚠️ Stderr: {result.stderr}")
            
            os.unlink(temp_script.name)  # Clean up script
            logger.info("🗑️ Cleaned up temporary script")
            
            # Verify PDF output
            if result.returncode == 0 and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                pdf_stats = os.stat(pdf_path)
                total_time = time.time() - start_time
                logger.info(f"✅ PDF generation successful!")
                logger.info(f"📊 PDF size: {pdf_stats.st_size} bytes")
                logger.info(f"⏱️ Total time: {total_time:.2f} seconds")
                return True, "A4 Landscape Puppeteer (Debug)"
            else:
                logger.error(f"❌ PDF generation failed")
                logger.error(f"📁 PDF exists: {os.path.exists(pdf_path)}")
                if os.path.exists(pdf_path):
                    logger.error(f"📊 PDF size: {os.path.getsize(pdf_path)} bytes")
                return False, None
                
        except subprocess.TimeoutExpired as e:
            total_time = time.time() - start_time
            logger.error(f"⏰ Puppeteer process timed out after {total_time:.2f} seconds")
            logger.error(f"⏰ Timeout limit was: 150 seconds")
            logger.error(f"⏰ Process output before timeout: {e.stdout if hasattr(e, 'stdout') else 'N/A'}")
            return False, None
        except FileNotFoundError as e:
            logger.error(f"📁 File not found error: {str(e)}")
            logger.error(f"📁 Make sure Node.js is installed and accessible")
            return False, None
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ Puppeteer error after {total_time:.2f} seconds: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            if hasattr(e, 'stderr'):
                logger.error(f"❌ Stderr: {e.stderr}")
            return False, None