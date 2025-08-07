import argparse
import subprocess
import git
import os
import shutil
from pathlib import Path
import json
import re
from typing import List, Tuple, Dict
import yaml
from collections import Counter

# Enhanced patterns for comprehensive analysis
IGNORE_PATTERNS = {
    'directories': {
        '.git', '__pycache__', 'node_modules', '.vscode', '.idea',
        'dist', 'build', 'venv', 'env', '.pytest_cache', 'coverage',
        'logs', 'tmp', 'temp', '.next', '.nuxt', 'vendor'
    },
    'files': {
        '.gitignore', '.env', '.DS_Store', 'Thumbs.db', '*.log',
        '*.lock', '.coverage', '*.pid', '*.seed', '*.tmp'
    },
    'extensions': {
        '.pyc', '.pyo', '.so', '.dll', '.exe', '.class', '.jar',
        '.min.js', '.map', '.cache'
    }
}

# Language detection patterns
LANGUAGE_PATTERNS = {
    'Python': ['.py', 'requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile'],
    'JavaScript': ['package.json', '.js', '.jsx', '.ts', '.tsx'],
    'Java': ['.java', 'pom.xml', 'build.gradle', 'gradle.build'],
    'C++': ['.cpp', '.cc', '.cxx', '.hpp', '.h', 'CMakeLists.txt'],
    'C#': ['.cs', '*.csproj', '*.sln'],
    'Go': ['.go', 'go.mod', 'go.sum'],
    'Rust': ['.rs', 'Cargo.toml', 'Cargo.lock'],
    'PHP': ['.php', 'composer.json'],
    'Ruby': ['.rb', 'Gemfile', 'Rakefile'],
    'Swift': ['.swift', 'Package.swift'],
    'Kotlin': ['.kt', '.kts'],
    'Dart': ['.dart', 'pubspec.yaml'],
    'Shell': ['.sh', '.bash', '.zsh', 'Dockerfile'],
    'HTML': ['.html', '.htm'],
    'CSS': ['.css', '.scss', '.sass', '.less']
}

# Framework/Technology detection
TECH_SIGNATURES = {
    'React': ['react', '@types/react', 'react-dom', 'create-react-app'],
    'Vue.js': ['vue', '@vue', 'nuxt', 'quasar'],
    'Angular': ['@angular', 'angular', 'ng-', '@nguniversal'],
    'Next.js': ['next', 'next.js'],
    'Nuxt.js': ['nuxt', '@nuxt'],
    'Express.js': ['express', 'express-'],
    'Koa.js': ['koa', '@koa'],
    'Fastify': ['fastify'],
    'NestJS': ['@nestjs', 'nest'],
    'Django': ['django', 'Django'],
    'Flask': ['flask', 'Flask'],
    'FastAPI': ['fastapi', 'uvicorn'],
    'Spring Boot': ['spring-boot', '@SpringBootApplication'],
    'Laravel': ['laravel', 'artisan'],
    'Symfony': ['symfony'],
    'Rails': ['rails', 'actionpack'],
    'Sinatra': ['sinatra'],
    'Gin': ['gin-gonic', 'github.com/gin-gonic/gin'],
    'Echo': ['labstack/echo'],
    'Rocket': ['rocket', 'rocket.rs'],
    'Actix': ['actix-web'],
    'ASP.NET': ['Microsoft.AspNetCore', 'System.Web'],
    'Electron': ['electron'],
    'React Native': ['react-native', '@react-native'],
    'Flutter': ['flutter', 'dart:flutter'],
    'Unity': ['UnityEngine', 'Unity'],
    'Docker': ['Dockerfile', 'docker-compose'],
    'Kubernetes': ['kubectl', 'k8s', 'kubernetes'],
    'Redis': ['redis', 'ioredis'],
    'MongoDB': ['mongodb', 'mongoose', 'pymongo'],
    'PostgreSQL': ['postgresql', 'psycopg2', 'pg'],
    'MySQL': ['mysql', 'mysql2', 'PyMySQL'],
    'SQLite': ['sqlite', 'sqlite3'],
    'GraphQL': ['graphql', 'apollo', '@graphql'],
    'REST API': ['@RestController', 'flask-restful', 'express'],
    'WebSocket': ['socket.io', 'ws', 'websocket'],
    'Microservices': ['consul', 'eureka', 'istio'],
    'Machine Learning': ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'],
    'Data Science': ['jupyter', 'matplotlib', 'seaborn', 'plotly'],
    'Blockchain': ['web3', 'ethers', 'truffle', 'hardhat'],
    'Testing': ['jest', 'pytest', 'mocha', 'chai', 'cypress', 'selenium'],
    'CI/CD': ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', '.travis.yml']
}

