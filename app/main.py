####
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
####


from flask import Flask, render_template, request, redirect, url_for
from statistics import mean, stdev
import tabula
import pandas
import os, json, boto3

app = Flask(__name__)


# Listen for GET requests to yourdomain.com
@app.route("/")
def index():
  # Show the HTML page:
  return render_template('index.html')

# Listen for POST requests to yourdomain.com/submit/
@app.route("/submit/", methods = ["POST"])
def submit_form():
  # Collect the data posted from the HTML form in index.html:
  pdf_url = request.form["pdf-url"]
  pdf_path = request.form["pdf_path"]
  roll = request.form["roll"]

  # Provide some procedure for storing the new details

  if len(pdf_url) > 0:
      pdf_path = pdf_url

  errors = ""
  df = None
  try:
      df = tabula.read_pdf(pdf_path, pandas_options={'header': None}, pages='all')
  except:
      errors += "<p>{!r} is not a valid path for the pdf.</p>\n".format(pdf_path)
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
              <p>{errors}</p>
              <p><a href="/">Click here to calculate again</a>
          </body>
      </html>
  '''.format(errors=errors)


# Listen for GET requests to yourdomain.com/sign_s3/
#
# Please see https://gist.github.com/RyanBalfanz/f07d827a4818fda0db81 for an example using
# Python 3 for this view.
@app.route('/sign-s3/')
def sign_s3():
  # Load necessary information into the application
  S3_BUCKET = os.environ.get('S3_BUCKET')

  # Load required data from the request
  file_name = request.args.get('file-name')
  file_type = request.args.get('file-type')

  # Initialise the S3 client
  s3 = boto3.client('s3')

  # Generate and return the presigned URL
  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )

  # Return the data to the client
  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })
