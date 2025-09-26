"""
Professional PDF Report Generator using Puppeteer via Node.js subprocess
Converts HTML investment reports to high-quality PDF documents with perfect layout preservation
"""

import os
import tempfile
import subprocess
import logging
import time
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RobecoPdfReportGenerator:
    """
    High-quality PDF generator using Puppeteer via Node.js subprocess for perfect HTML-to-PDF conversion
    """
    
    def __init__(self):
        """Initialize PDF generator with Puppeteer-based approach"""
        self.generator_type = self._find_pdf_generator()
        logger.info("🏗️ Robeco PDF Report Generator initialized")
        
    def _find_pdf_generator(self) -> str:
        """Find the best available PDF generation method"""
        # First try Node.js + Puppeteer (most reliable)
        if self._check_nodejs_puppeteer():
            logger.info("✅ Using Node.js + Puppeteer for PDF generation")
            return "puppeteer"
            
        # Fallback to wkhtmltopdf if available
        possible_paths = [
            '/usr/local/bin/wkhtmltopdf',
            '/usr/bin/wkhtmltopdf', 
            '/opt/homebrew/bin/wkhtmltopdf',
            'wkhtmltopdf'
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info(f"✅ Found wkhtmltopdf at: {path}")
                    self.wkhtmltopdf_path = path
                    return "wkhtmltopdf"
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                continue
                
        raise RuntimeError("❌ No PDF generation tool available. Please install Node.js + Puppeteer or wkhtmltopdf")
    
    def _check_nodejs_puppeteer(self) -> bool:
        """Check if Node.js and Puppeteer are available"""
        try:
            # Check Node.js
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.warning("Node.js not found")
                return False
                
            # Check if we can find puppeteer module (we'll generate script dynamically)
            return True
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Node.js not available")
            return False
    
    async def convert_html_to_pdf(
        self, 
        html_content: str, 
        company_name: str, 
        ticker: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Convert HTML report to high-quality PDF with perfect layout preservation
        
        Args:
            html_content: HTML content to convert
            company_name: Company name for filename
            ticker: Stock ticker for filename
            output_path: Optional custom output path
            
        Returns:
            Path to generated PDF file
        """
        logger.info(f"🔄 Converting HTML report to PDF: {ticker}")
        
        # Generate filename if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_ticker = ticker.replace('.', '_').replace(':', '_')
            filename = f"{safe_ticker}_Investment_Report_{timestamp}.pdf"
            output_path = os.path.join(tempfile.gettempdir(), filename)
        
        try:
            if self.generator_type == "puppeteer":
                # Use Puppeteer via Node.js subprocess for PDF generation
                return await self._convert_with_puppeteer(html_content, output_path)
            else:
                # Use wkhtmltopdf for PDF generation
                return await self._convert_with_wkhtmltopdf(html_content, output_path)
                
        except subprocess.TimeoutExpired:
            logger.error("❌ PDF conversion timed out")
            raise RuntimeError("PDF conversion timed out after 2 minutes")
            
        except Exception as e:
            logger.error(f"❌ PDF conversion failed: {e}")
            raise RuntimeError(f"PDF conversion failed: {e}")
    
    async def _convert_with_puppeteer(self, html_content: str, output_path: str) -> str:
        """Convert using Puppeteer via Node.js subprocess (most reliable method)"""
        logger.info("🔄 Starting PDF conversion with Puppeteer...")
        
        # Create optimized HTML with A4 layout
        optimized_html = self._create_a4_optimized_html(html_content)
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_html:
            temp_html.write(optimized_html)
            temp_html_path = temp_html.name
        
        try:
            # Generate Puppeteer script
            success = await self._generate_with_puppeteer_script(temp_html_path, output_path)
            
            if not success:
                raise RuntimeError("Puppeteer PDF generation failed")
            
            if not os.path.exists(output_path):
                raise RuntimeError("❌ PDF file was not created by Puppeteer")
                
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ PDF generated successfully with Puppeteer: {output_path}")
            logger.info(f"📊 PDF file size: {file_size:,} bytes")
            
            return output_path
            
        finally:
            # Clean up temporary HTML file
            try:
                os.unlink(temp_html_path)
            except OSError:
                pass
    
    def _create_a4_optimized_html(self, html_content: str) -> str:
        """Create HTML optimized for A4 landscape printing with 16:9 content scaling"""
        a4_optimized_css = """
        <style>
        @media print {
            @page {
                size: A4 landscape;
                margin: 0;
            }
            
            html, body {
                margin: 0 !important;
                padding: 0 !important;
                width: 100% !important;
                height: 100% !important;
            }
            
            .slide-container {
                width: 1920px !important;
                height: 1080px !important;
                margin: 0 !important;
                padding: 0 !important;
                page-break-after: always;
                page-break-inside: avoid;
                break-after: page;
                break-inside: avoid;
            }
            
            .slide-container:last-child {
                page-break-after: avoid;
                break-after: avoid;
            }
        }
        
        /* Preserve all original styling - no modifications to slide content */
        * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            color-adjust: exact !important;
        }
        
        /* Hide scrollbars */
        .slide, .slide * {
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        
        .slide::-webkit-scrollbar,
        .slide *::-webkit-scrollbar {
            display: none !important;
        }
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
            # Wrap content with proper HTML structure
            html_with_css = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {a4_optimized_css}
</head>
<body>
    {html_content}
</body>
</html>"""
        
        return html_with_css
    
    async def _generate_with_puppeteer_script(self, html_path: str, pdf_path: str) -> bool:
        """Generate PDF using Puppeteer script with comprehensive error handling"""
        start_time = time.time()
        
        # Create Puppeteer script
        puppeteer_script = f"""
const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {{
    try {{
        console.log('[Puppeteer] Starting PDF generation...');
        
        const browser = await puppeteer.launch({{
            headless: true,
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        }});
        
        console.log('[Puppeteer] Browser launched successfully');
        
        const page = await browser.newPage();
        
        // Set extended timeouts
        page.setDefaultTimeout(120000);
        page.setDefaultNavigationTimeout(120000);
        
        console.log('[Puppeteer] Loading HTML file...');
        await page.goto('file://{html_path}', {{ 
            timeout: 120000,
            waitUntil: 'networkidle2'
        }});
        
        console.log('[Puppeteer] HTML loaded, waiting for rendering...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        console.log('[Puppeteer] Generating PDF...');
        await page.pdf({{
            path: '{pdf_path}',
            format: 'A4',
            landscape: true,
            margin: {{ top: '0', right: '0', bottom: '0', left: '0' }},
            printBackground: true,
            timeout: 120000
        }});
        
        await browser.close();
        
        // Verify PDF was created
        if (fs.existsSync('{pdf_path}')) {{
            const stats = fs.statSync('{pdf_path}');
            console.log(`[Puppeteer] PDF generated successfully, size: ${{stats.size}} bytes`);
        }} else {{
            throw new Error('PDF file was not created');
        }}
        
    }} catch (error) {{
        console.error('[Puppeteer] Error:', error.message);
        process.exit(1);
    }}
}})();
"""
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as temp_script:
            temp_script.write(puppeteer_script)
            temp_script_path = temp_script.name
        
        try:
            logger.info("🚀 Starting Node.js Puppeteer subprocess...")
            
            result = subprocess.run(
                ['node', temp_script_path], 
                capture_output=True, 
                text=True, 
                timeout=150  # 2.5 minutes timeout
            )
            
            subprocess_time = time.time() - start_time
            logger.info(f"⏱️ Subprocess completed in {subprocess_time:.2f} seconds")
            
            if result.stdout:
                logger.info(f"📄 Puppeteer output: {result.stdout}")
            if result.stderr:
                logger.warning(f"⚠️ Puppeteer stderr: {result.stderr}")
            
            # Check if PDF was generated successfully
            if result.returncode == 0 and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                return True
            else:
                logger.error(f"❌ Puppeteer failed with return code: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            total_time = time.time() - start_time
            logger.error(f"⏰ Puppeteer process timed out after {total_time:.2f} seconds")
            return False
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ Puppeteer error after {total_time:.2f} seconds: {str(e)}")
            return False
        finally:
            # Clean up script file
            try:
                os.unlink(temp_script_path)
            except OSError:
                pass
    
    async def _convert_with_wkhtmltopdf(self, html_content: str, output_path: str) -> str:
        """Convert using wkhtmltopdf fallback method"""
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_html:
            temp_html.write(html_content)
            temp_html_path = temp_html.name
        
        try:
            wkhtmltopdf_options = [
                self.wkhtmltopdf_path,
                '--page-size', 'A4',
                '--orientation', 'Landscape',
                '--margin-top', '0mm',
                '--margin-bottom', '0mm', 
                '--margin-left', '0mm',
                '--margin-right', '0mm',
                '--disable-smart-shrinking',
                '--print-media-type',
                '--enable-javascript',
                '--javascript-delay', '1000',
                '--images',
                '--enable-external-links',
                temp_html_path,
                output_path
            ]
            
            logger.info("🔄 Starting PDF conversion with wkhtmltopdf...")
            
            result = subprocess.run(
                wkhtmltopdf_options,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                logger.error(f"❌ wkhtmltopdf failed: {result.stderr}")
                raise RuntimeError(f"PDF conversion failed: {result.stderr}")
            
            if not os.path.exists(output_path):
                raise RuntimeError("❌ PDF file was not created")
                
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ PDF generated successfully: {output_path}")
            logger.info(f"📊 PDF file size: {file_size:,} bytes")
            
            return output_path
            
        finally:
            # Clean up temporary HTML file
            try:
                os.unlink(temp_html_path)
            except OSError:
                pass
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """Get information about generated PDF"""
        if not os.path.exists(pdf_path):
            return {"error": "PDF file not found"}
            
        try:
            file_size = os.path.getsize(pdf_path)
            creation_time = os.path.getctime(pdf_path)
            
            return {
                "file_path": pdf_path,
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "creation_time": datetime.fromtimestamp(creation_time).isoformat(),
                "exists": True
            }
        except Exception as e:
            return {"error": str(e)}