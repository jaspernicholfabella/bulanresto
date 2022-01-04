import datetime
from datetimerange import DateTimeRange
import calendar

def convert_time_24(str_time):
    if 'AM' in str_time:
        return int(str_time.split(':')[0])
    elif 'PM' in str_time:
        return int(str_time.split(':')[0]) + 12

def check_quarter(month):
    if any(x == month for x in [1,2,3]):
        return [1,3]
    elif any(x == month for x in [4,5,6]):
        return [4,6]
    elif any(x == month for x in [7,8,9]):
        return [7,9]
    elif any(x == month for x in [10,11,12]):
        return [10,12]


def number_to_month(month):
    no_month = {
        1 : 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }

    return no_month[month]


def setup_reservations(option_update='monthly',
                       skip_weekends=False,
                       business_hours_start_string='8:00 AM',
                       business_hours_end_string='6:00 PM',
                       gap_in_minutes = 60
                       ):

    reservation_hours = []
    reservation_month_days = {}
    reservation_hours.append(business_hours_start_string)
    business_hours_start = convert_time_24(business_hours_start_string)
    business_hours_end = convert_time_24(business_hours_end_string)


    if option_update == 'monthly':
        temp_reservation_days = []
        time_range = DateTimeRange(datetime.datetime.now(),
                                   datetime.datetime.strptime(f'{datetime.datetime.now().year}-12-31', '%Y-%m-%d'))

        if skip_weekends:
            for value in time_range.range(datetime.timedelta(days=1)):
                if value.month == datetime.datetime.now().month:
                    if value.weekday():
                        temp_reservation_days.append(value.day)
        else:
            for value in time_range.range(datetime.timedelta(days=1)):
                if value.month == datetime.datetime.now().month:
                     temp_reservation_days.append(value.day)

        reservation_month_days.update({number_to_month(datetime.datetime.now().month):temp_reservation_days})


    elif option_update == 'quarterly':
        start_month = check_quarter(datetime.datetime.now().month)[0]
        end_month = check_quarter(datetime.datetime.now().month)[1]
        for i in range(start_month, end_month+1):
            temp_current_day = []
            date_end = datetime.datetime.strptime(f'{datetime.datetime.now().year}-{str(i)}-1', '%Y-%m-%d')
            d_end = date_end.replace(day=calendar.monthrange(date_end.year, date_end.month)[1])
            time_range = DateTimeRange(datetime.datetime.strptime(f'{datetime.datetime.now().year}-{str(i)}-1','%Y-%m-%d'),d_end)
            for value in time_range.range(datetime.timedelta(days=1)):
                if skip_weekends:
                    if value.weekday():
                        if i == datetime.datetime.now().month:
                            if value.day >= datetime.datetime.now().day:
                                temp_current_day.append(value.day)
                            else:
                                pass
                        else:
                            temp_current_day.append(value.day)
                else:
                    if i == datetime.datetime.now().month:
                        if value.day >= datetime.datetime.now().day:
                            temp_current_day.append(value.day)
                        else:
                            pass
                    else:
                        temp_current_day.append(value.day)

            reservation_month_days.update({number_to_month(i): temp_current_day})



    elif option_update == 'annual':
        annual_time_range = DateTimeRange(datetime.datetime.now(),
                                   datetime.datetime.strptime(f'{datetime.datetime.now().year}-12-31', '%Y-%m-%d'),)

        current_month = datetime.datetime.now().month
        current_day = 0

        for month_val in annual_time_range.range(datetime.timedelta(days=31)):
            date_end = datetime.datetime.strptime(f'{datetime.datetime.now().year}-{str(month_val.month)}-1', '%Y-%m-%d')
            d_end = date_end.replace(day = calendar.monthrange(date_end.year, date_end.month)[1])
            time_range = DateTimeRange(datetime.datetime.strptime(f'{datetime.datetime.now().year}-{str(month_val.month)}-1','%Y-%m-%d'),d_end)
            temp_current_day = []
            for value in time_range.range(datetime.timedelta(days=1)):
                if skip_weekends:
                    if value.weekday():
                        if month_val.month == datetime.datetime.now().month:
                            if value.day >= datetime.datetime.now().day:
                                temp_current_day.append(value.day)
                            else:
                                pass
                        else:
                            temp_current_day.append(value.day)
                else:
                    if month_val.month == datetime.datetime.now().month:
                        if value.day >= datetime.datetime.now().day:
                            temp_current_day.append(value.day)
                        else:
                            pass
                    else:
                        temp_current_day.append(value.day)

            reservation_month_days.update({number_to_month(month_val.month):temp_current_day})




    delta = datetime.timedelta(minutes=gap_in_minutes)


    if business_hours_start < business_hours_end:
        current_time = business_hours_start
        while(True):
            t = datetime.time(current_time, 0, 0)
            temp = str(((datetime.datetime.combine(datetime.date(1,1,1),t) + delta).time()))
            mints = int(temp.split(':')[1]) == 0
            if current_time == business_hours_end and mints:
                break
            elif current_time == business_hours_end and not mints:
                reservation_hours = reservation_hours[:-1]
                break

            d = (datetime.datetime.combine(datetime.date(1, 1, 1), t) + delta).time()
            reservation_hours.append(d.strftime("%I:%M %p"))
            current_time = int(temp.split(':')[0])
    else:
        current_time = business_hours_start
        impass = False
        while (True):
            t = datetime.time(current_time, 0, 0)
            temp = str(((datetime.datetime.combine(datetime.date(1, 1, 1), t) + delta).time()))
            mints = int(temp.split(':')[1]) == 0
            if current_time == 0:
                impass = True
            if impass:
                if current_time == business_hours_end and mints:
                    break
                elif current_time == business_hours_end and not mints:
                    reservation_hours = reservation_hours[:-1]
                    break

            d = (datetime.datetime.combine(datetime.date(1, 1, 1), t) + delta).time()
            reservation_hours.append(d.strftime("%I:%M %p"))
            current_time = int(temp.split(':')[0])

    return reservation_month_days, reservation_hours
