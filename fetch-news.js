#!/usr/bin/env node
/**
 * AI Daily - 每日AI编程工具资讯抓取
 * 数据源: Hacker News, Product Hunt, GitHub Trending
 */

const fs = require('fs');
const path = require('path');

const BRAVE_API_KEY = process.env.BRAVE_API_KEY;
const OUTPUT_DIR = path.join(__dirname, 'docs');

// AI编程工具关键词
const KEYWORDS = [
  'AI coding assistant',
  'AI programming tools',
  'code generation AI',
  'LLM developer tools',
  'AI IDE plugin',
  'GitHub Copilot alternative',
  'Claude Code',
  'Cursor AI',
  'AI code review',
  'AI debugging'
];

async function searchBrave(query) {
  if (!BRAVE_API_KEY) {
    console.log('No Brave API key, using mock data');
    return [];
  }
  
  const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=5&freshness=pd`;
  
  try {
    const res = await fetch(url, {
      headers: { 'X-Subscription-Token': BRAVE_API_KEY }
    });
    const data = await res.json();
    return data.web?.results || [];
  } catch (e) {
    console.error('Search error:', e.message);
    return [];
  }
}

async function fetchAllNews() {
  const allResults = [];
  const seen = new Set();
  
  for (const keyword of KEYWORDS.slice(0, 5)) { // 限制请求数
    console.log(`Searching: ${keyword}`);
    const results = await searchBrave(keyword);
    
    for (const r of results) {
      if (!seen.has(r.url)) {
        seen.add(r.url);
        allResults.push({
          title: r.title,
          url: r.url,
          description: r.description,
          source: new URL(r.url).hostname,
          keyword
        });
      }
    }
    
    // 避免请求过快
    await new Promise(r => setTimeout(r, 500));
  }
  
  return allResults;
}

function generateHTML(news, date) {
  const dateStr = date.toISOString().split('T')[0];
  
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI 编程工具日报 - ${dateStr}</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #c9d1d9;
      --text-muted: #8b949e;
      --accent: #58a6ff;
      --accent-hover: #79c0ff;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 2rem;
    }
    .container { max-width: 800px; margin: 0 auto; }
    header {
      text-align: center;
      margin-bottom: 3rem;
      padding-bottom: 2rem;
      border-bottom: 1px solid var(--border);
    }
    h1 {
      font-size: 2rem;
      background: linear-gradient(135deg, #58a6ff 0%, #a371f7 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.5rem;
    }
    .date { color: var(--text-muted); font-size: 0.9rem; }
    .news-list { display: flex; flex-direction: column; gap: 1rem; }
    .news-item {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.25rem;
      transition: border-color 0.2s, transform 0.2s;
    }
    .news-item:hover {
      border-color: var(--accent);
      transform: translateY(-2px);
    }
    .news-item h3 {
      font-size: 1.1rem;
      margin-bottom: 0.5rem;
    }
    .news-item h3 a {
      color: var(--accent);
      text-decoration: none;
    }
    .news-item h3 a:hover { color: var(--accent-hover); }
    .news-item p {
      color: var(--text-muted);
      font-size: 0.9rem;
      margin-bottom: 0.75rem;
    }
    .news-meta {
      display: flex;
      gap: 1rem;
      font-size: 0.8rem;
      color: var(--text-muted);
    }
    .tag {
      background: rgba(88, 166, 255, 0.1);
      color: var(--accent);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
    }
    .empty {
      text-align: center;
      padding: 3rem;
      color: var(--text-muted);
    }
    footer {
      margin-top: 3rem;
      padding-top: 2rem;
      border-top: 1px solid var(--border);
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
    }
    .archive-link {
      display: inline-block;
      margin-top: 1rem;
      color: var(--accent);
      text-decoration: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🤖 AI 编程工具日报</h1>
      <p class="date">${dateStr}</p>
    </header>
    
    <main>
      ${news.length > 0 ? `
        <div class="news-list">
          ${news.map(item => `
            <article class="news-item">
              <h3><a href="${item.url}" target="_blank" rel="noopener">${item.title}</a></h3>
              <p>${item.description || ''}</p>
              <div class="news-meta">
                <span>📍 ${item.source}</span>
                <span class="tag">${item.keyword}</span>
              </div>
            </article>
          `).join('')}
        </div>
      ` : `
        <div class="empty">
          <p>今日暂无新资讯</p>
        </div>
      `}
    </main>
    
    <footer>
      <p>由 Moltbot 自动抓取生成</p>
      <a href="archive.html" class="archive-link">📚 查看历史归档</a>
    </footer>
  </div>
</body>
</html>`;
}

async function main() {
  console.log('=== AI Daily News Fetcher ===');
  console.log('Time:', new Date().toISOString());
  
  // 确保输出目录存在
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
  
  // 抓取新闻
  const news = await fetchAllNews();
  console.log(`Found ${news.length} news items`);
  
  // 生成今日页面
  const today = new Date();
  const html = generateHTML(news, today);
  
  // 写入 index.html
  fs.writeFileSync(path.join(OUTPUT_DIR, 'index.html'), html);
  console.log('Generated: docs/index.html');
  
  // 保存原始数据
  const dateStr = today.toISOString().split('T')[0];
  fs.writeFileSync(
    path.join(OUTPUT_DIR, `${dateStr}.json`),
    JSON.stringify({ date: dateStr, news }, null, 2)
  );
  console.log(`Saved: docs/${dateStr}.json`);
  
  console.log('Done!');
}

main().catch(console.error);
