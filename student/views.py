import datetime
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StudentInfo, DataSubmitrecord, DataTitleinfo, KnowledgeInfo, SubKnowledgeInfo
from django.db.models import Max, Subquery


# 返回所有学生的列表信息，包括student_id,class,以class为第一关键字，student_id为第二关键字，升序展示
@csrf_exempt
def student_home(request):
    if request.method == 'GET':
        students = StudentInfo.objects.all().order_by('class_field', 'student_id')
        student_list = []
        for student in students:
            student_list.append({
                'student_id': student.student_id,
                'class': student.class_field,
                'sex': student.sex,
                'age': student.age,
                'major': student.major
            })
        return JsonResponse({'error': 0, 'msg': 'success', 'data': student_list})
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


@csrf_exempt
def student_detail(request, student_id):
    if request.method == 'GET':
        student = StudentInfo.objects.filter(student_id=student_id)
        if not student.exists():
            return JsonResponse({'error': 1, 'msg': 'No student found'})
        student = student[0]
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'student_id': student.student_id,
                'class': student.class_field,
                'sex': student.sex,
                'age': student.age,
                'major': student.major
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# 返回学生对所有知识点的掌握程度
@csrf_exempt
def student_knowledge_mastery(request, student_id):
    if request.method == 'GET':
        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        knowledges = KnowledgeInfo.objects.all()
        konwledge_list = []
        for know in knowledges:
            # 查询该学生所有提交记录中的知识点为knowledge的提交记录
            submit_records_knowledge = submit_records.filter(
                title_id__in=DataTitleinfo.objects.filter(knowledge=know.knowledge).values('title_id'))
            if not submit_records_knowledge.exists():
                continue

            # 对于submit_records中的每一条记录，如果有title_id相同的，保留最后一次的提交记录
            # 使用子查询获取每个 title_id 对应的最后一次提交记录的 ID
            last_record_times = (
                submit_records_knowledge.values('title_id')
                .annotate(max_time=Max('time'))
                .values('max_time')
            )

            # 使用获取到的时间过滤原始的 QuerySet
            submit_records_knowledge = submit_records_knowledge.filter(time__in=Subquery(last_record_times))
            # 加权计算该学生对该knowledge的掌握程度
            total_score = 0
            total_max_score = 0
            for record in submit_records_knowledge:
                max_score = DataTitleinfo.objects.filter(title_id=record.title_id)
                if max_score:
                    total_score += record.score
                    total_max_score += max_score[0].score
            mastery = total_score / total_max_score

            # 计算该知识点的AC次数，总次数，AC率
            AC_count = 0
            total_count = 0
            for record in submit_records_knowledge:
                total_count += 1
                if record.state == 'Absolutely_Correct':
                    AC_count += 1
            ac_rate = AC_count / total_count
            konwledge_list.append({
                'mainpoint': know.knowledge,
                'mastery': mastery,
                'ac_rate': ac_rate
            })
        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': konwledge_list
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


