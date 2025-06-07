import argparse
import subprocess
import git
import os
import shutil
from pathlib import Path
import mimetypes
import json

# Configuration for file filtering and analysis
IGNORE_PATTERNS = {
    'directories': {'.git', '__pycache__', 'node_modules', '.vscode', '.idea', 'dist', 'build', '.next', 'coverage', 'target', 'bin', 'obj'},
    'files': {'.gitignore', '.env', '.env.local', '.DS_Store', 'Thumbs.db', '.eslintrc', '.prettierrc'},
    'extensions': {'.pyc', '.pyo', '.pyd', '.so', '.dylib', '.dll', '.exe', '.o', '.a', '.lib', '.class', '.jar'}
}

IMPORTANT_FILES = {
    'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml',
    'build.gradle', 'Dockerfile', 'docker-compose.yml', 'Makefile',
    'setup.py', 'pyproject.toml', 'composer.json', 'Gemfile', 'README.md',
    'main.py', 'app.py', 'index.js', 'main.js', 'server.js', 'app.js'
}

def should_ignore_file(file_path):
    """Check if a file should be ignored based on patterns."""
    path = Path(file_path)

    # Check directory patterns
    for part in path.parts:
        if part in IGNORE_PATTERNS['directories']:
            return True

    # Check file patterns
    if path.name in IGNORE_PATTERNS['files']:
        return True

    # Check extensions
    if path.suffix in IGNORE_PATTERNS['extensions']:
        return True

    return False

def is_text_file(file_path):
    """Check if a file is a text file."""
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('text'):
            return True

        # Common text file extensions
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sass',
            '.json', '.xml', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf',
            '.md', '.txt', '.rst', '.sh', '.bat', '.ps1', '.sql', '.graphql',
            '.vue', '.svelte', '.php', '.rb', '.go', '.rs', '.cpp', '.c', '.h',
            '.hpp', '.java', '.kt', '.swift', '.dart', '.r', '.m', '.pl', '.lua',
            '.env.example', '.gitignore'
        }

        return Path(file_path).suffix.lower() in text_extensions
    except:
        return False

def clone_repo(repo_url, dest_dir="cloned_repo"):
    """Clone the Git repository."""
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    print(f"🔄 Cloning {repo_url} into {dest_dir}...")

    try:
        git.Repo.clone_from(repo_url, dest_dir)
        print("✅ Repository cloned successfully!")
        return True
    except Exception as e:
        print(f"❌ Error cloning repository: {e}")
        return False

def analyze_dependencies(dest_dir="cloned_repo"):
    """Analyze project dependencies from various config files."""
    dependencies = {
        'python': [],
        'javascript': [],
        'docker': False,
        'databases': [],
        'frameworks': []
    }

    # Check package.json
    package_json = os.path.join(dest_dir, 'package.json')
    if os.path.exists(package_json):
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                dependencies['javascript'] = list(deps.keys())

                # Detect frameworks
                if 'react' in deps:
                    dependencies['frameworks'].append('React')
                if 'vue' in deps:
                    dependencies['frameworks'].append('Vue.js')
                if 'angular' in deps or '@angular/core' in deps:
                    dependencies['frameworks'].append('Angular')
                if 'express' in deps:
                    dependencies['frameworks'].append('Express.js')
                if 'next' in deps:
                    dependencies['frameworks'].append('Next.js')
        except:
            pass

    # Check requirements.txt
    req_file = os.path.join(dest_dir, 'requirements.txt')
    if os.path.exists(req_file):
        try:
            with open(req_file, 'r') as f:
                deps = [line.strip().split('==')[0].split('>=')[0].split('<=')[0]
                       for line in f if line.strip() and not line.startswith('#')]
                dependencies['python'] = deps

                # Detect Python frameworks
                if any(fw in deps for fw in ['django', 'Django']):
                    dependencies['frameworks'].append('Django')
                if any(fw in deps for fw in ['flask', 'Flask']):
                    dependencies['frameworks'].append('Flask')
                if any(fw in deps for fw in ['fastapi', 'FastAPI']):
                    dependencies['frameworks'].append('FastAPI')
        except:
            pass

    # Check for Docker
    if os.path.exists(os.path.join(dest_dir, 'Dockerfile')):
        dependencies['docker'] = True

    # Check for databases
    all_deps = dependencies['python'] + dependencies['javascript']
    db_keywords = ['mysql', 'postgres', 'mongodb', 'redis', 'sqlite', 'oracle']
    dependencies['databases'] = [db for db in db_keywords if any(db in dep.lower() for dep in all_deps)]

    return dependencies

