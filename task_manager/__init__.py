from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo

from task_manager import settings
from task_manager.celery_worker import celery

mongo = PyMongo()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)
    mongo.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error="Resource not found"), 404

    from task_manager.users.routes import users
    from task_manager.tasks.routes import tasks
    from swagger.routes import swagger

    app.register_blueprint(users)
    app.register_blueprint(tasks)
    app.register_blueprint(swagger, url_prefix='/swagger')

    return app


app = create_app()
