from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
   return render_template("helloworld.html")

@app.route("/<name>")
def hi(name):
   return render_template("helloworld.html", userName=name)



curl -s --user 'api:YOUR_API_KEY' \
    https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages \
    -F from='Excited User <mailgun@YOUR_DOMAIN_NAME>' \
    -F to=YOU@YOUR_DOMAIN_NAME \
    -F to=bar@example.com \
    -F subject='Hello' \
    -F text='Testing some Mailgun awesomeness!'