def analyze_project_structure(dest_dir="cloned_repo"):
    """Analyze project structure and categorize files."""
    structure = {
        'important_files': [],
        'source_files': [],
        'config_files': [],
        'documentation': [],
        'tests': [],
        'assets': [],
        'total_files': 0,
        'languages': set(),
        'frameworks': set(),
        'tools': set(),
        'main_directories': set()
    }

    for root, dirs, files in os.walk(dest_dir):
        # Remove ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS['directories']]

        # Track main directories
        rel_root = os.path.relpath(root, dest_dir)
        if rel_root != '.' and '/' not in rel_root:
            structure['main_directories'].add(rel_root)

        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, dest_dir)

            if should_ignore_file(relative_path):
                continue

            structure['total_files'] += 1
            path_obj = Path(relative_path)

            # Categorize files
            if path_obj.name.lower() in [f.lower() for f in IMPORTANT_FILES]:
                structure['important_files'].append(relative_path)
            elif any(test_indicator in relative_path.lower() for test_indicator in ['test', 'spec', '__test__']):
                structure['tests'].append(relative_path)
            elif path_obj.suffix.lower() in {'.md', '.rst', '.txt'} and 'readme' not in path_obj.name.lower():
                structure['documentation'].append(relative_path)
            elif path_obj.suffix.lower() in {'.json', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.env'}:
                structure['config_files'].append(relative_path)
            elif is_text_file(relative_path):
                structure['source_files'].append(relative_path)
            else:
                structure['assets'].append(relative_path)

            # Detect languages and frameworks
            detect_tech_stack(relative_path, structure)

    return structure

def detect_tech_stack(file_path, structure):
    """Detect programming languages and frameworks from file extensions and names."""
    path_obj = Path(file_path)
    ext = path_obj.suffix.lower()
    name = path_obj.name.lower()

    # Language detection
    language_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.jsx': 'React/JSX',
        '.tsx': 'React/TSX', '.vue': 'Vue.js', '.svelte': 'Svelte', '.php': 'PHP',
        '.rb': 'Ruby', '.go': 'Go', '.rs': 'Rust', '.cpp': 'C++', '.c': 'C',
        '.java': 'Java', '.kt': 'Kotlin', '.swift': 'Swift', '.dart': 'Dart',
        '.r': 'R', '.m': 'Objective-C', '.pl': 'Perl', '.lua': 'Lua',
        '.sh': 'Shell Script', '.ps1': 'PowerShell', '.sql': 'SQL',
        '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS'
    }

    if ext in language_map:
        structure['languages'].add(language_map[ext])

    # Framework/Tool detection
    if name == 'package.json':
        structure['tools'].add('Node.js/npm')
    elif name == 'requirements.txt':
        structure['tools'].add('pip')
    elif name == 'cargo.toml':
        structure['tools'].add('Cargo')
    elif name == 'go.mod':
        structure['tools'].add('Go Modules')
    elif name == 'dockerfile':
        structure['tools'].add('Docker')
    elif name == 'docker-compose.yml':
        structure['tools'].add('Docker Compose')
    elif name == 'makefile':
        structure['tools'].add('Make')

def get_prioritized_files(structure, dest_dir="cloned_repo", max_content_size=30000):
    """Get content from most important files first, respecting size limits."""
    prioritized_files = []

    # Priority order: important files > key source files > config files
    priority_order = [
        structure['important_files'],
        [f for f in structure['source_files'] if any(key in f.lower() for key in ['main', 'app', 'index', 'server'])][:10],
        structure['config_files'][:5],
        structure['source_files'][:15]  # Other source files
    ]

    total_size = 0
    processed_files = set()

    for file_group in priority_order:
        for file_path in file_group:
            if file_path in processed_files or total_size > max_content_size:
                continue

            content = get_file_content(file_path, dest_dir)
            if content and not content.startswith("Error reading"):
                file_size = len(content)
                if total_size + file_size <= max_content_size:
                    prioritized_files.append((file_path, content))
                    total_size += file_size
                    processed_files.add(file_path)

    return prioritized_files

