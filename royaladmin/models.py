from django.db import models


class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('AUTO', 'Automatic'),
        ('MANUAL', 'Manual'),
    ]

    image = models.ImageField(upload_to='car_images/')
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    automation = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

