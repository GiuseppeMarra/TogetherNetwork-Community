# -*- coding=utf-8 -*-
from django.forms import ModelForm
from .models import Profile

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            #"owner",
            "city",
            "bio",
            "interests_and_skilss",
            "mission",
            "personal_website_url",
            "twitter_url",
            "facebook_url",
        ]