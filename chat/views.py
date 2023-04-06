import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models import Q, Value, F, CharField, Func
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from chat.models import Message, UserPing, Command, Report
from functools import wraps
from django.core.exceptions import PermissionDenied


class Chat(LoginRequiredMixin, View):
    def get(self, req):
        cmds = Command.objects.all()
        return render(req, "chat.html", context={"commands": cmds})


class ReportView(LoginRequiredMixin, View):
    def get(self, req, msg_pk=None):
        Report(msg=Message.objects.get(pk=msg_pk),
               user=self.request.user)
        return redirect("/success?msg=You have successfully reported the message.")

class MessageMore(LoginRequiredMixin, ListView):
    model = Message
    template_name = "messagemore.html"

    def get_queryset(self):
        if self.kwargs["msg_id"]:
            return super().get_queryset().filter(
                msg_id=self.kwargs["msg_id"]).annotate(
                username=F("user__username"),
                current_user=Q(user=self.request.user),
                formatted_time=Func(
                    F('dt'),
                    Value('DD/MM/YY HH24:MI:SS'),
                    function='to_char',
                    output_field=CharField()
                )).values("pk", "current_user", "body", "username", "formatted_time", 'msg_id')
        else:
            raise Http404


class Function(LoginRequiredMixin, View):
    def post(self, req, tag=None):
        command = get_object_or_404(Command, tag=tag)
        cmd_obj = {}
        for cmd_input in [x.tag for x in command.inputs]:
            cmd_obj[cmd_input] = req.POST.get(cmd_input)
            if not cmd_obj[cmd_input]:
                return JsonResponse({"error": "missing input"})
        try:
            msg_id = Message.objects.all().order_by("-msg_id")[0].msg_id + 1
        except IndexError:
            msg_id = 0

        Message(body=exec(command.function_code, **cmd_obj),
                user=req.user, msg_id=msg_id).save()

        return JsonResponse({"success": "true"})


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
    def _get_edited(self, msg_list):
        if not len(msg_list)>0:
            return []
        out = []
        for i in range(len(msg_list)):
            out.append(Message.objects.filter(
                msg_id=msg_list[i]['msg_id']).order_by("-index").annotate(
                username=F("user__username"), formatted_time=Func(
                    F('dt'),
                    Value('HH24:MI:SS'),
                    function='to_char',
                    output_field=CharField()
                )).values("body", "username", "formatted_time", 'msg_id')[0])
        
        return out

    def get(self, req):
        from_dt = req.GET.get("from_dt")
        to_dt = req.GET.get("to_dt")

        msgs = Message.objects.filter(deleted=False,
                index=0).order_by("-dt").values("msg_id")[:100][::-1]

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


class EditView(LoginRequiredMixin, DetailView):
    template_name = "edit.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Message.objects.filter(user=self.request.user)
        else:
            return Message.objects.none()


class Edit(LoginRequiredMixin, View):
    def post(self, req):
        if req.POST.get("method", None) not in ("edit", "delete"):
            return JsonResponse({"error": "invalid method for endpoint"})
        elif not req.POST.get("msg_id", None):
            return JsonResponse({"error": "no msg_id provided"})

        msg_qs = Message.objects.filter(
            msg_id=req.POST["msg_id"]).order_by("-index")

        if not msg_qs[0].user == req.user or not req.user.is_staff:
            return JsonResponse({"error": "no message with that msg_id"})
        elif not (msg_qs[0].user == req.user) or \
                not req.user.is_staff:
            return JsonResponse({"error": "message is not yours to edit"})
        elif msg_qs[0].deleted:
            return JsonResponse({"error": "message deleted"})

        if req.POST["method"] == "delete":
            for msg in msg_qs:
                msg.deleted = True
                msg.save()
            return JsonResponse({"success": "true"})
        
        Message(msg_id=req.POST["msg_id"], index=msg_qs[0].index+1,
                body=req.POST["body"], user=msg_qs[0].user,
                edit_user=req.user).save()

        return JsonResponse({"success": True})
