import os
from flask import Flask, send_from_directory

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'mmirror.sqlite'),
    )

    if (test_config is None):
        app.config.from_pyfile('config.py', silent = True)
    else:
        app.config.from_mapping(test_config)


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Testing Route
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
           'favicon.ico') 

    # Database
    from . import db
    db.init_app(app)

    # Auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)
    
    # Console blueprint
    from . import console
    app.register_blueprint(console.bp)
    app.add_url_rule('/', endpoint = 'index')

    return(app)
