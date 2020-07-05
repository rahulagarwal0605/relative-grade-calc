from flask import Flask, request
from statistics import mean, stdev
import tabula
import pandas

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def grade_calc():
    errors = ""
    if request.method == "POST":
        df = None
        roll = None
        try:
            df = tabula.read_pdf(request.form["pdf_path"], pandas_options={'header': None}, pages='all')
        except:
            errors += "<p>{!r} is not a valid path for the pdf.</p>\n".format(request.form["pdf_path"])
        roll = request.form["roll"]
        if df is not None and roll is not None:
            df = pandas.concat(df)

            row_len = len(df.iloc[0])

            series_marks = df[row_len - 1]

            lst = series_marks.tolist()

            lst1 = list()
            for i in lst:
                try:
                    lst1.append(float(i))
                except:
                    None

            avg = mean(lst1)
            std = stdev(lst1)

            series_roll = df[0]

            df1 = df[df[0].str.contains(roll)]
            if len(df1) > 0:
                marks = float(df1[row_len - 1])
                a = avg
                b = std
                d = marks

                if d >= (a + (1.5 * b)):
                    result="Your Grade is A"
                elif (a + (1.5 * b)) > d >= (a + b):
                    result="Your Grade is AB"
                elif (a + b) > d >= (a + (0.5 * b)):
                    result="Your Grade is B"
                elif (a + (0.5 * b)) > d >= a:
                    result="Your Grade is BC"
                elif a > d >= (a - (0.5 * b)):
                    result="Your Grade is C"
                elif (a - (0.5 * b)) > d >= (a - b):
                    result="Your Grade is CD"
                elif (a - b) > d >= (a - (1.5 * b)):
                    result="Your Grade is D"
                elif (a - (1.5 * b)) > d:
                    result="Your Grade is F"
            else:
                result='Your roll no. is not in the list'
            return '''
                <html>
                    <body>
                        <p>{result}</p>
                        <p><a href="/">Click here to calculate again</a>
                    </body>
                </html>
            '''.format(result=result)

    return '''
        <html>
            <body>
                {errors}
                <form method="post" action=".">
                    <p>Enter valid path of pdf (URL/file):</p>
                    <p><input name="pdf_path" /></p>
                    <p>Enter your Roll No.</p>
                    <p><input name="roll" /></p>
                    <p><input type="submit" value="Submit" /></p>
                </form>
            </body>
        </html>
    '''.format(errors=errors)
