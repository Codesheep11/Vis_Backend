from django.urls import path
from .views import *

urlpatterns = [
    # Student
    path('student/knowledge_control1', student_knowledge_1),
    path('student/knowledge_control2', student_knowledge_2),
    path('student/submit_hour_distribution', student_submit_hour_distribution),
    path('student/submit_day_distribution', student_submit_day_distribution),
    path('student/submit_date_distribution', student_submit_date_distribution),

    # Knowledge
    path('knowledge/acrate', knowledge_ACrate),
    path('sub_knowledge/acrate', sub_knowledg_ACrate),
]