class EnhancedProjectAnalyzer:
    def __init__(self, repo_dir: str = "cloned_repo"):
        self.repo_dir = Path(repo_dir)
        self.project_data = {
            'name': '',
            'description': '',
            'version': '',
            'main_language': '',
            'languages': {},
            'frameworks': [],
            'technologies': [],
            'architecture_type': '',
            'has_docker': False,
            'docker_services': [],
            'databases': [],
            'entry_point': '',
            'install_cmd': '',
            'run_cmd': '',
            'dev_cmd': '',
            'test_cmd': '',
            'build_cmd': '',
            'dependencies': [],
            'dev_dependencies': [],
            'ports': [],
            'env_vars': [],
            'env_example_vars': [],
            'api_endpoints': [],
            'features': [],
            'project_structure': {},
            'license': '',
            'author': '',
            'repository_stats': {},
            'complexity_score': 0,
            'setup_difficulty': 'Easy'
        }
        self.file_contents = {}

    def should_ignore(self, file_path: Path) -> bool:
        """Enhanced file filtering with better logic."""
        # Skip hidden files and directories (except important ones)
        for part in file_path.parts:
            if part.startswith('.') and part not in {'.env.example', '.github', '.gitignore', '.dockerignore'}:
                return True
            if part in IGNORE_PATTERNS['directories']:
                return True

        if file_path.suffix in IGNORE_PATTERNS['extensions']:
            return True

        # Skip very large files
        try:
            if file_path.stat().st_size > 100000:  # 100KB
                return True
        except:
            pass

        return False

    def detect_languages(self) -> Dict[str, int]:
        """Detect programming languages and their usage."""
        language_counts = Counter()

        for file_path in self.repo_dir.rglob('*'):
            if file_path.is_file() and not self.should_ignore(file_path):
                suffix = file_path.suffix.lower()

                # Count by file extension
                if suffix == '.py':
                    language_counts['Python'] += 1
                elif suffix in ['.js', '.jsx']:
                    language_counts['JavaScript'] += 1
                elif suffix in ['.ts', '.tsx']:
                    language_counts['TypeScript'] += 1
                elif suffix == '.java':
                    language_counts['Java'] += 1
                elif suffix in ['.cpp', '.cc', '.cxx']:
                    language_counts['C++'] += 1
                elif suffix == '.cs':
                    language_counts['C#'] += 1
                elif suffix == '.go':
                    language_counts['Go'] += 1
                elif suffix == '.rs':
                    language_counts['Rust'] += 1
                elif suffix == '.php':
                    language_counts['PHP'] += 1
                elif suffix == '.rb':
                    language_counts['Ruby'] += 1
                elif suffix in ['.html', '.htm']:
                    language_counts['HTML'] += 1
                elif suffix in ['.css', '.scss', '.sass']:
                    language_counts['CSS'] += 1

        return dict(language_counts.most_common())

    def analyze_project_structure(self):
        """Analyze and categorize project structure."""
        structure = {}

        for item in self.repo_dir.iterdir():
            if item.is_dir() and not self.should_ignore(item):
                file_count = len(list(item.rglob('*'))) if item.exists() else 0
                structure[item.name] = {
                    'type': 'directory',
                    'file_count': file_count,
                    'description': self._categorize_directory(item.name)
                }
            elif item.is_file() and not self.should_ignore(item):
                structure[item.name] = {
                    'type': 'file',
                    'description': self._categorize_file(item.name)
                }

        self.project_data['project_structure'] = structure

    def _categorize_directory(self, dirname: str) -> str:
        """Categorize directory based on common naming conventions."""
        dirname_lower = dirname.lower()

        categories = {
            'src': 'Source code directory',
            'source': 'Source code directory',
            'app': 'Application code',
            'lib': 'Library files',
            'components': 'Reusable UI components',
            'pages': 'Application pages/routes',
            'views': 'Application views/templates',
            'controllers': 'MVC controllers',
            'models': 'Data models',
            'services': 'Business logic services',
            'utils': 'Utility functions',
            'helpers': 'Helper functions',
            'config': 'Configuration files',
            'static': 'Static assets (CSS, JS, images)',
            'public': 'Public/served files',
            'assets': 'Project assets',
            'tests': 'Test files',
            'test': 'Test files',
            'spec': 'Test specifications',
            'docs': 'Documentation',
            'documentation': 'Documentation',
            'scripts': 'Build/deployment scripts',
            'tools': 'Development tools',
            'migrations': 'Database migrations',
            'templates': 'Template files',
            'styles': 'Stylesheets',
            'images': 'Image assets',
            'fonts': 'Font files',
            'api': 'API related code',
            'middleware': 'Middleware components',
            'routes': 'Application routes',
            'database': 'Database related files',
            'storage': 'File storage',
            'logs': 'Log files',
            'cache': 'Cache files'
        }

        return categories.get(dirname_lower, 'Project directory')

    def _categorize_file(self, filename: str) -> str:
        """Categorize file based on name and extension."""
        filename_lower = filename.lower()

        config_files = {
            'package.json': 'Node.js package configuration',
            'requirements.txt': 'Python dependencies',
            'pyproject.toml': 'Python project configuration',
            'setup.py': 'Python package setup',
            'dockerfile': 'Docker container configuration',
            'docker-compose.yml': 'Docker multi-container setup',
            'makefile': 'Build automation',
            'readme.md': 'Project documentation',
            'license': 'Project license',
            '.gitignore': 'Git ignore rules',
            '.env.example': 'Environment variables template',
            'config.json': 'Application configuration',
            'tsconfig.json': 'TypeScript configuration',
            'webpack.config.js': 'Webpack bundler configuration',
            'babel.config.js': 'Babel transpiler configuration',
            'jest.config.js': 'Jest testing configuration',
            'eslint.config.js': 'ESLint configuration',
            'prettier.config.js': 'Prettier formatting configuration'
        }

        return config_files.get(filename_lower, 'Project file')

    def detect_technologies(self):
        """Detect frameworks and technologies used."""
        detected_tech = set()

        # Check package.json for Node.js projects
        self._check_package_json_tech(detected_tech)

        # Check requirements.txt for Python projects
        self._check_python_tech(detected_tech)

        # Check other config files
        self._check_config_files(detected_tech)

        # Check source code for technology signatures
        self._check_source_code_tech(detected_tech)

        self.project_data['technologies'] = sorted(list(detected_tech))

    def _check_package_json_tech(self, detected_tech: set):
        """Check package.json for technologies."""
        pkg_file = self.repo_dir / 'package.json'
        if not pkg_file.exists():
            return

        try:
            with open(pkg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            all_deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}

            for tech, signatures in TECH_SIGNATURES.items():
                for signature in signatures:
                    if any(signature in dep for dep in all_deps.keys()):
                        detected_tech.add(tech)

        except Exception as e:
            print(f"Warning: Could not parse package.json: {e}")

    def _check_python_tech(self, detected_tech: set):
        """Check Python files for technologies."""
        req_files = ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile']

        for req_file in req_files:
            file_path = self.repo_dir / req_file
            if file_path.exists():
                try:
                    content = self._read_file(file_path).lower()
                    for tech, signatures in TECH_SIGNATURES.items():
                        for signature in signatures:
                            if signature.lower() in content:
                                detected_tech.add(tech)
                except Exception as e:
                    print(f"Warning: Could not parse {req_file}: {e}")

    def _check_config_files(self, detected_tech: set):
        """Check configuration files for technology indicators."""
        config_files = [
            'docker-compose.yml', 'docker-compose.yaml', 'Dockerfile',
            'kubernetes.yml', 'k8s.yml', '.gitlab-ci.yml', '.travis.yml'
        ]

        for config_file in config_files:
            file_path = self.repo_dir / config_file
            if file_path.exists():
                content = self._read_file(file_path).lower()
                for tech, signatures in TECH_SIGNATURES.items():
                    for signature in signatures:
                        if signature.lower() in content:
                            detected_tech.add(tech)

    def _check_source_code_tech(self, detected_tech: set):
        """Scan source code for technology patterns."""
        source_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs', '.php', '.rb']

        for file_path in self.repo_dir.rglob('*'):
            if (file_path.is_file() and
                file_path.suffix in source_extensions and
                not self.should_ignore(file_path)):

                try:
                    content = self._read_file(file_path)[:5000]  # First 5KB
                    for tech, signatures in TECH_SIGNATURES.items():
                        for signature in signatures:
                            if signature in content:
                                detected_tech.add(tech)
                except:
                    continue

    def analyze_package_json(self):
        """Enhanced package.json analysis."""
        pkg_file = self.repo_dir / 'package.json'
        if not pkg_file.exists():
            return

        try:
            with open(pkg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.project_data.update({
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'version': data.get('version', ''),
                'main_language': 'JavaScript',
                'entry_point': data.get('main', 'index.js'),
                'author': data.get('author', ''),
                'license': data.get('license', '')
            })

            # Enhanced script detection
            scripts = data.get('scripts', {})
            script_mapping = {
                'start': 'run_cmd',
                'dev': 'dev_cmd',
                'develop': 'dev_cmd',
                'serve': 'dev_cmd',
                'test': 'test_cmd',
                'build': 'build_cmd',
                'compile': 'build_cmd'
            }

            for script, cmd_type in script_mapping.items():
                if script in scripts:
                    self.project_data[cmd_type] = f'npm run {script}'

            if not self.project_data['run_cmd'] and 'start' in scripts:
                self.project_data['run_cmd'] = 'npm start'

            self.project_data['install_cmd'] = 'npm install'

            # Extract dependencies
            self.project_data['dependencies'] = list(data.get('dependencies', {}).keys())
            self.project_data['dev_dependencies'] = list(data.get('devDependencies', {}).keys())

            # Detect frameworks from dependencies
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            frameworks = []

            framework_patterns = {
                'React': ['react', '@types/react'],
                'Vue.js': ['vue', '@vue'],
                'Angular': ['@angular/core'],
                'Next.js': ['next'],
                'Nuxt.js': ['nuxt'],
                'Express.js': ['express'],
                'Koa.js': ['koa'],
                'NestJS': ['@nestjs/core'],
                'Electron': ['electron'],
                'React Native': ['react-native']
            }

            for framework, patterns in framework_patterns.items():
                if any(pattern in deps for pattern in patterns):
                    frameworks.append(framework)

            self.project_data['frameworks'] = frameworks

        except Exception as e:
            print(f"Warning: Could not parse package.json: {e}")

    def analyze_python_files(self):
        """Enhanced Python project analysis."""
        python_configs = [
            ('requirements.txt', self._parse_requirements),
            ('pyproject.toml', self._parse_pyproject),
            ('setup.py', self._parse_setup_py)
        ]

        for config_file, parser in python_configs:
            file_path = self.repo_dir / config_file
            if file_path.exists():
                self.project_data['main_language'] = 'Python'
                parser(file_path)
                break

        # Find main Python file
        python_files = ['main.py', 'app.py', 'run.py', 'server.py', 'manage.py', '__main__.py']
        for py_file in python_files:
            file_path = self.repo_dir / py_file
            if file_path.exists():
                self.project_data['entry_point'] = py_file
                if not self.project_data['run_cmd']:
                    self.project_data['run_cmd'] = f'python {py_file}'
                break

        # Check for common Python frameworks in source code
        self._detect_python_frameworks()

    def _parse_requirements(self, file_path: Path):
        """Parse requirements.txt file."""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            deps = []
            frameworks = []

            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    dep_name = re.split(r'[>=<!\s]', line)[0].lower()
                    deps.append(dep_name)

                    # Detect frameworks
                    framework_map = {
                        'django': ('Django', 'python manage.py runserver'),
                        'flask': ('Flask', 'python app.py'),
                        'fastapi': ('FastAPI', 'uvicorn main:app --reload'),
                        'tornado': ('Tornado', 'python app.py'),
                        'pyramid': ('Pyramid', 'pserve development.ini'),
                        'bottle': ('Bottle', 'python app.py'),
                        'cherrypy': ('CherryPy', 'python app.py')
                    }

                    if dep_name in framework_map:
                        framework, run_cmd = framework_map[dep_name]
                        frameworks.append(framework)
                        if not self.project_data['run_cmd']:
                            self.project_data['run_cmd'] = run_cmd

            self.project_data['dependencies'] = deps
            self.project_data['frameworks'].extend(frameworks)
            self.project_data['install_cmd'] = 'pip install -r requirements.txt'

        except Exception as e:
            print(f"Warning: Could not parse requirements.txt: {e}")

    def _parse_pyproject(self, file_path: Path):
        """Parse pyproject.toml file."""
        try:
            import tomli
            with open(file_path, 'rb') as f:
                data = tomli.load(f)

            project_info = data.get('project', {})
            self.project_data.update({
                'name': project_info.get('name', ''),
                'description': project_info.get('description', ''),
                'version': project_info.get('version', ''),
                'author': ', '.join(project_info.get('authors', [])),
                'license': project_info.get('license', {}).get('text', '')
            })

            # Extract dependencies
            deps = project_info.get('dependencies', [])
            self.project_data['dependencies'] = [dep.split(' ')[0] for dep in deps]

        except ImportError:
            print("Warning: tomli not available for parsing pyproject.toml")
        except Exception as e:
            print(f"Warning: Could not parse pyproject.toml: {e}")

    def _parse_setup_py(self, file_path: Path):
        """Parse setup.py file (basic parsing)."""
        try:
            content = self._read_file(file_path)

            # Extract basic info using regex (limited parsing)
            name_match = re.search(r'name=["\']([^"\']+)["\']', content)
            if name_match:
                self.project_data['name'] = name_match.group(1)

            desc_match = re.search(r'description=["\']([^"\']+)["\']', content)
            if desc_match:
                self.project_data['description'] = desc_match.group(1)

            version_match = re.search(r'version=["\']([^"\']+)["\']', content)
            if version_match:
                self.project_data['version'] = version_match.group(1)

        except Exception as e:
            print(f"Warning: Could not parse setup.py: {e}")

    def _detect_python_frameworks(self):
        """Detect Python frameworks from source code."""
        python_files = list(self.repo_dir.rglob('*.py'))
        frameworks = set()

        for py_file in python_files[:10]:  # Check first 10 Python files
            if not self.should_ignore(py_file):
                try:
                    content = self._read_file(py_file)[:2000]  # First 2KB

                    # Framework detection patterns
                    patterns = {
                        'Django': ['from django', 'import django', 'django.'],
                        'Flask': ['from flask', 'Flask(', '@app.route'],
                        'FastAPI': ['from fastapi', 'FastAPI(', '@app.get', '@app.post'],
                        'Tornado': ['import tornado', 'tornado.web'],
                        'Pyramid': ['from pyramid', 'pyramid.'],
                        'Starlette': ['from starlette', 'Starlette('],
                        'Sanic': ['from sanic', 'Sanic('],
                        'Quart': ['from quart', 'Quart(']
                    }

                    for framework, signs in patterns.items():
                        if any(sign in content for sign in signs):
                            frameworks.add(framework)

                except:
                    continue

        self.project_data['frameworks'].extend(list(frameworks))

    def analyze_docker(self):
        """Enhanced Docker analysis."""
        dockerfile = self.repo_dir / 'Dockerfile'
        compose_files = ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml']

        if dockerfile.exists():
            self.project_data['has_docker'] = True
            self._analyze_dockerfile(dockerfile)

        # Find and analyze docker-compose files
        for compose_name in compose_files:
            compose_file = self.repo_dir / compose_name
            if compose_file.exists():
                self._analyze_compose_file(compose_file)
                break

    def _analyze_dockerfile(self, dockerfile: Path):
        """Analyze Dockerfile for detailed information."""
        try:
            with open(dockerfile, 'r') as f:
                content = f.read()

            # Extract ports
            port_matches = re.findall(r'EXPOSE\s+(\d+)', content, re.IGNORECASE)
            self.project_data['ports'].extend(port_matches)

            # Extract environment variables
            env_matches = re.findall(r'ENV\s+(\w+)', content, re.IGNORECASE)
            self.project_data['env_vars'].extend(env_matches)

            # Extract base image
            from_match = re.search(r'FROM\s+([^\s]+)', content, re.IGNORECASE)
            if from_match:
                base_image = from_match.group(1)
                if 'node' in base_image.lower():
                    self.project_data['technologies'].append('Node.js')
                elif 'python' in base_image.lower():
                    self.project_data['technologies'].append('Python')
                elif 'java' in base_image.lower():
                    self.project_data['technologies'].append('Java')

            # Extract working directory
            workdir_match = re.search(r'WORKDIR\s+([^\s]+)', content, re.IGNORECASE)
            if workdir_match:
                self.project_data['workdir'] = workdir_match.group(1)

        except Exception as e:
            print(f"Warning: Could not parse Dockerfile: {e}")

    def _analyze_compose_file(self, compose_file: Path):
        """Analyze docker-compose file for services and configuration."""
        try:
            with open(compose_file, 'r') as f:
                if compose_file.suffix in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                else:
                    # Fallback to simple parsing
                    content = f.read()
                    data = {'services': {}}

            services = data.get('services', {})
            self.project_data['docker_services'] = list(services.keys())

            # Analyze each service
            databases = []
            for service_name, service_config in services.items():
                image = service_config.get('image', '')

                # Detect databases
                db_patterns = {
                    'PostgreSQL': ['postgres', 'postgresql'],
                    'MySQL': ['mysql', 'mariadb'],
                    'MongoDB': ['mongo'],
                    'Redis': ['redis'],
                    'Elasticsearch': ['elasticsearch', 'elastic'],
                    'SQLite': ['sqlite']
                }

                for db, patterns in db_patterns.items():
                    if any(pattern in image.lower() for pattern in patterns):
                        databases.append(db)

                # Extract ports
                ports = service_config.get('ports', [])
                for port in ports:
                    if isinstance(port, str):
                        external_port = port.split(':')[0]
                        self.project_data['ports'].append(external_port)

                # Extract environment variables
                environment = service_config.get('environment', {})
                if isinstance(environment, dict):
                    self.project_data['env_vars'].extend(environment.keys())
                elif isinstance(environment, list):
                    for env_var in environment:
                        if '=' in env_var:
                            var_name = env_var.split('=')[0]
                            self.project_data['env_vars'].append(var_name)

            self.project_data['databases'] = list(set(databases))

        except Exception as e:
            print(f"Warning: Could not parse docker-compose file: {e}")

    def analyze_environment_files(self):
        """Analyze environment configuration files."""
        env_files = ['.env.example', '.env.template', '.env.sample', '.env.local']

        for env_file in env_files:
            file_path = self.repo_dir / env_file
            if file_path.exists():
                try:
                    content = self._read_file(file_path)
                    env_vars = []

                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            var_name = line.split('=')[0].strip()
                            env_vars.append(var_name)

                    self.project_data['env_example_vars'] = env_vars
                    break

                except Exception as e:
                    print(f"Warning: Could not parse {env_file}: {e}")

    def analyze_api_patterns(self):
        """Detect API endpoints and patterns from source code."""
        endpoints = []
        api_files = []

        # Find potential API files
        for file_path in self.repo_dir.rglob('*'):
            if (file_path.is_file() and
                not self.should_ignore(file_path) and
                file_path.suffix in ['.py', '.js', '.ts', '.java', '.go', '.php', '.rb']):

                try:
                    content = self._read_file(file_path)[:3000]  # First 3KB

                    # Common API patterns
                    api_patterns = [
                        r'@app\.route\(["\']([^"\']+)["\']',  # Flask
                        r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']',  # FastAPI
                        r'app\.(get|post|put|delete)\(["\']([^"\']+)["\']',  # Express.js
                        r'@(GetMapping|PostMapping|PutMapping|DeleteMapping)\(["\']([^"\']+)["\']',  # Spring Boot
                        r'@RequestMapping.*value\s*=\s*["\']([^"\']+)["\']',  # Spring Boot
                        r'Route::(get|post|put|delete)\(["\']([^"\']+)["\']',  # Laravel
                        r'router\.(get|post|put|delete)\(["\']([^"\']+)["\']',  # Various frameworks
                    ]

                    for pattern in api_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                endpoint = match[-1] if len(match) > 1 else match[0]
                            else:
                                endpoint = match
                            endpoints.append(endpoint)

                    # Check if file looks like an API file
                    api_indicators = ['route', 'endpoint', 'api', 'controller', 'handler', 'service']
                    if any(indicator in file_path.name.lower() for indicator in api_indicators):
                        api_files.append(str(file_path.relative_to(self.repo_dir)))

                except:
                    continue

        # Clean and deduplicate endpoints
        unique_endpoints = list(set(endpoints))[:20]  # Limit to 20 endpoints
        self.project_data['api_endpoints'] = unique_endpoints

    def calculate_complexity_score(self):
        """Calculate project complexity score based on various factors."""
        score = 0

        # Language diversity
        score += len(self.project_data['languages']) * 2

        # Technology stack
        score += len(self.project_data['technologies']) * 1.5

        # Docker complexity
        if self.project_data['has_docker']:
            score += 5
            score += len(self.project_data['docker_services']) * 2

        # Database usage
        score += len(self.project_data['databases']) * 3

        # Environment variables
        score += len(self.project_data['env_vars']) * 0.5

        # API endpoints
        score += len(self.project_data['api_endpoints']) * 0.3

        # Dependencies
        score += len(self.project_data['dependencies']) * 0.1

        self.project_data['complexity_score'] = int(score)

        # Determine setup difficulty
        if score < 10:
            self.project_data['setup_difficulty'] = 'Easy'
        elif score < 30:
            self.project_data['setup_difficulty'] = 'Medium'
        elif score < 60:
            self.project_data['setup_difficulty'] = 'Hard'
        else:
            self.project_data['setup_difficulty'] = 'Expert'

    def detect_project_features(self):
        """Detect project features based on code analysis."""
        features = []

        # Check for common features based on dependencies and technologies
        feature_indicators = {
            'Authentication': ['auth', 'jwt', 'passport', 'oauth', 'login', 'session'],
            'Database Integration': self.project_data['databases'],
            'API Development': ['api', 'rest', 'graphql', 'endpoint'],
            'Real-time Features': ['websocket', 'socket.io', 'ws', 'realtime'],
            'File Upload': ['multer', 'upload', 'file-upload', 'boto3'],
            'Email Services': ['nodemailer', 'sendgrid', 'mailgun', 'smtp'],
            'Payment Integration': ['stripe', 'paypal', 'payment'],
            'Caching': ['redis', 'memcached', 'cache'],
            'Testing': ['jest', 'pytest', 'mocha', 'phpunit', 'rspec'],
            'CI/CD': ['github-actions', 'travis', 'jenkins', 'gitlab-ci'],
            'Monitoring': ['sentry', 'newrelic', 'datadog', 'prometheus'],
            'Documentation': ['swagger', 'openapi', 'docs', 'sphinx'],
            'Containerization': ['docker', 'kubernetes'],
            'Microservices': ['consul', 'eureka', 'istio', 'service-mesh'],
            'Machine Learning': ['tensorflow', 'pytorch', 'scikit-learn', 'ml'],
            'Data Processing': ['pandas', 'numpy', 'spark', 'kafka'],
            'Frontend Framework': ['react', 'vue', 'angular', 'svelte'],
            'Mobile Development': ['react-native', 'flutter', 'ionic'],
            'Desktop Application': ['electron', 'qt', 'tkinter'],
            'Game Development': ['unity', 'pygame', 'phaser'],
            'Blockchain': ['web3', 'ethereum', 'solidity', 'bitcoin']
        }

        all_text = ' '.join([
            ' '.join(self.project_data['dependencies']),
            ' '.join(self.project_data['technologies']),
            ' '.join(self.project_data['frameworks']),
            self.project_data.get('description', '').lower()
        ]).lower()

        for feature, indicators in feature_indicators.items():
            if any(indicator in all_text for indicator in indicators):
                features.append(feature)

        self.project_data['features'] = features[:15]  # Limit to 15 features

    def get_key_files(self) -> List[Tuple[str, str]]:
        """Get content from important files with enhanced selection."""
        important_files = []

        # Priority files in order of importance
        priority_files = [
            # Config files
            'package.json', 'requirements.txt', 'pyproject.toml', 'setup.py',
            'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle', 'composer.json',

            # Docker files
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', 'compose.yml',

            # Documentation
            'README.md', 'README.rst', 'README.txt', 'CHANGELOG.md',

            # Environment and config
            '.env.example', '.env.template', 'config.json', 'config.yaml',

            # Entry points
            'main.py', 'app.py', 'index.js', 'server.js', 'app.js',
            'main.go', 'main.rs', 'Main.java', 'Program.cs',

            # Framework specific
            'manage.py',  # Django
            'artisan',    # Laravel
            'mix.exs',    # Elixir
            'Gemfile',    # Ruby

            # Build and CI
            'Makefile', 'CMakeLists.txt', 'webpack.config.js',
            '.github/workflows/main.yml', '.gitlab-ci.yml', 'Jenkinsfile',

            # Database
            'schema.sql', 'migration.sql', 'models.py', 'database.js'
        ]

        for filename in priority_files:
            # Handle nested files like .github/workflows/main.yml
            if '/' in filename:
                file_path = self.repo_dir / Path(filename)
            else:
                file_path = self.repo_dir / filename

            if file_path.exists() and not self.should_ignore(file_path):
                content = self._read_file(file_path)
                if content and len(content) < 8000:  # Increase size limit
                    important_files.append((str(file_path.relative_to(self.repo_dir)), content))
                    self.file_contents[filename] = content

        # Also include some source files for better understanding
        source_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.php', '.rb', '.cs']
        source_files_added = 0

        for file_path in self.repo_dir.rglob('*'):
            if (source_files_added >= 5 or  # Limit source files
                not file_path.is_file() or
                self.should_ignore(file_path) or
                file_path.suffix not in source_extensions):
                continue

            # Skip if already added
            rel_path = str(file_path.relative_to(self.repo_dir))
            if any(rel_path == existing[0] for existing in important_files):
                continue

            content = self._read_file(file_path)
            if content and len(content) < 3000:
                important_files.append((rel_path, content))
                source_files_added += 1

        return important_files

    def _read_file(self, file_path: Path) -> str:
        """Enhanced file reading with better error handling."""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                try:
                    # Last resort: read as binary and decode with errors ignored
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')
                except:
                    return ""
        except:
            return ""

        # Truncate if too long
        if len(content) > 5000:
            content = content[:4000] + "\n\n... [TRUNCATED] ..."

        return content

    def perform_full_analysis(self):
        """Perform comprehensive project analysis."""
        print("🔍 Performing deep project analysis...")

        # Language detection
        self.project_data['languages'] = self.detect_languages()
        if self.project_data['languages']:
            self.project_data['main_language'] = next(iter(self.project_data['languages']))

        # Technology and framework detection
        self.detect_technologies()

        # Project structure analysis
        self.analyze_project_structure()

        # Specific file analysis
        self.analyze_package_json()
        self.analyze_python_files()
        self.analyze_docker()
        self.analyze_environment_files()

        # Advanced analysis
        self.analyze_api_patterns()
        self.detect_project_features()
        self.calculate_complexity_score()

        # Determine architecture type
        if len(self.project_data['docker_services']) > 3:
            self.project_data['architecture_type'] = 'Microservices'
        elif self.project_data['has_docker']:
            self.project_data['architecture_type'] = 'Containerized Application'
        elif len(self.project_data['languages']) > 2:
            self.project_data['architecture_type'] = 'Multi-language Application'
        else:
            self.project_data['architecture_type'] = 'Monolithic Application'

def clone_repo(repo_url: str, dest_dir: str = "cloned_repo") -> bool:
    """Clone repository with enhanced error handling."""
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    print(f"🔄 Cloning {repo_url}...")
    try:
        # Support for different Git providers and protocols
        git.Repo.clone_from(repo_url, dest_dir, depth=1)  # Shallow clone for faster processing
        print("✅ Repository cloned!")
        return True
    except git.exc.GitCommandError as e:
        print(f"❌ Git error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error cloning: {e}")
        return False

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

def generate_comprehensive_readme(analyzer: EnhancedProjectAnalyzer, key_files: List[Tuple[str, str]],
                                repo_url: str, model: str = "llama3.2:latest") -> bool:
    """Generate comprehensive README with enhanced prompting."""
    print("🤖 Generating comprehensive README...")
    print(f"📊 Project complexity: {analyzer.project_data['setup_difficulty']} ({analyzer.project_data['complexity_score']} points)")

    prompt = create_comprehensive_prompt(analyzer, key_files, repo_url)

    try:
        # Use longer timeout for complex projects
        timeout = 600 if analyzer.project_data['complexity_score'] > 50 else 300

        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode('utf-8'),
            capture_output=True,
            timeout=timeout
        )

        if result.returncode != 0:
            print(f"❌ Ollama error: {result.stderr.decode()}")
            return False

        output = result.stdout.decode('utf-8').strip()

        # Enhanced output cleaning
        # Remove code block markers
        if output.startswith('```markdown'):
            output = output[11:]
        elif output.startswith('```'):
            output = output[3:]
        if output.endswith('```'):
            output = output[:-3]

        # Remove any meta-commentary at the beginning
        lines = output.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#') and not stripped.startswith('##') and len(stripped) > 1:
                start_idx = i
                break

        if start_idx > 0:
            output = '\n'.join(lines[start_idx:])

        # Clean up any remaining artifacts
        output = re.sub(r'\[.*?\]', '', output, flags=re.MULTILINE)
        output = re.sub(r'^\s*Note:.*', '', output, flags=re.MULTILINE | re.IGNORECASE)  # Remove notes

        # Save README
        with open("README.md", "w", encoding='utf-8') as f:
            f.write(output.strip())

        # Save analysis data for debugging
        if os.getenv('DEBUG'):
            with open("project_analysis.json", "w", encoding='utf-8') as f:
                json.dump(analyzer.project_data, f, indent=2, default=str)

        print("✅ Comprehensive README.md generated!")
        print(f"📄 Size: {len(output):,} characters")
        print(f"🎯 Features detected: {len(analyzer.project_data['features'])}")
        print(f"🛠 Technologies identified: {len(analyzer.project_data['technologies'])}")
        return True

    except subprocess.TimeoutExpired:
        print("❌ Generation timed out (project might be very complex)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced README generator with deep project analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python readme_generator.py --repo https://github.com/user/project
  python readme_generator.py --repo https://github.com/user/project --model llama3.2:3b
  python readme_generator.py --repo https://github.com/user/project --debug
        """
    )
    parser.add_argument('--repo', required=True, help='Git repository URL')
    parser.add_argument('--model', default='llama3.2:latest',
                       help='Ollama model to use (default: llama3.2:latest)')
    parser.add_argument('--debug', action='store_true',
                       help='Keep debug files and enable verbose output')
    parser.add_argument('--shallow', action='store_true',
                       help='Perform shallow analysis for faster processing')

    args = parser.parse_args()

    print("🚀 Enhanced README Generator with Deep Project Analysis")
    print("=" * 60)
    print(f"📂 Repository: {args.repo}")
    print(f"🧠 Model: {args.model}")
    print(f"🔍 Analysis: {'Shallow' if args.shallow else 'Deep'}")
    print("=" * 60)

    # Clone repository
    if not clone_repo(args.repo):
        return 1

    # Initialize enhanced analyzer
    print("\n🔍 Initializing project analysis...")
    analyzer = EnhancedProjectAnalyzer()

    # Perform analysis
    if not args.shallow:
        analyzer.perform_full_analysis()
    else:
        # Basic analysis only
        analyzer.analyze_package_json()
        analyzer.analyze_python_files()
        analyzer.analyze_docker()

    # Print analysis summary
    print(f"\n📊 Analysis Results:")
    print(f"   Main Language: {analyzer.project_data['main_language']}")
    print(f"   Languages: {len(analyzer.project_data['languages'])} detected")
    print(f"   Frameworks: {len(analyzer.project_data['frameworks'])} detected")
    print(f"   Technologies: {len(analyzer.project_data['technologies'])} detected")
    print(f"   Features: {len(analyzer.project_data['features'])} detected")
    print(f"   Docker: {'Yes' if analyzer.project_data['has_docker'] else 'No'}")
    print(f"   Complexity: {analyzer.project_data['setup_difficulty']} ({analyzer.project_data['complexity_score']} points)")

    if analyzer.project_data['has_docker']:
        print(f"   Services: {len(analyzer.project_data['docker_services'])}")
        print(f"   Databases: {len(analyzer.project_data['databases'])}")

    # Get key files
    key_files = analyzer.get_key_files()
    print(f"\n📋 Analyzing {len(key_files)} key files")

    # Generate README
    success = generate_comprehensive_readme(analyzer, key_files, args.repo, args.model)

    if success:
        print("\n🎉 Success! Generated comprehensive README.md")
        print("\n💡 README includes:")
        print("   ✅ Comprehensive project overview")
        print("   ✅ Technology stack analysis")
        print("   ✅ Step-by-step setup instructions")
        print("   ✅ Usage examples and commands")
        if analyzer.project_data['has_docker']:
            print("   ✅ Docker deployment guide")
        if analyzer.project_data['api_endpoints']:
            print("   ✅ API documentation")
        print("   ✅ Project structure overview")
        print("   ✅ Development guidelines")
        print("   ✅ Contributing instructions")
    else:
        print("\n❌ Failed to generate README")
        print("\n💡 Troubleshooting tips:")
        print("• Ensure Ollama is running: ollama serve")
        print(f"• Pull the model: ollama pull {args.model}")
        print("• Try a smaller model: --model llama3.2:1b")
        print("• Use shallow analysis: --shallow")
        print("• Check if repository is accessible")
        return 1

    # Cleanup
    if not args.debug:
        try:
            shutil.rmtree("cloned_repo")
            print("🧹 Cleaned up temporary files")
        except:
            pass
    else:
        print(f"🐛 Debug mode: Files preserved in 'cloned_repo' directory")
        if os.path.exists("project_analysis.json"):
            print(f"🐛 Project analysis saved to 'project_analysis.json'")

    return 0

if __name__ == "__main__":
    exit(main())
