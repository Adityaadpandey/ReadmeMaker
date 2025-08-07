# work

**work** is a lightweight, command‑line tool that scans any codebase, extracts key metadata (languages, frameworks, dependency graphs, ignored files, etc.), and presents a readable report.  
It’s especially handy for project onboarding, migration planning, or when you need a quick health check of an unfamiliar repository.

> **Why use work?**  
> • Detects the languages and tech stack used in a project.  
> • Flags unnecessary files/directories that should be cleaned up.  
> • Produces a high‑level overview of your repository’s structure.  
> • Acts as a foundation for automated documentation, CI/CD linting, or dependency audits.

---

## 📋 Table of Contents
- (#features)
- (#tech-stack)
- (#getting-started)
  - (#prerequisites)
  - (#installation)
  - (#configuration)
- (#usage)
- (#project-structure)
- (#development)
- (#contributing)
- (#license)
- (#support)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Language Detection** | Scans the repository and identifies all languages used (Python, JavaScript, Java, Rust, etc.). |
| **Framework & Library Identification** | Detects common libraries and frameworks such as Django, Flask, React, Angular, etc. |
| **Ignored Files/Directories** | Builds a comprehensive ignore list based on standard patterns (`.git`, `node_modules`, `venv`, etc.). |
| **Dependency Extraction** | Parses `requirements.txt`, `pyproject.toml`, `package.json`, `go.mod`, etc., to list external dependencies. |
| **Report Generation** | Outputs a clear, human‑readable summary directly to the console (and optionally to a JSON file). |
| **Extensible Patterns** | Built‑in ignore/extension rules can be expanded by editing the script. |

---

## 🛠 Tech Stack

- **Languages**  
  - Python

- **Frameworks & Libraries**  
  - `gitpython` – Git interactions  
  - `ollama` – (optional) integration for future LLM features  
  - `yaml` – parsing YAML files  
  - `argparse` – CLI argument parsing

- **Technologies**  
  - ASP.NET (detected if present)  
  - Actix (Rust)  
  - Angular  
  - Blockchain – recognized if relevant files found  
  - CI/CD – pipeline files detected  
  - Data Science – Jupyter notebooks, pandas, etc.  
  - Django  
  - Docker – detected via `Dockerfile` (if present)  
  - Echo (Go)  
  - Electron  

> **Note** – The tool will only report on what it actually finds; the above list is the full set of patterns it can match.

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Installation |
|-------------|---------|--------------|
| **Python** | ≥ 3.12 | `python3 -m venv venv && source venv/bin/activate` |
| **Git** | Any | `sudo apt install git` (Linux) / `brew install git` (macOS) |
| **Python packages** | Auto‑installed | `pip install -r requirements.txt` |

> **Why Python 3.12?**  
> The tool requires the latest type‑hints and pattern matching features introduced in 3.12. If you’re on an older distribution, upgrade Python first.

### Installation

```bash
# 1️⃣  Clone the repository
git clone https://github.com/Adityaadpandey/ReadmeMaker.git
cd ReadmeMaker          # repo root contains the "work" tool

# 2️⃣  Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# 3️⃣  Install the tool’s dependencies
pip install -r requirements.txt
```

> **Tip** – If you’re on Windows, use `py -3.12 -m venv .venv` and `.\.venv\Scripts\activate`.

### Configuration

`work` is a zero‑config tool; it will auto‑detect everything in the current working directory.  
If you want to exclude custom directories or files, edit the `IGNORE_PATTERNS` dictionary in `main.py` and run again.

---

## 🎯 Usage

### Basic Scan

```bash
python main.py
```

The tool will:

1. Walk the current directory recursively.  
2. Skip anything listed in `IGNORE_PATTERNS`.  
3. Detect file extensions, languages, frameworks, and dependencies.  
4. Print a concise report to stdout.

### Example Output

```
Scanning /path/to/project...
----------------------------------------
🛠 Languages Detected:
  - Python (42 files)
  - JavaScript (12 files)
  - Rust (3 files)

📦 Dependencies:
  Python: numpy==1.26.4, pandas==2.2.2
  JavaScript: react, express

📁 Ignored Paths:
  - .git/
  - node_modules/
  - venv/

📚 Report written to report.json (optional)
```

> **Optional JSON report** – Currently `main.py` prints only to console. To save a JSON file, you can pipe the output to a file or extend the script to write a structured file.

### Advanced Scenarios

| Scenario | Command | Description |
|----------|---------|-------------|
| **Scan a remote repository** | `python main.py --repo https://github.com/user/repo.git` | (Future feature – requires a clone flag) |
| **Include hidden files** | `python main.py --include-hidden` | (Future feature – modify `IGNORE_PATTERNS`) |
| **Filter by language** | `python main.py --lang python` | (Future feature – add filter logic) |

> *The current release does not support these flags; they are placeholders for future releases.*

---

## 📁 Project Structure

```
work/
├── .gitignore                # Standard ignore rules
├── README.md                 # Documentation
├── pyproject.toml            # Poetry/PEP‑517 config
├── requirements.txt          # Optional, mirrors pyproject
├── main.py                   # CLI entry point
└── LICENSE                   # (None specified)
```

> **Why `pyproject.toml`?**  
> It declares the package metadata and the required Python version (≥ 3.12). It also lists `gitpython` and `ollama` as runtime dependencies.

---

## 👨‍💻 Development

### Building & Linting

```bash
# Install development tools
pip install -r requirements-dev.txt   # if you create a dev requirements file

# Run static analysis
flake8 main.py
```

### Adding Features

1. Fork the repository.  
2. Create a branch: `git checkout -b feature/awesome-scanner`.  
3. Commit your changes.  
4. Push and submit a Pull Request.  
5. Include a clear description of the new feature and any updated docs.

---

## 🤝 Contributing

We welcome contributions of any size! Please follow these steps:

1. **Fork** the repository.  
2. **Create** a new feature branch:  
   ```bash
   git checkout -b feature/YourFeature
   ```
3. **Commit** your changes (`git commit -m "Add YourFeature"`).  
4. **Push** the branch:  
   ```bash
   git push origin feature/YourFeature
   ```
5. **Open** a Pull Request and reference any relevant issues.

### Code Style

- Follow PEP 8 for Python code.  
- Use type hints (`typing`) wherever possible.  
- Keep functions small and focused.  
- Add unit tests for new functionality.

---

## 📄 License

The project does not currently specify a license.  
If you plan to use or extend **work**, we recommend adding an MIT or Apache 2.0 license to ensure clarity for downstream users.

---

## 🆘 Support

1. Search existing issues on GitHub.  
2. If your issue is not covered, create a new issue with a detailed description, including:
   - Your operating system
   - Python version
   - Exact command you ran
   - Any error messages
3. Join the community discussion on the repository’s Discussions tab (if enabled).

---

### Project Complexity

- **Expert (Complexity Score: 65)**  
- **Estimated Setup Time:** ~2 hours  
- **Maintenance Status:** Active – new features and bug fixes are merged frequently

---