from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
from fpdf import FPDF

app = Flask(__name__)

df = pd.read_excel("../data/ecommerce_sales_dataset.xlsx")
df['order_date'] = pd.to_datetime(df['order_date'])

# -----------------------------
# Dashboard Page
# -----------------------------
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# -----------------------------
# KPI API
# -----------------------------
@app.route("/api/kpis")
def kpis():
    total_revenue = df['total_price'].sum()
    total_orders = df['order_id'].nunique()
    avg_order_value = total_revenue / total_orders

    return jsonify({
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_order_value": round(avg_order_value, 2)
    })

# -----------------------------
# Category Sales API
# -----------------------------
@app.route("/api/category_sales")
def category_sales():
    data = df.groupby('product_category')['total_price'].sum()
    return jsonify(data.to_dict())

# -----------------------------
# Report Generation API
# -----------------------------
@app.route("/api/generate_report")
def generate_report():
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    filtered = df[
        (df['order_date'] >= start) &
        (df['order_date'] <= end)
    ]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Sales Report", ln=True)
    pdf.cell(0, 10, f"Total Revenue: {filtered['total_price'].sum():.2f}", ln=True)
    pdf.cell(0, 10, f"Total Orders: {filtered['order_id'].nunique()}", ln=True)

    file_name = "sales_report.pdf"
    pdf.output(file_name)

    return send_file(file_name, as_attachment=True)

# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)