@csrf_exempt
def student_sub_knowledge_mastery(request, student_id):
    if request.method == 'GET':
        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        sub_knowledges = SubKnowledgeInfo.objects.all()
        sub_konwledge_list = []
        for sub_know in sub_knowledges:
            # 查询该学生所有提交记录中的知识点为knowledge的提交记录
            submit_records_sub_knowledge = submit_records.filter(
                title_id__in=DataTitleinfo.objects.filter(sub_knowledge=sub_know.sub_knowledge).values('title_id'))
            if not submit_records_sub_knowledge.exists():
                continue

            # 对于submit_records中的每一条记录，如果有title_id相同的，保留最后一次的提交记录
            # 使用子查询获取每个 title_id 对应的最后一次提交记录的 ID
            last_record_times = (
                submit_records_sub_knowledge.values('title_id')
                .annotate(max_time=Max('time'))
                .values('max_time')
            )

            # 使用获取到的时间过滤原始的 QuerySet
            submit_records_sub_knowledge = submit_records_sub_knowledge.filter(time__in=Subquery(last_record_times))
            # 加权计算该学生对该knowledge的掌握程度
            total_score = 0
            total_max_score = 0
            for record in submit_records_sub_knowledge:
                max_score = DataTitleinfo.objects.filter(title_id=record.title_id)
                if max_score:
                    total_score += record.score
                    total_max_score += max_score[0].score
            mastery = total_score / total_max_score

            # 计算该知识点的AC次数，总次数，AC率
            AC_count = 0
            total_count = 0
            for record in submit_records_sub_knowledge:
                total_count += 1
                if record.state == 'Absolutely_Correct':
                    AC_count += 1
            ac_rate = AC_count / total_count
            sub_konwledge_list.append({
                'mainpoint': sub_know.knowledge,
                'subpoint': sub_know.sub_knowledge,
                'mastery': mastery,
                'ac_rate': ac_rate
            })
        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': sub_konwledge_list
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# 学生每天的提交记录
@csrf_exempt
def student_submit_day_record(request, student_id):
    if request.method == 'GET':
        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        # 统计每个student_id 每天的提交记录
        submit_record_day = {}
        for record in submit_records:
            time = record.time
            date = datetime.datetime.fromtimestamp(time).date()
            if date not in submit_record_day:
                submit_record_day[date] = 1
            else:
                submit_record_day[date] += 1

        # 对于'2023-08-31'到'2024-01-26'的每一天，如果没有提交记录，添加一个空列表
        submit_record_day_list = []
        start_date = datetime.date(2023, 8, 31)
        end_date = datetime.date(2024, 1, 26)
        for i in range((end_date - start_date).days + 1):
            date = start_date + datetime.timedelta(days=i)
            if date not in submit_record_day:
                submit_record_day_list.append({
                    'day': date,
                    'count': 0
                })
            else:
                submit_record_day_list.append({
                    'day': date,
                    'count': submit_record_day[date]
                })

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': submit_record_day_list
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# 学生每小时的提交记录
@csrf_exempt
def student_submit_hour_record(request, student_id):
    if request.method == 'GET':
        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        # 统计每个student_id 每小时的提交记录
        submit_record_hour = {}
        for record in submit_records:
            time = record.time
            hour = datetime.datetime.fromtimestamp(time).hour
            if hour not in submit_record_hour:
                submit_record_hour[hour] = 1
            else:
                submit_record_hour[hour] += 1

        # 对于0到23的每个小时，如果没有提交记录，添加一个空列表
        submit_record_hour_list = []

        for i in range(24):
            if i not in submit_record_hour:
                submit_record_hour_list.append({
                    'period': i,
                    'count': 0
                })
            else:
                submit_record_hour_list.append({
                    'period': i,
                    'count': submit_record_hour[i]
                })

        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': submit_record_hour_list
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


@csrf_exempt
def student_submit_record(request, student_id):
    if request.method == 'GET':
        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        node_list = []
        link_list = []
        node_list.append({
            'name': 'total'
        })
        # 统计submit_records中的每一条记录，计算每个knowledge的提交次数以及每个sub_knowledge的提交次数
        knowledge_submit_count = {}
        sub_knowledge_submit_count = {}
        method_count = {}
        method_knowledge = {}
        for record in submit_records:
            method = record.method
            knows = DataTitleinfo.objects.filter(title_id=record.title_id).values_list('knowledge', flat=True)
            sub_knows = DataTitleinfo.objects.filter(title_id=record.title_id).values_list('sub_knowledge', flat=True)
            for know in knows:
                if know not in knowledge_submit_count:
                    knowledge_submit_count[know] = 1
                else:
                    knowledge_submit_count[know] += 1
                if (method, know) not in method_knowledge:
                    method_knowledge[(method, know)] = 1
                else:
                    method_knowledge[(method, know)] += 1
            for sub_know in sub_knows:
                if sub_know not in sub_knowledge_submit_count:
                    sub_knowledge_submit_count[sub_know] = 1
                else:
                    sub_knowledge_submit_count[sub_know] += 1
            if method not in method_count:
                method_count[method] = knows.count()
            else:
                method_count[method] += knows.count()
        for method in method_count:
            node_list.append({
                'name': method
            })
            link_list.append({
                'source': 'total',
                'target': method,
                'value': method_count[method]
            })
        for know in knowledge_submit_count:
            node_list.append({
                'name': know
            })
        for sub_know in sub_knowledge_submit_count:
            node_list.append({
                'name': sub_know
            })
            link_list.append({
                'source': str(sub_know).split('_')[0],
                'target': sub_know,
                'value': sub_knowledge_submit_count[sub_know]
            })
        for method_know in method_knowledge:
            link_list.append({
                'source': method_know[0],
                'target': method_know[1],
                'value': method_knowledge[method_know]
            })
        # 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'nodes': node_list,
                'links': link_list
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


# 按knowledge划分统计，取所有学生最后一次提交，统计每个knowledge通过的人数、部分通过的人数、出错的人数

