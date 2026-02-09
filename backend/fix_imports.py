#!/usr/bin/env python3
"""Fix imports by removing 'backend.' prefix"""
import os
import re

def fix_imports_in_file(filepath):
    """Replace 'from ' with relative imports"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    # Replace 'from ' with 'from '
    content = re.sub(r'from backend\.', 'from ', content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    """Walk through all Python files and fix imports"""
    fixed_count = 0
    for root, dirs, files in os.walk('.'):
        # Skip venv directories
        if 'venv' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
