from django.shortcuts import render
from use_function import namedtuplefetchall
from django.db import connections


# Create your views here.
def popular_courses_age_view(request):
    request.encoding = 'utf-8'
    to_render = {}
    data = []
    output = []
    if request.method == 'GET':
        to_render = suggested_by_age(request)

    return render(request, 'PopularCourseAge.html', to_render)


def popular_courses_education_view(request):
    request.encoding = 'utf-8'
    to_render = {}
    data = []
    output = []
    if request.method == 'GET':
        to_render = suggested_by_education(request)

    return render(request, 'PopularCourseEducation.html', to_render)


def suggested_by_age(request):
    to_render = {}

    with connections['ResultDB'].cursor() as cursor:
        cursor.execute(
            "SELECT max(統計日期) as max_date FROM course_total_data_v2 WHERE 課程代碼='C01'"
        )
        result = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT 課程代碼, course_id, course_name, age_17, age_18_25, age_26_ "
            "FROM course_total_data_v2 "
            "WHERE 統計日期 >= %s", [str(result[-1].max_date)]
        )
        result = namedtuplefetchall(cursor)

        max_17 = 0
        max_18_25 = 0
        max_26_ = 0
        total_17 = 0
        total_18_25 = 0
        total_26_ = 0

        output_17 = [[0 for i in range(4)] for i in range(3)]
        output_18_25 = [[0 for i in range(4)] for i in range(3)]
        output_26_ = [[0 for i in range(4)] for i in range(3)]

        for rs in result:
            totalage = rs.age_17 + rs.age_18_25 + rs.age_26_

            for temp_17 in output_17:
                if temp_17[3] == 0 or temp_17[3] < rs.age_17:
                    max_17 = rs.age_17
                    total_17 = totalage
                    temp_17[0] = rs.課程代碼
                    temp_17[1] = rs.course_id
                    temp_17[2] = rs.course_name
                    temp_17[3] = max_17
                    break
                elif temp_17[3] == rs.age_18_25:
                    if total_17 > totalage:
                        temp_17[0] = rs.課程代碼
                        temp_17[1] = rs.course_id
                        temp_17[2] = rs.course_name
                        temp_17[3] = max_17
                        break

            for temp_18_25 in output_18_25:
                if temp_18_25[3] == 0 or temp_18_25[3] < rs.age_18_25:
                    max_18_25 = rs.age_18_25
                    total_18_25 = totalage
                    temp_18_25[0] = rs.課程代碼
                    temp_18_25[1] = rs.course_id
                    temp_18_25[2] = rs.course_name
                    temp_18_25[3] = max_18_25
                    break

                elif temp_18_25[3] == rs.age_18_25:
                    if total_18_25 > totalage:
                        temp_18_25[0] = rs.課程代碼
                        temp_18_25[1] = rs.course_id
                        temp_18_25[2] = rs.course_name
                        temp_18_25[3] = max_18_25
                        break
            for temp_26_ in output_26_:
                if temp_26_[3] == 0 or temp_26_[3] < rs.age_26_:
                    max_26_ = rs.age_26_
                    total_26_ = totalage
                    temp_26_[0] = rs.課程代碼
                    temp_26_[1] = rs.course_id
                    temp_26_[2] = rs.course_name
                    temp_26_[3] = max_26_
                    break

                elif temp_26_[3] == rs.age_26_:
                    if total_26_ > totalage:
                        temp_26_[0] = rs.課程代碼
                        temp_26_[1] = rs.course_id
                        temp_26_[2] = rs.course_name
                        temp_26_[3] = max_26_
                        break

            output_17.sort(key=lambda x: x[3], reverse=True)
            output_18_25.sort(key=lambda x: x[3], reverse=True)
            output_26_.sort(key=lambda x: x[3], reverse=True)

        to_render['output_26_'] = output_26_
        to_render['output_18_25'] = output_18_25
        to_render['output_17'] = output_17

        return to_render


