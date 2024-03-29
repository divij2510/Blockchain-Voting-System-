# voting_app/serializers.py
from rest_framework import serializers
from .models import Candidate, Vote
import datetime

class CandidateSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = ['w3id', 'name', 'vote_count']

    def get_vote_count(self, obj):
        return obj.vote_count

class VoteSerializer(serializers.ModelSerializer):
    candidate = CandidateSerializer(read_only=True)
    formatted_timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = ['block_id', 'unique_id', 'candidate', 'timestamp', 'formatted_timestamp']

    def get_formatted_timestamp(self, obj):
        dt = datetime.datetime.fromtimestamp(obj.timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')