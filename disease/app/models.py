from django.db import models

# Create your models here.
class PredictionHistory(models.Model):
    symptoms = models.JSONField() 
    extra_symptoms = models.TextField(blank=True, null=True)
    predicted_disease = models.CharField(max_length=100)
    predicted_at = models.DateTimeField(auto_now_add=True)