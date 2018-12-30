from django.shortcuts import render
#from try1.models import Country, Course
from use_function import namedtuplefetchall
from django.db import connections, DatabaseError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sympy import *
import numpy as np
from sklearn.linear_model import LinearRegression


# Create your views here.
def C_T(request):
    to_render = {}
    with connections['ResultDB'].cursor() as cursor:
        to_render = {}
        jsonArray_temp = []

        if request.method == 'GET':
            to_render = {}
            now = datetime.now()
            twoMonthAgo = (now + relativedelta(months=-2)).strftime('%Y-%m-%d')

            cursor.execute(
                "SELECT max(統計日期) as max_date FROM course_total_data_v2 WHERE 課程代碼='C01'"
            )
            result = namedtuplefetchall(cursor)

            update_course_total_data = result[-1].max_date

            cursor.execute(
                "SELECT 博士, 碩士, 學士, 副學士, 高中, 國中, 國小, 討論區參與度 "
                "FROM course_total_data_v2 "
                "WHERE 統計日期 = %s and start_date < %s ", [update_course_total_data, twoMonthAgo]
            )
            result = namedtuplefetchall(cursor)

            matrix = [[0 for i in range(7)] for i in range(7)]
            Sum = [0 for i in range(7)]
            errors = [0 for i in range(5)]
            amount = len(result)
            temp = []
            gogo = []
            values = []

            for rs in result:
                temp.clear()
                temp.append(rs.博士)
                temp.append(rs.碩士)
                temp.append(rs.學士)
                temp.append(rs.副學士)
                temp.append(rs.高中)
                temp.append(rs.國中)
                temp.append(rs.國小)
                values.append(rs.討論區參與度)
                gogo.append(temp.copy())

            X = np.array(
                gogo
            )
            y = np.array(values)

            lm = LinearRegression()
            lm.fit(X, y)

            to_render['country'] = list(lm.coef_)

    return render(request, 'try1.html', to_render)



