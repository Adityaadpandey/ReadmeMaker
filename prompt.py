from typing import List, Tuple

from analyzer import EnhancedProjectAnalyzer

def create_comprehensive_prompt(analyzer: EnhancedProjectAnalyzer, key_files: List[Tuple[str, str]], repo_url: str) -> str:
    """Create a comprehensive prompt for README generation."""

    project_name = analyzer.project_data.get('name') or repo_url.split('/')[-1].replace('.git', '')

    # Build file content section with better organization
    file_contents = ""
    config_files = []
    source_files = []

    for filename, content in key_files:
        if any(filename.endswith(ext) for ext in ['.json', '.txt', '.toml', '.yml', '.yaml', 'Dockerfile']):
            config_files.append((filename, content))
        else:
            source_files.append((filename, content))

    if config_files:
        file_contents += "\n=== CONFIGURATION FILES ===\n"
        for filename, content in config_files:
            file_contents += f"\n--- {filename} ---\n{content}\n"

    if source_files:
        file_contents += "\n=== SOURCE FILES ===\n"
        for filename, content in source_files[:3]:  # Limit source files in prompt
            file_contents += f"\n--- {filename} ---\n{content[:1500]}\n"

    # Build technology stack info
    tech_info = f"""
TECHNOLOGY STACK:
- Main Language: {analyzer.project_data['main_language']}
- Languages: {', '.join(analyzer.project_data['languages'].keys()) if analyzer.project_data['languages'] else 'Not detected'}
- Frameworks: {', '.join(analyzer.project_data['frameworks']) if analyzer.project_data['frameworks'] else 'None detected'}
- Technologies: {', '.join(analyzer.project_data['technologies'][:10]) if analyzer.project_data['technologies'] else 'None detected'}
- Architecture: {analyzer.project_data['architecture_type']}
- Setup Difficulty: {analyzer.project_data['setup_difficulty']} (Complexity Score: {analyzer.project_data['complexity_score']})
"""

    # Build Docker info
    docker_info = ""
    if analyzer.project_data['has_docker']:
        services_info = ', '.join(analyzer.project_data['docker_services']) if analyzer.project_data['docker_services'] else 'Standard container'
        ports_info = ', '.join(analyzer.project_data['ports']) if analyzer.project_data['ports'] else 'Not specified'
        docker_info = f"""
DOCKER CONFIGURATION:
- Services: {services_info}
- Exposed Ports: {ports_info}
- Databases: {', '.join(analyzer.project_data['databases']) if analyzer.project_data['databases'] else 'None'}
"""

    # Build features info
    features_info = ""
    if analyzer.project_data['features']:
        features_info = f"""
DETECTED FEATURES:
{', '.join(analyzer.project_data['features'])}
"""

    # Build API info
    api_info = ""
    if analyzer.project_data['api_endpoints']:
        api_info = f"""
API ENDPOINTS DETECTED:
{', '.join(analyzer.project_data['api_endpoints'][:10])}
"""

    # Build environment variables info
    env_info = ""
    if analyzer.project_data['env_example_vars']:
        env_info = f"""
ENVIRONMENT VARIABLES:
{', '.join(analyzer.project_data['env_example_vars'][:10])}
"""

    prompt = f"""You are tasked with creating a comprehensive, professional README.md for a software project. Analyze the provided information and create documentation that would be helpful for both developers and users.

PROJECT INFORMATION:
- Name: {project_name}
- Repository: {repo_url}
- Description: {analyzer.project_data.get('description', '[Analyze the code to write a description]')}
- Version: {analyzer.project_data.get('version', 'Not specified')}
- Author: {analyzer.project_data.get('author', 'Not specified')}
- License: {analyzer.project_data.get('license', 'Not specified')}

{tech_info}
{docker_info}
{features_info}
{api_info}
{env_info}

PROJECT FILES ANALYSIS:
{file_contents}

COMMANDS DETECTED:
- Install: {analyzer.project_data.get('install_cmd', '[Determine from files above]')}
- Run: {analyzer.project_data.get('run_cmd', '[Determine from files above]')}
- Development: {analyzer.project_data.get('dev_cmd', '[Determine from files above if different from run]')}
- Test: {analyzer.project_data.get('test_cmd', '[Determine from files above]')}
- Build: {analyzer.project_data.get('build_cmd', '[Determine from files above]')}

Create a comprehensive README.md with the following structure:

# {project_name}

[Write a compelling project description based on the analysis above. Include what the project does, its main purpose, and key features.]

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation) [Include only if APIs detected]
- [Docker Deployment](#docker-deployment) [Include only if Docker detected]
- [Development](#development)
- [Testing](#testing) [Include only if tests detected]
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

[List the key features based on the detected features and code analysis]

## 🛠 Tech Stack

**Languages:** {', '.join(analyzer.project_data['languages'].keys()) if analyzer.project_data['languages'] else '[List from analysis]'}

**Frameworks & Libraries:**
{chr(10).join(f'- {framework}' for framework in analyzer.project_data['frameworks']) if analyzer.project_data['frameworks'] else '[List from analysis]'}

**Technologies:**
{chr(10).join(f'- {tech}' for tech in analyzer.project_data['technologies'][:10]) if analyzer.project_data['technologies'] else '[List from analysis]'}

{f'''**Databases:**
{chr(10).join(f'- {db}' for db in analyzer.project_data['databases'])}''' if analyzer.project_data['databases'] else ''}

## 🚀 Getting Started

### Prerequisites

[List the prerequisites based on the technology stack and analysis above]

### Installation

1. **Clone the repository**
   ```bash
   git clone {repo_url}
   cd {project_name}
   ```

2. **Install dependencies**
   ```bash
   {analyzer.project_data.get('install_cmd', '[Add install command based on analysis]')}
   ```

{f'''3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required environment variables:
   {chr(10).join(f'   - `{var}`' for var in analyzer.project_data['env_example_vars'][:8])}''' if analyzer.project_data['env_example_vars'] else ''}

### Configuration

[Describe any additional configuration steps based on the project analysis]

## 🎯 Usage

### Development Mode
```bash
{analyzer.project_data.get('dev_cmd', analyzer.project_data.get('run_cmd', '[Add development command]'))}
```

### Production Mode
```bash
{analyzer.project_data.get('run_cmd', '[Add production command]')}
```

{f'''The application will be available at:
- Main application: http://localhost:{analyzer.project_data['ports'][0] if analyzer.project_data['ports'] else '3000'}
{chr(10).join(f'- Service port: http://localhost:{port}' for port in analyzer.project_data['ports'][1:4])}''' if analyzer.project_data['ports'] else ''}

{f'''## 📚 API Documentation

This project exposes the following API endpoints:

{chr(10).join(f'- `{endpoint}`' for endpoint in analyzer.project_data['api_endpoints'][:15])}

[Add more detailed API documentation based on the detected endpoints]''' if analyzer.project_data['api_endpoints'] else ''}

{f'''## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
docker-compose up -d
```

This will start the following services:
{chr(10).join(f'- **{service}**: [Describe the service purpose]' for service in analyzer.project_data['docker_services'])}

### Using Docker
```bash
docker build -t {project_name.lower()} .
docker run -p {analyzer.project_data['ports'][0] if analyzer.project_data['ports'] else '3000'}:{analyzer.project_data['ports'][0] if analyzer.project_data['ports'] else '3000'} {project_name.lower()}
```

Access the application at http://localhost:{analyzer.project_data['ports'][0] if analyzer.project_data['ports'] else '3000'}''' if analyzer.project_data['has_docker'] else ''}

## 👨‍💻 Development

### Project Structure
```
{project_name}/
{chr(10).join(f'├── {name}{"/" if item["type"] == "directory" else "":<20} # {item["description"]}' for name, item in list(analyzer.project_data.get('project_structure', {}).items())[:15])}
```

### Development Guidelines
[Add development guidelines based on the project type and complexity]

{f'''## 🧪 Testing

Run the test suite:
```bash
{analyzer.project_data['test_cmd']}
```''' if analyzer.project_data.get('test_cmd') else ''}

{f'''## 🏗 Building

Build the project:
```bash
{analyzer.project_data['build_cmd']}
```''' if analyzer.project_data.get('build_cmd') else ''}

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

{f'This project is licensed under the {analyzer.project_data["license"]} License.' if analyzer.project_data.get('license') else 'This project license is not specified.'}

## 🆘 Support

If you encounter any problems or have questions, please:
1. Check the existing issues on GitHub
2. Create a new issue with detailed description
3. Join our community discussions

---

**Project Complexity:** {analyzer.project_data['setup_difficulty']} • **Setup Time:** {
    'Few minutes' if analyzer.project_data['setup_difficulty'] == 'Easy' else
    '15-30 minutes' if analyzer.project_data['setup_difficulty'] == 'Medium' else
    '1-2 hours' if analyzer.project_data['setup_difficulty'] == 'Hard' else
    '2+ hours'
} • **Maintenance:** {'Active' if analyzer.project_data['complexity_score'] > 20 else 'Stable'}

INSTRUCTIONS FOR GENERATION:
1. **BE ACCURATE**: Only include information you can verify from the files and analysis
2. **BE COMPREHENSIVE**: Cover all aspects of the project setup and usage
3. **BE PRACTICAL**: Make all commands copy-pasteable and tested
4. **BE ORGANIZED**: Use clear sections and proper markdown formatting
5. **BE HELPFUL**: Include troubleshooting tips and common issues
6. **BE SPECIFIC**: Replace all placeholder text with actual information from the analysis
7. **BE MODERN**: Use contemporary documentation practices and formatting
8. **CUSTOMIZE DEPTH**: Adjust detail level based on project complexity ({analyzer.project_data['setup_difficulty']})

If you cannot determine specific information from the provided files, use your best judgment based on the detected technology stack, but clearly indicate any assumptions made.
"""

    return prompt
