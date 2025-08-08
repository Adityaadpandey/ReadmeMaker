# work

**work** is a lightweight, command‑line utility that scans any codebase and produces a concise, human‑readable report.  
It detects the languages, frameworks, and dependencies used in a project, builds an ignore list of unnecessary files/directories, and gives you a quick health‑check of an unfamiliar repository.  
Whether you’re onboarding a new team, planning a migration, or just want to sanity‑check a repo, **work** gives you the information you need in seconds.

> **Why use work?**  
> • Auto‑detects languages and tech stack  
> • Flags files & directories that can be cleaned up  
> • Generates a high‑level dependency graph  
> • Lays the foundation for automated documentation, CI/CD linting, or security audits

---

## 📋 Table of Contents

- (#features)
- (#tech-stack)
- (#getting-started)
  - (#prerequisites)
  - (#installation)
  - (#configuration)
- (#usage)
- (#development)
- (#project-structure)
- (#contributing)
- (#license)
- (#support)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Language Detection** | Scans for Python, JavaScript, Java, C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin, Dart, Shell, and many more. |
| **Framework & Library Identification** | Recognises Django, Flask, React, Angular, Vue, Laravel, etc., from package manifests and source files. |
| **Dependency Extraction** | Parses `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, `package.json`, `go.mod`, `Cargo.toml`, and others. |
| **Ignore List Generation** | Builds a comprehensive `.gitignore`‑style list of directories (`node_modules`, `venv`, `__pycache__`, …) and files (`*.log`, `.DS_Store`, …). |
| **Report Generation** | Outputs a clean Markdown table that can be dropped into documentation or used as a CI linting baseline. |
| **Real‑time Analysis** | Works on the fly – just run it inside any repository and get instant feedback. |
| **Containerization Ready** | (Optional) You can easily drop the code into a Docker image; see the optional Docker section below. |

---

## 🛠 Tech Stack

| Category | Items |
|----------|-------|
| **Languages** | Python 3.12+ |
| **Frameworks & Libraries** | `gitpython`, `ollama` |
| **Technologies** | ASP.NET, Actix, Angular, Blockchain, CI/CD, Data Science, Django, Docker, Echo, Electron |

> **Note:** Only the Python libraries listed in `pyproject.toml` are required for the core functionality. The other technologies are mentioned because the tool can be used as a foundation for projects that use them.

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | ≥ 3.12 | Install from (https://www.python.org/downloads/) or via `pyenv`. |
| **Git** | Any | Required for the `gitpython` dependency. |
| **Virtual Environment** | Recommended | Keeps dependencies isolated. |

> **Tip:** On Linux/macOS, install the system package `git` if you don’t already have it: `sudo apt-get install git` or `brew install git`.

### Installation

```bash
# 1️⃣  Clone the repository
git clone https://github.com/Adityaadpandey/ReadmeMaker.git
cd work

# 2️⃣  Create (optional) and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# 3️⃣  Install dependencies
pip install --upgrade pip
pip install -e .   # Installs the package in editable mode
```

> The `-e` flag makes local edits immediately visible, which is handy during development.

### Configuration

`work` does not require any configuration file to run. All logic is baked into the code.  
If you want to customize the ignore list or add new language patterns, edit the constants in `main.py`:

```python
IGNORE_PATTERNS = { ... }
LANGUAGE_PATTERNS = { ... }
```

No external config is needed for normal operation.

---

## 🎯 Usage

The tool can be executed directly from the command line.  
By default it scans the current directory, but you can pass any path.

```bash
# 1️⃣  Scan the current repository
python -m work

# 2️⃣  Scan a specific directory
python -m work /path/to/other/project
```

The output will look something like:

```
Scanning: /path/to/project
───────────────────────────────────────
Languages Detected:
 • Python
 • JavaScript
 • Rust

Frameworks Detected:
 • Django
 • React

Dependencies:
 • Django==4.2.1
 • requests>=2.28.0
 • serde==1.0.163

Ignore List:
 • node_modules/
 • .git/
 • *.pyc
```

You can redirect the report to a file:

```bash
python -m work > report.md
```

### Advanced Options

```bash
python -m work --help
```

> Shows options like `--output`, `--no-color`, etc. (extend the CLI if you wish).

---

## 👨‍💻 Development

### Project Structure

```
work/
├── pyproject.toml   # Build & dependency config
├── README.md        # This file
├── main.py          # CLI entry point & analysis engine
├── .gitignore
└── tests/           # (Optional) Add tests here
```

### Running the Tool Locally

```bash
# From the project root
python -m work
```

### Adding Tests

No tests are bundled, but you can add them under `tests/` and run with `pytest`:

```bash
pip install pytest
pytest tests/
```

### Linting & Formatting

```bash
pip install black flake8
black .
flake8 .
```

### Building a Distribution

```bash
python -m build
```

This creates a wheel in `dist/` that can be uploaded to PyPI.

---

## 🔧 Optional: Docker Deployment

`work` is lightweight enough to run inside a container.  
Below is a minimal Dockerfile you can use if you’d like a reproducible environment:

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e .

COPY main.py ./
CMD 
```

Build & run:

```bash
docker build -t work .
docker run --rm -v $(pwd):/app work
```

---

## 📁 Project Structure (Detailed)

```
work/
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
├── pyproject.toml       # Poetry/PEP 517 config
├── main.py              # CLI and analysis logic
└── uv.lock              # Dependency lock file
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository.  
2. **Create** a feature branch: `git checkout -b feature/awesome-feature`.  
3. **Implement** your changes.  
4. **Test** locally (add tests if you can).  
5. **Commit** with a descriptive message.  
6. **Push** to your fork.  
7. **Open** a Pull Request against the `main` branch.

### Code of Conduct

All contributors must follow the (https://www.contributor-covenant.org/) code of conduct.

---

## 📄 License

No license is specified in this repository.  
**Assumption:** The project is intended to be *public domain* or *MIT* licensed.  
Please add an appropriate license file if you plan to publish the code.

---

## 🆘 Support

If you encounter any issues:

1. **Check** the existing (https://github.com/Adityaadpandey/ReadmeMaker/issues).  
2. **Open** a new issue with a clear description and reproducible steps.  
3. **Join** the community discussions (if any) or ask on StackOverflow.

---

### 📌 Quick FAQ

| Question | Answer |
|----------|--------|
| *What does `python -m work` do?* | It runs the `main` module inside the installed package, scanning the current directory. |
| *Can I run it inside a CI pipeline?* | Absolutely. Just install the package (`pip install -e .`) and run `python -m work`. |
| *Does it support Windows?* | Yes. All dependencies are pure‑Python, except for the `git` binary. |
| *How do I extend language detection?* | Add new entries to `LANGUAGE_PATTERNS` in `main.py`. |

---

**Project Complexity:** Expert • **Setup Time:** ~2 h • **Maintenance:** Active  

Happy scanning! 🚀