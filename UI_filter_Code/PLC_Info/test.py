from datetime import datetime

first_time = '2023/04/10 12:34:26'#
second_time='2023-04-10 13:34:26'
time_replace= second_time.replace('-','/')
print(time_replace)
time1 = datetime.strptime(first_time, '%Y/%m/%d %H:%M:%S')
tiem2 = datetime.strptime(time_replace, '%Y/%m/%d %H:%M:%S')
time3=tiem2-time1
print(time3)