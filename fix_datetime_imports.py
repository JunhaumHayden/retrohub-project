import os
import re

for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            
            if 'datetime.now(timezone.utc)' in content and 'from datetime import timezone' not in content:
                # Add timezone import if missing
                if 'from datetime import datetime' in content:
                    content = content.replace('from datetime import datetime', 'from datetime import datetime, timezone')
                else:
                    content = 'from datetime import timezone\n' + content
                
            with open(filepath, 'w') as f:
                f.write(content)
