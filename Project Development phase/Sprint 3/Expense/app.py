from web import createApp

if(__name__=="__main__"):
    app = createApp()
    app.run(host="0.0.0.0",port=int("5000"),debug=True)