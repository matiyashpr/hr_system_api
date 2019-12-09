from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions

from hr_system.models import User, Candidate, Recruiter, Skills


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("user with this email address already exists.")
        return email

    def validate_password(self, value):
        try:
            validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        email = validated_data.pop('email')
        user = User.objects.create(email=email, profile_type=self.context['profile_type'])
        user.set_password(validated_data.pop('password'))
        user.save()
        return user


class CandidateProfileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = ('first_name', 'last_name', 'title', 'about', 'category', 'gender', 'city', 'phone', 'in_search')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = []
        for ctgr in instance.category.get_queryset():
            data['category'].append(ctgr.name)
        data['skills'] = []
        for skill in instance.skills_set.get_queryset():
            skill = SkillsSerializer(skill).data
            del skill['user']
            data['skills'].append(skill)
        return data


class RecruiterProfileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recruiter
        fields = ('first_name', 'last_name')


class SkillsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skills
        fields = ('user', 'name', 'years_experience', 'details')

    def validate_user(self, instance):
        if not instance.user.is_candidate:
            raise serializers.ValidationError("Current user is not candidate")
        return instance
