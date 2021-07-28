from flaskblog import CreateApp

app = CreateApp()

if __name__ == '__main__':
    app.run(debug=True)