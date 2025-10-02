from django.db import models
import uuid


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    complete_name = models.CharField(max_length=255, null=False, blank=False)
    registration_number = models.CharField(
        max_length=20, unique=True, null=False, blank=False
    )
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    course = models.CharField(max_length=100, null=False, blank=False)
    entry_date = models.DateField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "students"
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["complete_name"]

    def __str__(self):
        return self.complete_name


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    complete_name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    area_of_activity = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teachers"
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        ordering = ["complete_name"]

    def __str__(self):
        return self.complete_name


class Discipline(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discipline_name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    workload = models.IntegerField(null=False, blank=False)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="disciplines"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "disciplines"
        verbose_name = "Discipline"
        verbose_name_plural = "Disciplines"
        ordering = ["discipline_name"]

    def __str__(self):
        return self.discipline_name


class ClassRoomDiscipline(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    classroom = models.ForeignKey(
        "Classroom", on_delete=models.CASCADE, related_name="classroom_disciplines"
    )
    discipline = models.ForeignKey(
        Discipline, on_delete=models.CASCADE, related_name="discipline_classrooms"
    )
    workload = models.IntegerField(null=False, blank=False)
    class_schedule = models.CharField(max_length=100, null=False, blank=False)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="teacher_classrooms"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "classroom_disciplines"
        verbose_name = "ClassRoomDiscipline"
        verbose_name_plural = "ClassRoomDisciplines"
        unique_together = ("classroom", "discipline")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.classroom.class_name} - {self.discipline.discipline_name}"


class Classroom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_name = models.CharField(max_length=100, null=False, blank=False)
    discipline = models.ManyToManyField(
        Discipline, through="ClassRoomDiscipline", related_name="classrooms"
    )
    school_period = models.CharField(max_length=50, null=False, blank=False)
    students = models.ManyToManyField(Student, related_name="classrooms", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "classrooms"
        verbose_name = "Classroom"
        verbose_name_plural = "Classrooms"
        ordering = ["class_name"]

    def __str__(self):
        return self.class_name


class ActivityType(models.TextChoices):
    EXAM = "EXAM", "Prova"
    HOMEWORK = "HOMEWORK", "Trabalho"
    PROJECT = "PROJECT", "Projeto"
    SEMINAR = "SEMINAR", "Seminário"
    EXERCISE = "EXERCISE", "Exercício"


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, null=False, blank=False)
    type = models.CharField(
        max_length=20, choices=ActivityType.choices, null=False, blank=False
    )
    delivery_date = models.DateField(null=False, blank=False)
    value = models.DecimalField(max_digits=5, decimal_places=2, null=False, blank=False)

    # Agora a atividade está ligada a uma disciplina específica da turma
    classroom_discipline = models.ForeignKey(
        ClassRoomDiscipline, on_delete=models.CASCADE, related_name="activities"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activities"
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        ordering = ["-delivery_date"]

    def __str__(self):
        return f"{self.title} ({self.classroom_discipline.classroom.class_name} - {self.classroom_discipline.discipline.discipline_name})"


class DeliveryStatus(models.TextChoices):
    PENDING = "PENDING", "Pendente"
    SUBMITTED = "SUBMITTED", "Entregue"
    GRADED = "GRADED", "Avaliado"
    LATE = "LATE", "Atrasado"


class ActivitySubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="submissions"
    )
    submission_date = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="graded_submissions"
    )
    status = models.CharField(
        max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING
    )
    value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activity_submissions"
        verbose_name = "Activity Submission"
        verbose_name_plural = "Activity Submissions"
        ordering = ["-submission_date"]
        unique_together = ("activity", "student")

    def save(self, *args, **kwargs):
        if not self.teacher_id and self.activity:
            self.teacher = self.activity.classroom_discipline.teacher
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.activity.title} - {self.student.complete_name}"


class PresenceStatus(models.TextChoices):
    PRESENT = "PRESENT", "Presente"
    ABSENT = "ABSENT", "Ausente"
    EXCUSED = "EXCUSED", "Justificado"


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name="attendances"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="attendances"
    )
    date = models.DateField(null=False, blank=False)
    status = models.CharField(
        max_length=20, choices=PresenceStatus.choices, default=PresenceStatus.PRESENT
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="attendances"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendances"
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        ordering = ["-date"]
        unique_together = ("classroom", "student", "date")

    def __str__(self):
        return (
            f"{self.classroom.class_name} - {self.student.complete_name} - {self.date}"
        )
