from django.db import models

class KeywordRanking(models.Model):
    keyword = models.CharField(max_length=255)
    ranking_position = models.PositiveIntegerField()
    impressions = models.PositiveIntegerField(default=0)
    ctr = models.FloatField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]