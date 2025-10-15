#!/usr/bin/env python3
import argparse, json, pathlib, re
from bs4 import BeautifulSoup

def parse_report_html(path: pathlib.Path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")

    total_decisions = 0
    mismatches = 0

    # ヒューリスティック：
    # - 行・手番テーブルの中でAI推奨と自分の選択が「一致/不一致」を示す箇所を拾う
    # - "mismatch", "difference", "best", "あなたの打牌" などのテキストを緩く探索
    text = soup.get_text("\n", strip=True).lower()

    # 総手数（雑に「巡」や turn カウント）— フォールバックで <tr> 数など
    total_decisions = max(len(re.findall(r"\bturn\b|\b巡\b", text)), 1)

    # 不一致らしき表現を拾う
    patterns = [
        r"\bmismatch\b", r"\bdifference\b", r"ai.+best.+you", r"あなた.+(誤り|ミス)",
        r"最善.+あなた.+(一致せず|不一致)"
    ]
    for pat in patterns:
        mismatches += len(re.findall(pat, text))

    # 正規化（過剰カウントのガード）
    mismatches = min(mismatches, total_decisions)

    return {
        "total_decisions": int(total_decisions),
        "mismatches": int(mismatches),
        "mismatch_rate": (mismatches / total_decisions) if total_decisions else 0.0
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="indir", required=True)
    ap.add_argument("--out", dest="outfile", required=True)
    args = ap.parse_args()

    month_dir = pathlib.Path(args.indir)
    rows = []
    for idx_html in month_dir.glob("**/index.html"):
        gid = idx_html.parent.name
        stats = parse_report_html(idx_html)
        rows.append({"game_id": gid, **stats})

    # 月次サマリ
    total = sum(r["total_decisions"] for r in rows)
    mism = sum(r["mismatches"] for r in rows)
    summary = {
        "month": month_dir.name,
        "games": len(rows),
        "total_decisions": total,
        "mismatches": mism,
        "mismatch_rate": (mism / total) if total else 0.0,
        "by_game": rows
    }

    pathlib.Path(args.outfile).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

if __name__ == "__main__":
    main()
