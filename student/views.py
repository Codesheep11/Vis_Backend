from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DataStudentinfo, DataSubmitrecord, DataTitleinfo
from django.db.models import Max, Subquery
import datetime


# w_{学生s对某知识点的掌握程度} = \frac{1}{n} \sum^n_{i=1} \frac{score^s_i}{max\_score_i}
@csrf_exempt
def student_knowledge_1(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        knowledge = request.POST.get('knowledge')

        if not student_id or not knowledge:
            return JsonResponse({'error': 1, 'msg': 'Missing student_id or knowledge'})

        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        # 查询该学生所有提交记录中的知识点为knowledge的提交记录
        submit_records = submit_records.filter(
            title_id__in=DataTitleinfo.objects.filter(knowledge=knowledge).values('title_id'))
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': f'No records found for knowledge point {knowledge}'})

        # 对于submit_records中的每一条记录，如果有title_id相同的，保留最后一次的提交记录
        # 使用子查询获取每个 title_id 对应的最后一次提交记录的 ID
        last_record_times = (
            submit_records.values('title_id')
            .annotate(max_time=Max('time'))
            .values('max_time')
        )

        # 使用获取到的时间过滤原始的 QuerySet
        submit_records = submit_records.filter(time__in=Subquery(last_record_times))
        # 计算该学生对该knowledge的掌握程度
        total_score_ratio = 0
        n = submit_records.count()
        for record in submit_records:
            print(record.title_id)
            max_score = DataTitleinfo.objects.filter(title_id=record.title_id)
            if max_score:
                total_score_ratio += record.score / max_score[0].score
        rate = total_score_ratio / n

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'knowledge': knowledge,
                'student_id': student_id,
                'rate': rate
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# w_{学生s对某知识点的掌握程度} = \frac{\sum^n_{i=1} {score^s_i}}{\sum^n_{i=1}max\_score_i}
@csrf_exempt
def student_knowledge_2(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        knowledge = request.POST.get('knowledge')

        if not student_id or not knowledge:
            return JsonResponse({'error': 1, 'msg': 'Missing student_id or knowledge'})

        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        # 查询该学生所有提交记录中的知识点为knowledge的提交记录
        submit_records = submit_records.filter(
            title_id__in=DataTitleinfo.objects.filter(knowledge=knowledge).values('title_id'))
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': f'No records found for knowledge point {knowledge}'})

        # 对于submit_records中的每一条记录，如果有title_id相同的，保留最后一次的提交记录
        # 使用子查询获取每个 title_id 对应的最后一次提交记录的 ID
        last_record_times = (
            submit_records.values('title_id')
            .annotate(max_time=Max('time'))
            .values('max_time')
        )

        # 使用获取到的时间过滤原始的 QuerySet
        submit_records = submit_records.filter(time__in=Subquery(last_record_times))
        # 计算该学生对该knowledge的掌握程度
        total_score = 0
        total_max_score = 0
        for record in submit_records:
            max_score = DataTitleinfo.objects.filter(title_id=record.title_id)
            if max_score:
                total_score += record.score
                total_max_score += max_score[0].score
        rate = total_score / total_max_score

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'knowledge': knowledge,
                'student_id': student_id,
                'rate': rate
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# 对于knowledge，取得所有提交记录中每个学生，每道题对的该知识点的最后一次提交记录，计算所有学生该知识点的掌握程度的平均值
# @csrf_exempt
# def knowledge_control_1(request):


# 对于knowledge，取得所有提交记录中的该知识点的最后一次提交记录，计算AC的次数，总次数，AC率
@csrf_exempt
def knowledge_ACrate(request):
    if request.method == 'POST':
        knowledge = request.POST.get('knowledge')

        if not knowledge:
            return JsonResponse({'error': 1, 'msg': 'Missing knowledge'})

        # 查询该知识点的所有提交记录
        submit_records = DataSubmitrecord.objects.filter(
            title_id__in=DataTitleinfo.objects.filter(knowledge=knowledge).values('title_id'))
        print(submit_records.count())
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': f'No submit records found for knowledge {knowledge}'})
        # 对于submit_records中的每一条记录，如果有title_id相同的，保留最后一次的提交记录
        # 使用子查询获取每个 title_id 和 student_id 对应的最后一次提交记录的 ID
        last_record_times = (
            submit_records.values('title_id', 'student_id')
            .annotate(max_time=Max('time'))
            .values('max_time')
        )

        # 使用获取到的时间过滤原始的 QuerySet
        submit_records = submit_records.filter(time__in=Subquery(last_record_times))
        print(submit_records.count())
        # 计算该知识点的AC次数，总次数，AC率
        AC_count = 0
        total_count = 0
        for record in submit_records:
            total_count += 1
            if record.state == 'Absolutely_Correct':
                AC_count += 1
        rate = AC_count / total_count

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'knowledge': knowledge,
                'AC_count': AC_count,
                'total_count': total_count,
                'rate': rate
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


@csrf_exempt
def sub_knowledg_ACrate(request):
    if request.method == 'POST':
        sub_knowledge = request.POST.get('sub_knowledge')

        if not sub_knowledge:
            return JsonResponse({'error': 1, 'msg': 'Missing sub_knowledge'})

        # 查询该知识点的所有提交记录
        submit_records = DataSubmitrecord.objects.filter(
            title_id__in=DataTitleinfo.objects.filter(sub_knowledge=sub_knowledge).values('title_id'))
        if not submit_records.exists():
            return JsonResponse({'error': 1,
                                 'msg': f'No submit records found for knowledge {knowledge} and sub_knowledge {sub_knowledge}'})
        # 对于submit_records中的每一条记录，如果有title_id相同的，保留最后一次的提交记录
        # 使用子查询获取每个 title_id 和 student_id 对应的最后一次提交记录的 ID
        last_record_times = (
            submit_records.values('title_id', 'student_id')
            .annotate(max_time=Max('time'))
            .values('max_time')
        )

        # 使用获取到的时间过滤原始的 QuerySet
        submit_records = submit_records.filter(time__in=Subquery(last_record_times))
        # 计算该知识点的AC次数，总次数，AC率
        AC_count = 0
        total_count = 0
        for record in submit_records:
            total_count += 1
            if record.state == 'Absolutely_Correct':
                AC_count += 1
        rate = AC_count / total_count

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'sub_knowledge': sub_knowledge,
                'AC_count': AC_count,
                'total_count': total_count,
                'rate': rate
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# 统计每个student_id 每天中每个小时的提交分布统计
@csrf_exempt
def student_submit_hour_distribution(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')

        if not student_id:
            return JsonResponse({'error': 1, 'msg': 'Missing student_id'})

        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        # 统计每个student_id 每2个小时的提交分布统计
        submit_distribution = {}
        for record in submit_records:
            time = record.time
            hour = datetime.datetime.fromtimestamp(time).hour
            time_slot = hour
            if time_slot not in submit_distribution:
                submit_distribution[time_slot] = 1
            else:
                submit_distribution[time_slot] += 1

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'student_id': student_id,
                'submit_distribution': submit_distribution
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# 统计每个student_id 每个月中每天的提交分布统计
@csrf_exempt
def student_submit_day_distribution(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')

        if not student_id:
            return JsonResponse({'error': 1, 'msg': 'Missing student_id'})

        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        # 统计每个student_id 每个月的提交分布统计
        submit_distribution = {}
        for record in submit_records:
            time = record.time
            day = datetime.datetime.fromtimestamp(time).day
            if day not in submit_distribution:
                submit_distribution[day] = 1
            else:
                submit_distribution[day] += 1

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'student_id': student_id,
                'submit_distribution': submit_distribution
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# 统计每个student_id 在日期上的提交分布统计
@csrf_exempt
def student_submit_date_distribution(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')

        if not student_id:
            return JsonResponse({'error': 1, 'msg': 'Missing student_id'})

        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        # 统计每个student_id 每个月的提交分布统计
        submit_distribution = {}
        for record in submit_records:
            time = record.time
            date = datetime.datetime.fromtimestamp(time).date()
            if date not in submit_distribution:
                submit_distribution[date] = 1
            else:
                submit_distribution[date] += 1

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'student_id': student_id,
                'submit_distribution': submit_distribution
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# 统计每个student_id 在不同knowledge上的提交分布统计
@csrf_exempt
def student_knowledge_distribution(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')

        if not student_id:
            return JsonResponse({'error': 1, 'msg': 'Missing student_id'})

        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        # 统计每个student_id 每个月的提交分布统计
        submit_distribution = {}
        for record in submit_records:
            knowledge = DataTitleinfo.objects.filter(title_id=record.title_id).values('knowledge')
            if knowledge:
                if knowledge[0]['knowledge'] not in submit_distribution:
                    submit_distribution[knowledge[0]['knowledge']] = 1
                else:
                    submit_distribution[knowledge[0]['knowledge']] += 1

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'student_id': student_id,
                'submit_distribution': submit_distribution
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})
