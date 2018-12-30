# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta
from index.models import OpenEduDB, ResultDB
from django.db import DatabaseError
from use_function import namedtuplefetchall
from django.db import connections
import json
import math


def index_view(request):
    request.encoding = 'utf-8'

    if request.method == 'GET':
        to_render = {}

        with connections['OpenEduDB'].cursor() as cursor:
            # 計算每年每月的註冊人數
            nowYear = datetime.today().year
            startYear = 2014
            countYear = startYear

            maxPeople = [0 for i in range(nowYear-startYear+1)]
            everyYearMonthPeople = []

            while countYear <= nowYear:
                index = countYear - 2014

                # 搜尋該年的註冊總人數
                cursor.execute(
                    "SELECT id,date_joined "
                    "FROM auth_user "
                    "WHERE date_joined < '" + str(countYear+1) + "-01-01' AND date_joined > '" + str(countYear) + "-01-01'"
                )
                result = namedtuplefetchall(cursor)

                everyMonthPeople = [0 for i in range(12)]

                # 統計
                for rs in result:
                    maxPeople[index] += 1
                    thisDate = str(rs.date_joined)
                    thisMonth = datetime.strptime(thisDate, '%Y-%m-%d %H:%M:%S').month - 1
                    everyMonthPeople[thisMonth] += 1

                everyYearMonthPeople.append(everyMonthPeople.copy())
                countYear += 1

            allRegisterPeople = 0
            for i in range(len(maxPeople)):
                allRegisterPeople += maxPeople[i]

            to_render['registered_All'] = '{:,}'.format(allRegisterPeople)
            to_render['everyYearMonthPeople'] = everyYearMonthPeople

            # 今日登入人數
            todayLogin = 0
            cursor.execute(
                "SELECT count(*) as number "
                "FROM edxapp.auth_user "
                "WHERE last_login > %s", [datetime.strftime(datetime.today(), '%Y-%m-%d')]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                todayLogin = int(rs.number)

            to_render['todayLogin'] = todayLogin

        with connections['ResultDB'].cursor() as cursor:
            # 取得資料最後更新日期
            cursor.execute("SELECT 統計日期 FROM course_total_data_v2")
            result = namedtuplefetchall(cursor)

            finalUpdate_course_total_data = ''
            for rs in result:
                finalUpdate_course_total_data = str(rs.統計日期)

            to_render['finalUpdate_course_total_data'] = finalUpdate_course_total_data

            # 計算課程總數
            max_course = 0
            cursor.execute(
                "select * from course_total_data_v2 where 統計日期 = %s", [finalUpdate_course_total_data]
            )
            result = namedtuplefetchall(cursor)
            for rs in result:
                max_course += 1

            to_render['course_All'] = '{:,}'.format(max_course)

            # 計算開課中課程數
            studyingCourse = 0
            now = datetime.strftime(datetime.today(), '%Y-%m-%d')
            cursor.execute(
                "SELECT * "
                "FROM course_total_data_v2  "
                "WHERE start_date < %s and end_date > %s and 統計日期 = %s", [now, now, finalUpdate_course_total_data]
            )
            result = namedtuplefetchall(cursor)

            studyingCourse = len(result)
            to_render['studyingCourse'] = studyingCourse

            # 最近一年日期
            recentYearDay = []
            # 近一年登入人數
            YearLogin = []

            join_count = 0
            loginUpdate = ''
            jsonObject = {}
            jsonArray_temp = []

            cursor.execute(
                "SELECT max(date) as A from edxresult.login_date"
            )
            result = namedtuplefetchall(cursor)
            for rs in result:
                loginUpdate = str(rs.A)

            now1 = datetime.today()
            longday = (now1 - datetime.strptime(loginUpdate, '%Y-%m-%d')).days
            now1 = now1 + timedelta(days=-longday)
            now1 = now1 + timedelta(days=-729)

            cursor.execute(
                "SELECT date,count(distinct(user_id)) as loginPeople "
                "FROM edxresult.login_date "
                "WHERE date >= %s group by date", [datetime.strftime(now1, '%Y-%m-%d')]
            )
            result = namedtuplefetchall(cursor)
            recentYearDay = ['' for i in range(730)]
            YearLogin = [0 for i in range(730)]
            day = 0

            i=0
            while i < len(result):
                recentYearDay[day] = datetime.strftime(now1, '%Y-%m-%d')
                if str(result[i].date) == datetime.strftime(now1, '%Y-%m-%d'):
                    YearLogin[day] = int(result[i].loginPeople)
                else:
                    YearLogin[day] = 0
                    i = i-1

                day += 1
                now1 = now1 + timedelta(days=1)
                i = i+1

            length = math.ceil(len(recentYearDay) / 2)
            for join_count in range(length):
                jsonObject.clear()
                jsonObject['date'] = recentYearDay[join_count+365]
                jsonObject['value'] = YearLogin[join_count]
                jsonObject['value2'] = YearLogin[join_count+365]
                jsonArray_temp.append(jsonObject.copy())

            to_render['recentYearLogin'] = json.dumps(jsonArray_temp)
            to_render['test'] = YearLogin
            to_render['finalUpdate_recent_Year_Login'] = recentYearDay[len(recentYearDay)-1]

            # 近一月內課程登入人數排名
            courseLogin = [['' for i in range(4)] for i in range(10)]
            k = 0
            cursor.execute(
                "select course_name, course_id, 課程代碼, login_count_month "
                "from course_total_data_v2 "
                "where 統計日期 = %s order by login_count_month desc", [str(finalUpdate_course_total_data)]
            )
            result = namedtuplefetchall(cursor)
            for rs in result:
                if k < 10:
                    courseLogin[k][0] = str(rs.course_name)
                    courseLogin[k][1] = str(rs.course_id)
                    courseLogin[k][2] = '{:,}'.format(int(rs.login_count_month))
                    courseLogin[k][3] = str(rs.課程代碼)
                    k += 1
                else:
                    break

            to_render['courseLogin'] = courseLogin

            return render(request, 'index-admin.html', to_render)


def justnothing(request):
    request.encoding = 'utf-8'
    to_render = {}

    # 各年度每個月分的上下底，搜尋統計用，假設要找四月人數，就要找在三月最後一天之後，及五月第一天之前
    everyMonthTopAndBottomToSearch_2014 = [
        "2014-04-30", "2014-05-01", "2014-05-31", "2014-06-01", "2014-06-30", "2014-07-01", "2014-07-31", "2014-08-01",
        "2014-08-31", "2014-09-01", "2014-09-30", "2014-10-01", "2014-10-31", "2014-11-01", "2014-11-30", "2014-12-01",
        "2014-12-31", "2015-01-01"
    ]
    everyMonthTopAndBottomToSearch_2015 = [
        "2014-12-31", "2015-01-01", "2015-01-31", "2015-02-01", "2015-02-28", "2015-03-01", "2015-03-31", "2015-04-01",
        "2015-04-30", "2015-05-01", "2015-05-31", "2015-06-01", "2015-06-30", "2015-07-01", "2015-07-31", "2015-08-01",
        "2015-08-31", "2015-09-01", "2015-09-30", "2015-10-01", "2015-10-31", "2015-11-01", "2015-11-30", "2015-12-01",
        "2015-12-31", "2016-01-01"
    ]
    everyMonthTopAndBottomToSearch_2016 = [
        "2015-12-31", "2016-01-01", "2016-01-31", "2016-02-01", "2016-02-29", "2016-03-01", "2016-03-31", "2016-04-01",
        "2016-04-30", "2016-05-01", "2016-05-31", "2016-06-01", "2016-06-30", "2016-07-01", "2016-07-31", "2016-08-01",
        "2016-08-31", "2016-09-01", "2016-09-30", "2016-10-01", "2016-10-31", "2016-11-01", "2016-11-30", "2016-12-01",
        "2016-12-31", "2017-01-01"
    ]
    everyMonthTopAndBottomToSearch_2017 = [
        "2016-12-31", "2017-01-01", "2017-01-31", "2017-02-01", "2017-02-28", "2017-03-01", "2017-03-31", "2017-04-01",
        "2017-04-30", "2017-05-01", "2017-05-31", "2017-06-01", "2017-06-30", "2017-07-01", "2017-07-31", "2017-08-01",
        "2017-08-31", "2017-09-01", "2017-09-30", "2017-10-01", "2017-10-31", "2017-11-01", "2017-11-30", "2017-12-01",
        "2017-12-31", "2018-01-01"
    ]

    # 每年註冊人數總和
    max_2014 = 0
    max_2015 = 0
    max_2016 = 0
    max_2017 = 0
    max_course = 0

    # 最近兩週內課程登入人數排名
    courseRecentLogin = [[None for i in range(4)] for i in range(10)]

    # 近一月內課程登入人數排名
    courseLogin = [[None for i in range(4)] for i in range(10)]

    # 開課中課程
    studyingCourse = 0

    # 最近一年日期
    recentYearDay = []

    # 資料庫更新日
    finalUpdate_course_total_data = None

    # 今日登入人數
    todayLogin = 0

    jsonArray_temp = []

    if request.method == 'GET':
        select = request.GET.get('optradio', None)
        recent = request.GET.get('recent', None)
        recentRangeStart = request.GET.get('recentRangeStart', None)
        recentRangeEnd = request.GET.get('recentRangeEnd', None)
        Recentnow = datetime.now()

        # 存放每個月分的人數，openedu從2014年5月開始
        numberOfPeopleEveryMonth_2014 = [0 for i in range(8)]
        numberOfPeopleEveryMonth_2015 = [0 for i in range(12)]
        numberOfPeopleEveryMonth_2016 = [0 for i in range(12)]
        numberOfPeopleEveryMonth_2017 = [0 for i in range(12)]

        request.GET = request.GET.copy()

        if select is None:
            to_render['recent'] = 7
            to_render['select'] = 0
            Recentnow = Recentnow + timedelta(days=1)
            to_render['recentRangeEnd'] = Recentnow.strftime('%Y-%m-%d')
            Recentnow = Recentnow + timedelta(days=-7)
            to_render['recentRangeStart'] = Recentnow.strftime('%Y-%m-%d')
            select = '0'
            recent = '7'

        elif select == '0':
            to_render['recent'] = recent
            to_render['select'] = select
            Recentnow = Recentnow + timedelta(days=1)
            to_render['recentRangeEnd'] = Recentnow.strftime('%Y-%m-%d')
            Recentnow = Recentnow + timedelta(days=-7)
            to_render['recentRangeStart'] = Recentnow.strftime('%Y-%m-%d')

        elif select == '1':
            to_render['recent'] = 7
            to_render['select'] = select
            to_render['recentRangeStart'] = recentRangeStart
            to_render['recentRangeEnd'] = recentRangeEnd

        # 以下使用OpenEduDB
        try:
            '''
            ------------2014------------
            '''
            # 搜尋2014年的註冊總人數
            cursor = connections['OpenEduDB'].cursor()  # OpenEduDB
            cursor.execute(
                "SELECT id,date_joined FROM auth_user where date_joined < '2015-01-01' AND date_joined > '2014-05-01'"
            )
            result = namedtuplefetchall(cursor)
            # 統計2014總註冊人數
            max_2014 = len(result)

            # 該變數為存放所以2014年資料，並將資料存入
            data_2014 = []
            for i in range(max_2014):
                data_2014.append(result[i].date_joined)

            # count為跑迴圈用，month_20XX用來作為numberOfPeopleEveryMonth_20XX中的月份
            count = 0
            month_2014 = 0

            # 判斷並計算每月人數
            while count < max_2014:
                # 判斷是否在上個月最後一天之後，及下個月第一天之前
                if everyMonthTopAndBottomToSearch_2014[month_2014 * 2] < str(data_2014[count]) < \
                        everyMonthTopAndBottomToSearch_2014[month_2014 * 2 + 3]:
                    # 若是的話，該月人數+1
                    numberOfPeopleEveryMonth_2014[month_2014] = numberOfPeopleEveryMonth_2014[month_2014] + 1
                else:
                    # 因為月份資料有經過排序，所以當有一筆資料不符合，就將月份+1
                    month_2014 = month_2014 + 1
                    numberOfPeopleEveryMonth_2014[month_2014] = 0
                    # count減1是因為不減的話會略過這筆資料
                count = count + 1
            '''
            ------------2014------------
            '''

            '''
            ------------2015------------
            '''
            # 搜尋2015年的註冊總人數
            cursor.execute(
                "SELECT id,date_joined FROM auth_user where date_joined < '2016-01-01' AND date_joined > '2015-01-01'"
            )
            result = namedtuplefetchall(cursor)
            # 統計2015總註冊人數
            max_2015 = len(result)

            # 該變數為存放所以2015年資料，並將資料存入
            data_2015 = []
            for i in range(max_2015):
                data_2015.append(result[i].date_joined)

            # count為跑迴圈用，month_20XX用來作為numberOfPeopleEveryMonth_20XX中的月份
            count = 0
            month_2015 = 0

            # 判斷並計算每月人數
            while count < max_2015:
                # 判斷是否在上個月最後一天之後，及下個月第一天之前
                if everyMonthTopAndBottomToSearch_2015[month_2015 * 2] < str(data_2015[count]) < \
                        everyMonthTopAndBottomToSearch_2015[month_2015 * 2 + 3]:
                    # 若是的話，該月人數+1
                    numberOfPeopleEveryMonth_2015[month_2015] = numberOfPeopleEveryMonth_2015[month_2015] + 1
                else:
                    # 因為月份資料有經過排序，所以當有一筆資料不符合，就將月份+1
                    month_2015 = month_2015 + 1
                    numberOfPeopleEveryMonth_2015[month_2015] = 0
                    # count減1是因為不減的話會略過這筆資料
                count = count + 1
            '''
            ------------2015------------
            '''

            '''
            ------------2016------------
            '''
            # 搜尋2016年的註冊總人數
            cursor.execute(
                "SELECT id,date_joined FROM auth_user where date_joined < '2017-01-01' AND date_joined > '2016-01-01'"
            )
            result = namedtuplefetchall(cursor)
            # 統計2016總註冊人數
            max_2016 = len(result)

            # 該變數為存放所以2016年資料，並將資料存入
            data_2016 = []
            for i in range(max_2016):
                data_2016.append(result[i].date_joined)

            # count為跑迴圈用，month_20XX用來作為numberOfPeopleEveryMonth_20XX中的月份
            count = 0
            month_2016 = 0

            # 判斷並計算每月人數
            while count < max_2016:
                # 判斷是否在上個月最後一天之後，及下個月第一天之前
                if everyMonthTopAndBottomToSearch_2016[month_2016 * 2] < str(data_2016[count]) < \
                        everyMonthTopAndBottomToSearch_2016[month_2016 * 2 + 3]:
                    # 若是的話，該月人數+1
                    numberOfPeopleEveryMonth_2016[month_2016] = numberOfPeopleEveryMonth_2016[month_2016] + 1
                else:
                    # 因為月份資料有經過排序，所以當有一筆資料不符合，就將月份+1
                    month_2016 = month_2016 + 1
                    numberOfPeopleEveryMonth_2016[month_2016] = 0
                    # count減1是因為不減的話會略過這筆資料
                count = count + 1
            '''
            ------------2016------------
            '''

            '''
            2017年
            '''
            # 搜尋2017年的註冊總人數
            cursor.execute(
                "SELECT id,date_joined FROM auth_user where date_joined < '2018-01-01' AND date_joined > '2017-01-01'"
            )
            result = namedtuplefetchall(cursor)
            # 統計2017總註冊人數
            max_2017 = len(result)

            # 該變數為存放所以2016年資料, 並將資料存入
            data_2017 = []
            for i in range(max_2017):
                data_2017.append(result[i].date_joined)

            # count為跑迴圈用, month_20XX用來作為numberOfPeopleEveryMonth_20XX中的月份
            count = 0
            month_2017 = 0

            # 判斷並計算每月人數
            while count < max_2017:
                # 判斷是否在上個月最後一天之後，及下個月第一天之前
                if everyMonthTopAndBottomToSearch_2017[month_2017 * 2] < str(data_2017[count]) < \
                        everyMonthTopAndBottomToSearch_2017[month_2017 * 2 + 3]:
                    # 若是的話，該月人數+1
                    numberOfPeopleEveryMonth_2017[month_2017] = numberOfPeopleEveryMonth_2017[month_2017] + 1
                else:
                    # 因為月份資料有經過排序, 所以當有一筆資料不符合, 就將月份+1
                    month_2017 = month_2017 + 1
                    numberOfPeopleEveryMonth_2017[month_2017] = 0
                    # count減1是因為不減的話會略過這筆資料
                count = count + 1
            '''
            2017年
            '''

            '''
            今日登入人數
            '''
            now = datetime.today()
            now = now.strftime('%Y-%m-%d')
            cursor.execute(
                "SELECT count(*) as number FROM auth_user where last_login > %s", [now]
            )
            result = namedtuplefetchall(cursor)
            for rs in result:
                todayLogin = rs.number
            ''' 今日登入人數完'''

            cursor.close()

        except DatabaseError:
            pass

        try:
            # 顯示資料
            cursor = connections['ResultDB'].cursor()
            cursor.execute(
                "select * from course_total_data_v2"
            )
            result = namedtuplefetchall(cursor)

            finalUpdate_course_total_data = ''
            i = 0
            maxRS = len(result)
            for rs in result:
                if i + 1 == maxRS - 1:
                    finalUpdate_course_total_data = rs.統計日期
                    break
                i = i + 1

            cursor.execute(
                "select * from course_total_data_v2 where 統計日期 = %s", [finalUpdate_course_total_data]
            )
            result = namedtuplefetchall(cursor)

            max_course = len(result)
            # 顯示資料
            # ----------------------------------------

            # ----------------------------------------
            # 自學課程
            now = datetime.today().strftime('%Y-%m-%d')
            cursor.execute(
                "SELECT * FROM course_total_data_v2  where start_date < %s and end_date > %s and 統計日期 = %s"
                , [now, now, finalUpdate_course_total_data]
            )
            result = namedtuplefetchall(cursor)

            studyingCourse = len(result)
            # 自學課程
            # ----------------------------------------

            # 近一年登入數
            loginUpdate = None
            cursor.execute(
                "SELECT max(date) as A from edxresult.login_date"
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                loginUpdate = rs.A

            now = datetime.today()
            longday = (now - datetime.strptime(loginUpdate, '%Y-%m-%d')).days
            now = now + timedelta(days=-longday)
            now = now + timedelta(days=-729)

            cursor.execute(
                "SELECT date,count(distinct(user_id)) as loginPeople FROM edxresult.login_date "
                "where date>= %s group by date", [now.strftime('%Y-%m-%d')]
            )
            result = namedtuplefetchall(cursor)

            # recentYearDay:最近一年日期, YearLogin:近一年登入數
            recentYearDay = [None for i in range(730)]
            YearLogin = [0 for i in range(730)]
            day = 0
            for i in range(len(result)):
                recentYearDay[day] = now.strftime('%Y-%m-%d')

                if result[i].date == now.strftime('%Y-%m-%d'):
                    YearLogin[day] = result[i].loginPeople
                else:
                    YearLogin[day] = 0
                    i = i - 1

                print(str(day) + ' ' + str(recentYearDay[day]) + ' ' + str(YearLogin[day]))
                day = day + 1
                now = now + timedelta(days=1)

            count = 0
            jsonArray_temp = []
            forloop = int(len(recentYearDay) / 2)
            while count < forloop:
                jsonObject = {}
                jsonObject['date'] = recentYearDay[count + 365]
                jsonObject['value'] = YearLogin[count]
                jsonObject['value2'] = YearLogin[count + 365]
                jsonArray_temp.append(jsonObject.copy())
                count = count + 1

            # jsonArray_temp = json.dumps(array)
            # 近一年登入人數
            # -----------------------------

            # 最近一個月內, 課程參與度排行
            # courseLogin是用來存放近一個月內課程登入人數排名
            i = 0
            cursor.execute(
                "select course_name,course_id,`課程代碼`,login_count_month from course_total_data_v2 "
                "where 統計日期 = %s order by login_count_month desc", [finalUpdate_course_total_data]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                if i < 10:
                    courseLogin[i][0] = rs.course_name
                    courseLogin[i][1] = rs.course_id
                    courseLogin[i][2] = rs.login_count_month
                    courseLogin[i][3] = rs.課程代碼
                    i = i + 1
                else:
                    break
            # -----------------------------

            cursor.close()

        except DatabaseError:
            print('can\'t connect mysql database')

        to_render['numberOfPeopleEveryMonth_2014'] = numberOfPeopleEveryMonth_2014
        to_render['numberOfPeopleEveryMonth_2015'] = numberOfPeopleEveryMonth_2015
        to_render['numberOfPeopleEveryMonth_2016'] = numberOfPeopleEveryMonth_2016
        to_render['numberOfPeopleEveryMonth_2017'] = numberOfPeopleEveryMonth_2017

        to_render['registered_All'] = '{:,}'.format(max_2017 + max_2016 + max_2015 + max_2014)
        to_render['course_All'] = '{:,}'.format(max_course)
        to_render['studyingCourse'] = studyingCourse
        to_render['todayLogin'] = todayLogin
        to_render['recentYearLogin'] = json.dumps(jsonArray_temp)
        to_render['courseRecentLogin'] = courseRecentLogin
        to_render['courseLogin'] = courseLogin
        to_render['finalUpdate_course_total_data'] = finalUpdate_course_total_data
        to_render['finalUpdate_recent_Year_Login'] = recentYearDay[-10]

        # return render(request, 'index-admin.html', to_render)

