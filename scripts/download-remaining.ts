/**
 * Download the 4 remaining artifacts that failed
 * Run: npx tsx scripts/auth-refresh.ts && npx tsx scripts/download-remaining.ts
 */
import { NotebookLMClient } from 'notebooklm-kit';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

dotenv.config();

const OUTPUT_DIR = path.join(process.cwd(), 'notebook-lm-research', 'full-archive');
const NOTEBOOK_ID = '1ddb4475-1a08-4eba-9615-ad64fbc73365';

// The 4 missing artifacts
const MISSING_ARTIFACTS = [
  { id: '572cff53-86be-42af-a56c-6e1c02bc0c94', title: 'The SAMAS Blueprint (Audio)', type: 1 },
  { id: '2c510914-2d3e-44b4-a653-264b05c82444', title: 'Agent Quiz', type: 5 },
  { id: '6359b13e-8030-4b69-b992-106ea132759e', title: 'Agents Flashcards', type: 6 },
  { id: 'e4df6c94-b451-4a2e-9a9d-402e48a848ab', title: 'SAMAS Architecture Comparison', type: 9 },
];

function saveJSON(filename: string, data: any) {
  const filepath = path.join(OUTPUT_DIR, filename);
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
  console.log(`  💾 Saved: ${filename}`);
}

async function main() {
  console.log('🔌 Connecting...\n');
  const sdk = new NotebookLMClient({ authUser: '1' });
  
  try {
    await sdk.connect();
    console.log('✅ Connected!\n');

    for (const art of MISSING_ARTIFACTS) {
      console.log(`\n🔄 ${art.title} (type ${art.type})`);
      
      // Get details
      try {
        const detail = await sdk.artifacts.get(art.id, NOTEBOOK_ID);
        const safeName = art.title.replace(/[^a-zA-Z0-9_-]/g, '_').substring(0, 50);
        saveJSON(`artifacts/${safeName}-detail.json`, detail);
        console.log(`  ✅ Details saved`);
      } catch (e: any) {
        console.log(`  ⚠️  Details: ${e.message}`);
      }

      // Download file
      try {
        const downloadPath = path.join(OUTPUT_DIR, 'artifacts');
        await sdk.artifacts.download(art.id, downloadPath, NOTEBOOK_ID, art.type);
        console.log(`  ✅ Downloaded!`);
      } catch (e: any) {
        console.log(`  ⚠️  Download: ${e.message}`);
      }
    }

    // Final inventory
    console.log('\n' + '='.repeat(50));
    console.log('📁 FINAL FILES:');
    const files = fs.readdirSync(path.join(OUTPUT_DIR, 'artifacts'));
    for (const f of files) {
      const size = fs.statSync(path.join(OUTPUT_DIR, 'artifacts', f)).size;
      console.log(`  ${(size/1024).toFixed(1)} KB  ${f}`);
    }
  } catch (e: any) {
    console.error('❌', e.message);
  } finally {
    sdk.dispose();
  }
}

main();
