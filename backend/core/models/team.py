from django.db import models

class Team(models.Model):
    RESPONSIBILITY_CHOICES = [
        ("gövde", "Gövde"),
        ("kanat", "Kanat"),
        ("aviyonik", "Aviyonik"),
        ("motor", "Motor"),
        ("montaj", "Montaj"),
        ("kuyruk", "Kuyruk"),
    ]

    name = models.CharField(max_length=50, unique=True)
    responsibility = models.CharField(max_length=20, choices=RESPONSIBILITY_CHOICES)

    def __str__(self):
        return self.name
