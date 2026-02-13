/**
 * Download source guides by asking NotebookLM chat to summarize each source
 * This works around the API limitation of not returning source guides directly
 */
import { NotebookLMClient } from 'notebooklm-kit';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
dotenv.config();

const OUT = path.join(process.cwd(), 'notebook-lm-research', 'full-archive');
const NB = '1ddb4475-1a08-4eba-9615-ad64fbc73365';

async function main() {
  console.log('🔌 Connecting...');
  const sdk = new NotebookLMClient({ authUser: '1' });
  
  try {
    await sdk.connect();
    console.log('✅ Connected!\n');

    const sources = await sdk.sources.list(NB);
    console.log(`📎 ${sources.length} sources — generating guides via chat...\n`);

    const guides: any[] = [];

    for (let i = 0; i < sources.length; i++) {
      const src = sources[i] as any;
      console.log(`🔄 [${i+1}/${sources.length}] ${src.title}`);
      
      try {
        // Ask NotebookLM to give us the source guide for this specific source
        const prompt = `Give me a comprehensive source guide for the source titled "${src.title}". Include: 1) A summary of what this source covers 2) The key topics and concepts 3) Any important details, quotes or data points. Be thorough — this is for archival purposes.`;
        
        const response = await sdk.generation.chat(NB, prompt, {
          sourceIds: [src.sourceId],
        });
        
        const content = typeof response === 'string' ? response : (response as any).text || (response as any).answer || JSON.stringify(response);
        
        guides.push({
          sourceId: src.sourceId,
          title: src.title,
          type: src.type,
          url: src.url,
          guide: content,
          generatedAt: new Date().toISOString(),
        });
        
        console.log(`  ✅ Guide generated (${content.length} chars)`);
      } catch (e: any) {
        console.log(`  ⚠️ ${e.message}`);
        guides.push({
          sourceId: src.sourceId,
          title: src.title,
          type: src.type,
          error: e.message,
        });
      }
    }

    // Save
    const outPath = path.join(OUT, 'source-guides.json');
    fs.writeFileSync(outPath, JSON.stringify(guides, null, 2));
    console.log(`\n💾 Saved: source-guides.json (${(fs.statSync(outPath).size/1024).toFixed(1)} KB)`);
    
    const withGuide = guides.filter(g => g.guide && g.guide.length > 100).length;
    console.log(`📊 Sources with guides: ${withGuide}/${guides.length}`);
    
  } catch (e: any) {
    console.error('❌', e.message);
  } finally {
    sdk.dispose();
  }
}

main();
