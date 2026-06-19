import os
import re

for root, dirs, files in os.walk('tests'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Replace Jogo with Catalogo in imports
            content = re.sub(r'\bJogo\b', 'Catalogo', content)
            # Replace id_jogo with id_catalogo
            content = re.sub(r'\bid_jogo\b', 'id_catalogo', content)
            
            with open(filepath, 'w') as f:
                f.write(content)
                
