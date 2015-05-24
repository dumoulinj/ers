from rest_framework.response import Response
from rest_framework.views import APIView
import time
from dataset_manager.enums import ComputingStateType


class TestServerViewSet(APIView):
    def get(self, request, format=None):
        try:
            time.sleep(2)
            response = {"state": ComputingStateType.SUCCESS}
        except:
            response = {"state": ComputingStateType.FAILED}
        return Response(response)