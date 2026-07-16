from app.schemas.lesson import Lesson


class LessonService:

    def __init__(self):
        self.lessons = [
            Lesson(
                id=1,
                sign="A",
                description="Closed fist with thumb resting on the side.",
                meaning="Represents the letter A.",
                image="assets/asl/A.jpg",
                difficulty="Beginner"
            ),
            Lesson(
                id=2,
                sign="B",
                description="Open hand with fingers together and thumb across the palm.",
                meaning="Represents the letter B.",
                image="assets/asl/B.jpg",
                difficulty="Beginner"
            ),
            Lesson(
                id=3,
                sign="C",
                description="Hand curved into the shape of the letter C.",
                meaning="Represents the letter C.",
                image="assets/asl/C.jpg",
                difficulty="Beginner"
            ),
            Lesson(
                id=4,
                sign="D",
                description="Index finger points upward while other fingers touch the thumb.",
                meaning="Represents the letter D.",
                image="assets/asl/D.jpg",
                difficulty="Beginner"
            ),
            Lesson(
                id=5,
                sign="E",
                description="Fingers curl down to touch the thumb.",
                meaning="Represents the letter E.",
                image="assets/asl/E.jpg",
                difficulty="Beginner"
            ),
        ]

    def get_all_lessons(self):
        return self.lessons

    def get_lesson_by_id(self, lesson_id: int):
        for lesson in self.lessons:
            if lesson.id == lesson_id:
                return lesson
        return None