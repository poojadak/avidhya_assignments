from flask import Flask, jsonify

tasks = {}


def create_app():
    app = Flask(__name__)

    from .routes import bp
    app.register_blueprint(bp)

    @app.errorhandler(400)
    @app.errorhandler(404)
    def http_error(e):
        return jsonify({"error": e.description}), e.code

    return app
