/**
 * Download ONLY the 3 missing non-audio/video artifacts: Quiz, Flashcards, Comparison
 */
import { NotebookLMClient } from 'notebooklm-kit';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
dotenv.config();

const OUT = path.join(process.cwd(), 'notebook-lm-research', 'full-archive');
const NB = '1ddb4475-1a08-4eba-9615-ad64fbc73365';

const TARGETS = [
  { id: '2c510914-2d3e-44b4-a653-264b05c82444', title: 'Agent_Quiz', type: 5 },
  { id: '6359b13e-8030-4b69-b992-106ea132759e', title: 'Agents_Flashcards', type: 6 },
  { id: 'e4df6c94-b451-4a2e-9a9d-402e48a848ab', title: 'SAMAS_Architecture_Comparison', type: 9 },
];

async function main() {
  console.log('🔌 Connecting...');
  const sdk = new NotebookLMClient({ authUser: '1' });
  try {
    await sdk.connect();
    console.log('✅ Connected!\n');

    for (const t of TARGETS) {
      console.log(`🔄 ${t.title} (type ${t.type})`);
      
      try {
        const detail = await sdk.artifacts.get(t.id, NB);
        const fp = path.join(OUT, 'artifacts', `${t.title}-detail.json`);
        fs.writeFileSync(fp, JSON.stringify(detail, null, 2));
        console.log(`  ✅ Detail saved (${(Buffer.byteLength(JSON.stringify(detail,null,2))/1024).toFixed(1)} KB)`);
      } catch (e: any) { console.log(`  ⚠️ Detail: ${e.message}`); }

      try {
        await sdk.artifacts.download(t.id, path.join(OUT, 'artifacts'), NB, t.type);
        console.log(`  ✅ File downloaded!`);
      } catch (e: any) { console.log(`  ⚠️ Download: ${e.message}`); }
    }

    console.log('\n📁 ARTIFACTS FOLDER:');
    fs.readdirSync(path.join(OUT, 'artifacts')).forEach(f => {
      const s = fs.statSync(path.join(OUT, 'artifacts', f));
      const sz = s.size > 1048576 ? `${(s.size/1048576).toFixed(1)}MB` : `${(s.size/1024).toFixed(1)}KB`;
      console.log(`  ${sz.padStart(8)}  ${f}`);
    });
    console.log('\n✅ DONE');
  } catch (e: any) { console.error('❌', e.message); }
  finally { sdk.dispose(); }
}
main();
