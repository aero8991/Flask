from flask_blog import create_app

app = create_app()
print(app.config)

if __name__ == '__main__':
    app.run(debug=True)