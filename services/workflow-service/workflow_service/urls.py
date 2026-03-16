import json

from ariadne import graphql_sync
from django.http import JsonResponse
from django.urls import path

from workflows.schema import schema


def health(_request):
    return JsonResponse({"ok": True})


def graphql_endpoint(request):
    if request.method == "GET":
        return JsonResponse({"status": "ok", "service": "workflow-service"})
    data = json.loads(request.body or "{}")
    success, result = graphql_sync(schema, data, context_value=request)
    return JsonResponse(result, status=200 if success else 400)


urlpatterns = [
    path("health/", health),
    path("graphql/", graphql_endpoint),
]
