import datetime
import function

# 取得當天日期
Date=datetime.datetime.now().strftime("%Y%m%d")

for i in function.getSIDMatch(Date,'TX00'):
  print(i)
