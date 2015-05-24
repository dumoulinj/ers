from rest_framework import viewsets
from arousal_modeler.models import Arousal
from arousal_modeler.serializers import ArousalSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


class ArousalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Arousal.objects.all()
    serializer_class = ArousalSerializer
    def retrieve(self, request, pk=None):
        queryset = Arousal.objects.all()
        q = get_object_or_404(queryset,pk=pk)
        try:
            z = int(self.request.QUERY_PARAMS['stride_val'])
            q.arousal_curve = q.arousal_curve[::z]
        except:
            pass
        serializer = ArousalSerializer(q,context={'request': request})
        return Response(serializer.data)