__author__ = 'michel'

from rest_framework.views import APIView

class CombaApiView(APIView):

    def get(self,request, format=None):
        args = request.GET
        return self.getResponse(request, args)

    def post(self,request, format=None):
        if request.data:
            args = request.data
        else:
            args = request.POST
        return self.getResponse(request, args)

    def getResponse(self, request, args):
        pass

