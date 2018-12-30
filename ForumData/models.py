from django.db import models

# Create your models here.
class ResultDB(models.Model):
    課程代碼 = models.CharField(primary_key=True, max_length=45)

    class Meta:
        db_table = 'course_total_data_v2'