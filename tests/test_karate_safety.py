import pytest

git = pytest.importorskip("git")

from autofixer_agent.karate.safety import ensure_safe_branch


def test_ensure_safe_branch_blocks_main(tmp_path):
    repo = git.Repo.init(tmp_path)
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    repo.index.add(["a.txt"])
    repo.index.commit("init")
    repo.git.branch("-M", "main")

    with pytest.raises(ValueError):
        ensure_safe_branch(str(tmp_path))
