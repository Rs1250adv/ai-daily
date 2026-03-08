#!/usr/bin/env python3
"""
AI Daily - 轻量级版本（先跑通）
使用 requests + BeautifulSoup
"""

import os
import json
import re
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'requests', 'beautifulsoup4', '-q'])
    import requests
    from bs4 import BeautifulSoup

OUTPUT_DIR = "docs"

def ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_hackernews():
    """抓取 Hacker News"""
    print("🕷️ 抓取 Hacker News...")
    try:
        resp = requests.get('https://news.ycombinator.com/', timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        news = []
        ai_keywords = ['ai', 'llm', 'gpt', 'claude', 'cursor', 'copilot', 'coding', 'programming', 
                      'developer', 'code', 'agent', 'openai', 'anthropic', 'mistral', 'deepseek']
        
        items = soup.select('.athing')
        for item in items[:20]:
            try:
                title_elem = item.select_one('.titleline a')
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                url = title_elem.get('href', '')
                
                # 处理相对链接
                if url.startswith('item?'):
                    url = f"https://news.ycombinator.com/{url}"
                
                # 筛选 AI 相关内容
                if any(kw in title.lower() for kw in ai_keywords):
                    news.append({
                        'title': title,
                        'url': url,
                        'description': 'Hacker News 热门讨论',
                        'source': 'Hacker News',
                        'category': '社区讨论'
                    })
                    print(f"  ✓ {title[:60]}...")
            except:
                continue
        
        return news[:6]
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return []

def fetch_github_trending():
    """抓取 GitHub Trending Python AI 项目"""
    print("🕷️ 抓取 GitHub Trending...")
    try:
        # 直接搜索 GitHub API
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        # 获取最近更新的 AI 相关仓库
        ai_keywords = ['ai', 'llm', 'gpt', 'code-assistant', 'cursor', 'copilot', 'claude']
        news = []
        
        for keyword in ai_keywords[:3]:
            try:
                url = f'https://api.github.com/search/repositories?q={keyword}+created:>2025-01-01+stars:>100&sort=updated&order=desc&per_page=5'
                resp = requests.get(url, headers=headers, timeout=15)
                data = resp.json()
                
                for repo in data.get('items', [])[:3]:
                    news.append({
                        'title': f"📦 {repo['full_name']}",
                        'url': repo['html_url'],
                        'description': repo.get('description', '无描述')[:120],
                        'source': 'GitHub',
                        'category': '开源项目',
                        'stars': repo.get('stargazers_count', 0)
                    })
            except:
                continue
        
        # 去重
        seen = set()
        unique = []
        for item in news:
            if item['title'] not in seen:
                seen.add(item['title'])
                unique.append(item)
                print(f"  ✓ {item['title']}")
        
        return unique[:5]
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return []

def fetch_reddit_local_llama():
    """抓取 Reddit r/LocalLLaMA"""
    print("🕷️ 抓取 Reddit r/LocalLLaMA...")
    try:
        # Reddit RSS feed
        resp = requests.get('https://www.reddit.com/r/LocalLLaMA/hot.json?limit=10', 
                          headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        data = resp.json()
        
        news = []
        for post in data.get('data', {}).get('children', []):
            try:
                post_data = post['data']
                title = post_data['title']
                url = post_data['url']
                score = post_data.get('score', 0)
                
                # 筛选高赞且非自我帖子的
                if score > 20 and not post_data.get('is_self', True):
                    news.append({
                        'title': f"🦙 {title[:80]}",
                        'url': url if not url.startswith('/r/') else f"https://reddit.com{url}",
                        'description': f"r/LocalLLaMA 讨论 ({score} upvotes)",
                        'source': 'Reddit',
                        'category': '社区动态'
                    })
                    print(f"  ✓ {title[:60]}...")
            except:
                continue
        
        return news[:4]
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return []

def fetch_techcrunch_ai():
    """抓取 TechCrunch AI 新闻"""
    print("🕷️ 抓取 TechCrunch AI...")
    try:
        resp = requests.get('https://techcrunch.com/category/artificial-intelligence/', 
                          headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        news = []
        articles = soup.select('article a')[:10]
        
        seen = set()
        for article in articles:
            try:
                title = article.text.strip()
                url = article.get('href', '')
                
                if not title or len(title) < 20 or title in seen:
                    continue
                seen.add(title)
                
                # 确保是完整 URL
                if url.startswith('/'):
                    url = f"https://techcrunch.com{url}"
                
                # 筛选编程工具相关
                if any(kw in title.lower() for kw in ['code', 'programming', 'developer', 'api', 'tool', 'ai']):
                    news.append({
                        'title': f"📰 {title}",
                        'url': url,
                        'description': 'TechCrunch AI 报道',
                        'source': 'TechCrunch',
                        'category': '行业新闻'
                    })
                    print(f"  ✓ {title[:60]}...")
            except:
                continue
        
        return news[:4]
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return []

def generate_html(news, date_str):
    """生成 HTML 日报"""
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI 编程工具日报 - {date_str}</title>
  <style>
    :root {{
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #c9d1d9;
      --text-muted: #8b949e;
      --accent: #58a6ff;
      --accent-hover: #79c0ff;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 2rem;
    }}
    .container {{ max-width: 800px; margin: 0 auto; }}
    header {{
      text-align: center;
      margin-bottom: 3rem;
      padding-bottom: 2rem;
      border-bottom: 1px solid var(--border);
    }}
    h1 {{
      font-size: 2rem;
      background: linear-gradient(135deg, #58a6ff 0%, #a371f7 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.5rem;
    }}
    .subtitle {{ color: var(--text-muted); font-size: 0.9rem; margin-top: 0.5rem; }}
    .date {{ color: var(--text-muted); font-size: 0.9rem; }}
    .news-list {{ display: flex; flex-direction: column; gap: 1rem; }}
    .news-item {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.25rem;
      transition: border-color 0.2s, transform 0.2s;
    }}
    .news-item:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
    }}
    .news-item h3 {{
      font-size: 1.1rem;
      margin-bottom: 0.5rem;
    }}
    .news-item h3 a {{
      color: var(--accent);
      text-decoration: none;
    }}
    .news-item h3 a:hover {{ color: var(--accent-hover); }}
    .news-item p {{
      color: var(--text-muted);
      font-size: 0.9rem;
      margin-bottom: 0.75rem;
    }}
    .news-meta {{
      display: flex;
      gap: 1rem;
      font-size: 0.8rem;
      color: var(--text-muted);
      flex-wrap: wrap;
    }}
    .tag {{
      background: rgba(163, 113, 247, 0.1);
      color: #a371f7;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
    }}
    .source-badge {{
      background: rgba(88, 166, 255, 0.1);
      color: var(--accent);
      padding: 0.2rem 0.5rem;
      border-radius: 12px;
      font-size: 0.75rem;
    }}
    .empty {{
      text-align: center;
      padding: 3rem;
      color: var(--text-muted);
    }}
    footer {{
      margin-top: 3rem;
      padding-top: 2rem;
      border-top: 1px solid var(--border);
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
    }}
    .stats {{
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
      margin-bottom: 2rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🤖 AI 编程工具日报</h1>
      <p class="date">{date_str}</p>
      <p class="subtitle">使用 Python requests + BeautifulSoup 抓取</p>
    </header>
    
    <p class="stats">今日抓取 {len(news)} 条资讯</p>
    
    <main>
      {''.join([f'''
      <article class="news-item">
        <h3><a href="{item['url']}" target="_blank" rel="noopener">{item['title']}</a></h3>
        <p>{item.get('description', '')}</p>
        <div class="news-meta">
          <span class="source-badge">{item['source']}</span>
          <span class="tag">{item.get('category', 'AI工具')}</span>
        </div>
      </article>
      ''' for item in news]) if news else '<div class="empty"><p>今日暂无新资讯</p></div>'}
    </main>
    
    <footer>
      <p>由 OpenClaw Bot 自动抓取生成</p>
    </footer>
  </div>
</body>
</html>'''
    return html

def main():
    print("=" * 50)
    print("🤖 AI Daily - 轻量版")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    ensure_dir()
    
    all_news = []
    
    # 抓取各个源
    all_news.extend(fetch_hackernews())
    all_news.extend(fetch_github_trending())
    all_news.extend(fetch_reddit_local_llama())
    all_news.extend(fetch_techcrunch_ai())
    
    # 去重
    seen = set()
    unique_news = []
    for item in all_news:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_news.append(item)
    
    print(f"\n📊 共抓取 {len(unique_news)} 条资讯")
    
    # 生成文件
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # HTML
    html = generate_html(unique_news, date_str)
    with open(f"{OUTPUT_DIR}/index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 生成: docs/index.html")
    
    # JSON
    with open(f"{OUTPUT_DIR}/{date_str}.json", 'w', encoding='utf-8') as f:
        json.dump({'date': date_str, 'news': unique_news}, f, ensure_ascii=False, indent=2)
    print(f"✅ 保存: docs/{date_str}.json")
    
    print("\n🎉 完成!")
    
    # 显示预览
    print("\n📋 今日资讯预览:")
    for i, item in enumerate(unique_news[:5], 1):
        print(f"  {i}. [{item['source']}] {item['title'][:50]}...")

if __name__ == '__main__':
    main()
