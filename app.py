import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session,send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from modules.data_loader import load_dataset, get_dataset_info
from modules.data_cleaning import clean_dataset, get_cleaning_summary
from modules.statistics import calculate_statistics
from modules.correlation import get_strong_correlations
from modules.outlier import get_outlier_summary
from modules.visualization import (
    create_histogram,
    create_bar_chart,
    create_boxplot,
    create_correlation_heatmap,
    create_pie_chart
)
from modules.insights import generate_insights
from modules.report_generator import generate_report, format_report

load_dotenv()
app = Flask(__name__)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

def get_db_connection():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    return connection
def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            filename VARCHAR(255) NOT NULL,
            file_type VARCHAR(20) NOT NULL,
            file_size BIGINT NOT NULL
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT id, name, password FROM users WHERE email = %s",
                (email,)
            )

            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user and check_password_hash(user[2], password):

                session["user_id"] = user[0]
                session["user_name"] = user[1]
                session["user_email"] = email

                flash("Login successful!", "success")

                return redirect(url_for("dashboard"))

            else:

                flash("Invalid email or password.", "error")

                return redirect(url_for("login"))

        except Exception as error:

            return f"<h2>Login Failed</h2><p>{error}</p>"

    return render_template("login.html")
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please login to access the dashboard.", "error")
        return redirect(url_for("login"))

    datasets = []

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, filename, file_type, file_size
            FROM datasets
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (session["user_id"],)
        )

        datasets = cursor.fetchall()

        cursor.close()
        connection.close()

    except Exception as error:
        flash("Unable to load your datasets.", "error")

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name"),
        user_email=session.get("user_email"),
        datasets=datasets
    )


