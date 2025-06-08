from flask import Flask, render_template, request
import pandas as pd
from analyze_competitors import analyze_keyword  # <- You’ll create this function

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    table_html = None

    if request.method == "POST":
        keyword = request.form["keyword"]

        # Run analysis
        df = analyze_keyword(keyword)

        # Convert DataFrame to HTML table
        table_html = df.to_html(classes="data", header="true", index=False)

    return render_template("index.html", table=table_html)

if __name__ == "__main__":
    app.run(debug=True)
