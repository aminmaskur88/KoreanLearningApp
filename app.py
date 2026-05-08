from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'korean-learning-secret'
    app.config['DATABASE'] = os.path.join(os.getcwd(), 'database.db')

    from routes.views import views_bp
    from routes.api import api_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
