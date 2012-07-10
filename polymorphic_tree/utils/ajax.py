"""
Generic Ajax functionality
"""
from django.http import HttpResponse
from django.utils import simplejson


class JsonResponse(HttpResponse):
    """
    A convenient HttpResponse class, which encodes the response in JSON format.
    """
    def __init__(self, jsondata, status=200):
        self.jsondata = jsondata
        jsonstr = simplejson.dumps(jsondata)
        super(JsonResponse, self).__init__(jsonstr, content_type='application/javascript', status=status)
