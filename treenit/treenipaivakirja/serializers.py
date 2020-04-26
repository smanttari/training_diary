from rest_framework import serializers
from treenipaivakirja.models import Harjoitus


class HarjoitusSerializer(serializers.ModelSerializer):
    laji = serializers.StringRelatedField(many=False)
    user = serializers.StringRelatedField(many=False)

    class Meta:
        model = Harjoitus
        fields = [
            'id',
            'pvm',
            'vuorokaudenaika',
            'laji',
            'kesto_h',
            'kesto_min',
            'keskisyke',
            'matka',
            'vauhti_km_h',
            'vauhti_min_km',
            'nousu',
            'kalorit',
            'tuntuma',
            'kommentti',
            'user'
        ]
            
