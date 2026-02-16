from __future__ import annotations

from pathlib import Path



PROTECTED_BRANCHES = {"main", "master", "release"}


def ensure_safe_branch(repo_path: str, allow_protected: bool = False) -> dict:
    from git import Repo

    repo = Repo(Path(repo_path))
    branch = repo.active_branch.name
    if branch in PROTECTED_BRANCHES and not allow_protected:
        raise ValueError(
            f"Refusing write operations on protected branch '{branch}'. Use feature branch or set allow_protected=True"
        )
    return {"branch": branch, "safe": True, "protected": branch in PROTECTED_BRANCHES}
