#!/usr/bin/env node
/**
 * AI Daily - 更新并推送到 GitHub
 * 由 Moltbot cron 每日 0:00 调用
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, 'docs');

// 模拟一些热门 AI 编程工具资讯来源
const SOURCES = [
  { name: 'Hacker News', url: 'https://news.ycombinator.com/', category: 'community' },
  { name: 'GitHub Trending', url: 'https://github.com/trending', category: 'repos' },
  { name: 'Product Hunt', url: 'https://www.producthunt.com/', category: 'products' },
  { name: 'Dev.to', url: 'https://dev.to/', category: 'articles' },
];

// 这个脚本会被 Moltbot agent 调用
// Moltbot 会使用浏览器或 web_fetch 获取实际内容

async function main() {
  console.log('=== AI Daily Update ===');
  console.log('Time:', new Date().toISOString());
  
  const today = new Date();
  const dateStr = today.toISOString().split('T')[0];
  
  // 读取今日数据（如果由 Moltbot 预先获取）
  const dataFile = path.join(OUTPUT_DIR, `${dateStr}.json`);
  let news = [];
  
  if (fs.existsSync(dataFile)) {
    const data = JSON.parse(fs.readFileSync(dataFile, 'utf-8'));
    news = data.news || [];
  }
  
  console.log(`News items: ${news.length}`);
  
  // Git 提交并推送
  try {
    process.chdir(__dirname);
    execSync('git add -A', { stdio: 'inherit' });
    execSync(`git commit -m "Update ${dateStr}" --allow-empty`, { stdio: 'inherit' });
    execSync('git push', { stdio: 'inherit' });
    console.log('Pushed to GitHub!');
  } catch (e) {
    console.error('Git error:', e.message);
  }
}

main().catch(console.error);
