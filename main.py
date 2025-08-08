import argparse
import os
import shutil

from analyzer import EnhancedProjectAnalyzer
from docker import clone_repo
from readme import generate_comprehensive_readme


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced README generator with deep project analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
                python main.py --repo https://github.com/user/project
                python main.py --repo https://github.com/user/project --model llama3.2:3b
                python main.py --repo https://github.com/user/project --debug
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
