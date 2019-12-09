from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from hr_system.models import User, Candidate
from hr_system.serializers import UserSerializer, CandidateProfileCreateSerializer, RecruiterProfileCreateSerializer, \
    SkillsSerializer


class CandidateRegistrationAPIView(APIView):

    def post(self, request, *args, **kwargs):
        user__serializer = UserSerializer(data=request.data, context={'profile_type': User.PROFILE_TYPE_CANDIDATE})
        candidate_serializer = CandidateProfileCreateSerializer(data=request.data)
        errors = {}
        for serializer in {user__serializer, candidate_serializer}:
            if not serializer.is_valid():
                errors.update(serializer.errors)
        if not errors:
            with transaction.atomic():
                user = user__serializer.save()
                candidate_serializer.save(user=user)
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class RecruiterRegistrationAPIView(APIView):

    def post(self, request, *args, **kwargs):
        user__serializer = UserSerializer(data=request.data, context={'profile_type': User.PROFILE_TYPE_RECRUITER})
        recruiter_serializer = RecruiterProfileCreateSerializer(data=request.data)
        errors = {}
        for serializer in {user__serializer, recruiter_serializer}:
            if not serializer.is_valid():
                errors.update(serializer.errors)
        if not errors:
            with transaction.atomic():
                user = user__serializer.save()
                recruiter_serializer.save(user=user)
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class AddSkillsAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SkillsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchCandidates(APIView):
    def post(self, request, *args, **kwargs):
        data = []
        fields = request.data
        if "skills" in fields:
            for key, value in fields['skills'].items():
                fields[f'skills__{key}'] = value
            del fields['skills']
        if "category" in fields:
            fields[f'category__name'] = fields['category']
            del fields['category']
        for candidate in Candidate.objects.filter(user__is_active=True, in_search=True, **fields):
            data.append(CandidateProfileCreateSerializer(candidate).data)
        if data:
            return Response({'success': True, 'data': data})
        return Response({'success': True, 'data': 'There is no candidates which can pass your criteria'})




