from django.db import models

class Voter(models.Model):
    email_id = models.CharField(max_length=50)

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    w3id = models.BigIntegerField(null=True)
    def __str__(self):
        return self.name

    @property
    def vote_count(self):
        return self.votes.count()

class Vote(models.Model):
    block_id = models.BigIntegerField()
    unique_id = models.CharField(max_length=50)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.BigIntegerField()