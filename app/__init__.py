from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from app.config import Config


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)

    from app.routes.main import main
    from app.auth import auth
    from app.routes.courses import course_bp
    from app.routes.students import student_bp
    from app.routes.enrollments import enrollment_bp
    from app.routes.instructors import instructor_bp

    app.register_blueprint(main) 
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(course_bp, url_prefix="/courses")
    app.register_blueprint(student_bp, url_prefix="/students")
    app.register_blueprint(enrollment_bp, url_prefix="/enrollments")
    app.register_blueprint(instructor_bp, url_prefix="/instructors")

    return app
