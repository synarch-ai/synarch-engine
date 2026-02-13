/**
 * Download everything EXCEPT audio/video files
 * Quiz, Flashcards, Comparison, Study Guide details + all notes + all sources
 */
import { NotebookLMClient } from 'notebooklm-kit';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

dotenv.config();

const OUTPUT_DIR = path.join(process.cwd(), 'notebook-lm-research', 'full-archive');
const NOTEBOOK_ID = '1ddb4475-1a08-4eba-9615-ad64fbc73365';

// All 8 artifacts — skip audio/video DOWNLOADS but still get details
const ALL_ARTIFACTS = [
  { id: '664cf931-af9f-4c0c-b1b0-be18cd6816bb', title: 'SAMAS From Magic to Production', type: 11, skipDownload: true },  // Video
  { id: '748ad0a1-0851-44b1-8a0e-44cb068721e9', title: 'The Blueprint For Enterprise Agent Swarms', type: 10, skipDownload: true }, // Audio
  { id: 'a2a8c736-126b-44d4-ae6f-f0b2ed517b64', title: 'SAMAS Architecture Deep Dive', type: 9, skipDownload: false },  // Slides
  { id: '12ef54c5-83c4-4a1a-96a5-dda81cf06892', title: 'SAMAS Enterprise Multi-Agent Systems Blueprint', type: 8, skipDownload: false }, // Study Guide
  { id: '572cff53-86be-42af-a56c-6e1c02bc0c94', title: 'The SAMAS Blueprint Audio', type: 1, skipDownload: true },  // Audio
  { id: '2c510914-2d3e-44b4-a653-264b05c82444', title: 'Agent Quiz', type: 5, skipDownload: false },  // Quiz — WANT THIS
  { id: '6359b13e-8030-4b69-b992-106ea132759e', title: 'Agents Flashcards', type: 6, skipDownload: false },  // Flashcards — WANT THIS
  { id: 'e4df6c94-b451-4a2e-9a9d-402e48a848ab', title: 'SAMAS Architecture Comparison', type: 9, skipDownload: false },  // Comparison — WANT THIS
];

function save(filename: string, data: any) {
  const filepath = path.join(OUTPUT_DIR, filename);
  fs.mkdirSync(path.dirname(filepath), { recursive: true });
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
  console.log(`  💾 ${filename} (${(Buffer.byteLength(JSON.stringify(data, null, 2))/1024).toFixed(1)} KB)`);
}

async function main() {
  console.log('🔌 Connecting...');
  const sdk = new NotebookLMClient({ authUser: '1' });
  
  try {
    await sdk.connect();
    console.log('✅ Connected!\n');

    // Get ALL artifact details + download non-audio/video
    console.log('🎨 Artifacts (details for all, download for non-audio/video):');
    for (const art of ALL_ARTIFACTS) {
      const safeName = art.title.replace(/[^a-zA-Z0-9_-]/g, '_').substring(0, 60);
      
      // Always get details
      try {
        const detail = await sdk.artifacts.get(art.id, NOTEBOOK_ID);
        save(`artifacts/${safeName}-detail.json`, detail);
        console.log(`  ✅ ${art.title} — detail saved`);
      } catch (e: any) {
        console.log(`  ⚠️  ${art.title} detail: ${e.message}`);
      }

      // Download only non-audio/video
      if (!art.skipDownload) {
        try {
          const downloadPath = path.join(OUTPUT_DIR, 'artifacts');
          await sdk.artifacts.download(art.id, downloadPath, NOTEBOOK_ID, art.type);
          console.log(`  ✅ ${art.title} — file downloaded!`);
        } catch (e: any) {
          console.log(`  ⚠️  ${art.title} download: ${e.message}`);
        }
      } else {
        console.log(`  ⏭️  ${art.title} — skipped (audio/video, download manually)`);
      }
    }

    // Final file list
    console.log('\n' + '='.repeat(50));
    console.log('📁 ALL FILES IN ARCHIVE:');
    const listDir = (dir: string, prefix = '') => {
      for (const f of fs.readdirSync(dir).sort()) {
        const full = path.join(dir, f);
        const stat = fs.statSync(full);
        if (stat.isDirectory()) {
          console.log(`${prefix}📁 ${f}/`);
          listDir(full, prefix + '  ');
        } else {
          const size = stat.size > 1024*1024 ? `${(stat.size/1024/1024).toFixed(1)}MB` : `${(stat.size/1024).toFixed(1)}KB`;
          console.log(`${prefix}📄 ${f} (${size})`);
        }
      }
    };
    listDir(OUTPUT_DIR);
    
    console.log('\n✅ DONE — everything except audio/video files is downloaded.');
    
  } catch (e: any) {
    console.error('❌', e.message);
  } finally {
    sdk.dispose();
  }
}

main();
