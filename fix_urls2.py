import os, glob

for filepath in glob.glob('frontend/src/components/*.jsx'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(r'\${', '${')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
