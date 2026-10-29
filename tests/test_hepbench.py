import json
import math
import subprocess

import pytest

from hepbench import gated_reward, log_gain_vs_expert, median_time, write_result
from hepbench import snapshot


def test_scoring():
    assert log_gain_vs_expert(4.0, 4.0) == pytest.approx(1.0)
    assert log_gain_vs_expert(2.0, 4.0) == pytest.approx(0.5)
    assert log_gain_vs_expert(16.0, 4.0) == pytest.approx(2.0)  # uncapped
    assert log_gain_vs_expert(0.5, 4.0) == pytest.approx(-0.5)  # slower than baseline
    with pytest.raises(ValueError):
        log_gain_vs_expert(2.0, 1.0)
    with pytest.raises(ValueError):
        log_gain_vs_expert(0.0, 2.0)
    assert gated_reward(True, 2.0) == 1.0
    assert gated_reward(True, -0.5) == 0.0
    assert gated_reward(False, 0.9) == 0.0


def test_write_result(tmp_path):
    out = write_result(tmp_path / "v", 0.25, True, speedup=2.0)
    assert (tmp_path / "v" / "reward.txt").read_text() == "0.250000\n"
    assert json.loads((tmp_path / "v" / "metrics.json").read_text()) == out
    assert out["spec_version"] and out["speedup"] == 2.0
    with pytest.raises(ValueError):
        write_result(tmp_path, math.nan, True)
    with pytest.raises(ValueError):
        write_result(tmp_path, 1.5, True)


def test_median_time():
    seen = []
    p50, times = median_time(seen.append, lambda i: i * 10, 3)
    assert seen == [0, 10, 20] and len(times) == 3 and p50 == sorted(times)[1]


def test_snapshot_roundtrip(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.txt").write_text("hello\n")
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.check_call(git + ["init", "-q"])
    subprocess.check_call(git + ["add", "."])
    subprocess.check_call(git + ["commit", "-qm", "x"])
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps(snapshot.create(repo)))
    assert snapshot.verify(repo, manifest) == []
    (repo / "build").mkdir()
    (repo / "build" / "stale.o").write_text("old")
    assert snapshot.export(repo, manifest, tmp_path / "out") == []
    assert sorted(p.name for p in (tmp_path / "out").rglob("*")) == ["a.txt"]
    (repo / "a.txt").write_text("tampered\n")
    assert snapshot.export(repo, manifest, tmp_path / "out2") and not (tmp_path / "out2").exists()
    assert snapshot.verify(repo, manifest)[0].startswith("changed: a.txt")
    (repo / "a.txt").unlink()
    assert snapshot.verify(repo, manifest) == ["missing: a.txt"]
