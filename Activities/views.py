# -*- coding=utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import Activity

from .forms import ActivityForm
from .forms import CommentForm

from datetime import datetime
from datetime import timedelta

def activities_view(request):
    """
        List of activities from 3 hours ago to the infinite time of the universe
    """
    activities = Activity.objects.filter(
                    time__gte=( datetime.now()-timedelta(hours=3) 
                ) ).order_by('time')

    return render_to_response("activities.html", 
        {"activities": activities }, 
        context_instance=RequestContext(request))

@login_required
def single_activity_view(request, activity_pk):
    """
        Show the single Activity view
    """
    activity = get_object_or_404(Activity, pk=activity_pk)
    comments = Comment.objects.filter(activity=activity)
    return render_to_response("activity.html", 
        { "activity": activity, "comments": comments }, 
        context_instance=RequestContext(request))

@login_required
def edit_activity_view(request, activity_pk=None):
    """
        Create/edit a new activity
    """
    activity = None
    form_title = "New Activity"
    if activity_pk:
        form_title = "Edit Activity"
        activity = get_object_or_404(Activity, pk=activity_pk)

        if not activity.owner.username == request.user.username:
            #TODO: Message to say that he can't edit this object.
            return redirect(activity)

    if request.method == 'POST':
        formset = ActivityForm(request.POST, request.FILES, instance=activity)
        if formset.is_valid():
            activity_obj = formset.save(commit=False)
            
            activity_obj.owner = request.user
            activity_obj.save()
            return redirect(activity_obj)
    else:
        formset = ActivityForm(instance=activity)
        
    return render_to_response("form.html", {
        "form": formset,
        "title": form_title
    }, context_instance=RequestContext(request))

@login_required
def join_activity(request, activity_pk):
    """
        This function will join the user to the activity.
    """
    activity = get_object_or_404(Activity, pk=activity_pk)
    if not request.user in activity.attendees.all():
        activity.attendees.add(request.user)
        activity.save()
    return redirect(activity)

@login_required
def leave_activity(request, activity_pk):
    """
        This function will leave the user from the activity.
    """
    activity = get_object_or_404(Activity, pk=activity_pk)
    if request.user in activity.attendees.all():
        activity.attendees.remove(request.user)
        activity.save()
    return redirect(activity)

@login_required
def delete_activity(request, activity_pk):
    """
        This function will delete an activity
    """
    activity = get_object_or_404(Activity, pk=activity_pk)
    if request.user == activity.owner:
        activity.delete()
        return redirect(activities_view)
    return redirect(activity)

@login_required
def new_activity_comment(request, activity_pk=None):
    """
        Create a new comment
    """

    activity = get_object_or_404(Activity, pk=activity_pk)
    if request.method == 'POST':
        formset = CommentForm(request.POST, request.FILES)
        if formset.is_valid():
            comment_obj = formset.save(commit=False)
            comment_obj.owner = request.user
            comment_obj.activity = activity
            comment_obj.save()
            # Send Email to owner.
            messages.success(request, 'Your comment has been saved')
            return redirect(single_activity_view, activity_pk=activity_pk)
    else:
        formset = CommentForm()

    return render_to_response("form.html", {
        "form": formset,
        "title": "New Comment"
    }, context_instance=RequestContext(request))

