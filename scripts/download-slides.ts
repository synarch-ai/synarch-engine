/**
 * Download slide decks using the direct downloadSlidesFile function
 */
import { NotebookLMClient } from 'notebooklm-kit';
import { downloadSlidesFile } from 'notebooklm-kit/dist/src/services/artifacts.js';
import dotenv from 'dotenv';
import path from 'path';
dotenv.config();

const OUT = path.join(process.cwd(), 'notebook-lm-research', 'full-archive', 'artifacts');
const NB = '1ddb4475-1a08-4eba-9615-ad64fbc73365';

const SLIDES = [
  { id: 'a2a8c736-126b-44d4-ae6f-f0b2ed517b64', title: 'SAMAS Architecture Deep Dive' },
  { id: 'e4df6c94-b451-4a2e-9a9d-402e48a848ab', title: 'SAMAS Architecture Comparison' },
];

async function main() {
  console.log('🔌 Connecting...');
  const sdk = new NotebookLMClient({ authUser: '1' });
  
  try {
    await sdk.connect();
    console.log('✅ Connected!\n');

    // Access the internal RPC client
    const rpc = (sdk as any).rpc || (sdk as any)._rpc || (sdk as any).client;
    
    if (!rpc) {
      // Try alternative: use artifacts.get with download options
      console.log('Trying artifacts.get with options...');
      for (const slide of SLIDES) {
        console.log(`\n🔄 ${slide.title}`);
        try {
          // Try get with includeContent option
          const result = await sdk.artifacts.get(slide.id, NB, { 
            includeContent: true,
            download: true 
          } as any);
          console.log(`  Keys: ${Object.keys(result).join(', ')}`);
          
          // Check for any URL-like fields
          const str = JSON.stringify(result);
          const urlMatches = str.match(/https?:\/\/[^\s"]+/g);
          if (urlMatches) {
            console.log(`  Found ${urlMatches.length} URLs:`);
            urlMatches.forEach(u => console.log(`    ${u.substring(0, 100)}`));
          } else {
            console.log('  No URLs found in response');
          }
        } catch (e: any) {
          console.log(`  ⚠️ ${e.message}`);
        }
      }
    } else {
      console.log('Found RPC client, trying direct slide download...');
      for (const slide of SLIDES) {
        console.log(`\n🔄 ${slide.title}`);
        try {
          const result = await downloadSlidesFile(rpc, slide.id, NB, { outputPath: OUT });
          console.log(`  ✅ Downloaded: ${JSON.stringify(result).substring(0, 200)}`);
        } catch (e: any) {
          console.log(`  ⚠️ ${e.message}`);
        }
      }
    }
  } catch (e: any) {
    console.error('❌', e.message);
  } finally {
    sdk.dispose();
  }
}

main();
