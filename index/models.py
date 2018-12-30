from django.db import models

# Create your models here.

class OpenEduDB(models.Model):
    id = models.CharField(primary_key=True, max_length=45)
    date_joined = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'auth_user'


class ResultDB(models.Model):
    課程代碼 = models.CharField(primary_key=True, max_length=45)

    class Meta:
        managed = False
        db_table = 'course_total_data_v2'

