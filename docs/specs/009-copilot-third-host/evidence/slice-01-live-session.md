# Slice 009-01 live Copilot skill proof

Executed on 2026-10-12 with GitHub Copilot CLI 1.0.96-2, exit 0, after the
compliance-review repairs. An earlier successful 1.0.93-1 run is also retained
in session artifacts; it is not substituted for this final-package run.
This was an authenticated agent run, separate from the deterministic installed
discovery/helper probe in `slice-01-installed.json`.

## Invocation and isolation

The direct-install consumer/home retained by `smoke_copilot_install.py` were
used. `COPILOT_HOME` pointed at that disposable home, not the normal user
configuration. The consumer contained JIG/servo fixtures and no Shaper runtime.

```text
copilot -p <installed shape-release then release-slate request>
  --allow-all-tools --disable-builtin-mcps --no-ask-user
  --output-format json --share <session-artifact>/slice-01-live-transcript.md
```

Session ID: `ef0adb0c-9597-4786-98fb-1521f203db7d`.
Full exported transcript and JSONL output are retained in the implementation
session's artifact storage; the following is a checked, bounded transcript
extract rather than an invented success assertion.

## Witnessed skill/tool actions

- Transcript lines 21-41: `skill({"skill":"shape-release"})` loaded successfully.
- The loaded skill supplied its packaged instructions and absolute directory;
  the agent read the helper/template before using them.
- Lines 577-631: it set the installed `SHAPER_SKILL_DIR`, ran the documented
  data-only bootstrap, then executed the installed helper with `--repo . --slug
  live-probe --status candidate`, the supplied problem/appetite/solution/scope,
  no-go/risk/criteria. The helper exited 0.
- Lines 639-659: `skill({"skill":"release-slate"})` loaded successfully.
- Lines 917-974: it resolved that installed skill's directory and ran
  `python3 "$SHAPER_ROOT/skills/release-slate/scripts/release_slate.py" --repo .`,
  which exited 0. The parent independently asserted protected fixture hashes.

The parent independently confirmed `docs/releases/live-probe.md` exists and
`docs/releases/README.md` links `live-probe.md`. Both files were produced by
the installed helpers, not a hand-written substitute.

## Protected fixture hashes

SHA-256 values were identical before and after the agent run:

| Fixture | Before and after |
|---|---|
| `docs/specs/README.md` | `64ca0d5cc2b491d681cad6fc05f7bd04ee0d351fbce14d0558e710095ba9ab27` |
| `docs/specs/010-probe/spec.md` | `eb7b2784d11b0e39d19a0aef96916f40d2b3b6a3cdfa27983d5781ae9a7a3ce0` |
| `docs/servo/release-signals/probe.md` | `5954d54563c739124bf2fdec86b7503b80cf135c2a7c79484dff9eea0c2fb9c5` |

This proves local installed skill use and non-mutation. It does not claim a
remote marketplace publication or GitHub release upload.
