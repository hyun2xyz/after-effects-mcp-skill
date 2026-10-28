#!/usr/bin/env python3
"""Run one trusted, request-specific JSX body in After Effects and print a compact result.

No MCP server or bridge panel: macOS sends a DoScriptFile Apple event, Windows uses
AfterFX.exe -r. The JSX body is a function body; `return` a small plain summary.
"""
import argparse
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import time
import uuid

sys.dont_write_bytecode = True

MAC_SCRIPT = '''on run argv
    set targetApp to item 1 of argv
    set jsxFile to POSIX file (item 2 of argv)
    using terms from application id "com.adobe.AfterEffects.application"
        tell application targetApp
            DoScriptFile jsxFile
        end tell
    end using terms from
end run'''

# ExtendScript has no JSON object; encode plain values only and cap depth so an
# accidental AE object return cannot flood the result.
WRAPPER = r'''(function () {
    var out = new File(%(result)s);
    function enc(v, d) {
        if (v === null || v === undefined) return "null";
        if (typeof v === "string") return '"' + v.replace(/\\/g,"\\\\").replace(/"/g,'\\"').replace(/[\x00-\x1f\u2028\u2029]/g,function(c){return "\\u"+("0000"+c.charCodeAt(0).toString(16)).slice(-4);}) + '"';
        if (typeof v === "number") return isFinite(v) ? String(v) : "null";
        if (typeof v === "boolean") return v ? "true" : "false";
        if (typeof v === "function") return '"[function]"';
        if (d > 6) return '"[depth]"';
        var parts = [], i, k;
        if (v instanceof Array) {for (i = 0; i < v.length; i++) parts.push(enc(v[i], d + 1)); return "[" + parts.join(",") + "]";}
        if (v.constructor !== Object) return enc(String(v), d);
        for (k in v) if (v.hasOwnProperty(k)) parts.push(enc(k, d) + ":" + enc(v[k], d + 1));
        return "{" + parts.join(",") + "}";
    }
    var r = {status: "ok", ae_version: app.version, description: %(description)s};
    var undo = %(undo)s;
    if (undo) app.beginUndoGroup(%(description)s);
    try {
        r.value = (function () {
%(body)s
        })();
    } catch (e) {
        r.status = "error";
        r.error = String(e) + (e.line ? " (body line " + (e.line - %(offset)d) + ")" : "");
    } finally {
        if (undo) app.endUndoGroup();
    }
    out.encoding = "UTF-8";
    if (out.open("w")) {out.write(enc(r, 0)); out.close();}
})();
'''


def find_app(explicit=None):
    configured = explicit or os.environ.get("AE_APP", "").strip()
    if configured:
        choices = [Path(configured).expanduser().resolve()]
    elif sys.platform == "darwin":
        choices = list(Path("/Applications").glob("Adobe After Effects */Adobe After Effects *.app"))
    elif sys.platform == "win32":
        root = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Adobe"
        choices = list(root.glob("Adobe After Effects */Support Files/AfterFX.exe"))
    else:
        raise ValueError("Native execution supports macOS and Windows only")
    valid = []
    for path in choices:
        if sys.platform == "darwin":
            info = path / "Contents/Info.plist"
            if info.is_file():
                with info.open("rb") as f:
                    if plistlib.load(f).get("CFBundleIdentifier") == "com.adobe.AfterEffects.application":
                        valid.append(path)
        elif path.is_file() and path.name.lower() == "afterfx.exe":
            valid.append(path)
    if len(valid) != 1:
        raise ValueError("Specify exactly one AE app with --app or AE_APP; candidates: " + str([str(x) for x in valid]))
    return valid[0]


def build(body, description, undo, result):
    head = WRAPPER.split("%(body)s")[0] % {"result": json.dumps(str(result)), "description": json.dumps(description), "undo": "true" if undo else "false"}
    offset = head.count("\n")
    return WRAPPER % {
        "result": json.dumps(str(result)),
        "description": json.dumps(description),
        "undo": "true" if undo else "false",
        "body": body,
        "offset": offset,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("jsx", nargs="?", type=Path, help="file holding the JSX function body")
    src.add_argument("--code", help="inline JSX function body, e.g. 'return app.version;'")
    parser.add_argument("--description", required=True, help="human-readable purpose, also the undo label")
    parser.add_argument("--undo", action="store_true", help="wrap a mutation in one undo group")
    parser.add_argument("--app", help="AE .app (macOS) or AfterFX.exe (Windows) when several are installed")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--max-chars", type=int, default=4000, help="truncate printed result; full JSON stays in the run folder")
    parser.add_argument("--dry-run", action="store_true", help="write run.jsx and print its path without calling AE")
    args = parser.parse_args(argv)

    body = args.code if args.code is not None else args.jsx.read_text(encoding="utf-8")
    run_dir = Path(tempfile.gettempdir()) / "ae-jsx-runs" / uuid.uuid4().hex
    run_dir.mkdir(parents=True)
    result = run_dir / "result.json"
    jsx = run_dir / "run.jsx"
    jsx.write_text(build(body, args.description, args.undo, result), encoding="utf-8")
    if args.dry_run:
        print(json.dumps({"status": "prepared", "jsx": str(jsx)}, ensure_ascii=False))
        return 0

    app = find_app(args.app)
    if sys.platform == "darwin":
        cmd = ["/usr/bin/osascript", "-e", MAC_SCRIPT, str(app), str(jsx)]
    else:
        cmd = [str(app), "-r", str(jsx)]
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(json.dumps({"status": "unknown", "error": "AE call timed out; a modal dialog may be open. Do not resend; check the AE window.", "run": str(run_dir)}, ensure_ascii=False))
        return 2
    if proc.returncode:
        print(json.dumps({"status": "failed", "error": proc.stderr.strip()[:500], "run": str(run_dir)}, ensure_ascii=False))
        return 1
    # Windows -r returns before the script finishes; wait on the local file only.
    while not result.exists() and time.monotonic() - started < args.timeout:
        time.sleep(0.1)
    if not result.exists():
        print(json.dumps({"status": "unknown", "error": "No result file. Enable AE 'Allow Scripts to Write Files and Access Network', or a dialog is blocking AE. Do not resend.", "run": str(run_dir)}, ensure_ascii=False))
        return 2
    text = result.read_text(encoding="utf-8")
    status = json.loads(text).get("status")
    if len(text) > args.max_chars:
        text = text[: args.max_chars] + '…(truncated; full result: ' + str(result) + ')'
    print(text)
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
