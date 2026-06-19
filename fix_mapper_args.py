import os
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Remove status column definition if it exists to fix duplication
    content = re.sub(r'^\s*status:\s*Mapped\[.*?\].*?\n', '', content, flags=re.MULTILINE)

    with open(filepath, 'w') as f:
        f.write(content)

process_file('app/models/transacao/venda/venda.py')
process_file('app/models/transacao/aluguel/aluguel.py')
