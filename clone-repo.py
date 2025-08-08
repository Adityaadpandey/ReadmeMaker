import git
import os
import shutil




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