@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out successfully.", "success")

    return redirect(url_for("home"))
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user_id" not in session:
        flash("Please login to upload a dataset.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":

        if "dataset" not in request.files:
            flash("Please select a dataset.", "error")
            return redirect(url_for("upload"))

        file = request.files["dataset"]

        if file.filename == "":
            flash("Please select a dataset.", "error")
            return redirect(url_for("upload"))

        extension = file.filename.rsplit(".", 1)[-1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            flash("Only CSV and Excel files are allowed.", "error")
            return redirect(url_for("upload"))

        filename = secure_filename(file.filename)

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(file_path)

        file_size = os.path.getsize(file_path)

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO datasets
                (user_id, filename, file_type, file_size)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    session["user_id"],
                    filename,
                    extension,
                    file_size
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            flash(
                "Dataset uploaded successfully!",
                "success"
            )

            return redirect(url_for("dashboard"))

        except Exception as error:

            return f"<h2>Upload Failed</h2><p>{error}</p>"

    return render_template("upload.html")

@app.route("/analyze/<filename>")
def analyze(filename):

    if "user_id" not in session:
        flash("Please login to analyze a dataset.", "error")
        return redirect(url_for("login"))

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if not os.path.exists(file_path):
        flash("Dataset file not found.", "error")
        return redirect(url_for("dashboard"))

    try:
        # 1. Load dataset
        df = load_dataset(file_path)

        # 2. Dataset information
        dataset_info = get_dataset_info(df)

        # 3. Clean dataset
        cleaned_df = clean_dataset(df)

        # 4. Cleaning summary
        cleaning_summary = get_cleaning_summary(
            df,
            cleaned_df
        )

        # 5. Statistical analysis
        statistics = calculate_statistics(cleaned_df)

        # 6. Strong correlations
        correlations = get_strong_correlations(
            cleaned_df
        )

        # 7. Outlier detection
        outliers = get_outlier_summary(
            cleaned_df
        )

        # 8. Generate insights
        insights = generate_insights(
            cleaned_df,
            statistics,
            correlations,
            outliers
        )

        # 9. Generate final report
        report = generate_report(
            dataset_info,
            statistics,
            correlations,
            outliers,
            insights
        )

                # Create folder for analysis charts
        charts_folder = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "charts"
        )

        os.makedirs(charts_folder, exist_ok=True)

        chart_files = []

        # Get numeric columns
        numeric_columns = cleaned_df.select_dtypes(
            include="number"
        ).columns.tolist()

        # Create Histogram and Boxplot
        for column in numeric_columns:

            safe_column = str(column).replace(" ", "_")

            histogram_path = os.path.join(
                charts_folder,
                f"{filename}_{safe_column}_histogram.png"
            )

            boxplot_path = os.path.join(
                charts_folder,
                f"{filename}_{safe_column}_boxplot.png"
            )

            create_histogram(
                cleaned_df,
                column,
                histogram_path
            )

            create_boxplot(
                cleaned_df,
                column,
                boxplot_path
            )

            chart_files.append({
                "title": f"{column} - Histogram",
                "path": f"/uploads/charts/{filename}_{safe_column}_histogram.png"
            })

            chart_files.append({
                "title": f"{column} - Boxplot",
                "path": f"/uploads/charts/{filename}_{safe_column}_boxplot.png"
            })

        # Create Bar Chart and Pie Chart
        for column in cleaned_df.columns:

            if column not in numeric_columns:

                safe_column = str(column).replace(" ", "_")

                bar_path = os.path.join(
                    charts_folder,
                    f"{filename}_{safe_column}_bar.png"
                )

                pie_path = os.path.join(
                    charts_folder,
                    f"{filename}_{safe_column}_pie.png"
                )

                create_bar_chart(
                    cleaned_df,
                    column,
                    bar_path
                )

                create_pie_chart(
                    cleaned_df,
                    column,
                    pie_path
                )

                chart_files.append({
                    "title": f"{column} - Bar Chart",
                    "path": f"/uploads/charts/{filename}_{safe_column}_bar.png"
                })

                chart_files.append({
                    "title": f"{column} - Pie Chart",
                    "path": f"/uploads/charts/{filename}_{safe_column}_pie.png"
                })

        # Create Correlation Heatmap
        if len(numeric_columns) >= 2:

            heatmap_path = os.path.join(
                charts_folder,
                f"{filename}_correlation_heatmap.png"
            )

            create_correlation_heatmap(
                cleaned_df,
                heatmap_path
            )

            chart_files.append({
                "title": "Correlation Heatmap",
                "path": f"/uploads/charts/{filename}_correlation_heatmap.png"
            })

        return render_template(
            "analysis.html",
            filename=filename,
            dataset_info=dataset_info,
            cleaning_summary=cleaning_summary,
            statistics=statistics,
            correlations=correlations,
            outliers=outliers,
            insights=insights,
            report=report,
            format_report=format_report,
            chart_files=chart_files,
        )

    except Exception as error:
        return f"<h2>Analysis Failed</h2><p>{error}</p>"

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Check whether email already exists
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:
                cursor.close()
                connection.close()

                flash("Email already registered.", "error")
                return redirect(url_for("register"))

            # Securely hash password
            hashed_password = generate_password_hash(password)

            cursor.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
                """,
                (name, email, hashed_password)
            )

            connection.commit()

            cursor.close()
            connection.close()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))

        except Exception as error:
            return f"<h2>Registration Failed</h2><p>{error}</p>"

    return render_template("register.html")
@app.route("/test-db")
def test_db():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return f"<h2>PostgreSQL Connected Successfully!</h2><p>{version}</p>"

    except Exception as error:
        return f"<h2>Database Connection Failed</h2><p>{error}</p>"
@app.route("/check-db")
def check_db():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT current_database();")
        database = cursor.fetchone()[0]

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()

        cursor.close()
        connection.close()

        return f"""
        <h2>Database: {database}</h2>
        <h3>Tables:</h3>
        <pre>{tables}</pre>
        """

    except Exception as error:
        return f"<h2>Database Error</h2><p>{error}</p>"


init_db()


if __name__ == "__main__":
    app.run(debug=True)