def get_file_content(file_path, dest_dir="cloned_repo"):
    """Read content of a file with better error handling."""
    full_path = os.path.join(dest_dir, file_path)
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(full_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    # Limit file size to prevent overwhelming the model
                    if len(content) > 3000:
                        # For large files, take beginning and end
                        content = content[:2000] + "\n\n... [CONTENT TRUNCATED] ...\n\n" + content[-1000:]
                    return content
            except UnicodeDecodeError:
                continue
        return f"Error: Could not decode {file_path} with any encoding"
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def create_enhanced_prompt(structure, prioritized_files, repo_url, dependencies):
    """Create a comprehensive prompt for better README generation."""

    # Extract project name from repo URL
    project_name = repo_url.split('/')[-1].replace('.git', '')

    # Build tech stack summary
    tech_summary = {
        'languages': list(structure['languages']),
        'frameworks': list(structure['frameworks']) + dependencies['frameworks'],
        'tools': list(structure['tools']),
        'has_docker': dependencies['docker'],
        'databases': dependencies['databases']
    }

    # Create project analysis
    project_analysis = f"""
PROJECT ANALYSIS:
=================
Repository: {repo_url}
Project Name: {project_name}

TECHNOLOGY STACK:
- Languages: {', '.join(tech_summary['languages']) if tech_summary['languages'] else 'Not clearly detected'}
- Frameworks: {', '.join(tech_summary['frameworks']) if tech_summary['frameworks'] else 'None detected'}
- Tools: {', '.join(tech_summary['tools']) if tech_summary['tools'] else 'None detected'}
- Containerization: {'Docker' if tech_summary['has_docker'] else 'None detected'}
- Databases: {', '.join(tech_summary['databases']) if tech_summary['databases'] else 'None detected'}

PROJECT STRUCTURE:
- Total Files: {structure['total_files']}
- Main Directories: {', '.join(structure['main_directories']) if structure['main_directories'] else 'Standard structure'}
- Important Config Files: {', '.join(structure['important_files']) if structure['important_files'] else 'None found'}
- Source Files: {len(structure['source_files'])}
- Test Files: {len(structure['tests'])}

DEPENDENCIES DETECTED:
- Python packages: {', '.join(dependencies['python'][:10]) if dependencies['python'] else 'None'}
- JavaScript packages: {', '.join(dependencies['javascript'][:10]) if dependencies['javascript'] else 'None'}
"""

    # Build file contents section with better formatting
    file_contents = "\nKEY FILE CONTENTS FOR ANALYSIS:\n" + "="*50 + "\n"
    for file_path, content in prioritized_files:
        file_contents += f"\n📄 {file_path}\n{'-' * 50}\n{content}\n\n"

    prompt = f"""You are an expert technical writer creating a professional README.md file. Analyze the project thoroughly and create a comprehensive, well-structured README.

{project_analysis}

{file_contents}

INSTRUCTIONS FOR README GENERATION:
===================================

Create a professional README.md with these sections (use appropriate markdown formatting):

1. **# {project_name}**
   - Add relevant badges if you can infer them
   - Write a compelling one-line description based on the code

2. **## 📋 Description**
   - Provide a detailed description based on your analysis
   - Explain what the project does and its main purpose
   - Mention key features you identified from the code

3. **## ✨ Features**
   - List specific features you can identify from the codebase
   - Use bullet points with emojis

4. **## 🚀 Tech Stack**
   - List all detected technologies in a nice format
   - Group by categories (Languages, Frameworks, Tools, etc.)

5. **## 📋 Prerequisites**
   - List required software based on your analysis
   - Include version requirements if found in config files

6. **## 🛠️ Installation**
   - Provide step-by-step installation instructions
   - Make it specific to the detected tech stack
   - Include environment setup if needed

7. **## 🏃‍♂️ Usage**
   - Show how to run the project
   - Include common commands
   - Add code examples if you can infer them

8. **## 📁 Project Structure**
   - Explain the main directories and their purposes
   - Use a tree structure if helpful

9. **## 🧪 Testing**
   - Include testing instructions if test files were found
   - Mention testing frameworks if detected

10. **## 🤝 Contributing**
    - Add standard contributing guidelines

11. **## 📄 License**
    - State license if found, otherwise "License not specified"

12. **## 👨‍💻 Author**
    - End with "Made with ❤️ by KIMI"

IMPORTANT GUIDELINES:
- Use emojis to make it visually appealing
- Write in professional, clear language
- Include actual commands and examples where possible
- Make installation steps specific and actionable
- Don't make assumptions about functionality you can't verify from the code
- Focus on what you can actually determine from the analysis

Generate ONLY the markdown content for the README file. Make it comprehensive and professional."""

    return prompt

def generate_readme(structure, prioritized_files, repo_url, dependencies, model="llama3.2:latest"):
    """Generate README using Ollama with enhanced prompt."""
    print("🤖 Generating README with AI...")

    prompt = create_enhanced_prompt(structure, prioritized_files, repo_url, dependencies)

    # Save prompt for debugging
    with open("debug_prompt.txt", "w", encoding='utf-8') as f:
        f.write(prompt)

    try:
        # Use better parameters for Ollama
        ollama_cmd = [
            "ollama", "run", model,
            # "--num-ctx", "8192",  # Increase context window
            # "--temperature", "0.3",  # Lower temperature for more focused output
            # "--top-p", "0.9"
        ]

        result = subprocess.run(
            ollama_cmd,
            input=prompt.encode('utf-8'),
            capture_output=True,
            timeout=180  # 3 minute timeout
        )

        if result.returncode != 0:
            print(f"❌ Ollama error: {result.stderr.decode()}")
            # Try without parameters as fallback
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt.encode('utf-8'),
                capture_output=True,
                timeout=180
            )

        if result.returncode != 0:
            print(f"❌ Ollama error: {result.stderr.decode()}")
            return False

        output = result.stdout.decode('utf-8').strip()

        # Clean up the output
        if output.startswith('```markdown'):
            output = output[11:]
        if output.startswith('```'):
            output = output[3:]
        if output.endswith('```'):
            output = output[:-3]

        # Remove any system messages or artifacts
        lines = output.split('\n')
        clean_lines = []
        in_readme = False

        for line in lines:
            if line.strip().startswith('#') and not in_readme:
                in_readme = True
            if in_readme:
                clean_lines.append(line)

        if clean_lines:
            output = '\n'.join(clean_lines)

        with open("README.md", "w", encoding='utf-8') as f:
            f.write(output.strip())

        print("✅ README.md generated successfully!")
        print(f"📄 File saved as README.md ({len(output)} characters)")
        return True

    except subprocess.TimeoutExpired:
        print("❌ Ollama request timed out. Try using a smaller model like 'llama3.2:1b'.")
        return False
    except Exception as e:
        print(f"❌ Error generating README: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Clone a Git repo, analyze it intelligently, and generate a professional README with Ollama.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python script.py --repo https://github.com/user/project
  python script.py --repo https://github.com/user/project --model llama3.2:latest
  python script.py --repo https://github.com/user/project --output my-readme.md

Recommended models: llama3.2:latest, qwen2.5:latest, mistral:latest
        """
    )

    parser.add_argument('--repo', required=True, help='Git repository URL')
    parser.add_argument('--model', default='dolphin3:latest',
                       help='Ollama model to use (default: llama3.2:latest)')
    parser.add_argument('--output', default='MY-README.md',
                       help='Output filename (default: README.md)')
    parser.add_argument('--debug', action='store_true',
                       help='Save debug information and prompt')

    args = parser.parse_args()

    print("🚀 Starting Enhanced README Generator")
    print(f"📂 Repository: {args.repo}")
    print(f"🤖 Model: {args.model}")

    # Step 1: Clone repository
    if not clone_repo(args.repo):
        return 1

    # Step 2: Analyze project structure
    print("🔍 Analyzing project structure...")
    structure = analyze_project_structure()

    # Step 3: Analyze dependencies
    print("📦 Analyzing dependencies...")
    dependencies = analyze_dependencies()

    print(f"📊 Analysis complete:")
    print(f"   - Languages detected: {', '.join(structure['languages']) if structure['languages'] else 'None'}")
    print(f"   - Frameworks detected: {', '.join(dependencies['frameworks']) if dependencies['frameworks'] else 'None'}")
    print(f"   - Tools detected: {', '.join(structure['tools']) if structure['tools'] else 'None'}")
    print(f"   - Total files: {structure['total_files']}")

    # Step 4: Get prioritized file content
    print("📋 Extracting relevant file contents...")
    prioritized_files = get_prioritized_files(structure)
    print(f"   - Selected {len(prioritized_files)} files for analysis")

    # Step 5: Generate README
    if generate_readme(structure, prioritized_files, args.repo, dependencies, args.model):
        print(f"🎉 Success! Check out your new {args.output}")

        if args.debug:
            print("🐛 Debug files saved: debug_prompt.txt")
    else:
        print("❌ Failed to generate README")
        print("\n💡 Troubleshooting tips:")
        print("1. Try a different model: --model llama3.2:1b (smaller, faster)")
        print("2. Make sure Ollama is running: ollama serve")
        print("3. Pull the model first: ollama pull llama3.2:latest")
        return 1

    # Cleanup
    if not args.debug:
        try:
            shutil.rmtree("cloned_repo")
            if os.path.exists("debug_prompt.txt"):
                os.remove("debug_prompt.txt")
        except:
            pass

    return 0

if __name__ == "__main__":
    exit(main())
