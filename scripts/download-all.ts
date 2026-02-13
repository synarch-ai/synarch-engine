/**
 * Download EVERYTHING from a NotebookLM notebook
 * Run: npx tsx scripts/download-all.ts
 */
import { NotebookLMClient } from 'notebooklm-kit';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

dotenv.config();

const OUTPUT_DIR = path.join(process.cwd(), 'notebook-lm-research', 'full-archive');
const NOTEBOOK_URL_ID = '1ddb4475-1a08-4eba-9615-ad64fbc73365';

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function saveJSON(filename: string, data: any) {
  const filepath = path.join(OUTPUT_DIR, filename);
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
  console.log(`  💾 Saved: ${filename}`);
}

async function main() {
  ensureDir(OUTPUT_DIR);
  ensureDir(path.join(OUTPUT_DIR, 'artifacts'));
  
  console.log('🔌 Connecting to NotebookLM...\n');
  
  const sdk = new NotebookLMClient({
    authUser: '1',
  });
  
  try {
    await sdk.connect();
    console.log('✅ Connected!\n');

    // Step 1: Find the target notebook
    console.log('📚 Step 1: Finding target notebook...');
    const notebooks = await sdk.notebooks.list();
    console.log(`  Found ${notebooks.length} total notebooks`);
    
    // Save all notebook titles for reference
    saveJSON('all-notebooks.json', notebooks.map((nb: any) => ({
      title: nb.title,
      id: nb.notebookId || nb.id || nb.projectId,
      raw_keys: Object.keys(nb),
    })));

    // Find the target - inspect first to find the right ID property
    const firstNb = notebooks[0];
    console.log(`\n  📋 Notebook object keys: ${Object.keys(firstNb).join(', ')}`);
    
    // Try multiple possible ID fields
    let notebookId: string | undefined;
    for (const nb of notebooks) {
      const possibleId = (nb as any).notebookId || (nb as any).id || (nb as any).projectId || (nb as any).resourceId;
      const possibleUrl = JSON.stringify(nb);
      if (possibleUrl.includes(NOTEBOOK_URL_ID.replace(/-/g, '')) || possibleUrl.includes(NOTEBOOK_URL_ID)) {
        notebookId = possibleId;
        console.log(`\n  🎯 Found target: ${(nb as any).title}`);
        console.log(`     ID: ${notebookId}`);
        saveJSON('target-notebook-raw.json', nb);
        break;
      }
    }

    if (!notebookId) {
      // If ID matching fails, use the title match
      for (const nb of notebooks) {
        if ((nb as any).title?.includes('Pantheon')) {
          notebookId = (nb as any).notebookId || (nb as any).id || (nb as any).projectId;
          console.log(`\n  🎯 Found by title: ${(nb as any).title}`);
          console.log(`     ID: ${notebookId}`);
          saveJSON('target-notebook-raw.json', nb);
          break;
        }
      }
    }

    if (!notebookId) {
      // Last resort: dump all notebooks raw to find the ID
      console.log('\n  ⚠️  Could not find notebook ID automatically.');
      console.log('  Dumping first 3 notebooks raw for manual inspection...');
      saveJSON('debug-notebooks-raw.json', notebooks.slice(0, 3));
      console.log('  Check notebook-lm-research/full-archive/debug-notebooks-raw.json');
      sdk.dispose();
      return;
    }

    // Step 2: Download Sources
    console.log('\n📎 Step 2: Downloading sources...');
    try {
      const sources = await sdk.sources.list(notebookId);
      console.log(`  Found ${sources.length} sources`);
      saveJSON('sources-list.json', sources);

      // Try to get full source content
      try {
        const fullSources = await sdk.sources.get(notebookId);
        saveJSON('sources-full.json', fullSources);
        console.log(`  ✅ Full source content saved`);
      } catch (e: any) {
        console.log(`  ⚠️  Could not get full sources: ${e.message}`);
      }
    } catch (e: any) {
      console.log(`  ❌ Sources failed: ${e.message}`);
    }

    // Step 3: Download Notes
    console.log('\n📝 Step 3: Downloading notes...');
    try {
      const notes = await sdk.notes.list(notebookId);
      console.log(`  Found ${notes.length} notes`);
      saveJSON('notes.json', notes);
    } catch (e: any) {
      console.log(`  ❌ Notes failed: ${e.message}`);
    }

    // Step 4: Download Artifacts (mind maps, audio, video, slides, flashcards)
    console.log('\n🎨 Step 4: Downloading artifacts...');
    try {
      const artifacts = await sdk.artifacts.list(notebookId);
      console.log(`  Found ${artifacts.length} artifacts`);
      saveJSON('artifacts-list.json', artifacts);

      for (const art of artifacts) {
        const artId = (art as any).artifactId || (art as any).id;
        const artType = (art as any).type || (art as any).artifactType || 'unknown';
        const artTitle = (art as any).title || artType;
        console.log(`\n  🔄 Processing artifact: ${artTitle} (${artType})`);

        // Get artifact details — NOTE: artifactId comes FIRST, then notebookId
        try {
          const detail = await sdk.artifacts.get(artId, notebookId);
          const safeTitle = (artTitle || 'unknown').replace(/[^a-zA-Z0-9_-]/g, '_').substring(0, 50);
          saveJSON(`artifacts/${safeTitle}-detail.json`, detail);
          console.log(`    ✅ Details saved`);
        } catch (e: any) {
          console.log(`    ⚠️  Details failed: ${e.message}`);
        }

        // Download artifact file — NOTE: artifactId FIRST, then folderPath, then notebookId
        try {
          const downloadPath = path.join(OUTPUT_DIR, 'artifacts');
          const result = await sdk.artifacts.download(artId, downloadPath, notebookId, artType);
          console.log(`    ✅ Downloaded to artifacts/`);
        } catch (e: any) {
          console.log(`    ⚠️  Download failed: ${e.message}`);
        }
      }
    } catch (e: any) {
      console.log(`  ❌ Artifacts failed: ${e.message}`);
    }

    // Step 5: Chat History
    console.log('\n💬 Step 5: Downloading chat config...');
    try {
      // Note: Chat history from previous conversations may not be available via SDK
      // But we can save the chat configuration
      console.log('  (Chat history from previous sessions is browser-only)');
      console.log('  Existing chat_history.json from Antigravity archive is still valid');
    } catch (e: any) {
      console.log(`  ⚠️  Chat: ${e.message}`);
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 DOWNLOAD COMPLETE');
    console.log('='.repeat(60));
    console.log(`📂 Output: ${OUTPUT_DIR}`);
    console.log('\nFiles:');
    
    const files = fs.readdirSync(OUTPUT_DIR);
    for (const f of files) {
      const stat = fs.statSync(path.join(OUTPUT_DIR, f));
      if (stat.isDirectory()) {
        const subFiles = fs.readdirSync(path.join(OUTPUT_DIR, f));
        console.log(`  📁 ${f}/ (${subFiles.length} files)`);
      } else {
        const size = (stat.size / 1024).toFixed(1);
        console.log(`  📄 ${f} (${size} KB)`);
      }
    }

  } catch (error: any) {
    console.error('❌ Error:', error.message || error);
  } finally {
    sdk.dispose();
  }
}

main();
