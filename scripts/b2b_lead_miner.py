import sys
import re
import csv
import time
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

def get_urls(query, max_results=30):
    print(f"🔍 正在搜索关键词 (目标找客户官网): {query}")
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
        return [r['href'] for r in results]
    except Exception as e:
        print(f"搜索出错: {e}")
        return []

def extract_emails(text):
    # 正则匹配邮箱
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return set(re.findall(email_pattern, text))

def scrape_site(url):
    print(f"🌐 正在扫描挖掘: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 请求主页
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 从主页提取邮箱
        emails = extract_emails(soup.get_text())
        
        # 如果主页没有，尝试寻找 Contact 页面
        if not emails:
            contact_links = []
            for a in soup.find_all('a', href=True):
                if 'contact' in a['href'].lower() or 'about' in a['href'].lower():
                    link = a['href']
                    if link.startswith('/'):
                        link = url.rstrip('/') + link
                    elif not link.startswith('http'):
                        continue
                    contact_links.append(link)
                    
            if contact_links:
                # 只扫第一个 contact 页面，避免耗时太长
                c_resp = requests.get(contact_links[0], headers=headers, timeout=10)
                c_soup = BeautifulSoup(c_resp.text, 'html.parser')
                emails.update(extract_emails(c_soup.get_text()))
                
        return list(emails)
    except Exception as e:
        # 忽略访问失败的网站
        return []

def main():
    if len(sys.argv) < 2:
        print("用法: python3 b2b_lead_miner.py '<搜索关键词>'")
        print("示例: python3 b2b_lead_miner.py 'car floor mats manufacturer UK contact'")
        sys.exit(1)
        
    query = sys.argv[1]
    urls = get_urls(query, 30)
    
    if not urls:
        print("未找到结果，请检查网络或更换关键词。")
        return
        
    all_leads = []
    print(f"\n🚀 搜索到 {len(urls)} 个潜在客户网站，开始提取联系方式...\n")
    
    for url in urls:
        # 过滤掉明显的 B2B 平台（我们要找的是厂家官网）
        if any(x in url for x in ['alibaba.com', 'made-in-china.com', 'amazon.com', 'ebay.com']):
            continue
            
        emails = scrape_site(url)
        if emails:
            # 过滤掉常见的无用图片后缀误判 (例如 image@2x.png)
            valid_emails = [e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))]
            # 过滤掉 sentry, wix 等非客户邮箱
            valid_emails = [e for e in valid_emails if 'sentry' not in e and 'wix' not in e]
            
            if valid_emails:
                print(f"✅ 成功挖到邮箱: {valid_emails}")
                all_leads.append({'Website': url, 'Emails': ' | '.join(valid_emails)})
                
        time.sleep(1) # 礼貌防封
        
    if all_leads:
        filename = f"B2B客户线索_{query.replace(' ', '_')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['Website', 'Emails'])
            writer.writeheader()
            writer.writerows(all_leads)
        print(f"\n🎉 挖掘完毕！成功提取 {len(all_leads)} 家客户的联系方式。")
        print(f"📁 结果已自动存入 Excel 表格: {filename}")
    else:
        print("\n⚠️ 未能从这批网站中提取到有效邮箱，建议换个关键词（比如加上 'contact email' 等字眼）。")

if __name__ == "__main__":
    main()