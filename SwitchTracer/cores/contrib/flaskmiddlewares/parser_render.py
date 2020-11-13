import json

from flask import make_response

from SwitchTracer.universal.exceptions import ContentTypeErrors


class UniBase(object):

    ENCODING = "utf-8"
    CONTENT_TYPE = None


class ParserBase(UniBase):

    def __init__(self, request):
        self.request = request
        self.kwargs = dict()

    def __call__(self, mod="parse", **kwargs):
        self.kwargs = kwargs
        if self.request.headers.get("Content-Type") != self.CONTENT_TYPE:
            raise ContentTypeErrors("Wrong content type from data")
        return self.parse(self.request.get_data())

    def parse(self, data):
        raise NotImplementedError


class JsonParser(ParserBase):

    CONTENT_TYPE = "application/json"

    def parse(self, data: bytes):
        return json.loads(data.decode(self.kwargs.get("encoding", self.ENCODING)))


class RenderBase(UniBase):

    def __init__(self, **data):
        self.data = data
        self.kwargs = dict()

    def __call__(self, **kwargs):
        self.kwargs = kwargs
        return self.render()

    def render(self):
        raise NotImplementedError


class JsonRender(RenderBase):

    CONTENT_TYPE = "application/json"

    def render(self):
        try:
            data = json.dumps(self.data)
        except Exception as e:
            raise ContentTypeErrors(e)
        resp = make_response(data)
        resp.status = self.kwargs.get("status", "200 OK")
        resp.headers["Content-Type"] = self.CONTENT_TYPE
        return resp
