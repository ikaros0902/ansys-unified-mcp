"""verification_report.md: everything needed to judge one run without opening any other file."""
from __future__ import annotations

from pathlib import Path

from .util import UM_PER_MIL, fmt


def write(path: Path, ctx: dict) -> None:
    L = []
    a = L.append
    ok = ctx["overall_ok"]
    a(f"# Verification report - {ctx['project']} / {ctx['vendor']}")
    a("")
    a(f"Result: **{'PASS' if ok else 'FAIL'}**  ")
    a(f"Run: `{ctx['run_name']}`  ")
    a(f"Tool: ODB Modifying Tool {ctx['tool_version']} (pcb-thermal-warpage), config `{ctx['config_path']}`")
    a("")
    a("## Acceptance checks")
    a("")
    a("| Check | Result |")
    a("|---|---|")
    for name, passed, detail in ctx["checks"]:
        a(f"| {name} | {'PASS' if passed else 'FAIL'} - {detail} |")
    a("")
    a("## Inputs")
    a("")
    a("| Input | File (relative to the project JSON) | SHA-256 before = after |")
    a("|---|---|---|")
    for role, p, same in ctx["inputs"]:
        a(f"| {role} | `{p}` | {'unchanged' if same else 'CHANGED'} |")
    a("")
    a("## Decisions and notes")
    a("")
    for lvl, txt in ctx["notes"]:
        a(f"- **{lvl}** {txt}")
    if ctx["answers"]:
        a("")
        a("Answers used (from the project JSON or asked in this run):")
        a("")
        for k, v in ctx["answers"].items():
            a(f"- `{k}` = `{v}`")
    a("")
    a("## Stackup written into the ODB++")
    a("")
    a("| # | ODB++ layer | Kind | Material | Thickness mil | um | Vendor ODB++ | Design name | Vendor rows | Design rows | Coverage |")
    a("|---|---|---|---|---|---|---|---|---|---|---|")
    for x in ctx["layers"]:
        cov = "" if x.coverage is None else f"{x.coverage:.3f}"
        a(f"| {x.seq} | {x.odb_name} | {x.kind if x.kind == 'copper' else x.diel_type} | {x.material} | "
          f"{fmt(x.thickness_mil, 4)} | {fmt(x.thickness_mil * UM_PER_MIL, 3)} | {x.vendor_odb_name} | "
          f"{x.ecad_name} | {x.vendor_row} | {x.design_row} | {cov} |")
    tot = sum(x.thickness_mil for x in ctx["layers"])
    a("")
    a(f"Total thickness {tot:.3f} mil = {tot * UM_PER_MIL:.3f} um = {tot * 0.0254:.4f} mm")
    b = ctx["build"]
    a("")
    a("## ODB++ changes")
    a("")
    a(f"- Kept step `{ctx['step']}`; removed steps: {', '.join(b.dropped_steps) or 'none'}")
    a(f"- Removed {len(b.dropped_layers)} non-copper layers: {', '.join(b.dropped_layers)}")
    a(f"- Profile before: ({b.profile_before_in[0]:.4f}, {b.profile_before_in[1]:.4f}) .. "
      f"({b.profile_before_in[2]:.4f}, {b.profile_before_in[3]:.4f}) in; shift "
      f"({b.shift_in[0] * 25.4:+.3f}, {b.shift_in[1] * 25.4:+.3f}) mm; after: "
      f"({b.profile_after_in[0]:.4f}, {b.profile_after_in[1]:.4f}) .. "
      f"({b.profile_after_in[2]:.4f}, {b.profile_after_in[3]:.4f}) in")
    a("")
    cov = ctx.get("coverage")
    if cov:
        a("## Copper coverage")
        a("")
        a(f"Resolution {ctx['coverage_res']} mil, regions: {', '.join(ctx['coverage_regions'])}. "
          f"Coverage written to the CSV files uses region `{ctx['coverage_region_for_outputs']}`.")
        a("")
        a("| Layer | " + " | ".join(ctx["coverage_regions"]) + " | Unrendered | Approximated |")
        a("|---|" + "---|" * len(ctx["coverage_regions"]) + "---|---|")
        for name, r in cov.items():
            vals = " | ".join(f"{r['regions'][k]['coverage']:.4f}" if r['regions'].get(k) else "-"
                              for k in ctx["coverage_regions"])
            un = ", ".join(f"{k} {v}" for k, v in r["unrendered"].items()) or "-"
            ap = ", ".join(f"{k} {v}" for k, v in r["approx"].items()) or "-"
            a(f"| {name} | {vals} | {un} | {ap} |")
        a("")
    a("## ANSYS translator check")
    for v in ctx["verify"]:
        a("")
        a(f"### {v.version}: {'PASS' if v.ok else 'FAIL'}")
        a("")
        a(f"- {v.summary}, {v.seconds:.0f} s, log `{v.log_file}`")
        a(f"- EDB total {v.total_edb:.3f} mil vs stackup {v.total_ref:.3f} mil; layer mismatches {v.mismatches}")
        if v.materials:
            a(f"- Materials in the EDB: {', '.join(v.materials)}")
        for e in v.errors:
            a(f"- ERROR: {e}")
        if v.warnings:
            a("- Warnings by kind:")
            for k, n in sorted(v.warnings.items(), key=lambda x: -x[1]):
                a(f"  - {n} x {k}")
        bad = [r for r in v.rows if not r["ok"]]
        if bad:
            a("")
            a("| # | expected | EDB |")
            a("|---|---|---|")
            for r in bad[:40]:
                a(f"| {r['seq']} | {r['expected_name']} {r['expected_type']} {r['expected_mil']:.3f} | "
                  f"{r['edb_name']} {r['edb_type']} {r['edb_mil']} |")
    a("")
    a("## Output files")
    a("")
    for p, desc in ctx["outputs"]:
        a(f"- `{p}` - {desc}")
    a("")
    a("Next steps: docs/07_downstream_workflow.md (LayerBuilder -> Workbench -> External Data -> "
      "Trace Mapping -> v6 equivalent material -> BGA shadow -> supports -> thermal -> Z export -> leveling).")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
