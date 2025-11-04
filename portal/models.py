from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, tr_number, name, role, password=None):
        if not tr_number:
            raise ValueError("TR number is required")
        user = self.model(tr_number=tr_number, name=name, role=role)
        user.set_password(password or tr_number)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    ROLE_CHOICES = [('student', 'Student'), ('admin', 'Admin')]
    tr_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'tr_number'
    REQUIRED_FIELDS = ['name', 'role']

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.role})"


class Book(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# portal/models.py
# class PageEntry(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     from_page = models.PositiveIntegerField()
#     to_page = models.PositiveIntegerField()
#     revised = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.user.tr_number} - {self.book.name} ({self.from_page}-{self.to_page})"

class PageEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    from_page = models.PositiveIntegerField()
    to_page = models.PositiveIntegerField()
    revised = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'book', 'from_page', 'to_page')


class Group(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    shared_pages = models.TextField()  # e.g. "5-10,12-15"

class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    extra_pages = models.TextField(blank=True)
