/**
 * Automated cookie refresh using persistent browser profile.
 * 
 * First run:  Opens browser → you log in → saves profile
 * Later runs: Reuses saved profile → extracts fresh cookies automatically
 * 
 * Run: npx tsx scripts/auth-refresh.ts
 */
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const PROFILE_DIR = path.join(process.cwd(), '.auth-profile');
const ENV_PATH = path.join(process.cwd(), '.env');
const NOTEBOOK_URL = 'https://notebooklm.google.com/?authuser=1';

async function refreshAuth() {
  console.log('🔐 NotebookLM Auth Refresh\n');

  const isFirstRun = !fs.existsSync(path.join(PROFILE_DIR, 'Default'));
  
  if (isFirstRun) {
    console.log('🆕 First run — a browser will open. Please log in to your Google account.');
    console.log('   The session will be saved for future automatic refreshes.\n');
  } else {
    console.log('♻️  Reusing saved session — extracting fresh cookies...\n');
  }

  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: !isFirstRun, // Show browser only on first run
    channel: 'chrome',     // Use system Chrome if available
    args: ['--disable-blink-features=AutomationControlled'],
  });

  const page = context.pages()[0] || await context.newPage();
  
  try {
    // Navigate to NotebookLM
    await page.goto(NOTEBOOK_URL, { waitUntil: 'networkidle', timeout: 60000 });
    
    if (isFirstRun) {
      // Wait for user to log in
      console.log('⏳ Waiting for you to log in (up to 5 minutes)...');
      console.log('   Once you see your notebooks, close the browser or press Ctrl+C.\n');
      
      // Wait until we're on the NotebookLM page (not Google login)
      await page.waitForURL('**/notebooklm.google.com/**', { timeout: 300000 });
      
      // Wait a bit more for page to fully load
      await page.waitForTimeout(3000);
    }

    // Check if we're authenticated
    const url = page.url();
    if (url.includes('accounts.google.com')) {
      console.log('❌ Not authenticated. Please run again and log in.');
      await context.close();
      return false;
    }

    console.log('✅ Authenticated on NotebookLM!');
    
    // Extract cookies
    const cookies = await context.cookies('https://notebooklm.google.com');
    const cookieString = cookies.map(c => `${c.name}=${c.value}`).join('; ');
    
    // Extract auth token (SNlM0e) from page
    let authToken = '';
    try {
      authToken = await page.evaluate(() => {
        return (window as any).WIZ_global_data?.SNlM0e || '';
      });
    } catch (e) {
      console.log('  ⚠️  Could not extract SNlM0e token from page');
    }

    if (!authToken) {
      // Try alternative extraction
      const content = await page.content();
      const match = content.match(/SNlM0e":"([^"]+)"/);
      if (match) authToken = match[1];
    }

    if (!cookieString || !authToken) {
      console.log('❌ Could not extract credentials.');
      console.log(`   Cookies: ${cookieString ? 'OK' : 'MISSING'}`);
      console.log(`   Token: ${authToken ? 'OK' : 'MISSING'}`);
      await context.close();
      return false;
    }

    // Update .env file
    const envContent = `NOTEBOOKLM_AUTH_TOKEN=${authToken}\nNOTEBOOKLM_COOKIES=${cookieString}\n`;
    fs.writeFileSync(ENV_PATH, envContent);
    
    console.log('✅ .env updated with fresh credentials!');
    console.log(`   Token: ${authToken.substring(0, 20)}...`);
    console.log(`   Cookies: ${cookieString.substring(0, 50)}...`);
    console.log(`\n💡 Now run: npx tsx scripts/download-all.ts`);

    await context.close();
    return true;
    
  } catch (error: any) {
    console.error('❌ Error:', error.message);
    await context.close();
    return false;
  }
}

refreshAuth();
