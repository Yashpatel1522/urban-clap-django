from rest_framework.renderers import JSONRenderer
import json


class CustomJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_status = (
            renderer_context["response"].status_code
            if renderer_context["response"]
            else None
        )

        custom_response = {
            "status": (
                "success" if response_status and response_status < 400 else "error"
            ),
            "context": data,
            "system_status": response_status,
        }

        return super().render(custom_response, accepted_media_type, renderer_context)
