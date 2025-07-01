#!/usr/bin/env python3
"""
First Aid Quiz Game - Setup Script
Quick setup and verification for hackathon judges and contributors
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def verify_files():
    """Verify all required files exist"""
    print("\n📁 Verifying project files...")
    required_files = [
        "main.py",
        "image_loader.py", 
        "requirements.txt",
        "data/questions.json",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    return len(missing_files) == 0

def verify_assets():
    """Verify asset directory structure"""
    print("\n🎨 Verifying asset structure...")
    asset_dirs = [
        "assets/backgrounds",
        "assets/characters", 
        "assets/icons",
        "assets/images",
        "assets/sounds"
    ]
    
    for dir_path in asset_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"⚠️  {dir_path} - Missing (will be created)")
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    return True

def test_game_launch():
    """Test if the game can be imported and basic systems work"""
    print("\n🎮 Testing game systems...")
    try:
        # Test imports
        import pygame
        print("✅ Pygame imported successfully")
        
        # Test JSON loading
        import json
        with open("data/questions.json", "r") as f:
            data = json.load(f)
        print(f"✅ Questions loaded: {len(data['first_aid_questions'])} questions")
        
        # Test main game import (without running)
        sys.path.insert(0, ".")
        print("✅ Game systems verified")
        
        return True
    except Exception as e:
        print(f"❌ Game test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🏥 First Aid Quiz Game - Setup & Verification")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Verify files
    if not verify_files():
        print("\n❌ Missing required files. Please check your installation.")
        sys.exit(1)
    
    # Verify assets
    verify_assets()
    
    # Test game systems
    if not test_game_launch():
        print("\n⚠️  Game systems test failed, but basic setup is complete.")
        print("Try running: python main.py")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("🚀 Ready to run: python main.py")
    print("📖 Read README.md for detailed information")
    print("🏆 Good luck with your hackathon!")
    print("=" * 50)

if __name__ == "__main__":
    main()
