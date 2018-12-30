from django.shortcuts import render
from django.db import DatabaseError, connections
from use_function import namedtuplefetchall, removeExtemeValueForAnalysisDiscussion, getMedian
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
from sklearn.linear_model import LinearRegression


def analysis_forum_view(request):
    request.encoding = 'utf-8'

    if request.method == 'GET':
        to_render = {}
        jsonArray_temp = []

        with connections['ResultDB'].cursor() as cursor:
            now = datetime.now()
            twoMonthAgo = (now + relativedelta(months=-2)).strftime('%Y-%m-%d')

            cursor.execute(
                "SELECT max(統計日期) as max_date FROM course_total_data_v2"
            )
            result = namedtuplefetchall(cursor)

            update_course_total_data = result[-1].max_date

            cursor.execute(
                "SELECT 博士, 碩士, 學士, 副學士, 高中, 國中, 國小, 討論區參與度 "
                "FROM course_total_data_v2 "
                "WHERE 統計日期 = %s and start_date < %s order by 討論區參與度 asc",
                [update_course_total_data, twoMonthAgo]
            )
            result = namedtuplefetchall(cursor)

            matrix = [[0 for i in range(7)] for i in range(7)]
            Sum = [0 for i in range(7)]
            errors = [0 for i in range(5)]
            temp = []
            values = []
            education = []

            newData = removeExtemeValueForAnalysisDiscussion(result)
            Median = getMedian(newData)
            amount = len(newData)

            '''
            for data in newData:
                temp.clear()
                temp.append(data.博士)
                temp.append(data.碩士)
                temp.append(data.學士)
                temp.append(data.副學士)
                temp.append(data.高中)
                temp.append(data.國中)
                temp.append(data.國小)
                education.append(temp.copy())
                values.append(data.討論區參與度)

            X = np.array(education)
            y = np.array(values)

            lm = LinearRegression()
            lm.fit(X, y)
            output = lm.coef_
            '''

            for data in newData:
                for i in range(7):
                    for j in range(7):
                        matrix[i][j] = matrix[i][j] + data[i] * data[j]

                    Sum[i] = Sum[i] + data[i] * data[7]

            matrix = np.mat(matrix)
            Sum = np.mat(Sum).T
            output = np.linalg.solve(matrix, Sum)

            # 計算預估誤差
            for data in newData:
                total = 0
                for i in range(7):
                    total = total + data[i] * np.asscalar(output[i])

                if data[7] == 0:
                    error = abs(total - data[7]) / Median
                else:
                    error = abs(total - data[7]) / data[7]

                # 計算各誤差值的數量
                if error <= 0.05:
                    errors[0] += 1
                elif error <= 0.1:
                    errors[1] += 1
                elif error <= 0.2:
                    errors[2] += 1
                elif error <= 0.5:
                    errors[3] += 1
                elif error > 0.5:
                    errors[4] += 1

            print(errors)
            # 計算各誤差值的比例
            for i in range(5):
                errors[i] = errors[i] / amount

            to_render['output_p'] = output[0].item
            to_render['output_m'] = output[1].item
            to_render['output_b'] = output[2].item
            to_render['output_a'] = output[3].item
            to_render['output_hs'] = output[4].item
            to_render['output_jhs'] = output[5].item
            to_render['output_el'] = output[6].item

            to_render['below_5'] = errors[0] * 100
            to_render['below_10'] = errors[1] * 100
            to_render['below_20'] = errors[2] * 100
            to_render['below_50'] = errors[3] * 100
            to_render['outOf_50'] = errors[4] * 100

            return render(request, 'AnalysisDiscussion.html', to_render)


def calculate_education(data, avg_data):
    output = (data.博士 * 7 * (data.博士 / avg_data.avg_p)) + (data.碩士 * 6 * (data.碩士 / avg_data.avg_m)) + \
             (data.學士 * 5 * (data.學士 / avg_data.avg_b)) + (data.副學士 * 4 * (data.副學士 / avg_data.avg_a)) + \
             (data.高中 * 3 * (data.高中 / avg_data.avg_hs)) + (data.國中 * 2 * (data.國中 / avg_data.avg_jhs)) + \
             (data.國小 * 1 * (data.國小 / avg_data.avg_el)) * (data.total / avg_data.avg_all)
    return output


