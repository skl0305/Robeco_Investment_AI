#!/usr/bin/env python3
"""
Robeco HTML-to-Word Report Generator
Converts generated HTML reports to Word documents (.docx) with exact layout preservation
Maintains Robeco professional styling, metrics grids, and institutional formatting
"""

import logging
import re
import io
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Word document generation
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION_START
from docx.oxml.shared import OxmlElement, qn
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

# HTML parsing
from bs4 import BeautifulSoup, NavigableString
import requests
from io import BytesIO
from PIL import Image

# Import InlineShape for image insertion
try:
    from docx.shared import Mm
    from docx.enum.dml import MSO_THEME_COLOR_INDEX
except ImportError:
    pass  # Optional imports

logger = logging.getLogger(__name__)

class RobecoWordReportGenerator:
    """
    Professional HTML-to-Word conversion for Robeco investment reports
    Preserves exact layout, styling, and structure from HTML reports
    """
    
    def __init__(self):
        # Image cache for company logos
        self._image_cache = {}
        
        # Flags for one-time elements
        self._first_analysis_item = False
        self._robeco_logo_added = False
        
        # Professional font configuration
        self.primary_font = 'Calibri'  # Fallback for Taz Semilight
        
        # Robeco brand colors (RGB values)
        self.robeco_colors = {
            'blue': RGBColor(0, 95, 144),         # #005F90
            'blue_darker': RGBColor(0, 61, 90),    # #003D5A
            'brown_black': RGBColor(59, 49, 42),   # #3B312A
            'orange': RGBColor(255, 140, 0),       # #FF8C00
            'text_dark': RGBColor(0, 0, 0),        # #000000
            'text_secondary': RGBColor(51, 51, 51), # #333333
            'accent_green': RGBColor(46, 125, 50),  # #2E7D32
            'accent_red': RGBColor(198, 40, 40),    # #C62828
        }
        
        # Font sizes mapping from HTML to Word (pt to pt conversion)
        self.font_size_mapping = {
            '57px': 57,     # report-title
            '27px': 27,     # report-subtitle  
            '25.5px': 26,   # section-title
            '20px': 20,     # bold-black-header.report-prose
            '18px': 18,     # bold-black-header, body
            '16.5pt': 17,   # report-footer
            '10pt': 10,     # metrics labels
        }
        
        logger.info("🏗️ Robeco Word Report Generator initialized")
    
    async def convert_html_to_word(
        self, 
        html_content: str, 
        company_name: str, 
        ticker: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Convert HTML report to Word document with exact layout preservation
        
        Args:
            html_content: Complete HTML report content
            company_name: Company name for document properties
            ticker: Stock ticker symbol
            output_path: Optional custom output path
            
        Returns:
            str: Path to generated Word document
        """
        logger.info(f"🔄 Converting HTML report to Word: {ticker}")
        
        try:
            # Parse HTML content
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Create new Word document
            doc = Document()
            
            # Set document properties
            self._set_document_properties(doc, company_name, ticker)
            
            # Configure page layout
            self._configure_page_layout(doc)
            
            # Process presentation container or find slides directly
            presentation = soup.find('div', class_='presentation-container')
            if presentation:
                # ENHANCED SLIDE DETECTION: Find ALL slide variations used in 3-call architecture
                slides = []
                
                # Method 1: Find all divs with "slide" in their class attribute
                all_slide_divs = presentation.find_all('div', class_=lambda c: c and 'slide' in ' '.join(c))
                slides.extend(all_slide_divs)
                
                # Method 1.5: SPECIFIC ID SEARCH - Find slides by expected IDs (critical for 3-call architecture)
                expected_slide_ids = ['portrait-page-1', 'portrait-page-1A', 'investment-highlights-pitchbook-page', 
                                     'catalyst-page', 'company-analysis-page', 'financial-highlights-table-page',
                                     'slide-industry-analysis-part1', 'slide-financial-income-statement', 
                                     'slide-financial-balance-sheet', 'cash-flow-page', 'dcf-analysis-page', 
                                     'bull-bear-analysis-comprehensive']
                
                for slide_id in expected_slide_ids:
                    # First try within presentation container
                    slide_by_id = presentation.find('div', id=slide_id)
                    if slide_by_id:
                        slides.append(slide_by_id)
                        logger.info(f"🎯 DIRECT ID MATCH (in presentation): Found slide with ID '{slide_id}'")
                    else:
                        # If not found in presentation, search entire document
                        slide_by_id = soup.find('div', id=slide_id)
                        if slide_by_id:
                            slides.append(slide_by_id)
                            logger.info(f"🎯 DIRECT ID MATCH (in document): Found slide with ID '{slide_id}'")
                
                # Method 2: Backup CSS selectors for specific patterns
                backup_slides = (
                    presentation.select('div.slide') +              # Basic slide
                    presentation.select('div.slide.report-prose') + # Slide with report-prose  
                    presentation.select('div[class*="slide"]') +    # Any div containing "slide"
                    presentation.select('div[id*="page"]')          # Slides with page IDs
                )
                slides.extend(backup_slides)
                
                logger.info(f"🔍 ENHANCED DETECTION: Found {len(all_slide_divs)} slide divs, {len(backup_slides)} backup slides")
                
            else:
                # If no presentation container, find slides directly in body
                slides = []
                
                # Method 1: Find all divs with "slide" in their class attribute
                all_slide_divs = soup.find_all('div', class_=lambda c: c and 'slide' in ' '.join(c))
                slides.extend(all_slide_divs)
                
                # Method 2: Backup selectors
                backup_slides = (
                    soup.select('div.slide') + 
                    soup.select('div.slide.report-prose') + 
                    soup.select('div[class*="slide"]') +
                    soup.select('div[id*="page"]')
                )
                slides.extend(backup_slides)
                
                logger.info(f"🔍 ENHANCED DETECTION (no container): Found {len(all_slide_divs)} slide divs, {len(backup_slides)} backup slides")
            
            # DEBUG: Show raw slides before deduplication
            logger.info(f"🔍 RAW SLIDES BEFORE DEDUP: {len(slides)} total")
            raw_slide_info = []
            for i, slide in enumerate(slides):
                slide_id = slide.get('id', f'no-id-{i}')
                slide_classes = slide.get('class', [])
                raw_slide_info.append(f"{slide_id}({' '.join(slide_classes)})")
            logger.info(f"   📋 Raw slide details: {raw_slide_info}")
            
            # Remove duplicates while preserving order using element IDs and content
            seen_elements = set()
            unique_slides = []
            for slide in slides:
                # Create unique identifier using element ID or content hash
                slide_id = slide.get('id') or str(hash(str(slide)[:100]))
                if slide_id not in seen_elements:
                    seen_elements.add(slide_id)
                    unique_slides.append(slide)
                    logger.info(f"✅ KEPT SLIDE: {slide_id} ({slide.get('class', [])})")
                else:
                    logger.info(f"🔄 SKIPPED DUPLICATE: {slide_id} ({slide.get('class', [])})")
            
            slides = unique_slides
            
            logger.info(f"📄 Processing {len(slides)} slides")
            
            # ENHANCED DEBUG: Log comprehensive slide information
            slide_info = []
            for i, slide in enumerate(slides):
                slide_id = slide.get('id', f'no-id-{i}')
                slide_classes = slide.get('class', [])
                slide_info.append(f"{slide_id}({' '.join(slide_classes)})")
            
            logger.info(f"🔍 ENHANCED SLIDE DETECTION RESULTS:")
            logger.info(f"   📄 Total slides found: {len(slides)}")
            logger.info(f"   📋 Slide details: {slide_info}")
            
            # Debug: Log HTML structure summary if we found fewer slides than expected
            expected_min_slides = 5  # We expect at least 5 slides from 3-call architecture
            if len(slides) < expected_min_slides:
                logger.warning(f"⚠️ Only found {len(slides)} slides (expected >= {expected_min_slides}), analyzing HTML...")
                
                # Count all divs with any slide-related content
                all_divs = soup.find_all('div')
                slide_related_divs = [div for div in all_divs if div.get('class') and any('slide' in cls for cls in div.get('class', []))]
                page_id_divs = [div for div in all_divs if div.get('id') and 'page' in div.get('id', '')]
                
                logger.info(f"🔍 HTML ANALYSIS:")
                logger.info(f"   📄 Total divs in HTML: {len(all_divs)}")
                logger.info(f"   📄 Divs with 'slide' in class: {len(slide_related_divs)}")
                logger.info(f"   📄 Divs with 'page' in ID: {len(page_id_divs)}")
                logger.info(f"   📄 Total HTML length: {len(html_content):,} characters")
                
                # Show first few div classes for debugging
                div_classes = [div.get('class', []) for div in all_divs[:15]]
                logger.info(f"   📋 First 15 div classes: {div_classes}")
                
                # Look for specific slide IDs we expect
                expected_ids = ['portrait-page-1', 'portrait-page-1A', 'investment-highlights-pitchbook-page', 
                               'catalyst-page', 'company-analysis-page', 'financial-highlights-table-page']
                found_ids = []
                for expected_id in expected_ids:
                    if soup.find('div', id=expected_id):
                        found_ids.append(expected_id)
                
                logger.info(f"   ✅ Expected slide IDs found: {found_ids}")
                logger.info(f"   ❌ Missing slide IDs: {set(expected_ids) - set(found_ids)}")
                
                # Check for presentation container
                if presentation:
                    logger.info("   ✅ Found presentation-container")
                    pres_divs = presentation.find_all('div')
                    logger.info(f"   📄 Divs inside presentation-container: {len(pres_divs)}")
                else:
                    logger.warning("   ⚠️ No presentation-container found, searching entire document")
            
            # Initialize header flag for the document
            self._header_added = False
            
            for i, slide in enumerate(slides):
                logger.info(f"🎯 Processing slide {i+1}/{len(slides)}")
                
                if i > 0:
                    # Add page break between slides
                    self._add_page_break(doc)
                
                # Process slide content
                self._process_slide(doc, slide, i+1)
            
            # Generate output filename
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"/tmp/{ticker}_Investment_Report_{timestamp}.docx"
            
            # Save document
            doc.save(output_path)
            logger.info(f"✅ Word document generated: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ HTML to Word conversion failed: {e}")
            raise
    
    def _set_document_properties(self, doc: Document, company_name: str, ticker: str):
        """Set document properties and metadata"""
        core_props = doc.core_properties
        core_props.title = f"{company_name} ({ticker}) - Investment Analysis"
        core_props.author = "Robeco Investment Analysis Platform"
        core_props.subject = f"Professional Investment Analysis - {ticker}"
        core_props.created = datetime.now()
        
    def _configure_page_layout(self, doc: Document):
        """Configure page layout to match HTML dimensions"""
        # Get page dimensions from HTML (1620px width, 2291px height)
        # Convert to inches (assuming 96 DPI: 1620px = 16.875", 2291px = 23.86")
        section = doc.sections[0]
        section.page_width = Inches(16.875)
        section.page_height = Inches(23.86)
        section.top_margin = Inches(1.09)    # 105px padding
        section.bottom_margin = Inches(0.47) # 45px footer space
        section.left_margin = Inches(1.02)   # 98px padding
        section.right_margin = Inches(1.02)  # 98px padding
        
    def _add_page_break(self, doc: Document):
        """Add page break between slides"""
        from docx.enum.text import WD_BREAK
        paragraph = doc.add_paragraph()
        run = paragraph.add_run()
        run.add_break(WD_BREAK.PAGE)
        
    def _process_slide(self, doc: Document, slide_soup, slide_number: int):
        """Process individual slide content"""
        logger.info(f"🎯 Processing slide {slide_number}")
        
        # Debug: Log slide structure
        slide_classes = slide_soup.get('class', [])
        slide_id = slide_soup.get('id', 'no-id')
        logger.info(f"🔍 Slide classes: {slide_classes}, ID: {slide_id}")
        
        # Extract and process ALL images in this slide
        self._process_all_images_in_slide(doc, slide_soup)
        
        # Initialize header flag for this instance
        if not hasattr(self, '_header_added'):
            self._header_added = False
        
        # Process slide header if exists
        header = slide_soup.find('div', class_='slide-header')
        if header:
            logger.info("✅ Found slide-header")
            self._process_slide_header(doc, header)
        else:
            logger.info("ℹ️ No slide-header found")
        
        # Process slide content if exists
        content = slide_soup.find('div', class_='slide-content')
        if content:
            logger.info("✅ Found slide-content")
            self._process_slide_content(doc, content)
        else:
            logger.info("ℹ️ No slide-content found, processing slide directly")
            # If no slide-content wrapper, process the slide itself
            self._process_slide_content(doc, slide_soup)
        
        # Process report footer if exists
        footer = slide_soup.find('div', class_='report-footer')
        if footer:
            logger.info("✅ Found report-footer")
            self._process_report_footer(doc, footer)
        else:
            logger.info("ℹ️ No report-footer found")
    
    def _process_slide_header(self, doc: Document, header_soup):
        """Process slide header with title and subtitle"""
        # Report title
        title = header_soup.find(class_='report-title')
        if title:
            p = doc.add_paragraph()
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            run = p.add_run(title.get_text().strip())
            run.font.size = Pt(57)
            run.font.name = self.primary_font
            run.font.bold = True
            run.font.color.rgb = self.robeco_colors['brown_black']
            p.space_after = Pt(0)
        
        # Report subtitle
        subtitle = header_soup.find(class_='report-subtitle')
        if subtitle:
            p = doc.add_paragraph()
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            run = p.add_run(subtitle.get_text().strip())
            run.font.size = Pt(27)
            run.font.name = self.primary_font
            run.font.color.rgb = self.robeco_colors['text_dark']
            p.space_after = Pt(22)
    
    def _process_slide_content(self, doc: Document, content_soup):
        """Process main slide content"""
        logger.info(f"🔍 Processing slide content, type: {type(content_soup)}")
        
        # Check if content_soup has children (BeautifulSoup element) or needs different processing
        if hasattr(content_soup, 'children'):
            elements_processed = 0
            for element in content_soup.children:
                if hasattr(element, 'name') and element.name is not None:
                    elements_processed += 1
                    logger.info(f"🎯 Processing element: {element.name}, classes: {element.get('class', [])}")
                    
                    # Section titles (prioritize specific classes)
                    if 'section-title' in element.get('class', []):
                        self._add_section_title(doc, element)
                    
                    # Report header container (only add once)
                    elif 'report-header-container' in element.get('class', []):
                        if not self._header_added:
                            self._add_report_header(doc, element)
                            self._header_added = True
                            logger.info("✅ Added report header (first slide only)")
                        else:
                            logger.info("🔄 Skipping duplicate report header")
                    
                    # Company header with logo and rating
                    elif 'company-header' in element.get('class', []):
                        self._add_company_header(doc, element)
                    
                    # Metrics grid
                    elif 'metrics-grid' in element.get('class', []):
                        self._add_metrics_grid(doc, element)
                    
                    # Introduction and chart container
                    elif 'intro-and-chart-container' in element.get('class', []):
                        self._add_intro_chart_container(doc, element)
                    
                    # Main content container (contains metrics, text, etc.)
                    elif element.name == 'main':
                        self._process_main_content(doc, element, slide_classes)
                    
                    # Analysis items  
                    elif 'analysis-item' in element.get('class', []):
                        self._add_analysis_item(doc, element)
                    
                    # Headers (h1, h2, h3, etc.)
                    elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        self._add_header(doc, element)
                    
                    # Tables
                    elif element.name == 'table':
                        self._add_table(doc, element)
                    
                    # Regular paragraphs and divs (catch-all for content)
                    elif element.name in ['p', 'div', 'span']:
                        # Only add if it has meaningful text content
                        text_content = element.get_text().strip()
                        if text_content and len(text_content) > 0:
                            self._add_paragraph(doc, element)
                    
                    # Lists
                    elif element.name in ['ul', 'ol']:
                        self._add_list(doc, element)
            
            logger.info(f"✅ Processed {elements_processed} elements in slide content")
        else:
            logger.warning("⚠️ content_soup has no children attribute, attempting text extraction")
            # Fallback: extract text directly
            text_content = str(content_soup) if content_soup else ""
            if text_content.strip():
                p = doc.add_paragraph(text_content.strip())
                logger.info(f"✅ Added fallback paragraph with {len(text_content)} characters")
    
    def _add_section_title(self, doc: Document, element):
        """Add section title with Robeco styling and proper alignment"""
        p = doc.add_paragraph()
        # Use intelligent alignment detection
        self._fix_element_alignment(p, element)
        run = p.add_run(element.get_text().strip())
        run.font.size = Pt(26)
        run.font.name = self.primary_font
        run.font.bold = True
        run.font.color.rgb = self.robeco_colors['blue_darker']
        p.space_after = Pt(18)
        
        # Add underline border (approximate CSS border-bottom)
        p_pr = p._element.get_or_add_pPr()
        p_bdr = OxmlElement('w:pBdr')
        bottom_border = OxmlElement('w:bottom')
        bottom_border.set(qn('w:val'), 'single')
        bottom_border.set(qn('w:sz'), '30')  # 5px equivalent
        bottom_border.set(qn('w:color'), '005F90')  # Robeco blue
        p_bdr.append(bottom_border)
        p_pr.append(p_bdr)
    
    def _add_metrics_grid(self, doc: Document, grid_soup):
        """Add metrics grid as a formatted table"""
        metrics_items = grid_soup.find_all(class_='metrics-item')
        if not metrics_items:
            return
        
        # Create 5-column table (as per CSS grid-template-columns: repeat(5, 1fr))
        rows_needed = (len(metrics_items) + 4) // 5
        table = doc.add_table(rows=rows_needed, cols=5)
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        
        # Add top border
        self._add_table_border(table, 'top')
        
        # Fill table with metrics
        for i, item in enumerate(metrics_items):
            row = i // 5
            col = i % 5
            cell = table.cell(row, col)
            
            # Get label and value
            label_elem = item.find(class_='label')
            value_elem = item.find(class_='value') 
            
            if label_elem and value_elem:
                # Add label
                label_p = cell.paragraphs[0]
                label_run = label_p.add_run(label_elem.get_text().strip())
                label_run.font.size = Pt(10)
                label_run.font.bold = True
                label_run.font.color.rgb = self.robeco_colors['text_secondary']
                
                # Add value
                value_p = cell.add_paragraph()
                value_run = value_p.add_run(value_elem.get_text().strip())
                value_run.font.size = Pt(14)  # Matches CSS font-size: 14pt
                value_run.font.name = self.primary_font
                value_run.font.bold = True
        
        # Add bottom border
        self._add_table_border(table, 'bottom')
    
    def _add_analysis_item(self, doc: Document, item_soup):
        """Add analysis item with proper formatting - ENHANCED: Direct two-column processing"""
        logger.info("🎯 ENHANCED: Processing analysis item with direct two-column layout")
        self._add_two_column_analysis_item(doc, item_soup)
    
    def _add_paragraph(self, doc: Document, p_soup):
        """Add paragraph with text formatting and proper alignment"""
        text = p_soup.get_text().strip()
        if not text:
            return
        
        p = doc.add_paragraph()
        # Use intelligent alignment detection
        self._fix_element_alignment(p, p_soup)
        
        # Handle citations and formatting
        if hasattr(p_soup, 'children'):
            for child in p_soup.children:
                if isinstance(child, NavigableString):
                    run = p.add_run(str(child))
                    run.font.size = Pt(18)
                    run.font.name = self.primary_font
                elif hasattr(child, 'name'):
                    if child.name == 'strong' or child.name == 'b':
                        run = p.add_run(child.get_text())
                        run.font.bold = True
                        run.font.size = Pt(18)
                        run.font.name = self.primary_font
                    elif child.name == 'em' or child.name == 'i':
                        run = p.add_run(child.get_text())
                        run.font.italic = True
                        run.font.size = Pt(18)
                        run.font.name = self.primary_font
                    else:
                        run = p.add_run(child.get_text())
                        run.font.size = Pt(18)
                        run.font.name = self.primary_font
        else:
            run = p.add_run(text)
            run.font.size = Pt(18)
            run.font.name = self.primary_font
        
        p.space_after = Pt(12)
    
    def _add_table(self, doc: Document, table_soup):
        """Add HTML table to Word document"""
        rows = table_soup.find_all('tr')
        if not rows:
            return
        
        # Create Word table
        max_cols = max(len(row.find_all(['td', 'th'])) for row in rows)
        table = doc.add_table(rows=len(rows), cols=max_cols)
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        
        # Fill table content
        for i, row_soup in enumerate(rows):
            cells = row_soup.find_all(['td', 'th'])
            for j, cell_soup in enumerate(cells):
                if j < max_cols:
                    cell = table.cell(i, j)
                    cell_p = cell.paragraphs[0]
                    run = cell_p.add_run(cell_soup.get_text().strip())
                    
                    # Header styling for th elements
                    if cell_soup.name == 'th':
                        run.font.bold = True
                        run.font.color.rgb = self.robeco_colors['blue_darker']
                    
                    run.font.size = Pt(14)
                    run.font.name = self.primary_font
    
    def _add_header(self, doc: Document, header_element):
        """Add header element (h1, h2, h3, etc.) with appropriate styling and alignment"""
        text = header_element.get_text().strip()
        if not text:
            return
            
        p = doc.add_paragraph()
        # Use intelligent alignment detection
        self._fix_element_alignment(p, header_element)
        run = p.add_run(text)
        run.font.name = self.primary_font
        run.font.bold = True
        run.font.color.rgb = self.robeco_colors['blue_darker']
        
        # Size based on header level
        header_level = int(header_element.name[1])  # h1 -> 1, h2 -> 2, etc.
        sizes = {1: 28, 2: 24, 3: 20, 4: 18, 5: 16, 6: 14}
        run.font.size = Pt(sizes.get(header_level, 18))
        
        p.space_after = Pt(16)
    
    def _add_list(self, doc: Document, list_element):
        """Add list (ul or ol) to Word document with enhanced formatting"""
        # Check if this is within a bullet-list-square container
        parent_classes = []
        current = list_element.parent
        while current and hasattr(current, 'get'):
            parent_classes.extend(current.get('class', []))
            current = getattr(current, 'parent', None)
        
        is_special_bullet = 'bullet-list-square' in parent_classes
        
        items = list_element.find_all('li')
        for item in items:
            text = item.get_text().strip()
            if text:
                p = doc.add_paragraph()
                # Use intelligent alignment for list items
                if is_special_bullet:
                    self._fix_element_alignment(p, item)
                else:
                    p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                
                # Add bullet or number with special formatting for bullet-list-square
                if list_element.name == 'ul':
                    p.style = doc.styles['List Bullet']
                else:
                    p.style = doc.styles['List Number']
                
                # Process text with potential formatting (bold, italic)
                if is_special_bullet:
                    # Use formatted text processing for special lists
                    self._add_formatted_text_to_paragraph(p, item)
                else:
                    # Standard list formatting
                    run = p.add_run(text)
                    run.font.size = Pt(16)
                    run.font.name = self.primary_font
                    run.font.color.rgb = self.robeco_colors['text_dark']
                
                # Add extra spacing for special bullet lists
                if is_special_bullet:
                    p.space_after = Pt(8)
    
    def _process_report_footer(self, doc: Document, footer_soup):
        """Add report footer"""
        footer_text = footer_soup.get_text().strip()
        if footer_text:
            p = doc.add_paragraph()
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run = p.add_run(footer_text)
            run.font.size = Pt(17)
            run.font.name = self.primary_font
            run.font.color.rgb = self.robeco_colors['text_secondary']
            
            # Add top border
            p_pr = p._element.get_or_add_pPr()
            p_bdr = OxmlElement('w:pBdr')
            top_border = OxmlElement('w:top')
            top_border.set(qn('w:val'), 'single')
            top_border.set(qn('w:sz'), '30')  # 5px equivalent
            top_border.set(qn('w:color'), '005F90')  # Robeco blue
            p_bdr.append(top_border)
            p_pr.append(p_bdr)
    
    def _add_table_border(self, table, position: str):
        """Add border to table (top or bottom)"""
        tbl_pr = table._element.find(qn('w:tblPr'))
        if tbl_pr is None:
            tbl_pr = OxmlElement('w:tblPr')
            table._element.insert(0, tbl_pr)
        
        tbl_borders = tbl_pr.find(qn('w:tblBorders'))
        if tbl_borders is None:
            tbl_borders = OxmlElement('w:tblBorders')
            tbl_pr.append(tbl_borders)
        
        border = OxmlElement(f'w:{position}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '30')  # 5px equivalent
        border.set(qn('w:color'), '005F90')  # Robeco blue
        tbl_borders.append(border)

    def _add_report_header(self, doc: Document, header_soup):
        """Add report header with proper Robeco styling and logos"""
        # Process Robeco logo if present - but ONLY once per document
        if not hasattr(self, '_robeco_logo_added'):
            self._robeco_logo_added = False
            
        if not self._robeco_logo_added:
            robeco_logo_container = header_soup.find(class_='robeco-logo-container')
            if robeco_logo_container:
                # Try to find actual Robeco logo image
                robeco_img = robeco_logo_container.find('img')
                if robeco_img:
                    img_src = robeco_img.get('src', '')
                    p = doc.add_paragraph()
                    p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT  # Robeco logo is positioned top-right
                    success = self._download_and_insert_image_inline(p, img_src, "Robeco Logo", Inches(1.2))
                    if not success:
                        # Fallback to text
                        run = p.add_run("ROBECO")
                        run.font.size = Pt(24)
                        run.font.name = self.primary_font
                        run.font.bold = True
                        run.font.color.rgb = self.robeco_colors['blue_darker']
                    p.space_after = Pt(12)
                    self._robeco_logo_added = True
                    logger.info("✅ Added Robeco logo to document header (once only)")
                else:
                    # No image, use text fallback
                    p = doc.add_paragraph("ROBECO")
                    p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
                    run = p.runs[0]
                    run.font.size = Pt(24)
                    run.font.name = self.primary_font
                    run.font.bold = True
                    run.font.color.rgb = self.robeco_colors['blue_darker']
                    p.space_after = Pt(12)
                    self._robeco_logo_added = True
                    logger.info("✅ Added Robeco text logo to document header (once only)")
        else:
            logger.info("🔄 Skipping duplicate Robeco logo")
        
        # Process company header within the report header
        company_header = header_soup.find(class_='company-header')
        if company_header:
            self._add_company_header(doc, company_header)
        else:
            # Search for company header in broader scope
            parent = header_soup.parent if header_soup.parent else header_soup
            broader_company_header = parent.find(class_='company-header') if hasattr(parent, 'find') else None
            if broader_company_header:
                self._add_company_header(doc, broader_company_header)
    
    def _add_company_header(self, doc: Document, header_soup):
        """Add company header with proper flex layout: icon+name left, rating right"""
        logger.info("🏢 Adding company header with proper flex layout")
        
        # Create table to replicate CSS flex layout: display: flex, align-items: center, gap: 12px
        table = doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        
        # Set column widths for proper layout
        usable_width = Inches(7.5)  # Full page width minus margins
        left_width = Inches(5.0)    # Space for icon + name
        right_width = Inches(2.5)   # Space for rating
        
        table.columns[0].width = left_width
        table.columns[1].width = right_width
        
        # Hide table borders
        self._hide_table_borders(table)
        
        # LEFT CELL: Company icon + name
        left_cell = table.cell(0, 0)
        left_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        # Add company icon and name together
        self._add_company_icon_to_cell(left_cell, header_soup)
        
        # RIGHT CELL: Investment rating
        right_cell = table.cell(0, 1)
        right_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        rating_elem = header_soup.find(class_='rating')
        if rating_elem:
            rating_p = right_cell.paragraphs[0]
            rating_p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT  # Align to right
            rating_run = rating_p.add_run(rating_elem.get_text().strip())
            rating_run.font.size = Pt(20)
            rating_run.font.name = self.primary_font
            rating_run.font.bold = True
            
            # Color based on rating text
            rating_text = rating_elem.get_text().strip().upper()
            if 'UNDERWEIGHT' in rating_text or 'UNDERPERFORM' in rating_text:
                rating_run.font.color.rgb = RGBColor(198, 40, 40)  # Red for negative rating
            elif 'OVERWEIGHT' in rating_text or 'OUTPERFORM' in rating_text:
                rating_run.font.color.rgb = RGBColor(76, 175, 80)  # Green for positive rating  
            else:
                rating_run.font.color.rgb = RGBColor(255, 152, 0)  # Orange for neutral rating
        
        # Add spacing after header
        spacing_para = doc.add_paragraph()
        spacing_para.space_after = Pt(16)
    
    def _add_company_icon_to_cell(self, cell, header_soup):
        """Add company icon and name to a table cell with proper inline layout"""
        try:
            # Look for company icon (Clearbit logo)
            img_tags = header_soup.find_all('img')
            
            for img in img_tags:
                img_src = img.get('src', '')
                img_alt = img.get('alt', '')
                img_classes = img.get('class', [])
                
                logger.info(f"📸 Found img: src='{img_src}', alt='{img_alt}', classes='{img_classes}'")
                
                # Check if it's a company icon (clearbit or has 'icon' class)
                if ('clearbit.com' in img_src or 'icon' in img_classes or 
                    'icon' in img_alt.lower() or img_src.endswith('.co.jp')):
                    
                    # Create inline company icon with name in the cell
                    company_name_elem = header_soup.find('h1', class_='name') or header_soup.find(class_='name')
                    if company_name_elem:
                        p = cell.paragraphs[0]
                        p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                        
                        # Generate intelligent fallback URLs
                        company_name = company_name_elem.get_text().strip()
                        fallback_urls = self._generate_intelligent_logo_fallbacks(img_src, company_name)
                        logger.info(f"🎯 Generated {len(fallback_urls)} intelligent logo fallbacks for '{company_name}'")
                        
                        # Try each fallback URL
                        icon_added = False
                        for i, fallback_url in enumerate(fallback_urls):
                            logger.info(f"📸 Downloading image: {fallback_url}")
                            success = self._download_and_insert_image_inline(p, fallback_url, img_alt, Inches(0.4))
                            if success:
                                logger.info(f"✅ Success with fallback URL {i}: {fallback_url}")
                                icon_added = True
                                break
                        
                        # Add company name next to icon
                        if icon_added:
                            # Add space between icon and name
                            p.add_run(" ")
                        
                        name_run = p.add_run(company_name)
                        name_run.font.size = Pt(20)
                        name_run.font.name = self.primary_font
                        name_run.font.bold = True
                        name_run.font.color.rgb = self.robeco_colors['text_dark']
                        
                        if icon_added:
                            logger.info(f"✅ Added company icon with name: {img_alt}")
                        else:
                            logger.info(f"⚠️ Added company name without icon: {company_name}")
                        return True
                        
        except Exception as e:
            logger.error(f"❌ Company icon insertion failed: {e}")
            return False
    
    def _add_intro_chart_container(self, doc: Document, container_soup):
        """Add introduction and chart container with proper 2-column layout (60%/40% split)"""
        logger.info("🔍 Processing intro-and-chart-container with flex layout preservation")
        
        # Extract content from both columns
        intro_block = container_soup.find(class_='intro-text-block')
        chart_area = container_soup.find(class_='chart-area') or container_soup.find(class_='stock-chart-container')
        
        # Create 2-column table to replicate CSS flexbox layout
        table = doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Set column widths to match CSS flex layout (50% intro, 50% chart with 30px gap)
        # Total page width is approximately 9 inches, minus margins = ~7.5 inches usable
        # Account for 30px gap = ~0.4 inches gap between columns
        usable_width = Inches(7.1)  # 7.5 - 0.4 for gap
        intro_width = Inches(3.55)  # 50% of usable width (flex: 1) = 7.1 / 2
        chart_width = Inches(3.55)  # 50% of usable width (flex: 1) = 7.1 / 2
        
        table.columns[0].width = intro_width
        table.columns[1].width = chart_width
        
        # Configure table borders (hidden to match CSS)
        self._hide_table_borders(table)
        
        # LEFT COLUMN: Process intro text block
        left_cell = table.cell(0, 0)
        left_cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        
        if intro_block:
            logger.info("✅ Processing intro-text-block in left column")
            # Clear default paragraph
            left_cell.paragraphs[0].clear()
            
            # Process each paragraph in intro block
            for para in intro_block.find_all('p'):
                cell_para = left_cell.add_paragraph()
                self._fix_element_alignment(cell_para, para)
                
                # Process text with proper bold formatting
                self._process_paragraph_with_formatting(cell_para, para)
                cell_para.space_after = Pt(12)
        
        # RIGHT COLUMN: Process chart area (if exists)
        right_cell = table.cell(0, 1)
        right_cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        
        if chart_area:
            logger.info("✅ Processing chart area in right column")
            # Clear default paragraph
            right_cell.paragraphs[0].clear()
            
            # Add simple static stock chart content
            self._add_simple_static_chart(right_cell, chart_area)
        else:
            # No chart area found, make left column span full width
            logger.info("⚠️ No chart area found, using single column layout")
            # Clear right cell
            right_cell.paragraphs[0].clear()
        
        # Add spacing after container
        spacing_para = doc.add_paragraph()
        spacing_para.space_after = Pt(20)
    
    def _add_simple_static_chart(self, cell, chart_area):
        """Add simple static stock chart - just key price data"""
        try:
            # Extract stock data from JavaScript
            script_tags = chart_area.find_all('script')
            current_price = None
            price_data = []
            
            for script in script_tags:
                script_text = script.get_text()
                if 'stockData' in script_text:
                    import re
                    # Extract the last few price points
                    price_matches = re.findall(r"'price':\s*([\d.]+)", script_text)
                    date_matches = re.findall(r"'date':\s*'([\d-]+)'", script_text)
                    
                    if price_matches and date_matches:
                        # Get recent data points
                        recent_data = list(zip(date_matches[-6:], price_matches[-6:]))
                        current_price = float(price_matches[-1])
                        start_price = float(price_matches[0])
                        min_price = min(float(p) for p in price_matches)
                        max_price = max(float(p) for p in price_matches)
                        price_change = current_price - start_price
                        price_change_pct = (price_change / start_price) * 100
                        break
            
            if current_price:
                # Chart title
                title_para = cell.add_paragraph()
                title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                title_run = title_para.add_run("📈 Stock Price Summary")
                title_run.font.size = Pt(14)
                title_run.font.bold = True
                title_run.font.name = self.primary_font
                title_run.font.color.rgb = self.robeco_colors['robeco_blue']
                title_para.space_after = Pt(10)
                
                # Current price (large)
                price_para = cell.add_paragraph()
                price_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                price_run = price_para.add_run(f"HKD ${current_price:.2f}")
                price_run.font.size = Pt(24)
                price_run.font.bold = True
                price_run.font.name = self.primary_font
                price_run.font.color.rgb = self.robeco_colors['robeco_blue']
                price_para.space_after = Pt(8)
                
                # Change summary
                change_para = cell.add_paragraph()
                change_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                change_color = self.robeco_colors.get('accent_green', RGBColor(46, 125, 50)) if price_change >= 0 else self.robeco_colors.get('accent_red', RGBColor(198, 40, 40))
                change_symbol = "+" if price_change >= 0 else ""
                change_run = change_para.add_run(f"{change_symbol}HKD ${price_change:.2f} ({change_symbol}{price_change_pct:.1f}%)")
                change_run.font.size = Pt(12)
                change_run.font.bold = True
                change_run.font.name = self.primary_font
                change_run.font.color.rgb = change_color
                change_para.space_after = Pt(8)
                
                # Price range
                range_para = cell.add_paragraph()
                range_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                range_run = range_para.add_run(f"Range: ${min_price:.2f} - ${max_price:.2f}")
                range_run.font.size = Pt(11)
                range_run.font.name = self.primary_font
                range_run.font.color.rgb = self.robeco_colors['text_secondary']
                range_para.space_after = Pt(12)
                
                # Recent prices (simple list)
                recent_para = cell.add_paragraph()
                recent_para.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                recent_run = recent_para.add_run("Recent 6 Months:")
                recent_run.font.size = Pt(11)
                recent_run.font.bold = True
                recent_run.font.name = self.primary_font
                recent_para.space_after = Pt(4)
                
                # List recent prices
                for date, price in recent_data:
                    point_para = cell.add_paragraph()
                    point_para.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    point_run = point_para.add_run(f"• {date}: ${float(price):.2f}")
                    point_run.font.size = Pt(9)
                    point_run.font.name = self.primary_font
                    point_run.font.color.rgb = self.robeco_colors['text_secondary']
                    point_para.space_after = Pt(2)
                
                logger.info(f"✅ Added simple static chart: Current ${current_price:.2f}, Change {price_change_pct:.1f}%")
            else:
                # Simple fallback
                self._add_chart_fallback(cell)
                logger.info("⚠️ Added chart fallback (no price data found)")
                
        except Exception as e:
            logger.error(f"❌ Simple chart failed: {e}")
            self._add_chart_fallback(cell)
    
    def _add_stock_chart_content(self, cell, chart_area):
        """Add sophisticated stock chart representation based on D3.js chart data"""
        try:
            # Look for stock data in script tags
            script_tags = chart_area.find_all('script')
            stock_data = None
            
            for script in script_tags:
                script_text = script.get_text()
                if 'stockData' in script_text and 'date' in script_text and 'price' in script_text:
                    # Extract stock data from JavaScript with enhanced parsing
                    import re
                    import json
                    
                    # Find the complete stockData array
                    match = re.search(r'stockData\s*=\s*(\[.*?\]);', script_text, re.DOTALL)
                    if match:
                        try:
                            # Convert JavaScript object notation to Python-readable JSON
                            data_str = match.group(1)
                            # Replace single quotes with double quotes for JSON compatibility
                            json_str = re.sub(r"'([^']*)':", r'"\1":', data_str)
                            json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
                            
                            # Parse the complete dataset
                            data_list = json.loads(json_str)
                            stock_data = [(item['date'], float(item['price'])) for item in data_list]
                            break
                        except Exception as e:
                            logger.error(f"JSON parsing failed, using regex fallback: {e}")
                            # Fallback to regex extraction
                            price_matches = re.findall(r"'price':\s*([\d.]+)", data_str)
                            date_matches = re.findall(r"'date':\s*'([\d-]+)'", data_str)
                            if price_matches and date_matches:
                                stock_data = list(zip(date_matches, [float(p) for p in price_matches]))
                                break
            
            if stock_data and len(stock_data) > 0:
                # Add sophisticated chart representation
                title_para = cell.add_paragraph()
                title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                title_run = title_para.add_run("📈 Stock Price Performance (HKD)")
                title_run.font.size = Pt(14)
                title_run.font.bold = True
                title_run.font.name = self.primary_font
                title_run.font.color.rgb = self.robeco_colors['robeco_blue']
                title_para.space_after = Pt(8)
                
                # Calculate key metrics
                prices = [price for _, price in stock_data]
                start_price = prices[0]
                current_price = prices[-1]
                max_price = max(prices)
                min_price = min(prices)
                price_change = current_price - start_price
                price_change_pct = (price_change / start_price) * 100
                
                # Current price highlight
                current_para = cell.add_paragraph()
                current_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                current_run = current_para.add_run(f"Current Price: HKD ${current_price:.2f}")
                current_run.font.size = Pt(18)
                current_run.font.bold = True
                current_run.font.name = self.primary_font
                current_run.font.color.rgb = self.robeco_colors['robeco_blue']
                current_para.space_after = Pt(8)
                
                # Performance summary
                perf_para = cell.add_paragraph()
                perf_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                change_color = self.robeco_colors.get('accent_green', RGBColor(46, 125, 50)) if price_change >= 0 else self.robeco_colors.get('accent_red', RGBColor(198, 40, 40))
                change_symbol = "+" if price_change >= 0 else ""
                perf_run = perf_para.add_run(f"Period Change: {change_symbol}HKD ${price_change:.2f} ({change_symbol}{price_change_pct:.1f}%)")
                perf_run.font.size = Pt(12)
                perf_run.font.bold = True
                perf_run.font.name = self.primary_font
                perf_run.font.color.rgb = change_color
                perf_para.space_after = Pt(8)
                
                # Price range
                range_para = cell.add_paragraph()
                range_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                range_run = range_para.add_run(f"Range: HKD ${min_price:.2f} - ${max_price:.2f}")
                range_run.font.size = Pt(11)
                range_run.font.name = self.primary_font
                range_run.font.color.rgb = self.robeco_colors['text_secondary']
                range_para.space_after = Pt(12)
                
                # Simple ASCII-style chart representation
                chart_para = cell.add_paragraph()
                chart_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                
                # Create a simple trend visualization using characters
                trend_length = min(20, len(stock_data))
                if trend_length > 1:
                    # Sample data points for visualization
                    sample_indices = [int(i * (len(stock_data) - 1) / (trend_length - 1)) for i in range(trend_length)]
                    sample_prices = [prices[i] for i in sample_indices]
                    
                    # Normalize prices to create visual representation
                    price_range = max_price - min_price
                    if price_range > 0:
                        normalized = [(p - min_price) / price_range for p in sample_prices]
                        
                        # Create visual trend line using characters
                        trend_chars = []
                        for i, norm_price in enumerate(normalized):
                            if i == 0:
                                trend_chars.append("●")  # Start point
                            elif i == len(normalized) - 1:
                                trend_chars.append("●")  # End point
                            else:
                                # Use trend direction
                                if i > 0:
                                    if normalized[i] > normalized[i-1]:
                                        trend_chars.append("↗")
                                    elif normalized[i] < normalized[i-1]:
                                        trend_chars.append("↘")
                                    else:
                                        trend_chars.append("→")
                        
                        chart_run = chart_para.add_run(" ".join(trend_chars))
                        chart_run.font.size = Pt(12)
                        chart_run.font.name = self.primary_font
                        chart_run.font.color.rgb = self.robeco_colors['robeco_blue']
                
                # Recent key data points (last 6 months)
                data_para = cell.add_paragraph()
                data_para.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                data_run = data_para.add_run("Recent Data Points:")
                data_run.font.size = Pt(11)
                data_run.font.bold = True
                data_run.font.name = self.primary_font
                data_para.space_after = Pt(4)
                
                # Show last 6 data points
                recent_data = stock_data[-6:] if len(stock_data) >= 6 else stock_data
                for date, price in recent_data:
                    point_para = cell.add_paragraph()
                    point_para.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    point_text = f"• {date}: HKD ${price:.2f}"
                    point_run = point_para.add_run(point_text)
                    point_run.font.size = Pt(9)
                    point_run.font.name = self.primary_font
                    point_run.font.color.rgb = self.robeco_colors['text_secondary']
                    point_para.space_after = Pt(2)
                
                logger.info(f"✅ Added sophisticated stock chart with {len(stock_data)} data points, range: ${min_price:.2f}-${max_price:.2f}")
            else:
                # Enhanced fallback when no data found
                self._add_chart_fallback(cell)
                logger.info("⚠️ Added enhanced chart fallback (no data parsed)")
                
        except Exception as e:
            logger.error(f"❌ Stock chart processing failed: {e}")
            self._add_chart_fallback(cell)
    
    def _add_chart_fallback(self, cell):
        """Add enhanced chart fallback when data extraction fails"""
        title_para = cell.add_paragraph()
        title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        title_run = title_para.add_run("📊 Stock Price Chart")
        title_run.font.size = Pt(14)
        title_run.font.bold = True
        title_run.font.name = self.primary_font
        title_run.font.color.rgb = self.robeco_colors['robeco_blue']
        
        desc_para = cell.add_paragraph()
        desc_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        desc_run = desc_para.add_run("Interactive D3.js chart available in web version")
        desc_run.font.size = Pt(10)
        desc_run.font.italic = True
        desc_run.font.name = self.primary_font
        desc_run.font.color.rgb = self.robeco_colors['text_secondary']
    
    def _hide_table_borders(self, table):
        """Hide all table borders to mimic CSS borderless layout"""
        try:
            # Hide table borders
            for row in table.rows:
                for cell in row.cells:
                    # Get cell properties
                    tc_pr = cell._element.find(qn('w:tcPr'))
                    if tc_pr is None:
                        tc_pr = OxmlElement('w:tcPr')
                        cell._element.insert(0, tc_pr)
                    
                    # Create border element with no borders
                    tc_borders = OxmlElement('w:tcBorders')
                    for border_name in ['top', 'left', 'bottom', 'right']:
                        border = OxmlElement(f'w:{border_name}')
                        border.set(qn('w:val'), 'nil')
                        tc_borders.append(border)
                    
                    tc_pr.append(tc_borders)
        except Exception as e:
            logger.warning(f"⚠️ Could not hide table borders: {e}")
    
    def _process_paragraph_with_formatting(self, word_para, html_para):
        """Process HTML paragraph with proper bold/strong formatting preservation"""
        try:
            # Process all content elements in order
            for element in html_para.contents:
                if hasattr(element, 'name'):
                    if element.name == 'strong':
                        # Bold text
                        run = word_para.add_run(element.get_text())
                        run.font.bold = True
                        run.font.size = Pt(16)
                        run.font.name = self.primary_font
                    else:
                        # Other HTML tags - extract text
                        run = word_para.add_run(element.get_text())
                        run.font.size = Pt(16)
                        run.font.name = self.primary_font
                else:
                    # Plain text node
                    text = str(element).strip()
                    if text:
                        run = word_para.add_run(text)
                        run.font.size = Pt(16)
                        run.font.name = self.primary_font
        except Exception as e:
            # Fallback to simple text extraction
            run = word_para.add_run(html_para.get_text())
            run.font.size = Pt(16)
            run.font.name = self.primary_font

    def _process_main_content(self, doc: Document, main_soup, slide_classes=None):
        """Process main content container - handles both analysis-item layout and prose layout"""
        main_classes = main_soup.get('class', [])
        slide_classes = slide_classes or []
        logger.info(f"🔍 Processing MAIN content container with {len(list(main_soup.children))} children")
        logger.info(f"🔍 Main classes: {main_classes}")
        
        # Check if this is a prose layout (Pages 3-15) - check both main and slide classes
        is_prose = 'report-prose' in main_classes or 'report-prose' in slide_classes
        if is_prose:
            logger.info("📝 Processing PROSE LAYOUT (Pages 3-15)")
            self._process_prose_layout(doc, main_soup)
        else:
            logger.info("📊 Processing ANALYSIS LAYOUT (Pages 1-2)")
            self._process_analysis_layout(doc, main_soup)
    
    def _process_prose_layout(self, doc: Document, main_soup):
        """Process prose layout for Pages 3-15"""
        for child in main_soup.children:
            if hasattr(child, 'name') and child.name is not None:
                if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    logger.info(f"✅ Found prose header {child.name}")
                    self._add_header(doc, child)
                elif child.name == 'p':
                    logger.info("✅ Found prose paragraph")
                    self._add_paragraph(doc, child)
                elif child.name == 'div' and 'content-item' in child.get('class', []):
                    logger.info("✅ Found content-item in prose layout")
                    # Process content-item as simple paragraphs
                    for para in child.find_all('p'):
                        self._add_paragraph(doc, para)
                else:
                    # Process other elements recursively
                    self._process_main_content(doc, child)
    
    def _process_analysis_layout(self, doc: Document, main_soup):
        """Process analysis layout for Pages 1-2 with metrics grid, intro-chart, and analysis sections"""
        # Recursively process all children of main element
        for child in main_soup.children:
            if hasattr(child, 'name') and child.name is not None:
                child_classes = child.get('class', [])
                logger.info(f"🎯 Processing MAIN child: {child.name}, classes: {child_classes}")
                
                # Handle specific content types within main
                if 'metrics-grid' in child_classes:
                    logger.info("✅ Found metrics-grid in main content")
                    self._add_metrics_grid(doc, child)
                
                elif 'intro-and-chart-container' in child_classes:
                    logger.info("✅ Found intro-and-chart-container in main content")
                    self._add_intro_chart_container(doc, child)
                
                elif 'analysis-sections' in child_classes:
                    logger.info("✅ Found analysis-sections in main content")
                    self._process_analysis_sections(doc, child)
                
                elif 'content-grid' in child_classes:
                    logger.info("✅ Found content-grid in main content") 
                    self._process_content_grid(doc, child)
                
                elif 'analysis-item' in child_classes:
                    logger.info("✅ Found analysis-item in main content")
                    self._add_two_column_analysis_item(doc, child)
                
                elif 'section' in child_classes or child.name == 'section':
                    logger.info("✅ Found section in main content")
                    # Process section content recursively
                    self._process_section_content(doc, child)
                
                elif child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    logger.info(f"✅ Found header {child.name} in main content")
                    self._add_header(doc, child)
                
                elif child.name == 'p':
                    logger.info("✅ Found paragraph in main content")
                    self._add_paragraph(doc, child)
                
                elif child.name == 'table':
                    logger.info("✅ Found table in main content")
                    self._add_table(doc, child)
                
                elif child.name in ['ul', 'ol']:
                    logger.info(f"✅ Found list {child.name} in main content")
                    self._add_list(doc, child)
                
                elif child.name == 'div':
                    # Enhanced div processing - check for specific layout classes
                    if 'analysis-sections' in child_classes:
                        logger.info("✅ Found analysis-sections in div")
                        self._process_analysis_sections(doc, child)
                    elif 'content-grid' in child_classes:
                        logger.info("✅ Found content-grid in div")
                        self._process_content_grid(doc, child)
                    elif 'analysis-item' in child_classes:
                        logger.info("✅ Found analysis-item in div")
                        self._add_two_column_analysis_item(doc, child)
                    elif 'bullet-list-square' in child_classes:
                        logger.info("✅ Found bullet-list-square in div")
                        self._process_bullet_list_square(doc, child)
                    else:
                        # Generic div - check if it has meaningful content
                        text_content = child.get_text().strip()
                        if text_content and len(text_content) > 0:
                            logger.info(f"✅ Found content div in main: {len(text_content)} chars, classes: {child_classes}")
                            # If it has nested structure, recurse first
                            if child.find_all(['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table']):
                                logger.info("🔄 Recursing into structured div content")
                                self._process_main_content(doc, child)
                            else:
                                self._add_paragraph(doc, child)
                        else:
                            # Empty div, but may contain other elements - recurse
                            logger.info("🔄 Recursing into empty div in main content")
                            self._process_main_content(doc, child)
                
                else:
                    # Generic element with text content
                    text_content = child.get_text().strip()
                    if text_content and len(text_content) > 0:
                        logger.info(f"✅ Found generic content element {child.name}: {len(text_content)} chars")
                        self._add_paragraph(doc, child)

    def _process_section_content(self, doc: Document, section_soup):
        """Process section content with proper handling"""
        logger.info(f"🔍 Processing SECTION content")
        
        # Look for section title
        section_title = section_soup.find(class_='section-title')
        if section_title:
            self._add_section_title(doc, section_title)
        
        # Process other content in section
        for child in section_soup.children:
            if hasattr(child, 'name') and child.name is not None:
                if 'section-title' not in child.get('class', []):  # Skip already processed title
                    if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        self._add_header(doc, child)
                    elif child.name == 'p':
                        self._add_paragraph(doc, child)
                    elif child.name == 'table':
                        self._add_table(doc, child)
                    elif child.name in ['ul', 'ol']:
                        self._add_list(doc, child)

    def _process_analysis_sections(self, doc: Document, sections_soup):
        """Process analysis sections with proper hierarchy and structure"""
        logger.info("🔍 Processing ANALYSIS SECTIONS with structured content")
        
        # Look for h3 headers first
        headers = sections_soup.find_all('h3')
        for header in headers:
            logger.info(f"📋 Found section header: {header.get_text().strip()}")
            self._add_header(doc, header)
        
        # Process paragraphs
        paragraphs = sections_soup.find_all('p')
        for para in paragraphs:
            logger.info(f"📝 Found section paragraph: {len(para.get_text())} chars")
            self._add_paragraph(doc, para)
        
        # Look for bullet lists
        bullet_lists = sections_soup.find_all(class_='bullet-list-square')
        for bullet_list in bullet_lists:
            logger.info("🔘 Found bullet-list-square in analysis section")
            self._process_bullet_list_square(doc, bullet_list)
        
        # Process any remaining analysis items
        analysis_items = sections_soup.find_all(class_='analysis-item')
        for item in analysis_items:
            logger.info("📊 Found analysis-item in analysis section")
            self._add_two_column_analysis_item(doc, item)

    def _process_content_grid(self, doc: Document, grid_soup):
        """Process content grid layouts"""
        logger.info("🔍 Processing CONTENT GRID layout")
        
        # Look for content blocks within the grid
        content_blocks = grid_soup.find_all(class_='content-block')
        
        for block in content_blocks:
            logger.info("📦 Processing content block within grid")
            
            # Process section titles
            section_titles = block.find_all(class_='section-title')
            for title in section_titles:
                self._add_section_title(doc, title)
            
            # Process other content recursively
            self._process_main_content(doc, block)

    def _add_two_column_analysis_item(self, doc: Document, item_soup):
        """Add two-column analysis item with PERFECT HTML flexbox replication (16%/84% layout)"""
        logger.info("🎯 ENHANCED: Processing TWO-COLUMN ANALYSIS ITEM with precise HTML structure replication")
        
        # 🔍 ANALYZE HTML STRUCTURE: Extract precise layout information
        item_title = item_soup.find(class_='item-title')
        content_item = item_soup.find(class_='content-item')
        
        # Get CSS classes for advanced layout detection
        item_classes = item_soup.get('class', [])
        is_first_item = 'first-analysis-item' in item_classes
        
        logger.info(f"🔍 Structure Analysis:")
        logger.info(f"   📋 Has item-title: {bool(item_title)}")
        logger.info(f"   📄 Has content-item: {bool(content_item)}")
        logger.info(f"   🎯 Is first item: {is_first_item}")
        logger.info(f"   📦 Item classes: {item_classes}")
        
        if item_title and content_item:
            title_text = item_title.get_text().strip()
            content_text = content_item.get_text().strip()
            
            logger.info(f"📋 Title: '{title_text}'")
            logger.info(f"📄 Content: {len(content_text)} chars")
            
            # 🏗️ CREATE PRECISE FLEXBOX-STYLE TABLE: Mimic CSS display:flex with flex:0 0 16% and flex:1
            table = doc.add_table(rows=1, cols=2)
            table.alignment = WD_TABLE_ALIGNMENT.LEFT
            
            # 🎨 APPLY EXACT HTML STYLING: Replicate CSS border-bottom and padding
            self._apply_analysis_item_html_styling(table, is_first_item)
            
            # 📐 FORCE EXACT 16%/84% COLUMN LAYOUT: Use advanced XML manipulation
            self._force_precise_flexbox_layout(table)
            
            # 📋 LEFT COLUMN (16%): Item Title - Exact HTML replication
            left_cell = table.cell(0, 0)
            left_cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            
            # Apply exact HTML title styling (.item-title CSS)
            title_p = left_cell.paragraphs[0]
            title_p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            title_run = title_p.add_run(title_text)
            title_run.font.size = Pt(16)  # Matches CSS font-size: 16px
            title_run.font.name = self.primary_font
            title_run.font.bold = True  # Matches CSS font-weight: 500 (bold)
            title_run.font.color.rgb = self.robeco_colors['blue_darker']  # Matches CSS color: var(--robeco-blue)
            
            # Apply HTML padding-right: 15px equivalent
            self._apply_cell_padding(left_cell, right_padding=15)
            
            # 📄 RIGHT COLUMN (84%): Content Item - Perfect HTML content structure
            right_cell = table.cell(0, 1)
            right_cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            
            # 🔍 DEEP CONTENT ANALYSIS: Process nested HTML structure precisely
            self._process_content_item_with_html_structure(right_cell, content_item)
            
            logger.info(f"✅ ENHANCED: Two-column analysis created with perfect HTML replication")
            
            # Add proper spacing (matches CSS margin-bottom)
            spacing_para = doc.add_paragraph()
            spacing_para.space_after = Pt(12)  # Matches HTML margin-bottom: 10px + padding
            
        else:
            logger.warning("⚠️ FALLBACK: Analysis item missing required structure - using basic processing")
            # Fallback to basic content processing
            if item_soup.get_text().strip():
                self._add_paragraph(doc, item_soup)
    
    def _apply_analysis_item_html_styling(self, table, is_first_item: bool):
        """Apply exact HTML analysis-item CSS styling to Word table"""
        logger.info(f"🎨 Applying HTML analysis-item styling (first_item: {is_first_item})")
        
        try:
            # Get table properties
            tbl_pr = table._element.find(qn('w:tblPr'))
            if tbl_pr is None:
                tbl_pr = OxmlElement('w:tblPr')
                table._element.insert(0, tbl_pr)
            
            # Add table borders to match HTML styling
            tbl_borders = tbl_pr.find(qn('w:tblBorders'))
            if tbl_borders is None:
                tbl_borders = OxmlElement('w:tblBorders')
                tbl_pr.append(tbl_borders)
            
            # Bottom border: matches CSS border-bottom: 3.5px solid #E0E0E0 EXACTLY
            bottom_border = OxmlElement('w:bottom')
            bottom_border.set(qn('w:val'), 'single')
            bottom_border.set(qn('w:sz'), '21')  # 3.5px equivalent
            bottom_border.set(qn('w:color'), 'E0E0E0')  # Light gray to match CSS exactly
            tbl_borders.append(bottom_border)
            
            # Top border for first item: matches CSS .first-analysis-item { border-top: 5px solid var(--robeco-blue) }
            if is_first_item:
                top_border = OxmlElement('w:top')
                top_border.set(qn('w:val'), 'single')
                top_border.set(qn('w:sz'), '30')  # 5px equivalent
                top_border.set(qn('w:color'), '005F90')  # Robeco blue
                tbl_borders.append(top_border)
                logger.info("🔵 Added top border for first analysis item")
            
            # Set table spacing to match HTML padding-top: 9px, padding-bottom: 9px
            tbl_cellmargin = OxmlElement('w:tblCellMar')
            
            # Top and bottom padding
            for direction, value in [('top', '54'), ('bottom', '54')]:  # 9px = 54 twips
                margin = OxmlElement(f'w:{direction}')
                margin.set(qn('w:w'), value)
                margin.set(qn('w:type'), 'dxa')
                tbl_cellmargin.append(margin)
            
            tbl_pr.append(tbl_cellmargin)
            
            logger.info("✅ Applied exact HTML analysis-item styling")
            
        except Exception as e:
            logger.error(f"❌ Error applying HTML styling: {e}")
    
    def _force_precise_flexbox_layout(self, table):
        """Force EXACT 16%/84% flexbox layout using advanced XML manipulation"""
        logger.info("📐 PRECISION: Forcing exact CSS flexbox layout (16%/84%) to match HTML")
        
        try:
            tbl = table._element
            
            # Set table properties for full width (using twips for better precision)
            tblPr = tbl.find(qn('w:tblPr'))
            if tblPr is None:
                tblPr = OxmlElement('w:tblPr')
                tbl.insert(0, tblPr)
            
            # Table width: 100% (use DXA units for better precision)
            tblW = OxmlElement('w:tblW')
            tblW.set(qn('w:w'), '9000')  # 100% width (9000 twips ≈ 6.25")
            tblW.set(qn('w:type'), 'dxa')
            tblPr.append(tblW)
            
            # Create precise column grid with exact measurements
            tblGrid = tbl.find(qn('w:tblGrid'))
            if tblGrid is None:
                tblGrid = OxmlElement('w:tblGrid')
                tbl.insert(1, tblGrid)
            else:
                tblGrid.clear()
            
            # Column 1: EXACT 16% = 1440 twips (16% of 9000)
            gridCol1 = OxmlElement('w:gridCol')
            gridCol1.set(qn('w:w'), '1440')  
            tblGrid.append(gridCol1)
            
            # Column 2: EXACT 84% = 7560 twips (84% of 9000)
            gridCol2 = OxmlElement('w:gridCol')
            gridCol2.set(qn('w:w'), '7560')  
            tblGrid.append(gridCol2)
            
            # Force individual cell widths with EXACT measurements
            for row in tbl.findall(qn('w:tr')):
                cells = row.findall(qn('w:tc'))
                if len(cells) >= 2:
                    # Cell 1: EXACT 16% width
                    tcPr1 = cells[0].find(qn('w:tcPr'))
                    if tcPr1 is None:
                        tcPr1 = OxmlElement('w:tcPr')
                        cells[0].insert(0, tcPr1)
                    
                    tcW1 = OxmlElement('w:tcW')
                    tcW1.set(qn('w:w'), '1440')  # Exact 16% in twips
                    tcW1.set(qn('w:type'), 'dxa')
                    tcPr1.append(tcW1)
                    
                    # Cell 2: EXACT 84% width  
                    tcPr2 = cells[1].find(qn('w:tcPr'))
                    if tcPr2 is None:
                        tcPr2 = OxmlElement('w:tcPr')
                        cells[1].insert(0, tcPr2)
                    
                    tcW2 = OxmlElement('w:tcW')
                    tcW2.set(qn('w:w'), '7560')  # Exact 84% in twips
                    tcW2.set(qn('w:type'), 'dxa')
                    tcPr2.append(tcW2)
            
            logger.info("✅ PRECISION: Applied EXACT 16%/84% layout (1440/7560 twips)")
            
        except Exception as e:
            logger.error(f"❌ PRECISION FAILED: {e}")
    
    def _apply_cell_padding(self, cell, right_padding: int = 0):
        """Apply cell padding to match HTML CSS padding"""
        try:
            if right_padding > 0:
                # Convert px to twips (1px = 6 twips)
                padding_twips = str(right_padding * 6)
                
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                tcMar = OxmlElement('w:tcMar')
                
                right_mar = OxmlElement('w:right')
                right_mar.set(qn('w:w'), padding_twips)
                right_mar.set(qn('w:type'), 'dxa')
                tcMar.append(right_mar)
                
                tcPr.append(tcMar)
                
                logger.info(f"✅ Applied right padding: {right_padding}px ({padding_twips} twips)")
        except Exception as e:
            logger.error(f"❌ Error applying cell padding: {e}")
    
    def _process_content_item_with_html_structure(self, cell, content_item):
        """Process content-item with exact HTML structure preservation"""
        logger.info("📄 PRECISION: Processing content-item with HTML structure analysis")
        
        # Analyze the content structure
        content_paragraphs = content_item.find_all('p')
        content_lists = content_item.find_all(['ul', 'ol'])
        content_text = content_item.get_text().strip()
        
        logger.info(f"📊 Content Analysis:")
        logger.info(f"   📝 Paragraphs: {len(content_paragraphs)}")
        logger.info(f"   📋 Lists: {len(content_lists)}")
        logger.info(f"   📄 Total text: {len(content_text)} chars")
        
        if content_paragraphs:
            # Process each paragraph with exact HTML formatting
            for i, para in enumerate(content_paragraphs):
                para_text = para.get_text().strip()
                
                if para_text:  # Only process non-empty paragraphs
                    if i == 0:
                        # Use existing cell paragraph
                        content_p = cell.paragraphs[0]
                    else:
                        # Add new paragraph
                        content_p = cell.add_paragraph()
                    
                    # Apply exact HTML content styling (.content-item CSS)
                    content_p.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY  # Matches typical content alignment
                    
                    # Process with advanced text formatting that preserves HTML structure
                    self._add_html_formatted_text_to_paragraph(content_p, para)
                    
                    # Match CSS spacing
                    content_p.space_after = Pt(8)  # Slightly less than default for tighter layout
        
        elif content_lists:
            # Process lists with exact HTML structure
            for list_elem in content_lists:
                # Add list items as properly formatted paragraphs
                items = list_elem.find_all('li')
                for item in items:
                    item_p = cell.add_paragraph()
                    self._add_html_formatted_text_to_paragraph(item_p, item)
                    item_p.space_after = Pt(4)
        
        else:
            # Fallback: single text block
            content_p = cell.paragraphs[0]
            content_run = content_p.add_run(content_text)
            content_run.font.size = Pt(18)  # Matches CSS font-size: 18px
            content_run.font.name = self.primary_font
            content_run.font.color.rgb = self.robeco_colors['text_dark']  # Matches CSS color: var(--text-dark)
    
    def _add_html_formatted_text_to_paragraph(self, paragraph, html_element):
        """Add text with EXACT HTML formatting preservation (bold, italic, etc.)"""
        logger.info(f"🎨 HTML FORMATTING: Processing {html_element.name} with precise style replication")
        
        # Process all content including nested tags
        for element in html_element.contents:
            if hasattr(element, 'name') and element.name:
                element_text = element.get_text()
                
                if element.name == 'strong' or element.name == 'b':
                    # Bold text - matches HTML <strong> or <b>
                    run = paragraph.add_run(element_text)
                    run.font.bold = True
                    run.font.size = Pt(18)
                    run.font.name = self.primary_font
                    run.font.color.rgb = self.robeco_colors['text_dark']
                elif element.name == 'em' or element.name == 'i':
                    # Italic text - matches HTML <em> or <i>
                    run = paragraph.add_run(element_text)
                    run.font.italic = True
                    run.font.size = Pt(18)
                    run.font.name = self.primary_font
                    run.font.color.rgb = self.robeco_colors['text_dark']
                else:
                    # Regular text
                    run = paragraph.add_run(element_text)
                    run.font.size = Pt(18)
                    run.font.name = self.primary_font
                    run.font.color.rgb = self.robeco_colors['text_dark']
            else:
                # Plain text node
                text = str(element).strip()
                if text:
                    run = paragraph.add_run(text)
                    run.font.size = Pt(18)  # Matches CSS .content-item font-size: 18px
                    run.font.name = self.primary_font
                    run.font.color.rgb = self.robeco_colors['text_dark']  # Matches CSS color: var(--text-dark)

    def _process_bullet_list_square(self, doc: Document, list_soup):
        """Process bullet-list-square with special formatting"""
        logger.info("🔍 Processing BULLET-LIST-SQUARE")
        
        # Look for h4 headers within the list
        headers = list_soup.find_all('h4')
        for header in headers:
            p = doc.add_paragraph()
            run = p.add_run(header.get_text().strip())
            run.font.size = Pt(20)  # Matches 22.5px from CSS
            run.font.name = self.primary_font
            run.font.bold = True
            run.font.color.rgb = self.robeco_colors['blue_darker']
            p.space_after = Pt(6)
        
        # Process paragraphs
        paragraphs = list_soup.find_all('p')
        for para in paragraphs:
            p = doc.add_paragraph()
            self._add_formatted_text_to_paragraph(p, para)
            # Use intelligent alignment for bullet list paragraphs
            self._fix_element_alignment(p, para)
            p.space_after = Pt(8)
        
        # Process ul/ol lists within
        lists = list_soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            self._add_list(doc, list_elem)

    def _add_formatted_text_to_paragraph(self, paragraph, html_element):
        """Add formatted text from HTML element to Word paragraph, preserving bold/italic"""
        
        logger.info(f"🔍 Processing formatted text: {html_element.name} with {len(html_element.contents)} children")
        total_text_added = ""
        
        # Process all content including nested formatting
        for i, element in enumerate(html_element.contents):
            if hasattr(element, 'name') and element.name:
                element_text = element.get_text()
                logger.info(f"📝 Processing element {i}: {element.name} = '{element_text[:50]}...'")
                
                if element.name == 'strong':
                    run = paragraph.add_run(element_text)
                    run.font.bold = True
                    run.font.size = Pt(16)
                    run.font.name = self.primary_font
                    total_text_added += element_text
                elif element.name == 'em':
                    run = paragraph.add_run(element_text)
                    run.font.italic = True
                    run.font.size = Pt(16)
                    run.font.name = self.primary_font
                    total_text_added += element_text
                else:
                    # Other tags, get text content
                    run = paragraph.add_run(element_text)
                    run.font.size = Pt(16)
                    run.font.name = self.primary_font
                    total_text_added += element_text
            else:
                # Plain text node
                text = str(element).strip()
                if text:
                    logger.info(f"📝 Processing text node {i}: '{text[:50]}...'")
                    run = paragraph.add_run(text)
                    run.font.size = Pt(16)
                    run.font.name = self.primary_font
                    total_text_added += text
        
        logger.info(f"✅ Added {len(total_text_added)} characters to paragraph")
    
    # DEPRECATED: Old method replaced by _force_precise_flexbox_layout
    
    def _add_analysis_item_border(self, table):
        """Add bottom border to analysis item table to match HTML border-bottom: 3.5px solid #E0E0E0"""
        try:
            # Get table properties
            tbl_pr = table._element.find(qn('w:tblPr'))
            if tbl_pr is None:
                tbl_pr = OxmlElement('w:tblPr')
                table._element.insert(0, tbl_pr)
            
            # Add table borders
            tbl_borders = tbl_pr.find(qn('w:tblBorders'))
            if tbl_borders is None:
                tbl_borders = OxmlElement('w:tblBorders')
                tbl_pr.append(tbl_borders)
            
            # Add bottom border (matches CSS border-bottom: 3.5px solid #E0E0E0)
            bottom_border = OxmlElement('w:bottom')
            bottom_border.set(qn('w:val'), 'single')
            bottom_border.set(qn('w:sz'), '21')  # 3.5px equivalent (21 = 3.5px * 6)
            bottom_border.set(qn('w:color'), 'E0E0E0')  # Light gray
            tbl_borders.append(bottom_border)
            
            # Add top border for first analysis item (matches CSS border-top: 5px solid var(--robeco-blue))
            if hasattr(self, '_first_analysis_item') and not self._first_analysis_item:
                top_border = OxmlElement('w:top')
                top_border.set(qn('w:val'), 'single')
                top_border.set(qn('w:sz'), '30')  # 5px equivalent
                top_border.set(qn('w:color'), '005F90')  # Robeco blue
                tbl_borders.append(top_border)
                self._first_analysis_item = True
                logger.info("🔵 Added blue top border for first analysis item")
            
            logger.info("📏 Added analysis item borders to match HTML styling")
            
        except Exception as e:
            logger.error(f"❌ Error adding analysis item border: {e}")
    
    def _add_orange_separator_line(self, doc: Document):
        """Add orange separator line to match HTML .orange-separator"""
        try:
            p = doc.add_paragraph()
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            
            # Add orange top border to paragraph
            p_pr = p._element.get_or_add_pPr()
            p_bdr = OxmlElement('w:pBdr')
            top_border = OxmlElement('w:top')
            top_border.set(qn('w:val'), 'single')
            top_border.set(qn('w:sz'), '42')  # 7px equivalent (7 * 6)
            top_border.set(qn('w:color'), 'FF8C00')  # Orange color
            p_bdr.append(top_border)
            p_pr.append(p_bdr)
            
            p.space_after = Pt(12)
            logger.info("🟠 Added orange separator line")
            
        except Exception as e:
            logger.error(f"❌ Error adding orange separator: {e}")
    
    def _process_all_images_in_slide(self, doc: Document, slide_soup):
        """Process all images in slide with ENHANCED positioning and context analysis"""
        try:
            all_images = slide_soup.find_all('img')
            logger.info(f"📸 ENHANCED: Found {len(all_images)} images in slide")
            
            # 📍 CREATE IMAGE POSITION MAP: Analyze HTML structure for precise positioning
            image_position_map = self._create_image_position_map(slide_soup, all_images)
            
            for i, img in enumerate(all_images):
                img_src = img.get('src', '')
                img_alt = img.get('alt', '')
                img_classes = img.get('class', [])
                
                logger.info(f"📸 Processing image {i+1}/{len(all_images)}: '{img_alt}' at {img_src}")
                
                # Skip placeholders and empty sources
                if not img_src or 'placehold.co' in img_src or '[COMPANY_LOGO]' in img_src:
                    logger.info("🔄 Skipping placeholder/template image")
                    continue
                
                # 🏢 CATEGORIZE IMAGE TYPE for proper positioning
                image_type = self._determine_image_type(img, img_src, img_alt, img_classes)
                
                if image_type == 'robeco_logo':
                    logger.info("🏢 Robeco logo - processed in header section")
                    continue
                elif image_type == 'company_icon':
                    logger.info("🏢 Company icon - processed in company header section")
                    continue
                elif image_type == 'chart':
                    logger.info("📊 Chart image - inserting with chart-specific positioning")
                    self._insert_chart_image_with_context(doc, img, img_src, img_alt, image_position_map.get(i, {}))
                elif image_type == 'content_image':
                    logger.info("📷 Content image - inserting with content-specific positioning")
                    self._insert_content_image_with_context(doc, img, img_src, img_alt, image_position_map.get(i, {}))
                else:
                    logger.info("🖼️ Generic image - using contextual insertion")
                    self._insert_contextual_image(doc, img, img_src, img_alt)
                    
        except Exception as e:
            logger.error(f"❌ Enhanced image processing failed: {e}")
    
    def _create_image_position_map(self, slide_soup, images):
        """Create a detailed position map for images based on HTML structure"""
        position_map = {}
        
        for i, img in enumerate(images):
            try:
                # Analyze parent hierarchy
                parent = img.parent
                parent_classes = parent.get('class', []) if parent else []
                
                # Find containing section
                section_container = img
                while section_container and section_container.parent:
                    section_container = section_container.parent
                    section_classes = section_container.get('class', []) if hasattr(section_container, 'get') else []
                    if any(cls in section_classes for cls in ['slide', 'content-block', 'analysis-item', 'metrics-grid']):
                        break
                
                position_info = {
                    'parent_classes': parent_classes,
                    'section_classes': section_classes if 'section_classes' in locals() else [],
                    'position_in_slide': i,
                    'total_images': len(images)
                }
                
                position_map[i] = position_info
                logger.info(f"📍 Image {i} position: parent={parent_classes}, section={position_info.get('section_classes', [])}")
                
            except Exception as e:
                logger.warning(f"⚠️ Could not map position for image {i}: {e}")
                position_map[i] = {}
        
        return position_map
    
    def _determine_image_type(self, img, img_src: str, img_alt: str, img_classes: list) -> str:
        """Determine image type for precise positioning"""
        # Check for Robeco branding
        if 'robeco' in img_src.lower() or 'robeco' in img_alt.lower():
            return 'robeco_logo'
        
        # Check for company icons (Clearbit, etc.)
        if ('clearbit.com' in img_src or 'icon' in img_classes or 
            'icon' in img_alt.lower() or 'company' in img_alt.lower()):
            return 'company_icon'
        
        # Check for charts and data visualizations
        if ('chart' in img_classes or 'chart' in img_alt.lower() or 
            'graph' in img_alt.lower() or 'visualization' in img_alt.lower()):
            return 'chart'
        
        # Check parent context for chart containers
        parent = img.parent
        if parent:
            parent_classes = parent.get('class', [])
            if any(cls in parent_classes for cls in ['chart-container', 'stock-chart-container', 'visualization']):
                return 'chart'
        
        # Default to content image
        return 'content_image'
    
    def _insert_chart_image_with_context(self, doc: Document, img_element, img_src: str, img_alt: str, position_info: dict):
        """Insert chart image with precise chart-specific positioning"""
        try:
            # Charts typically center-aligned and larger
            p = doc.add_paragraph()
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            
            # Larger size for charts
            target_width = Inches(5.0)  # Charts need to be readable
            
            success = self._download_and_insert_image_inline(p, img_src, img_alt, target_width)
            
            if success:
                # Add chart caption if meaningful
                if img_alt and len(img_alt) > 3 and 'chart' not in img_alt.lower():
                    caption_p = doc.add_paragraph(f"Figure: {img_alt}")
                    caption_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    caption_run = caption_p.runs[0]
                    caption_run.font.size = Pt(10)
                    caption_run.font.italic = True
                    caption_run.font.color.rgb = self.robeco_colors['text_secondary']
                
                logger.info(f"✅ Chart image inserted: {img_alt}")
            else:
                # Remove failed paragraph
                doc.paragraphs.pop()
                
        except Exception as e:
            logger.error(f"❌ Chart image insertion failed: {e}")
    
    def _insert_content_image_with_context(self, doc: Document, img_element, img_src: str, img_alt: str, position_info: dict):
        """Insert content image with context-aware positioning"""
        try:
            # Determine alignment based on context
            parent_classes = position_info.get('parent_classes', [])
            
            p = doc.add_paragraph()
            
            if any(cls in parent_classes for cls in ['center', 'text-center']):
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                target_width = Inches(3.0)
            elif any(cls in parent_classes for cls in ['right', 'text-right']):
                p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
                target_width = Inches(2.5)
            else:
                p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                target_width = Inches(2.0)
            
            success = self._download_and_insert_image_inline(p, img_src, img_alt, target_width)
            
            if success:
                logger.info(f"✅ Content image inserted: {img_alt}")
            else:
                doc.paragraphs.pop()
                
        except Exception as e:
            logger.error(f"❌ Content image insertion failed: {e}")
    
    def _generate_intelligent_logo_fallbacks(self, original_url: str, company_name: str) -> list:
        """Generate intelligent logo fallback URLs for any company"""
        fallback_urls = [original_url]  # Always try original first
        
        try:
            # Extract company name parts for intelligent URL generation
            company_clean = company_name.lower().strip()
            
            # Remove common suffixes and words
            suffixes_to_remove = [
                'inc', 'inc.', 'corp', 'corp.', 'corporation', 'company', 'co', 'co.', 
                'ltd', 'ltd.', 'limited', 'plc', 'llc', 'trust', 'reit', 'group', 
                'holdings', 'holding', 'international', 'intl', 'global', 'worldwide',
                'logistics', 'commercial', 'property', 'properties', 'real estate',
                '&', 'and', 'the'
            ]
            
            words = company_clean.replace('&', '').replace(',', '').split()
            filtered_words = []
            
            for word in words:
                word_clean = word.strip('.,()[]{}')
                if word_clean and word_clean not in suffixes_to_remove:
                    filtered_words.append(word_clean)
            
            # Generate various domain combinations
            if len(filtered_words) >= 1:
                # Single word domains
                main_word = filtered_words[0]
                fallback_urls.extend([
                    f"https://logo.clearbit.com/{main_word}.com",
                    f"https://logo.clearbit.com/{main_word}.co.uk",
                    f"https://logo.clearbit.com/{main_word}.sg",
                    f"https://logo.clearbit.com/{main_word}.com.au"
                ])
                
                # Two word combinations
                if len(filtered_words) >= 2:
                    two_words = filtered_words[0] + filtered_words[1]
                    fallback_urls.extend([
                        f"https://logo.clearbit.com/{two_words}.com",
                        f"https://logo.clearbit.com/{filtered_words[0]}{filtered_words[1]}.com",
                        f"https://logo.clearbit.com/{filtered_words[0]}-{filtered_words[1]}.com",
                        f"https://logo.clearbit.com/{filtered_words[0]}_{filtered_words[1]}.com"
                    ])
                
                # Three word combinations (for companies like "Frasers Logistics Commercial")
                if len(filtered_words) >= 3:
                    three_words = filtered_words[0] + filtered_words[1] + filtered_words[2]
                    fallback_urls.extend([
                        f"https://logo.clearbit.com/{three_words}.com",
                        f"https://logo.clearbit.com/{filtered_words[0]}{filtered_words[1]}{filtered_words[2]}.com"
                    ])
            
            # Stock ticker-based fallbacks (extract from URL or use common patterns)
            if 'clearbit.com/' in original_url:
                original_domain = original_url.split('clearbit.com/')[-1]
                if original_domain and '.' not in original_domain:
                    # Try common extensions for the domain
                    for ext in ['.com', '.co.uk', '.sg', '.com.au', '.de', '.fr', '.nl']:
                        fallback_urls.append(f"https://logo.clearbit.com/{original_domain}{ext}")
            
            # Remove duplicates while preserving order
            seen = set()
            unique_fallbacks = []
            for url in fallback_urls:
                if url not in seen:
                    seen.add(url)
                    unique_fallbacks.append(url)
            
            logger.info(f"🎯 Generated {len(unique_fallbacks)} intelligent logo fallbacks for '{company_name}'")
            return unique_fallbacks[:10]  # Limit to 10 attempts
            
        except Exception as e:
            logger.warning(f"⚠️ Error generating logo fallbacks: {e}")
            return [original_url]  # Return at least the original URL
    
    def _insert_contextual_image(self, doc: Document, img_element, img_src: str, img_alt: str):
        """Insert image at its contextual position based on HTML structure"""
        try:
            # Determine image context based on parent elements
            parent = img_element.parent
            parent_classes = parent.get('class', []) if parent else []
            
            logger.info(f"📸 Image context - parent: {parent.name if parent else 'None'}, classes: {parent_classes}")
            
            # Create paragraph for the image
            p = doc.add_paragraph()
            
            # Determine alignment based on context
            if 'chart' in parent_classes or 'chart' in img_alt.lower():
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                target_width = Inches(4.0)  # Charts are typically larger
                logger.info("📈 Chart image - center aligned, large size")
            elif 'icon' in parent_classes or 'logo' in parent_classes:
                p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                target_width = Inches(0.5)  # Icons are small
                logger.info("📷 Icon image - left aligned, small size")
            else:
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                target_width = Inches(2.0)  # Default size
                logger.info("📷 Generic image - center aligned, medium size")
            
            # Try to download and insert the image
            success = self._download_and_insert_image_inline(p, img_src, img_alt, target_width)
            
            if success:
                logger.info(f"✅ Successfully inserted contextual image: {img_alt}")
                # Add caption if alt text is meaningful
                if img_alt and len(img_alt) > 3 and 'icon' not in img_alt.lower():
                    caption_p = doc.add_paragraph(img_alt)
                    caption_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    caption_run = caption_p.runs[0]
                    caption_run.font.size = Pt(10)
                    caption_run.font.italic = True
                    caption_run.font.color.rgb = self.robeco_colors['text_secondary']
            else:
                # Remove empty paragraph if image failed
                doc.paragraphs.pop()
                logger.warning(f"⚠️ Failed to insert image, paragraph removed: {img_src}")
                
        except Exception as e:
            logger.error(f"❌ Error inserting contextual image: {e}")
    
    # Removed _add_robeco_logo method - functionality moved to _add_report_header
    
    def _add_company_icon(self, doc: Document, header_soup) -> bool:
        """Add company icon from HTML - positioned next to company name"""
        try:
            # Look for company icon (Clearbit logo)
            img_tags = header_soup.find_all('img')
            
            for img in img_tags:
                img_src = img.get('src', '')
                img_alt = img.get('alt', '')
                img_classes = img.get('class', [])
                
                logger.info(f"📸 Found img: src='{img_src}', alt='{img_alt}', classes='{img_classes}'")
                
                # Check if it's a company icon (clearbit or has 'icon' class)
                if ('clearbit.com' in img_src or 'icon' in img_classes or 
                    'icon' in img_alt.lower() or img_src.endswith('.co.jp')):
                    
                    # Create inline company icon with name
                    company_name_elem = header_soup.find('h1', class_='name')
                    if company_name_elem:
                        p = doc.add_paragraph()
                        p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                        
                        # Try intelligent fallback URLs for company logos
                        success = False
                        company_name = company_name_elem.get_text().strip()
                        fallback_urls = self._generate_intelligent_logo_fallbacks(img_src, company_name)
                        
                        for i, url in enumerate(fallback_urls):
                            if i > 0:  # Don't log for original URL
                                logger.info(f"🔄 Trying intelligent fallback {i}: {url}")
                            success = self._download_and_insert_image_inline(p, url, img_alt, Inches(0.4))
                            if success:
                                logger.info(f"✅ Success with fallback URL {i}: {url}")
                                break
                        
                        # Add company name after icon (whether icon succeeded or not)
                        run = p.add_run((" " if success else "") + company_name_elem.get_text().strip())
                        run.font.size = Pt(32)
                        run.font.name = self.primary_font
                        run.font.bold = True
                        run.font.color.rgb = self.robeco_colors['text_dark']
                        p.space_after = Pt(8)
                        
                        if success:
                            logger.info(f"✅ Added company icon with name: {img_alt}")
                        else:
                            logger.info(f"📝 Added company name without icon (logo failed): {company_name_elem.get_text().strip()}")
                        return True
                    else:
                        # No company name found, try to add icon only
                        p = doc.add_paragraph()
                        p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                        success = self._download_and_insert_image_inline(p, img_src, img_alt, Inches(0.4))
                        if success:
                            logger.info(f"✅ Added company icon: {img_alt}")
                            return True
                        else:
                            # Remove empty paragraph if no icon and no name
                            doc.paragraphs.pop()
            
            logger.info("ℹ️ No company icon found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error adding company icon: {e}")
            return False
    
    def _download_and_insert_image_inline(self, paragraph, img_url: str, alt_text: str, target_width: object) -> bool:
        """Download image from URL and insert into Word document"""
        try:
            # Check cache first
            if img_url in self._image_cache:
                logger.info(f"📸 Using cached image: {img_url}")
                image_data = self._image_cache[img_url]
            else:
                # Download image
                logger.info(f"📸 Downloading image: {img_url}")
                response = requests.get(img_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                image_data = response.content
                self._image_cache[img_url] = image_data
                logger.info(f"✅ Downloaded {len(image_data)} bytes")
            
            # Insert image inline into the provided paragraph
            image_stream = BytesIO(image_data)
            
            # Try to determine optimal size
            try:
                with Image.open(image_stream) as pil_img:
                    width, height = pil_img.size
                    # Use target width, maintain aspect ratio
                    if width > 0:
                        aspect_ratio = height / width
                        img_width = target_width
                        img_height = Inches(target_width.inches * aspect_ratio)
                    else:
                        img_width = target_width
                        img_height = target_width
                        
                    logger.info(f"📐 Image dimensions: {width}x{height} -> {img_width.inches:.2f}x{img_height.inches:.2f} inches")
            except Exception as e:
                logger.warning(f"⚠️ Could not determine image size: {e}, using defaults")
                img_width = target_width
                img_height = target_width
            
            # Reset stream position
            image_stream.seek(0)
            
            # Add the image inline
            run = paragraph.add_run()
            run.add_picture(image_stream, width=img_width, height=img_height)
            
            logger.info(f"✅ Successfully inserted image: {alt_text}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download/insert image from {img_url}: {e}")
            return False
    
    def _fix_element_alignment(self, paragraph, html_element):
        """Fix element alignment to match HTML positioning with ENHANCED CSS analysis"""
        try:
            # 🔍 DEEP HTML STRUCTURE ANALYSIS
            element_classes = html_element.get('class', [])
            parent = html_element.parent
            parent_classes = parent.get('class', []) if parent else []
            
            # Check grandparent for layout context
            grandparent_classes = []
            if parent and hasattr(parent, 'parent') and parent.parent:
                grandparent_classes = parent.parent.get('class', []) if hasattr(parent.parent, 'get') else []
            
            # Default alignment based on HTML context
            alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            
            # 🎯 ADVANCED ALIGNMENT DETECTION
            
            # Check for explicit center alignment
            center_indicators = ['center', 'text-center', 'align-center', 'company-header', 'report-header', 'report-title', 'report-subtitle']
            if any(cls in element_classes + parent_classes + grandparent_classes for cls in center_indicators):
                alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                logger.info(f"🎯 CENTER alignment: {element_classes}")
            
            # Check for right alignment
            elif any(cls in element_classes + parent_classes for cls in ['right', 'text-right', 'align-right']):
                alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
                logger.info(f"🎯 RIGHT alignment: {element_classes}")
            
            # 📄 CONTENT-SPECIFIC ALIGNMENT RULES
            
            # Content items in analysis tables should justify for better readability
            elif 'content-item' in parent_classes or 'intro-text-block' in element_classes:
                alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
                logger.info(f"🎯 JUSTIFY alignment for content: {element_classes}")
            
            # Titles and headers typically left-align in analysis items
            elif 'item-title' in element_classes or html_element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                logger.info(f"🎯 LEFT alignment for title/header: {element_classes}")
            
            # 🏢 LAYOUT CONTEXT DETECTION
            
            # Elements in flexbox layouts (analysis-item) maintain left/justify alignment
            elif 'analysis-item' in parent_classes or 'analysis-item' in grandparent_classes:
                # For analysis items, content should justify, titles should left-align
                if 'content-item' in element_classes or html_element.name == 'p':
                    alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
                else:
                    alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                logger.info(f"🎯 Analysis item context alignment: {alignment}")
            
            # Company and report headers center
            elif any(cls in parent_classes + grandparent_classes for cls in ['company-header', 'report-header-container', 'slide-header']):
                alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                logger.info(f"🎯 Header context CENTER: {parent_classes}")
            
            # Default left alignment
            else:
                alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                logger.info(f"🎯 DEFAULT LEFT alignment: {element_classes}")
            
            paragraph.alignment = alignment
            return alignment
            
        except Exception as e:
            logger.warning(f"⚠️ Alignment detection failed: {e}, using LEFT")
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            return WD_PARAGRAPH_ALIGNMENT.LEFT

# Global instance for use across the application
word_report_generator = RobecoWordReportGenerator()