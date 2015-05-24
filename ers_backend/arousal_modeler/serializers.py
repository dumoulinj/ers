from rest_framework import serializers
from arousal_modeler.models import Arousal

class ArousalSerializer(serializers.HyperlinkedModelSerializer):
    def transform_arousal_curve(self, obj):
        return obj.arousal_curve
    def transform_arousal_crests(self, obj):
        return obj.arousal_crests
    def transform_arousal_troughs(self, obj):
        return obj.arousal_troughs
    def transform_arousal_diff(self, obj):
        return obj.arousal_diff
    def transform_arousal_partitions(self, obj):
        return obj.arousal_partitions
    def transform_used_features(self, obj):
        return obj.used_features

    def to_representation(self,instance):
        ret = super(ArousalSerializer,self).to_representation(instance)
        ret['arousal_curve'] = eval(ret['arousal_curve'])
        ret['arousal_crests'] = eval(ret['arousal_crests'])
        ret['arousal_troughs'] = eval(ret['arousal_troughs'])
        ret['arousal_diff'] = eval(ret['arousal_diff'])
        ret['arousal_partitions'] = eval(ret['arousal_partitions'])
        ret['used_features'] = eval(ret['used_features'])
        return ret

    class Meta:
        model = Arousal