def suggested_by_education(request):
    to_render = {}
    with connections['ResultDB'].cursor() as cursor:
        cursor.execute(
            "SELECT max(統計日期) as max_date FROM course_total_data_v2 WHERE 課程代碼='C01'"
        )
        result = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT 課程代碼, course_id, course_name, 博士, 碩士, 學士, 副學士, 高中, 國中, 國小 "
            "FROM course_total_data_v2 "
            "WHERE 統計日期 >= %s", [str(result[-1].max_date)]
        )
        result = namedtuplefetchall(cursor)

        max_p = max_m = max_b = max_a = max_hs = max_jhs = max_el = 0
        totalall = 0
        total_p = total_m = total_b = total_a = total_hs = total_jhs = total_el = 0
        output_p = [[0 for i in range(4)] for i in range(3)]
        output_m = [[0 for i in range(4)] for i in range(3)]
        output_b = [[0 for i in range(4)] for i in range(3)]
        output_a = [[0 for i in range(4)] for i in range(3)]
        output_hs = [[0 for i in range(4)] for i in range(3)]
        output_jhs = [[0 for i in range(4)] for i in range(3)]
        output_el = [[0 for i in range(4)] for i in range(3)]

        for rs in result:
            totalall = rs.博士 + rs.碩士 + rs.學士 + rs.副學士 + rs.高中 + rs.國中 + rs.國小

            for o_p in output_p:
                if o_p[3] == 0 or o_p[3] < rs.博士:
                    max_p = rs.博士
                    total_p = totalall
                    o_p[0] = rs.課程代碼
                    o_p[1] = rs.course_id
                    o_p[2] = rs.course_name
                    o_p[3] = rs.博士
                    break

                elif o_p[3] == rs.博士:
                    if total_p > totalall:
                        o_p[0] = rs.課程代碼
                        o_p[1] = rs.course_id
                        o_p[2] = rs.course_name
                        o_p[3] = rs.博士
                        break

            for o_m in output_m:
                if o_m[3] == 0 or o_m[3] < rs.碩士:
                    max_m = rs.碩士
                    total_m = totalall
                    o_m[0] = rs.課程代碼
                    o_m[1] = rs.course_id
                    o_m[2] = rs.course_name
                    o_m[3] = rs.碩士
                    break

                elif o_m[3] == rs.碩士:
                    if total_m > totalall:
                        o_m[0] = rs.課程代碼
                        o_m[1] = rs.course_id
                        o_m[2] = rs.course_name
                        o_m[3] = rs.碩士
                        break

            for o_b in output_b:
                if o_b[3] == 0 or o_b[3] < rs.學士:
                    max_b = rs.學士
                    total_b = totalall
                    o_b[0] = rs.課程代碼
                    o_b[1] = rs.course_id
                    o_b[2] = rs.course_name
                    o_b[3] = rs.學士
                    break

                elif o_b[3] == rs.學士:
                    if total_b > totalall:
                        o_b[0] = rs.課程代碼
                        o_b[1] = rs.course_id
                        o_b[2] = rs.course_name
                        o_b[3] = rs.學士
                        break

            for o_a in output_a:
                if o_a[3] == 0 or o_a[3] < rs.副學士:
                    max_a = rs.副學士
                    total_a = totalall
                    o_a[0] = rs.課程代碼
                    o_a[1] = rs.course_id
                    o_a[2] = rs.course_name
                    o_a[3] = rs.副學士
                    break

                elif o_a[3] == rs.副學士:
                    if total_a > totalall:
                        o_a[0] = rs.課程代碼
                        o_a[1] = rs.course_id
                        o_a[2] = rs.course_name
                        o_a[3] = rs.副學士
                        break

            for o_hs in output_hs:
                if o_hs[3] == 0 or o_hs[3] < rs.高中:
                    max_hs = rs.高中
                    total_hs = totalall
                    o_hs[0] = rs.課程代碼
                    o_hs[1] = rs.course_id
                    o_hs[2] = rs.course_name
                    o_hs[3] = rs.高中
                    break

                elif o_hs[3] == rs.高中:
                    if total_hs > totalall:
                        o_hs[0] = rs.課程代碼
                        o_hs[1] = rs.course_id
                        o_hs[2] = rs.course_name
                        o_hs[3] = rs.高中
                        break

            for o_jhs in output_jhs:
                if o_jhs[3] == 0 or o_jhs[3] < rs.國中:
                    max_jhs = rs.國中
                    total_jhs = totalall
                    o_jhs[0] = rs.課程代碼
                    o_jhs[1] = rs.course_id
                    o_jhs[2] = rs.course_name
                    o_jhs[3] = rs.國中
                    break

                elif o_jhs[3] == rs.國中:
                    if total_jhs > totalall:
                        o_jhs[0] = rs.課程代碼
                        o_jhs[1] = rs.course_id
                        o_jhs[2] = rs.course_name
                        o_jhs[3] = rs.國中
                        break

            for o_el in output_el:
                if o_el[3] == 0 or o_el[3] < rs.國小:
                    max_el = rs.國小
                    total_el = totalall
                    o_el[0] = rs.課程代碼
                    o_el[1] = rs.course_id
                    o_el[2] = rs.course_name
                    o_el[3] = rs.國小
                    break

                elif o_el[3] == rs.國小:
                    if total_el > totalall:
                        o_el[0] = rs.課程代碼
                        o_el[1] = rs.course_id
                        o_el[2] = rs.course_name
                        o_el[3] = rs.國小
                        break

            output_p.sort(key=lambda x: x[3], reverse=True)
            output_m.sort(key=lambda x: x[3], reverse=True)
            output_b.sort(key=lambda x: x[3], reverse=True)
            output_a.sort(key=lambda x: x[3], reverse=True)
            output_hs.sort(key=lambda x: x[3], reverse=True)
            output_jhs.sort(key=lambda x: x[3], reverse=True)
            output_el.sort(key=lambda x: x[3], reverse=True)

        to_render['output_p'] = output_p
        to_render['output_m'] = output_m
        to_render['output_b'] = output_b
        to_render['output_a'] = output_a
        to_render['output_hs'] = output_hs
        to_render['output_jhs'] = output_jhs
        to_render['output_el'] = output_el

    return to_render
