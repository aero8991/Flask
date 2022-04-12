from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_blog.config import Config, ProductionConfig, DevelopmentConfig, TestingConfig


#database connection
db = SQLAlchemy()

#login manager
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

#email
mail = Mail()

#initialise app
def create_app(config_class=Config):
    app = Flask(__name__)
    
    if app.config['ENV'] == 'production':
        app.config.from_object(ProductionConfig)
    elif app.config['ENV'] == 'testing': 
        app.config.from_object(TestingConfig)    
    else:
        app.config.from_object(DevelopmentConfig)
    
    
    #initialize plugins
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    
    from flask_blog.users.routes import users
    from flask_blog.posts.routes import posts   
    from flask_blog.main.routes import main
    from flask_blog.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    
    return app

    