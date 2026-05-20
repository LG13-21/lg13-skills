#!/usr/bin/env python
"""legal-total-analysis — lean meta-skill helper.

Reuse existing optimize/audit výstupů 91-99 + audit_report. Provede 3 unique kroky
(DON'T grep, Cross-check, Verdict) a vygeneruje GO/NO-GO master report.

Author: legal instance, 2026-04-28
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REUSE_FILES = {
    "91_redundancy": "91_redundancy_analysis.md",
    "92_impact": "92_impact_simulation.md",
    "93_optim_log": "93_optimization_log.md",
    "94_optim_report": "94_optimization_report.md",
    "96_matrix": "96_matrix_updates.md",
    "97_distribution": "97_distribution_report.md",
    "98_preflight": "98_preflight_report.md",
    "99_risk": None,
}

DONT_SECTION_HEADERS = (
    "## A.4.1",
    "### A.4.1",
    "## DON'T",
    "### DON'T",
    "## DON",
)

CORE_SECTION_HEADERS = (
    "## CORE",
    "### CORE",
    "## A.1",
    "### A.1",
)

PETIT_REGEX = re.compile(r"\bnavrh(uje[mnt]?|ujeme)?\b", re.IGNORECASE)
RED_REGEX = re.compile(r"\b(RED|KRITICK[ÉÝ]|HARD-?FAIL|BLOCKER)\b", re.IGNORECASE)
ORANGE_REGEX = re.compile(r"\b(ORANGE|WARN(?:ING)?|VAROV[ÁA]N[ÍI])\b", re.IGNORECASE)
SCORE_REGEX = re.compile(r"\bscore\s*[:=]\s*(\d{1,3})", re.IGNORECASE)
COMPLIANCE_REGEX = re.compile(r"\bcompliance[^0-9]{0,30}(\d{1,3})", re.IGNORECASE)


@dataclass
class ReuseSignals:
    file: str
    score: int | None = None
    red_markers: int = 0
    orange_markers: int = 0
    warnings: list[str] = field(default_factory=list)
    excerpt: str = ""


@dataclass
class DontViolation:
    rule: str
    file: str
    line_no: int
    line: str
    context: str


@dataclass
class CrosscheckIssue:
    kind: str
    description: str
    prev_excerpt: str = ""
    curr_excerpt: str = ""


@dataclass
class Verdict:
    verdict: str
    timestamp: str
    folder: str
    scores: dict
    blocking_issues: list[str]
    warnings: list[str]
    next_steps: list[str]
    recommendation: str


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def find_audit_report(base: Path) -> Path | None:
    candidates = list(base.glob("kontrola_*_audit_report.md"))
    if not candidates:
        candidates = list(base.parent.glob("kontrola_*_audit_report.md"))
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def find_risk_file(optimize_dir: Path) -> Path | None:
    for pat in ("99_risk_assessment*.md", "99_risk*.md"):
        for p in optimize_dir.glob(pat):
            return p
    return None


def parse_reuse(optimize_dir: Path, audit_report: Path | None) -> dict[str, ReuseSignals]:
    signals: dict[str, ReuseSignals] = {}
    for key, fname in REUSE_FILES.items():
        if key == "99_risk":
            target = find_risk_file(optimize_dir)
        else:
            target = optimize_dir / fname
            if not target.exists():
                target = None
        if target is None or not target.exists():
            continue
        text = _read(target)
        sig = ReuseSignals(file=str(target))
        sig.red_markers = len(RED_REGEX.findall(text))
        sig.orange_markers = len(ORANGE_REGEX.findall(text))
        match = SCORE_REGEX.search(text)
        if match:
            sig.score = int(match.group(1))
        for line in text.splitlines():
            if RED_REGEX.search(line) or ORANGE_REGEX.search(line):
                stripped = line.strip()
                if stripped:
                    sig.warnings.append(stripped[:200])
        sig.excerpt = "\n".join(text.splitlines()[:8])
        signals[key] = sig
    if audit_report and audit_report.exists():
        text = _read(audit_report)
        sig = ReuseSignals(file=str(audit_report))
        sig.red_markers = len(RED_REGEX.findall(text))
        sig.orange_markers = len(ORANGE_REGEX.findall(text))
        match = SCORE_REGEX.search(text)
        if match:
            sig.score = int(match.group(1))
        for line in text.splitlines():
            if RED_REGEX.search(line) or ORANGE_REGEX.search(line):
                stripped = line.strip()
                if stripped:
                    sig.warnings.append(stripped[:200])
        sig.excerpt = "\n".join(text.splitlines()[:8])
        signals["audit_report"] = sig
    return signals


def extract_dont_rules(matrix_path: Path) -> list[str]:
    text = _read(matrix_path)
    if not text:
        return []
    lines = text.splitlines()
    inside = False
    rules: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if any(stripped.startswith(h) for h in DONT_SECTION_HEADERS):
            inside = True
            continue
        if inside and stripped.startswith("## ") and not any(stripped.startswith(h) for h in DONT_SECTION_HEADERS):
            inside = False
            continue
        if inside and stripped:
            m = re.match(r"^\s*[-*\d.]+\s*[\"„']?([^\"\"'\n]{3,200})", line)
            if m:
                rule = m.group(1).strip().rstrip("\"\"'.,")
                if len(rule) >= 3 and rule.lower() not in ("don't", "dont", "zákazy", "zakazy"):
                    rules.append(rule)
    seen = set()
    deduped = []
    for r in rules:
        key = r.lower()[:60]
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped


def stem_pattern(rule: str) -> re.Pattern:
    tokens = re.findall(r"\b[\w]{4,}\b", rule, flags=re.UNICODE)
    if not tokens:
        return re.compile(re.escape(rule), re.IGNORECASE)
    stems = []
    for tok in tokens[:5]:
        stem = tok[:max(4, len(tok) - 2)]
        stems.append(re.escape(stem))
    pat = r"\b" + r"\w*\b.{0,40}?\b".join(stems) + r"\w*\b"
    return re.compile(pat, re.IGNORECASE | re.UNICODE)


def dont_grep(folder: Path, rules: list[str]) -> list[DontViolation]:
    violations: list[DontViolation] = []
    for md in folder.glob("*.md"):
        text = _read(md)
        if not text:
            continue
        lines = text.splitlines()
        for rule in rules:
            pat = stem_pattern(rule)
            for i, line in enumerate(lines):
                if pat.search(line):
                    ctx_start = max(0, i - 2)
                    ctx_end = min(len(lines), i + 3)
                    ctx = "\n".join(lines[ctx_start:ctx_end])
                    violations.append(
                        DontViolation(
                            rule=rule[:120],
                            file=md.name,
                            line_no=i + 1,
                            line=line.strip()[:200],
                            context=ctx[:600],
                        )
                    )
    return violations


def auto_detect_cross(folder: Path) -> Path | None:
    parent = folder.parent
    current_name = folder.name
    candidates = [d for d in parent.iterdir() if d.is_dir() and d.name != current_name and d.name.startswith("optimize_output")]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for cand in candidates:
        if cand.stat().st_mtime < folder.stat().st_mtime:
            return cand
    return None


def crosscheck(folder: Path, prev: Path) -> list[CrosscheckIssue]:
    issues: list[CrosscheckIssue] = []
    curr_files = {f.name.replace("_F13", "").replace("_optimized", ""): f for f in folder.glob("*.md")}
    prev_files = {f.name.replace("_F13", "").replace("_optimized", ""): f for f in prev.glob("*.md")}

    common = set(curr_files.keys()) & set(prev_files.keys())
    for key in sorted(common):
        curr_text = _read(curr_files[key])
        prev_text = _read(prev_files[key])
        curr_petit = _extract_petit(curr_text)
        prev_petit = _extract_petit(prev_text)
        if prev_petit and curr_petit and prev_petit[:300] != curr_petit[:300]:
            issues.append(
                CrosscheckIssue(
                    kind="petit_diff",
                    description=f"Petit změněn v {curr_files[key].name}",
                    prev_excerpt=prev_petit[:300],
                    curr_excerpt=curr_petit[:300],
                )
            )

    for field_name, regex in (
        ("datum", re.compile(r"\b(\d{1,2}\.\s*\d{1,2}\.\s*20\d{2})\b")),
        ("dny_izolace", re.compile(r"(\d+)\s*dn[íů]\s*izolace", re.IGNORECASE)),
        ("sp_zn", re.compile(r"\b(\d+\s*P\s*\d+/\d+)\b", re.IGNORECASE)),
    ):
        curr_vals = set()
        prev_vals = set()
        for f in curr_files.values():
            curr_vals.update(regex.findall(_read(f)))
        for f in prev_files.values():
            prev_vals.update(regex.findall(_read(f)))
        only_prev = prev_vals - curr_vals
        only_curr = curr_vals - prev_vals
        if only_prev and only_curr:
            issues.append(
                CrosscheckIssue(
                    kind=f"{field_name}_drift",
                    description=f"{field_name}: prev unique={list(only_prev)[:3]}, curr unique={list(only_curr)[:3]}",
                )
            )
    return issues


def _extract_petit(text: str) -> str:
    lines = text.splitlines()
    out = []
    capture = 0
    for line in lines:
        if PETIT_REGEX.search(line):
            capture = 8
        if capture > 0:
            out.append(line)
            capture -= 1
    return "\n".join(out)


def render_verdict(reuse: dict, dont_v: list, cross_i: list, strict: bool, folder: Path) -> Verdict:
    blocking: list[str] = []
    warnings: list[str] = []
    next_steps: list[str] = []

    if dont_v:
        blocking.append(f"DON'T violations: {len(dont_v)} (hard-fail)")
        for v in dont_v[:3]:
            blocking.append(f"  - {v.rule!r} v {v.file}:{v.line_no}")
        next_steps.append("Opravit DON'T violations před F1X.4 capsule")

    risk = reuse.get("99_risk")
    if risk and risk.red_markers > 0:
        blocking.append(f"Risk RED markers: {risk.red_markers} v {Path(risk.file).name}")
        next_steps.append("Re-evaluate RED rizika nebo dokumentovat mitigaci")

    audit = reuse.get("audit_report")
    if audit and audit.score is not None and audit.score < 80:
        blocking.append(f"Audit score < 80: {audit.score}")
        next_steps.append("Re-run optimize a audit, score >= 80 vyžadováno")

    optim = reuse.get("94_optim_report")
    if optim and optim.score is not None and optim.score < 80:
        blocking.append(f"Optimize score < 80: {optim.score}")

    preflight = reuse.get("98_preflight")
    if preflight and preflight.red_markers > 3:
        blocking.append(f"Capsule blockers > 3 ({preflight.red_markers})")
        next_steps.append("Vyřešit capsule blockery (98_preflight) před F1X.4")

    petit_conflicts = [i for i in cross_i if i.kind == "petit_diff"]
    if petit_conflicts:
        blocking.append(f"Petit konflikt s předchozí dávkou ({len(petit_conflicts)})")
        next_steps.append("Ověřit zda změna petitu je záměrná, jinak revertovat")

    for key, sig in reuse.items():
        if sig.orange_markers > 0:
            warnings.append(f"{key}: {sig.orange_markers} ORANGE/WARN markerů")

    for issue in cross_i:
        if issue.kind != "petit_diff":
            warnings.append(f"Cross-check {issue.kind}: {issue.description}")

    if blocking:
        verdict_value = "NO_GO"
        rec = f"NO_GO — {len(blocking)} blocker(ů). Opravit před F1X.4 capsule."
    elif warnings or strict:
        verdict_value = "CONDITIONAL_GO" if not strict or not warnings else "NO_GO"
        if verdict_value == "CONDITIONAL_GO":
            rec = f"CONDITIONAL_GO — {len(warnings)} warning(ů). Opravit a re-run pro GO."
        else:
            rec = f"NO_GO (strict) — {len(warnings)} warning(ů) blokuje strict GO."
    else:
        verdict_value = "GO"
        rec = "GO — všechny checky OK. Připraveno pro F1X.4 capsule + Tom approval."

    if not next_steps:
        if verdict_value == "GO":
            next_steps.append("Pokračovat F1X.4 capsule build (locks-workflow F10.4 T002)")
        elif verdict_value == "CONDITIONAL_GO":
            next_steps.append("Opravit warnings → re-run total_analysis")

    scores = {
        "reuse_aggregated": {
            k: {"score": v.score, "red": v.red_markers, "orange": v.orange_markers}
            for k, v in reuse.items()
        },
        "dont_violations": {"count": len(dont_v), "status": "OK" if not dont_v else "FAIL"},
        "crosscheck": {"conflicts": len(cross_i), "status": "OK" if not cross_i else "WARN"},
    }

    return Verdict(
        verdict=verdict_value,
        timestamp=_dt.datetime.now().isoformat(timespec="seconds"),
        folder=str(folder),
        scores=scores,
        blocking_issues=blocking,
        warnings=warnings,
        next_steps=next_steps,
        recommendation=rec,
    )


def render_master_report(verdict: Verdict, reuse: dict, dont_v: list, cross_i: list) -> str:
    lines = [
        "# TOTAL ANALYSIS REPORT",
        "",
        f"**Verdict:** {verdict.verdict}",
        f"**Timestamp:** {verdict.timestamp}",
        f"**Folder:** {verdict.folder}",
        "",
        "## Doporučení",
        "",
        verdict.recommendation,
        "",
        "## Blocking issues",
        "",
    ]
    if verdict.blocking_issues:
        for b in verdict.blocking_issues:
            lines.append(f"- {b}")
    else:
        lines.append("(žádné)")
    lines += ["", "## Warnings", ""]
    if verdict.warnings:
        for w in verdict.warnings:
            lines.append(f"- {w}")
    else:
        lines.append("(žádné)")
    lines += ["", "## Next steps", ""]
    for s in verdict.next_steps:
        lines.append(f"- {s}")
    lines += ["", "## Reuse signály", ""]
    for key, sig in reuse.items():
        lines.append(f"### {key}")
        lines.append(f"- file: {Path(sig.file).name}")
        lines.append(f"- score: {sig.score}")
        lines.append(f"- RED markers: {sig.red_markers} | ORANGE: {sig.orange_markers}")
        lines.append("")
    lines += ["## DON'T violations summary", ""]
    if dont_v:
        lines.append(f"Total: **{len(dont_v)}** violations (hard-fail).")
        for v in dont_v[:10]:
            lines.append(f"- `{v.rule}` v {v.file}:{v.line_no} → {v.line}")
        if len(dont_v) > 10:
            lines.append(f"... ({len(dont_v) - 10} dalších v 03_dont_violations.md)")
    else:
        lines.append("Žádné violations. ✅")
    lines += ["", "## Cross-check summary", ""]
    if cross_i:
        for issue in cross_i:
            lines.append(f"- **{issue.kind}**: {issue.description}")
    else:
        lines.append("(žádné konflikty / cross-check neproveden)")
    return "\n".join(lines) + "\n"


def render_dont_md(violations: list[DontViolation]) -> str:
    lines = ["# DON'T violations", "", f"Total: {len(violations)}", ""]
    for v in violations:
        lines += [
            f"## {v.file}:{v.line_no}",
            f"**Rule:** `{v.rule}`",
            "",
            "```",
            v.context,
            "```",
            "",
        ]
    return "\n".join(lines) + "\n"


def render_cross_md(issues: list[CrosscheckIssue]) -> str:
    lines = ["# Cross-check report", "", f"Total issues: {len(issues)}", ""]
    for i in issues:
        lines += [
            f"## {i.kind}",
            i.description,
            "",
        ]
        if i.prev_excerpt:
            lines += ["**Předchozí:**", "```", i.prev_excerpt, "```", ""]
        if i.curr_excerpt:
            lines += ["**Aktuální:**", "```", i.curr_excerpt, "```", ""]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Lean total analysis pre-flight audit.")
    p.add_argument("--folder", required=True, type=Path)
    p.add_argument("--matrix", required=True, type=Path)
    p.add_argument("--prehled", required=True, type=Path)
    p.add_argument("--optimize-dir", type=Path, default=None)
    p.add_argument("--audit-report", type=Path, default=None)
    p.add_argument("--cross", type=Path, default=None)
    p.add_argument("--mode", choices=("full", "quick"), default="full")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--no-reuse", action="store_true")
    args = p.parse_args(argv)

    folder = args.folder.resolve()
    if not folder.exists():
        print(f"FATAL: folder neexistuje: {folder}", file=sys.stderr)
        return 2
    if not args.matrix.exists():
        print(f"FATAL: matrix neexistuje: {args.matrix}", file=sys.stderr)
        return 2

    optimize_dir = args.optimize_dir
    if optimize_dir is None and not args.no_reuse:
        guess = folder.parent / "optimize_output_F11"
        optimize_dir = guess if guess.exists() else folder

    audit_report = args.audit_report or (find_audit_report(folder.parent) if not args.no_reuse else None)

    output = args.output or (folder.parent / f"total_analysis_{_dt.datetime.now().strftime('%Y-%m-%d_%H%M')}")
    output.mkdir(parents=True, exist_ok=True)

    reuse: dict[str, ReuseSignals] = {}
    if not args.no_reuse and optimize_dir and optimize_dir.exists():
        reuse = parse_reuse(optimize_dir, audit_report)

    rules = extract_dont_rules(args.matrix)
    dont_v = dont_grep(folder, rules) if rules else []

    cross_i: list[CrosscheckIssue] = []
    if args.mode == "full":
        cross = args.cross or auto_detect_cross(folder)
        if cross and cross.exists():
            cross_i = crosscheck(folder, cross)

    verdict = render_verdict(reuse, dont_v, cross_i, args.strict, folder)

    (output / "TOTAL_ANALYSIS_REPORT.md").write_text(
        render_master_report(verdict, reuse, dont_v, cross_i), encoding="utf-8"
    )
    (output / "go_no_go.json").write_text(
        json.dumps(asdict(verdict), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "03_dont_violations.md").write_text(render_dont_md(dont_v), encoding="utf-8")
    if args.mode == "full":
        (output / "05_crosscheck.md").write_text(render_cross_md(cross_i), encoding="utf-8")
    (output / "reuse_signals.json").write_text(
        json.dumps({k: asdict(v) for k, v in reuse.items()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"VERDICT: {verdict.verdict}")
    print(f"  blocking: {len(verdict.blocking_issues)}")
    print(f"  warnings: {len(verdict.warnings)}")
    print(f"  output: {output}")
    print(f"  recommendation: {verdict.recommendation}")
    return 0 if verdict.verdict in ("GO", "CONDITIONAL_GO") else 1


if __name__ == "__main__":
    sys.exit(main())