def degree(x):
    if x > 0.7:
        return '高度正相關'
    elif x >= 0.3:
        return '中度正相關'
    elif x >= 0:
        return '低度正相關'
    elif x <= -0.7:
        return '高度負相關'
    elif x <= -0.3:
        return '中度負相關'
    else:
        return '低度負相關'


def justnothing(request):
    to_render = {}
    jsonArray_temp = []
    update_course_total_data = '2018-06-11'
    twoMonthAgo = '2018-09-29'
    # p, m, b, a, hs, jhs, el = symbols('p, m, b, a, hs, jhs, el')
    '''

    with connections['ResultDB'].cursor() as cursor:
        cursor.execute(
            "SELECT 討論區討論次數, 博士, 碩士, 學士, 副學士, 高中, 國中, 國小, (博士+碩士+學士+副學士+高中+國中+國小) as total "
            "FROM course_total_data_v2 "
            "WHERE 統計日期 = %s and start_date < %s ", [update_course_total_data, twoMonthAgo]
        )
        education_data = namedtuplefetchall(cursor)

        paras = []

        for ed in education_data:
            a1 = ed.博士
            a2 = ed.碩士
            a3 = ed.學士
            a4 = ed.副學士
            a5 = ed.高中
            a6 = ed.國中
            a7 = ed.國小
            a8 = ed.討論區討論次數
            paras.append(a1 * p + a2 * m + a3 * b + a4 * a + a5 * hs + a6 * jhs + a7 * el - a8)

        solve(paras, [p, m, b, a, hs, jhs, el])
    '''

    '''
    with connections['ResultDB'].cursor() as cursor:
        # 取得課程所有學歷平均以及所有學歷加總平均
        cursor.execute(
            "SELECT avg(博士) as avg_p, avg(碩士) as avg_m, avg(學士) as avg_b, avg(副學士) as avg_a, "
            "avg(高中) as avg_hs, avg(國中) as avg_jhs, avg(國小) as avg_el, "
            "avg(博士+碩士+學士+副學士+高中+國中+國小) as avg_all "
            "FROM course_total_data_v2 "
            "WHERE 統計日期 = %s and start_date < %s ", [update_course_total_data, twoMonthAgo]
        )
        avg_course_data = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT 討論區討論次數, 博士, 碩士, 學士, 副學士, 高中, 國中, 國小, (博士+碩士+學士+副學士+高中+國中+國小) as total "
            "FROM course_total_data_v2 "
            "WHERE 統計日期 = %s and start_date < %s ", [update_course_total_data, twoMonthAgo]
        )
        education_data = namedtuplefetchall(cursor)

        Json_forum_education = []
        jsonArray_temp.clear()
        jsonArray_temp.append('課程學歷總和')  # 課程學歷總和
        jsonArray_temp.append('討論區討論次數')  # 討論區討論次數
        Json_forum_education.append(jsonArray_temp.copy())
        education_level_total = []
        forum_discuss_frequency = []

        # 處理數值，並加進顯示資料中
        for rs in education_data:
            forum_discuss_frequency.append(rs.討論區討論次數)
            edu_lvl = calculate_education(rs, avg_course_data[0])
            education_level_total.append(float(edu_lvl))

            jsonArray_temp.clear()
            jsonArray_temp.append(rs.討論區討論次數)
            jsonArray_temp.append(edu_lvl)
            Json_forum_education.append(jsonArray_temp.copy())

        forum_discuss_frequency = pd.Series(forum_discuss_frequency)
        education_level_total = pd.Series(education_level_total)
        cc_FDF_ELT = forum_discuss_frequency.corr(education_level_total)

        to_render['Json_AML_WHP'] = json.dumps(Json_forum_education, cls=DecimalEncoder)
        to_render['tt'] = json.dumps(Json_forum_education, cls=DecimalEncoder)
        to_render['cc_FDF_ELT'] = '{:,.2f}'.format(cc_FDF_ELT)
        to_render['degree_FDF_ELT'] = degree(cc_FDF_ELT)
        to_render['update_course_total_data'] = update_course_total_data

        return render(request, 'AnalysisDiscussion.html', to_render)
    '''
