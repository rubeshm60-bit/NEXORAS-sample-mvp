import os, glob

api_str = "const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';"

for filepath in glob.glob('frontend/src/components/*.jsx'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'API_URL' not in content:
        content = content.replace("'http://localhost:8000/", "`\\${API_URL}/")
        content = content.replace("'http://localhost:8000", "API_URL")
        # Fix the template literal backticks which got messed up if replacing in the middle of a string
        content = content.replace("`\\${API_URL}/dashboard/summary'", "`\\${API_URL}/dashboard/summary`")
        content = content.replace("`\\${API_URL}/anomalies?limit=50'", "`\\${API_URL}/anomalies?limit=50`")
        content = content.replace("`\\${API_URL}/projects?limit=50'", "`\\${API_URL}/projects?limit=50`")
        content = content.replace("`\\${API_URL}/projects/${id}`", "`\\${API_URL}/projects/${id}`")
        content = content.replace("`\\${API_URL}/vendors?limit=50'", "`\\${API_URL}/vendors?limit=50`")
        content = content.replace("`\\${API_URL}/network'", "`\\${API_URL}/network`")
        
        lines = content.split('\n')
        last_import = max([i for i, line in enumerate(lines) if line.startswith('import ')])
        lines.insert(last_import + 1, '\n' + api_str.replace('\\', '') + '\n')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
