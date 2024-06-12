from django.urls import path
from .views import *

urlpatterns = [
    # apifox
    path('students/list-all', student_home),
    path('students/<str:student_id>', student_detail),
    path('mainpoint/mastery/<str:student_id>', student_knowledge_mastery),
    path('subpoint/mastery/<str:student_id>', student_sub_knowledge_mastery),
    path('submit/day/<str:student_id>', student_submit_day_record),
    path('submit/hour/<str:student_id>', student_submit_hour_record),
    path('submit/student/<str:student_id>', student_submit_record),
    path('submit/total', submit_knowledge),
    path('submit/level/<str:student_id>', student_submit_grade),
    # Student
    path('student/knowledge_control1', student_knowledge_1),
    path('student/knowledge_control2', student_knowledge_2),
    path('student/submit_hour_distribution', student_submit_hour_distribution),
    path('student/submit_day_distribution', student_submit_day_distribution),
    path('student/submit_date_distribution', student_submit_date_distribution),
    path('student/knowledge_distribution', student_knowledge_distribution),

    # Knowledge
    path('knowledge/acrate', knowledge_ACrate),
    path('sub_knowledge/acrate', sub_knowledge_ACrate),
]
