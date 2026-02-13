/**
 * Download full source guides/summaries/transcripts for each source
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

    // Get source list first
    const sources = await sdk.sources.list(NB);
    console.log(`📎 Found ${sources.length} sources\n`);

    const fullSources: any[] = [];

    // Fetch EACH source individually to get full content/guide
    for (let i = 0; i < sources.length; i++) {
      const src = sources[i] as any;
      const srcId = src.sourceId || src.id;
      console.log(`🔄 [${i+1}/${sources.length}] ${src.title}`);
      
      try {
        const full = await sdk.sources.get(NB, srcId);
        fullSources.push(full);
        const str = JSON.stringify(full);
        const hasContent = str.length > 500;
        console.log(`  ✅ ${hasContent ? str.length + ' chars (HAS CONTENT)' : 'metadata only'}`);
        console.log(`  Keys: ${Object.keys(full as any).join(', ')}`);
      } catch (e: any) {
        console.log(`  ⚠️ ${e.message}`);
        fullSources.push({ ...src, error: e.message });
      }
    }

    // Save all full sources
    const outPath = path.join(OUT, 'sources-with-guides.json');
    fs.writeFileSync(outPath, JSON.stringify(fullSources, null, 2));
    console.log(`\n💾 Saved: sources-with-guides.json (${(fs.statSync(outPath).size/1024).toFixed(1)} KB)`);
    
    // Show what we got
    console.log('\n📊 Summary:');
    let withContent = 0;
    for (const s of fullSources) {
      const str = JSON.stringify(s);
      if (str.length > 500) withContent++;
    }
    console.log(`  Sources with content: ${withContent}/${fullSources.length}`);
    
  } catch (e: any) {
    console.error('❌', e.message);
  } finally {
    sdk.dispose();
  }
}

main();
