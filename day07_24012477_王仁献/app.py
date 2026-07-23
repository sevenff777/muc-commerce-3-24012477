from functools import wraps
from pathlib import Path

import pandas as pd
from flask import Flask, flash, jsonify, redirect, render_template, request, Response, session, url_for

from services.data_service import load_dashboard_data
from services.qa_service import answer_question


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
from functools import wraps
from pathlib import Path

import pandas as pd
from flask import Flask, flash, jsonify, redirect, render_template, request, Response, session, url_for

from services.data_service import load_dashboard_data
from services.qa_service import answer_question


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "day07-classroom-demo-key"


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("请先登录后再访问数据看板。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "student" and password == "day07":
            session["username"] = username
            flash("登录成功，欢迎进入电商用户分析系统。", "success")
            return redirect(url_for("dashboard"))
        flash("账号或密码错误。演示账号：student / day07", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("你已安全退出。", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    category = request.args.get("category", "全部")
    dashboard_data = load_dashboard_data(BASE_DIR, category)  # 注意这里完美调用了你的 data_service
    return render_template(
        "dashboard.html",
        username=session["username"],
        selected_category=category,
        category_bar_url=url_for("category_bar_chart", category=category),
        ordered_line_url=url_for("ordered_line_chart", category=category),
        **dashboard_data,  # 你的 metrics, categories, category_rows, insight 都会正常传递
    )


@app.route("/dashboard/category_bar.svg")
@login_required
def category_bar_chart():
    category = request.args.get("category", "全部")
    data_dir = BASE_DIR / "data"
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    labels = category_df["PreferedOrderCat"].tolist()
    values = category_df["用户数"].tolist()
    max_value = max(values) if values else 1
    width = 520
    height = 300
    margin = 40
    bar_width = (width - margin * 2) / len(values)
    bars = []
    for idx, (label, value) in enumerate(zip(labels, values)):
        x = margin + idx * bar_width
        bar_height = int((value / max_value) * (height - margin * 2))
        y = height - margin - bar_height
        fill = "#3A7CBD" if label == category else "#B0CFFF"
        bars.append(
            f'<rect x="{x}" y="{y}" width="{bar_width * 0.8}" height="{bar_height}" fill="{fill}" />'
            f'<text x="{x + bar_width * 0.4}" y="{height - margin + 15}" fill="#333" font-size="12" text-anchor="middle">{label}</text>'
        )
    svg = f"""
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <style>text{{font-family: "Microsoft YaHei", "SimHei", sans-serif;}}</style>
  <text x="{width / 2}" y="24" text-anchor="middle" font-size="18" fill="#333">不同偏好品类用户比较</text>
  {''.join(bars)}
  <line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#999" />
</svg>
"""
    return Response(svg, mimetype="image/svg+xml")


@app.route("/dashboard/ordered_line.svg")
@login_required
def ordered_line_chart():
    category = request.args.get("category", "全部")
    data_dir = BASE_DIR / "data"
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    labels = category_df["PreferedOrderCat"].tolist()
    values = category_df["平均订单数"].tolist()
    max_value = max(values) if values else 1
    width = 520
    height = 300
    margin = 40
    point_distance = (width - margin * 2) / (len(values) - 1 if len(values) > 1 else 1)
    points = []
    lines = []
    for idx, (label, value) in enumerate(zip(labels, values)):
        x = margin + idx * point_distance
        y = height - margin - (value / max_value) * (height - margin * 2)
        points.append((x, y, label, value))
        if idx > 0:
            prev_x, prev_y, _, _ = points[idx - 1]
            lines.append(f'<line x1="{prev_x}" y1="{prev_y}" x2="{x}" y2="{y}" stroke="#3A7CBD" stroke-width="2" />')
    circles = []
    for x, y, label, value in points:
        fill = "#FF7A2D" if label == category else "#3A7CBD"
        circles.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{fill}" />')
        circles.append(f'<text x="{x}" y="{y - 10}" fill="#333" font-size="12" text-anchor="middle">{value:.2f}</text>')
    svg = f"""
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <style>text{{font-family: "Microsoft YaHei", "SimHei", sans-serif;}}</style>
  <text x="{width / 2}" y="24" text-anchor="middle" font-size="18" fill="#333">不同偏好品类平均订单数趋势</text>
  {''.join(lines)}
  {''.join(circles)}
  <line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#999" />
</svg>
"""
    return Response(svg, mimetype="image/svg+xml")


@app.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html", username=session["username"])


@app.route("/api/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"ok": False, "answer": "请输入一个与项目数据有关的问题。"}), 400
    return jsonify({"ok": True, "answer": answer_question(BASE_DIR, question)})


# ==================== 第7天拓展任务A：导出CSV ====================
@app.route("/download")
@login_required
def download_csv():
    category = request.args.get("category", "全部")
    data_dir = BASE_DIR / "data"
    df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    if category != "全部":
        df = df[df["PreferedOrderCat"] == category]
    csv_data = df.to_csv(index=False, encoding="utf-8-sig")
    filename = f"category_analysis_{category}.csv" if category != "全部" else "category_analysis_all.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=False, port=5000)
app.config["SECRET_KEY"] = "day07-classroom-demo-key"


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("请先登录后再访问数据看板。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "student" and password == "day07":
            session["username"] = username
            flash("登录成功，欢迎进入电商用户分析系统。", "success")
            return redirect(url_for("dashboard"))
        flash("账号或密码错误。演示账号：student / day07", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("你已安全退出。", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    category = request.args.get("category", "全部")
    dashboard_data = load_dashboard_data(BASE_DIR, category)
    return render_template(
        "dashboard.html",
        username=session["username"],
        selected_category=category,
        category_bar_url=url_for("category_bar_chart", category=category),
        ordered_line_url=url_for("ordered_line_chart", category=category),
        **dashboard_data,
    )


@app.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html", username=session["username"])


@app.route("/dashboard/category_bar.svg")
@login_required
def category_bar_chart():
    category = request.args.get("category", "全部")
    data_dir = BASE_DIR / "data"
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    labels = category_df["PreferedOrderCat"].tolist()
    values = category_df["用户数"].tolist()
    max_value = max(values) if values else 1
    width = 520
    height = 300
    margin = 40
    bar_width = (width - margin * 2) / len(values)
    bars = []
    for idx, (label, value) in enumerate(zip(labels, values)):
        x = margin + idx * bar_width
        bar_height = int((value / max_value) * (height - margin * 2))
        y = height - margin - bar_height
        fill = "#3A7CBD" if label == category else "#B0CFFF"
        bars.append(
            f'<rect x="{x}" y="{y}" width="{bar_width * 0.8}" height="{bar_height}" fill="{fill}" />'
            f'<text x="{x + bar_width * 0.4}" y="{height - margin + 15}" fill="#333" font-size="12" text-anchor="middle">{label}</text>'
        )
    svg = f"""
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <style>text{{font-family: Arial, sans-serif;}}</style>
  <text x="{width / 2}" y="24" text-anchor="middle" font-size="18" fill="#333">不同偏好品类用户比较</text>
  {''.join(bars)}
  <line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#999" />
</svg>
"""
    return Response(svg, mimetype="image/svg+xml")


@app.route("/dashboard/ordered_line.svg")
@login_required
def ordered_line_chart():
    category = request.args.get("category", "全部")
    data_dir = BASE_DIR / "data"
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    labels = category_df["PreferedOrderCat"].tolist()
    values = category_df["平均订单数"].tolist()
    max_value = max(values) if values else 1
    width = 520
    height = 300
    margin = 40
    point_distance = (width - margin * 2) / (len(values) - 1 if len(values) > 1 else 1)
    points = []
    lines = []
    for idx, (label, value) in enumerate(zip(labels, values)):
        x = margin + idx * point_distance
        y = height - margin - (value / max_value) * (height - margin * 2)
        points.append((x, y, label, value))
        if idx > 0:
            prev_x, prev_y, _, _ = points[idx - 1]
            lines.append(f'<line x1="{prev_x}" y1="{prev_y}" x2="{x}" y2="{y}" stroke="#3A7CBD" stroke-width="2" />')
    circles = []
    for x, y, label, value in points:
        fill = "#FF7A2D" if label == category else "#3A7CBD"
        circles.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{fill}" />')
        circles.append(f'<text x="{x}" y="{y - 10}" fill="#333" font-size="12" text-anchor="middle">{value:.2f}</text>')
    svg = f"""
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <style>text{{font-family: Arial, sans-serif;}}</style>
  <text x="{width / 2}" y="24" text-anchor="middle" font-size="18" fill="#333">不同偏好品类平均订单数趋势</text>
  {''.join(lines)}
  {''.join(circles)}
  <line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#999" />
</svg>
"""
    return Response(svg, mimetype="image/svg+xml")


@app.route("/api/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"ok": False, "answer": "请输入一个与项目数据有关的问题。"}), 400
    return jsonify({"ok": True, "answer": answer_question(BASE_DIR, question)})


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=False, port=5000)
# ==================== 第7天拓展任务A：导出CSV ====================
@app.route("/download")
@login_required
def download_csv():
    category = request.args.get("category", "全部")
    data_dir = BASE_DIR / "data"
    df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    if category != "全部":
        df = df[df["PreferedOrderCat"] == category]
    csv_data = df.to_csv(index=False, encoding="utf-8-sig")
    filename = f"category_analysis_{category}.csv" if category != "全部" else "category_analysis_all.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=False, port=5000)
