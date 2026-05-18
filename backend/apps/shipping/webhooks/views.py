from django.http import JsonResponse
from django.views import View


class CourierWebhookView(View):

    def post(self, request, *args, **kwargs):

        payload = request.body

        return JsonResponse({
            "success": True,
        })