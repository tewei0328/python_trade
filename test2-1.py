import datetime
import function

# 取得當天日期
Date=datetime.datetime.now().strftime("%Y%m%d")

for i in function.getSIDMatch('20220106','TX00'):
  print(i)
