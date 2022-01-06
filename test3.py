# -*- coding: UTF-8 -*-
# 載入相關套件
# import datetime,function,indicator
import datetime,function
import sys

# 取得當天日期
Date=datetime.datetime.now().strftime("%Y%m%d")
# 定義要操作的股票
Sid=sys.argv[1]
# 定義要使用的券商、張數
BrokerID='Capital_Future'
OrderNum='1'

# 設定固定時間進場、出場
StartTime = datetime.datetime.strptime(Date+'09:00:00.00','%Y%m%d%H:%M:%S.%f')
EndTime = datetime.datetime.strptime(Date+'13:26:00.00','%Y%m%d%H:%M:%S.%f')

print(StartTime, " ", EndTime)
    
# 進場策略
Index=0
for i in function.getSIDMatch(Date,Sid):
    print("i:", i)
    print("i[0]:", i[0])
    #time=datetime.datetime.strptime(Date+i[0],'%Y%m%d%H:%M:%S.%f')
    #time=datetime.datetime.strptime(i[0],'%Y%m%d%H:%M:%S.%f')
    time=datetime.datetime.strptime(i[0],'%Y/%m/%d %H:%M:%S.%f')
    price=float(i[2])
    ask=float(i[5])
    bid=float(i[6])
    print(time, price)
    
    # 現在時間 大於 進場時間
    if time > StartTime:
            Index=1
            OrderTime=time
            OrderPrice=price
            # 若要實單交易 可以將註解取消
            #OrderInfo=Order(BrokerID,Sid,'B',bid,OrderNum,'0')
            #OrderPrice=OrderInfo[0][4]
            #OrderTime=datetime.datetime.strptime(OrderInfo[0][6],'%Y/%m/%d %H:%M:%S')
            print(OrderTime,"Order Buy Price:",OrderPrice,"Success!")
            #break

   