@csrf_exempt
def submit_knowledge(request):
    if request.method == 'GET':
        # submit_records = DataSubmitrecord.objects.all()
        # if not submit_records.exists():
        #     return JsonResponse({'error': 1, 'msg': 'No submit records'})
        # # 对于提交按学生ID分组，只保留time最大的记录
        # last_record_times = (
        #     submit_records.values('student_id', 'title_id')
        #     .annotate(max_time=Max('time'))
        #     .values('max_time')
        # )
        # submit_records = submit_records.filter(time__in=Subquery(last_record_times))
        # # 统计submit_records中的每一条记录，计算每个knowledge的score为满分的次数，部分分的次数，以及0分的次数
        # knowledge_submit_count = {}
        # for record in submit_records:
        #     knowledge = DataTitleinfo.objects.filter(title_id=record.title_id).values_list('knowledge', flat=True)
        #     for know in knowledge:
        #         if know not in knowledge_submit_count:
        #             knowledge_submit_count[know] = {
        #                 'ac': 0,
        #                 'partial_ac': 0,
        #                 'error': 0
        #             }
        #         if record.state == 'Absolutely_Correct':
        #             knowledge_submit_count[know]['ac'] += 1
        #         elif record.state == 'Partially_Correct':
        #             knowledge_submit_count[know]['partial_ac'] += 1
        #         else:
        #             knowledge_submit_count[know]['error'] += 1

        knowledges = KnowledgeInfo.objects.all()
        knowledge_list = []
        for know in knowledges:
            knowledge_list.append({
                'mainpoint': know.knowledge,
                'ac': know.ac,
                'partial_ac': know.partial_ac,
                'error': know.error
            })
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': knowledge_list
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})


def getColor(name) -> str:
    # 如果name包含知识点，则返回知识点对应的颜色
    if name.count('-') == 2:
        if "r8S3g" in name:
            return "#FACAA7"
        if "t5V9e" in name:
            return "#E4FAA8"
        if "y9W5d" in name:
            return "#7A604D"
        if "s8Y2f" in name:
            return "#9CA583"
        if "m3D1v" in name:
            return "#A7F2FA"
        if "g7R2j" in name:
            return "#E1A7FA"
        if "b3C9s" in name:
            return "#4D767A"
        if "k4W1c" in name:
            return "#6D4D7A"
    switcher = {
        "已通过-困难": "#30BF39",
        "已通过-中等": "#40FF4C",
        "已通过-简单": "#73FF7C",
        "尝试中-困难": "#BF9030",
        "尝试中-中等": "#FFC040",
        "尝试中-简单": "#FFD173",
        "未提交-困难": "#808080",
        "未提交-中等": "#C0C0C0",
        "未提交-简单": "#D3D3D3"
    }
    return switcher.get(name)


# 分等级统计每个学生对应的提交
@csrf_exempt
def student_submit_grade(request, student_id):
    if request.method == 'GET':
        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})
        # 对于submit_records中的每一条记录，如果有title_id相同的，保留最后一次的提交记录
        # 使用子查询获取每个 title_id 对应的最后一次提交记录的 ID
        last_record_times = (
            submit_records.values('title_id')
            .annotate(max_time=Max('time'))
            .values('max_time')
        )
        # 使用获取到的时间过滤原始的 QuerySet
        submit_records = submit_records.filter(time__in=Subquery(last_record_times))
        # 统计每个题目在当前提交记录的状态，ac还是part_ac还是error
        titles = DataTitleinfo.objects.all()
        count1 = []
        count2 = []
        count3 = []
        ac_list = [0, 0, 0, 0]
        trying_list = [0, 0, 0, 0]
        uncommited_list = [0, 0, 0, 0]
        # titles中title_id去重
        maps = {}
        knowledges = KnowledgeInfo.objects.all()
        for score in range(3, 0, -1):
            for know in knowledges:
                maps[("已通过", score, know.knowledge)] = 0
        for score in range(3, 0, -1):
            for know in knowledges:
                maps[("尝试中", score, know.knowledge)] = 0
        for score in range(3, 0, -1):
            for know in knowledges:
                maps[("未提交", score, know.knowledge)] = 0
        submit_records_dict = {
            record.title_id: record
            for record in submit_records.order_by('-time')
        }

        # 遍历 titles，进行分类处理
        for title in titles:
            score = title.score
            if score == 4:
                score = 3
            know = title.knowledge
            # 检查 title 是否在 submit_records 中
            if title.title_id in submit_records_dict:
                record = submit_records_dict[title.title_id]
                if record.state == 'Absolutely_Correct':
                    ac_list[0] += 1
                    ac_list[score] += 1
                    key = ("已通过", score, know)
                else:
                    trying_list[0] += 1
                    trying_list[score] += 1
                    key = ("尝试中", score, know)
            else:
                uncommited_list[0] += 1
                uncommited_list[score] += 1
                key = ("未提交", score, know)

            if key in maps:
                maps[key] += 1
            else:
                maps[key] = 1
        count1.append({
            'value': ac_list[0],
            'name': '已通过',
            'itemStyle': {
                'color': '#00FF11'
            }
        })
        count1.append({
            'value': trying_list[0],
            'name': '尝试中',
            'itemStyle': {
                'color': '#FFAB00'
            }
        })
        count1.append({
            'value': uncommited_list[0],
            'name': '未提交',
            'itemStyle': {
                'color': 'A9A9A9'
            }
        })
        switcher = {
            1: "简单",
            2: "中等",
            3: "困难"
        }
        for i in range(3, 0, -1):
            count2.append({
                'value': ac_list[i],
                'name': '已通过-' + switcher.get(i),
                'itemStyle': {
                    'color': getColor('已通过-' + switcher.get(i))
                }
            })
        for i in range(3, 0, -1):
            count2.append({
                'value': trying_list[i],
                'name': '尝试中-' + switcher.get(i),
                'itemStyle': {
                    'color': getColor('尝试中-' + switcher.get(i))
                }
            })
        for i in range(3, 0, -1):
            count2.append({
                'value': uncommited_list[i],
                'name': '未提交-' + switcher.get(i),
                'itemStyle': {
                    'color': getColor('未提交-' + switcher.get(i))
                }
            })

        for key in maps:
            name = key[0] + "-"
            name += switcher.get(key[1])
            name += "-" + key[2]
            count3.append({
                'value': maps[key],
                'name': name,
                'itemStyle': {
                    'color': getColor(name)
                }
            })
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'count1': count1,
                'count2': count2,
                'count3': count3
            }
        })


