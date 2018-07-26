from django.views.generic.base import ContextMixin, View
from django.http import JsonResponse


class JSONView(ContextMixin, View):
    def get_json_object(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.get_json_object(context), **response_kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
