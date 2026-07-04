from rest_framework import serializers


class AnimeSerializer(serializers.Serializer):
    anime_id = serializers.IntegerField()
    name     = serializers.CharField()
    genre    = serializers.CharField()
    type     = serializers.CharField()
    episodes = serializers.FloatField()
    rating   = serializers.FloatField(allow_null=True)