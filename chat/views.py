import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView

from chat.models import Message
from functools import wraps
from django.core.exceptions import PermissionDenied

def ajax_login_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


class New(CreateView):
    http_method_names = ["post"]
    model = Message


class History(View):
    def _get_edited(self, qs):
        if not qs.exists():
            return []
        for i in range(qs):
            qs[i] = Message.objects.filter(
                msg_id=qs[i].msg_id).order_by("-index")[0]
        return qs

    @login_required
    def get(self, req):
        from_dt = req.GET.get("from_dt")
        to_dt = req.GET.get("to_dt")

        msgs = Message.objects.filter(
            deleted=False, index=0
        ).order_by("-dt")

        if from_dt:
            msgs.filter(dt__gte=from_dt)
        if to_dt:
            msgs.filter(dt__lte=to_dt)

        return JsonResponse(self._get_edited(msgs), safe=False)


class Edit(View):
    @login_required
    def post(self, req):
        query = json.loads(req.get("query", None))

        if query.get("method", None) not in ("edit", "delete"):
            return JsonResponse({"error": "invalid method for endpoint"})
        elif query.get("msg_id", None):
            return JsonResponse({"error": "no msg_id provided"})

        msg_qs = Message.objects.filter(
            msg_id=query["msg_id"]).order_by("-index")

        if not msg_qs[0].user == req.user or not req.user.is_staff():
            return JsonResponse({"error": "no message with that msg_id"})
        elif not (msg_qs[0].user == req.user) or \
                not req.user.is_staff:
            return JsonResponse({"error": "message is not yours to edit"})
        elif msg_qs[0].deleted:
            return JsonResponse({"error": "message deleted"})

        Message(msg_id=query["msg_id"], index=msg_qs[0].index+1,
                body=query["body"], user=msg_qs[0].user,
                edit_user=req.user).save()

        return JsonResponse({"success": True})




