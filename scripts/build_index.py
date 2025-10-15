#!/usr/bin/env python3
import argparse, json, pathlib
from jinja2 import Template

TEMPLATE = """<!doctype html>
<html lang="ja"><meta charset="utf-8">
<title>mjai-reviewer reports</title>
<style>
body{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem}
h1{margin-bottom:.2rem}
.card{border:1px solid #ddd;border-radius:10px;padding:1rem;margin:.8rem 0}
small{color:#666}
table{width:100%;border-collapse:collapse}
th,td{border-bottom:1px solid #eee;padding:.4rem .2rem;text-align:right}
th:first-child,td:first-child{text-align:left}
.rate{font-weight:bold}
</style>
<h1>mjai-reviewer reports</h1>
<p><small>自動生成: GitHub Actions</small></p>

{% for month in months %}
<div class="card">
  <h2>{{ month.name }}</h2>
  {% if month.summary %}
  <p>対局数: {{ month.summary.games }} /
     総手数: {{ month.summary.total_decisions }} /
     不一致: {{ month.summary.mismatches }} /
     不一致率: <span class="rate">{{ "%.1f%%" % (month.summary.mismatch_rate*100) }}</span></p>
  {% endif %}
  <table>
    <tr><th>対局ID</th><th>手数</th><th>不一致</th><th>不一致率</th></tr>
    {% for g in month.games %}
    <tr>
      <td><a href="{{ month.name }}/{{ g.id }}/index.html">{{ g.id }}</a></td>
      <td>{{ g.total }}</td>
      <td>{{ g.mism }}</td>
      <td>{{ "%.1f%%" % (g.rate*100) }}</td>
    </tr>
    {% endfor %}
  </table>
</div>
{% endfor %}
</html>
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    args = ap.parse_args()
    root = pathlib.Path(args.root)

    months = []
    for mdir in sorted([p for p in root.iterdir() if p.is_dir() and p.name.isdigit()]):
        summary = None
        sfile = mdir / "summary.json"
        if sfile.exists():
            summary = json.loads(sfile.read_text(encoding="utf-8"))
        games = []
        for gdir in sorted([p for p in mdir.iterdir() if p.is_dir()]):
            idx = gdir / "index.html"
            if idx.exists():
                games.append({"id": gdir.name, "total": 0, "mism": 0, "rate": 0.0})
        if summary:
            # summary.by_game を合流
            stats_by_id = {r["game_id"]: r for r in summary.get("by_game", [])}
            for g in games:
                st = stats_by_id.get(g["id"])
                if st:
                    g["total"] = st["total_decisions"]
                    g["mism"]  = st["mismatches"]
                    g["rate"]  = st["mismatch_rate"]
        months.append({"name": mdir.name, "summary": summary, "games": games})

    html = Template(TEMPLATE).render(months=months)
    (root / "index.html").write_text(html, encoding="utf-8")

if __name__ == "__main__":
    main()
