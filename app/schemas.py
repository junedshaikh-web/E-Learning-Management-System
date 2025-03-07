from app import ma
from app.models import Course, User, Enrollment

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        fields = ("id", "name", "email", "role", "contact", "bio")

class InstructorSchema(UserSchema):
    class Meta(UserSchema.Meta):
        fields = ("id", "name", "email", "bio", "contact")  

class CourseSchema(ma.SQLAlchemyAutoSchema):
    instructor = ma.Nested(UserSchema, only=["id", "name", "email"])  

    class Meta:
        model = Course
        load_instance = True
        fields = ("id", "title", "description", "instructor") 

class EnrollmentSchema(ma.SQLAlchemyAutoSchema):
    student = ma.Nested(UserSchema, only=["id", "name", "email", "contact"])  
    course = ma.Nested(CourseSchema) 

    class Meta:
        model = Enrollment
        load_instance = True
        fields = ("id", "student", "course", "enrolled_at")