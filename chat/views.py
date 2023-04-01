import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models import Q, Value, F, CharField, Func
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView

from chat.models import Message, UserPing, Command
from functools import wraps
from django.core.exceptions import PermissionDenied


class Chat(View):
    def get(self, req):
        cmds = Command.objects.all()
        return render(req, "chat.html", context={"commands": cmds})


class New(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, req):
        if not req.POST.get("body"):
            return JsonResponse({"error": "no body"})
        try:
            msg_id = Message.objects.all().order_by("-msg_id")[0].msg_id + 1
        except IndexError:
            msg_id = 0
        Message(msg_id=msg_id, user=req.user,
                body=req.POST["body"]).save()
        return JsonResponse({"success": True})


class History(LoginRequiredMixin, View):
    def _get_edited(self, qs):
        if not qs.exists():
            return []
        out = []
        for i in range(qs.count()):
            out.append(dict(Message.objects.filter(
                msg_id=qs[i]['msg_id']).order_by("-index").annotate(
                username=F("user__username"), formatted_time=Func(
    F('dt'),
    Value('HH24:MI:SS'),
    function='to_char',
    output_field=CharField()
  )).values("body", "username", "formatted_time", 'msg_id')[0]))
        return out

    def get(self, req):
        from_dt = req.GET.get("from_dt")
        to_dt = req.GET.get("to_dt")

        msgs = Message.objects.filter(deleted=False,
                index=0).order_by("dt").values("msg_id")[0:100]
        print(msgs)

        if from_dt:
            msgs.filter(dt__gte=from_dt)
        if to_dt:
            msgs.filter(dt__lte=to_dt)

        UserPing(user=req.user).save()
        users = UserPing.objects.filter(
            dt__gte=timezone.now()-timedelta(
            minutes=1)).annotate(
            username=F("user__username"),
            formatted_time=Func(
                F('dt'),
                Value('HH:MM:SS'),
                function='to_char',
                output_field=CharField()
            )).order_by("-username", "dt").distinct("username"
                        ).values("formatted_time", "username")

        users = [dict(i) for i in users]

        return JsonResponse({"messages": self._get_edited(msgs),
                             "users": users}, safe=False)


class Edit(LoginRequiredMixin, View):
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




