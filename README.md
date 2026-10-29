# hep-agent-bench-tools

`hepbench`: grader helpers for [hep-agent-bench](https://github.com/hep-cce2/hep-agent-bench) tasks. Each helper implements one rule of the [spec](https://github.com/hep-cce2/hep-agent-bench-spec/blob/main/grading.md). Standard library only, Python 3.9+.

| | Spec rule |
|---|---|
| `log_gain_vs_expert(agent_gain, expert_gain)` | the `log-gain-vs-expert` score, uncapped |
| `gated_reward(correct, score)` | 0 unless the gate passed, else clamp to [0, 1] |
| `write_result(logs_dir, reward, correct, **metrics)` | `reward.txt` + `metrics.json` with `spec_version` |
| `median_time(fn, make_input, iterations)` | median of N timed calls, fresh input per call |
| `python -m hepbench.snapshot create / verify / export` | baseline integrity: manifest of Git blob hashes, check, clean copy |

## Use in a task

Install at grading time, pinned, so nothing in the agent's image is used:

```toml
# task.toml
[verifier.env]
HEPBENCH_TOOLS = "git+https://github.com/hep-cce2/hep-agent-bench-tools@v0.1.0"
```

```bash
# tests/test.sh
pip install --quiet --no-deps --target "$WORK/tools" "$HEPBENCH_TOOLS"
export PYTHONPATH="$WORK/tools"
python3 -m hepbench.snapshot export --root /opt/baseline --manifest /tests/source-manifest.json --dest "$WORK/base-src"
```

```python
from hepbench import gated_reward, log_gain_vs_expert, write_result
score = log_gain_vs_expert(base_time / agent_time, base_time / expert_time)
write_result("/logs/verifier", gated_reward(correct, score), correct, log_speedup_vs_expert=score)
```

[`tasks/frnn-exact-optimization/tests/`](https://github.com/hep-cce2/hep-agent-bench/tree/main/tasks/frnn-exact-optimization/tests) is a complete example.

Make a baseline manifest from a checkout of the pinned commit:

```bash
python -m hepbench.snapshot create --repo path/to/checkout --upstream https://github.com/org/repo > tests/source-manifest.json
```

## Development

```bash
pip install -e . pytest && pytest
```

Versions follow the spec: `hepbench` 0.1.x implements spec 0.1.
