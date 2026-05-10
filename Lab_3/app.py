from flask import Flask, render_template, request
import math

app = Flask(__name__)


def solve_quadratic(a, b, c):
    if a == 0:
        return None, "Коэффициент a не может быть равен нулю"

    d = b ** 2 - 4 * a * c

    if d > 0:
        x1 = (-b + math.sqrt(d)) / (2 * a)
        x2 = (-b - math.sqrt(d)) / (2 * a)
        return {
            "discriminant": round(d, 4),
            "type": "two_roots",
            "x1": round(x1, 4),
            "x2": round(x2, 4)
        }, None

    elif d == 0:
        x = -b / (2 * a)
        return {
            "discriminant": 0,
            "type": "one_root",
            "x": round(x, 4)
        }, None

    else:
        real = round(-b / (2 * a), 4)
        imag = round(math.sqrt(-d) / (2 * a), 4)
        return {
            "discriminant": round(d, 4),
            "type": "complex_roots",
            "x1": f"{real} + {imag}i",
            "x2": f"{real} - {imag}i"
        }, None


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    a_val = ""
    b_val = ""
    c_val = ""

    if request.method == "POST":
        try:
            a_val = request.form.get("a", "")
            b_val = request.form.get("b", "")
            c_val = request.form.get("c", "")

            a = float(a_val)
            b = float(b_val)
            c = float(c_val)

            result, error = solve_quadratic(a, b, c)

        except ValueError:
            error = "Пожалуйста, введите числовые значения."

    return render_template(
        "index.html",
        result=result,
        error=error,
        a=a_val,
        b=b_val,
        c=c_val
    )

if __name__ == "__main__":
    app.run(debug=True)

