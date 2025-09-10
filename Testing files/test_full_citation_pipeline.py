#!/usr/bin/env python3
"""
Full Citation Pipeline Test
Comprehensive test to diagnose exactly where citations are being lost
"""

import sys
import os
import asyncio
import json
from datetime import datetime

sys.path.append('src')
from robeco.backend.ultra_sophisticated_multi_agent_engine import UltraSophisticatedMultiAgentEngine, AnalysisContext

async def full_citation_pipeline_test():
    print('🔬 FULL CITATION PIPELINE DIAGNOSTIC')
    print('=' * 60)
    
    engine = UltraSophisticatedMultiAgentEngine()
    
    context = AnalysisContext(
        company_name='Apple Inc',
        ticker='AAPL',
        user_query='Generate comprehensive analysis with real citations and sources',
        session_id='full_pipeline_test',
        start_time=datetime.now()
    )
    
    print(f'🎯 Testing: {context.company_name} ({context.ticker})')
    print(f'📅 Session: {context.session_id}')
    print('\n' + '='*60)
    
    # Track the entire pipeline
    pipeline_stats = {
        'sources_detected': 0,
        'real_urls_found': 0,
        'content_chunks': 0,
        'final_content_length': 0,
        'citations_in_content': 0,
        'sources_in_final': False,
        'grounding_working': False,
        'pipeline_breakdown': []
    }
    
    all_sources = []
    content_chunks = []
    
    print('🚀 STARTING FUNDAMENTALS ANALYSIS...')
    print('-' * 40)
    
    async for result in engine.generate_single_agent_analysis('fundamentals', context):
        result_type = result.get('type', '')
        data = result.get('data', {})
        
        # Track sources being detected
        if result_type == 'streaming_research_source':
            pipeline_stats['sources_detected'] += 1
            source_data = data.get('source', {})
            all_sources.append(source_data)
            
            url = source_data.get('url', '')
            title = source_data.get('title', 'Unknown')
            
            if 'vertexaisearch.cloud.google.com' in url:
                pipeline_stats['real_urls_found'] += 1
                
            if pipeline_stats['sources_detected'] <= 5:
                print(f'  📚 Source {pipeline_stats["sources_detected"]}: {title}')
                print(f'      URL: {url[:80]}...')
                real_status = '✅ REAL' if 'vertexaisearch.cloud.google.com' in url else '⚠️ CONSTRUCTED'
                print(f'      Status: {real_status}')
        
        # Track content chunks
        elif result_type == 'streaming_ai_content':
            chunk = data.get('content_chunk', '') or data.get('chunk', '')
            if chunk.strip():
                pipeline_stats['content_chunks'] += 1
                content_chunks.append(chunk)
                
                if pipeline_stats['content_chunks'] <= 3:
                    print(f'  📝 Content chunk {pipeline_stats["content_chunks"]}: "{chunk[:50]}..."')
        
        # Final content analysis
        elif result_type == 'streaming_analysis_completed':
            print('\n🔍 FINAL PIPELINE ANALYSIS:')
            print('-' * 35)
            
            final_content = data.get('content', '')
            grounding_metadata = data.get('grounding_metadata', {})
            
            pipeline_stats['final_content_length'] = len(final_content)
            pipeline_stats['grounding_working'] = (
                grounding_metadata.get('grounding_chunks', 0) > 0 or 
                grounding_metadata.get('grounding_supports', 0) > 0
            )
            
            # Count citations in final content
            import re
            citations = re.findall(r'\[(\d+)\]', final_content)
            pipeline_stats['citations_in_content'] = len(citations)
            
            # Check for sources section
            pipeline_stats['sources_in_final'] = '## 📚 Research Sources' in final_content
            
            print(f'📊 PIPELINE RESULTS:')
            print(f'   Sources detected during streaming: {pipeline_stats["sources_detected"]}')
            print(f'   Real URLs found: {pipeline_stats["real_urls_found"]}')
            print(f'   Content chunks received: {pipeline_stats["content_chunks"]}')
            print(f'   Final content length: {pipeline_stats["final_content_length"]:,} characters')
            print(f'   Citations in final content: {pipeline_stats["citations_in_content"]}')
            print(f'   Sources section in final: {"✅" if pipeline_stats["sources_in_final"] else "❌"}')
            print(f'   Grounding metadata working: {"✅" if pipeline_stats["grounding_working"] else "❌"}')
            
            # Detailed analysis
            print(f'\n🔬 DETAILED BREAKDOWN:')
            
            if pipeline_stats['sources_detected'] > 0:
                print(f'   ✅ Source detection: WORKING ({pipeline_stats["sources_detected"]} sources)')
            else:
                print(f'   ❌ Source detection: FAILED')
                
            if pipeline_stats['real_urls_found'] > 0:
                print(f'   ✅ Real URL extraction: WORKING ({pipeline_stats["real_urls_found"]} real URLs)')
            else:
                print(f'   ❌ Real URL extraction: FAILED')
                
            if pipeline_stats['content_chunks'] > 0:
                print(f'   ✅ Content streaming: WORKING ({pipeline_stats["content_chunks"]} chunks)')
            else:
                print(f'   ❌ Content streaming: FAILED')
                
            if pipeline_stats['final_content_length'] > 0:
                print(f'   ✅ Final content assembly: WORKING ({pipeline_stats["final_content_length"]:,} chars)')
            else:
                print(f'   ❌ Final content assembly: FAILED - THIS IS THE ISSUE!')
                
            if pipeline_stats['citations_in_content'] > 0:
                print(f'   ✅ Citation integration: WORKING ({pipeline_stats["citations_in_content"]} citations)')
            else:
                print(f'   ❌ Citation integration: FAILED')
                
            if pipeline_stats['sources_in_final']:
                print(f'   ✅ Sources section: INCLUDED')
            else:
                print(f'   ❌ Sources section: MISSING')
            
            # Show content sample if available
            if pipeline_stats['final_content_length'] > 0:
                print(f'\n📄 FINAL CONTENT SAMPLE (first 300 chars):')
                print(f'"{final_content[:300]}..."')
            else:
                print(f'\n🚨 CRITICAL ISSUE: Final content is EMPTY despite receiving {pipeline_stats["content_chunks"]} content chunks!')
                
                if content_chunks:
                    combined_chunks = ''.join(content_chunks)
                    print(f'\n🔍 CHUNK ANALYSIS:')
                    print(f'   Total chunks collected: {len(content_chunks)}')
                    print(f'   Combined chunk length: {len(combined_chunks):,} characters')
                    print(f'   Sample chunk content: "{combined_chunks[:200]}..."')
                    print(f'\n💡 DIAGNOSIS: Content chunks are being received but not assembled into final content!')
            
            # Show source sample
            if all_sources:
                print(f'\n🔗 SOURCE SAMPLES (first 3):')
                for i, source in enumerate(all_sources[:3], 1):
                    title = source.get('title', 'Unknown')
                    url = source.get('url', 'No URL')
                    url_type = 'REAL Google' if 'vertexaisearch.cloud.google.com' in url else 'Constructed'
                    print(f'   [{i}] {title} ({url_type})')
                    print(f'       {url[:60]}...')
            
            break
    
    print(f'\n' + '='*60)
    print(f'🎯 DIAGNOSIS SUMMARY:')
    print(f'=' * 60)
    
    if pipeline_stats['sources_detected'] > 0 and pipeline_stats['real_urls_found'] > 0:
        print(f'✅ GOOGLE SEARCH: Working perfectly! Getting {pipeline_stats["real_urls_found"]} real URLs')
    else:
        print(f'❌ GOOGLE SEARCH: Not working')
        
    if pipeline_stats['content_chunks'] > 0 and pipeline_stats['final_content_length'] == 0:
        print(f'🚨 CRITICAL ISSUE: Content assembly pipeline is broken!')
        print(f'   • Receiving {pipeline_stats["content_chunks"]} content chunks')
        print(f'   • But final content length is 0 characters')
        print(f'   • This is where the citations are getting lost!')
    elif pipeline_stats['final_content_length'] > 0:
        print(f'✅ CONTENT ASSEMBLY: Working')
    
    if pipeline_stats['citations_in_content'] == 0:
        print(f'❌ CITATION INTEGRATION: Failed - no [1], [2], [3] citations in final content')
    else:
        print(f'✅ CITATION INTEGRATION: Working with {pipeline_stats["citations_in_content"]} citations')
    
    print(f'\n🔧 RECOMMENDED FIX:')
    if pipeline_stats['final_content_length'] == 0:
        print(f'   Focus on fixing the content assembly pipeline')
        print(f'   Sources are working, content chunks are received, but final assembly fails')
    else:
        print(f'   Focus on citation integration into the final content')

if __name__ == '__main__':
    try:
        asyncio.run(full_citation_pipeline_test())
        print(f'\n✅ Full pipeline test completed!')
    except Exception as e:
        print(f'\n❌ Test failed: {e}')
        import traceback
        traceback.print_exc()