# w_{学生s对某知识点的掌握程度} = \frac{1}{n} \sum^n_{i=1} \frac{score^s_i}{max\_score_i}
@csrf_exempt
def student_knowledge_1(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_id = data.get('student_id')
        knowledge = data.get('knowledge')

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
        data = json.loads(request.body)
        student_id = data.get('student_id')
        knowledge = data.get('knowledge')

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


# 对于knowledge，取得所有提交记录中的该知识点的最后一次提交记录，计算AC的次数，总次数，AC率
@csrf_exempt
def knowledge_ACrate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        knowledge = data.get('knowledge')

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
def sub_knowledge_ACrate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sub_knowledge = data.get('sub_knowledge')

        if not sub_knowledge:
            return JsonResponse({'error': 1, 'msg': 'Missing sub_knowledge'})

        # 查询该知识点的所有提交记录
        submit_records = DataSubmitrecord.objects.filter(
            title_id__in=DataTitleinfo.objects.filter(sub_knowledge=sub_knowledge).values('title_id'))
        if not submit_records.exists():
            return JsonResponse({'error': 1,
                                 'msg': f'No submit records found for knowledge {sub_knowledge} and sub_knowledge {sub_knowledge}'})
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
        data = json.loads(request.body)
        student_id = data.get('student_id')

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
        data = json.loads(request.body)
        student_id = data.get('student_id')

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
        data = json.loads(request.body)
        student_id = data.get('student_id')

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
        data = json.loads(request.body)
        student_id = data.get('student_id')
        if not student_id:
            return JsonResponse({'error': 1, 'msg': 'Missing student_id'})

        # 查询该学生所有提交记录
        submit_records = DataSubmitrecord.objects.filter(student_id=student_id)
        if not submit_records.exists():
            return JsonResponse({'error': 1, 'msg': 'No submit records found for this student'})

        # 统计每个student_id 在不同知识点上的提交分布统计
        knowledge_submit_distribution = {}
        for record in submit_records:
            knowledge_records = DataTitleinfo.objects.filter(title_id=record.title_id).values_list('knowledge',
                                                                                                   flat=True)
            for knowledge in knowledge_records:
                if knowledge not in knowledge_submit_distribution:
                    knowledge_submit_distribution[knowledge] = 1
                else:
                    knowledge_submit_distribution[knowledge] += 1
        sub_knowledge_submit_distribution = {}
        for record in submit_records:
            sub_knowledge_records = DataTitleinfo.objects.filter(title_id=record.title_id).values_list('sub_knowledge',
                                                                                                       flat=True)
            for sub_knowledge in sub_knowledge_records:
                if sub_knowledge not in sub_knowledge_submit_distribution:
                    sub_knowledge_submit_distribution[sub_knowledge] = 1
                else:
                    sub_knowledge_submit_distribution[sub_knowledge] += 1
        # 4. 返回结果
        return JsonResponse({
            'error': 0,
            'msg': 'success',
            'data': {
                'student_id': student_id,
                'knowledge_submit_distribution': knowledge_submit_distribution,
                'sub_knowledge_submit_distribution': sub_knowledge_submit_distribution
            }
        })
    return JsonResponse({'error': 1, 'msg': 'Invalid request method'})
