import os

for root, dirs, files in os.walk('app/models'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            if 'mapper_args' in content or 'status' in content:
                print(f"--- {filepath} ---")
                for line in content.split('\n'):
                    if 'status' in line or '__mapper_args__' in line:
                        print(line)
