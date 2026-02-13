/**
 * Test connection to NotebookLM via notebooklm-kit SDK
 * Run: npx tsx scripts/test-connection.ts
 */
import { NotebookLMClient } from 'notebooklm-kit';
import dotenv from 'dotenv';

dotenv.config();

async function main() {
  console.log('🔌 Connecting to NotebookLM...');
  
  const sdk = new NotebookLMClient({
    authUser: '1',  // Your notebook is on authuser=1 (2nd Google account)
  });
  
  try {
    await sdk.connect();
    console.log('✅ Connected successfully!\n');

    // List notebooks
    const notebooks = await sdk.notebooks.list();
    console.log(`📚 Found ${notebooks.length} notebooks:\n`);
    
    for (const nb of notebooks) {
      console.log(`  📓 ${nb.title || 'Untitled'}`);
      console.log(`     ID: ${nb.id}`);
      console.log('');
    }

    // If we have the target notebook, get details
    const targetId = '1ddb4475-1a08-4eba-9615-ad64fbc73365';
    const target = notebooks.find(nb => nb.id?.includes(targetId.replace(/-/g, '')));
    
    if (target) {
      console.log(`\n🎯 Found target notebook: ${target.title}`);
      
      // List sources
      const sources = await sdk.sources.list(target.id);
      console.log(`📎 Sources: ${sources.length}`);

      // List notes
      const notes = await sdk.notes.list(target.id);
      console.log(`📝 Notes: ${notes.length}`);

      // List artifacts
      const artifacts = await sdk.artifacts.list(target.id);
      console.log(`🎨 Artifacts: ${artifacts.length}`);
      
      for (const art of artifacts) {
        console.log(`   - ${art.title || art.type || 'Unknown'} (${art.type})`);
      }
    }

    console.log('\n✅ Connection test PASSED!');
  } catch (error: any) {
    console.error('❌ Connection FAILED:', error.message || error);
    if (error.message?.includes('auth') || error.message?.includes('401')) {
      console.error('\n💡 Tip: Your cookies may have expired. Get fresh ones from browser DevTools.');
    }
  } finally {
    sdk.dispose();
  }
}

main();
