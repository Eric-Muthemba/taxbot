from rest_framework import serializers

class ConversationSerializer(serializers.Serializer):
    channel = serializers.CharField()
    message = serializers.CharField()
    channel_id = serializers.CharField()

    class Meta:
        fields = ("channel","message",'channel_id',)