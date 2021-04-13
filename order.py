# -*- coding: UTF-8 -*-
# tewei: new ver. only for future/option)
#載入相關套件
import subprocess,time

#下單子程式放置位置
ExecPath="C:/gorder/CMD/"

#送出交易委託(new ver. only for future/option)
#1. Capital_Future
#2. ProductId(ex TX00, MTX00)
#3. B: Buy, S: Sell
#4. Price
#5. Qty(口數)
#6. ROD / IOC / FOK
#7. LMT / MKT
#8. 0:非當沖 1:當沖
def OrderLMT(BrokerID,Product,BS,Price,Qty,OrderType):
    print([ExecPath+"Order.exe",BrokerID,Product,BS,Price,Qty,RodIocFok,LmtMkt, '0'])
    OrderNo=subprocess.check_output([ExecPath+"Order.exe",BrokerID,Product,BS,Price,Qty,RodIocFok,LmtMkt,'0']).decode('big5').strip('\r\n')
    return OrderNo

#送出交易委託(old ver. only for stock)
def OrderLMT1(BrokerID,Product,BS,Price,Qty,OrderType):
    print([ExecPath+"Order.exe",BrokerID,Product,BS,Price,Qty,'0',OrderType])
    OrderNo=subprocess.check_output([ExecPath+"Order.exe",BrokerID,Product,BS,Price,Qty,'0',OrderType]).decode('big5').strip('\r\n')
    return OrderNo


#取得下單帳務
def GetAccount(BrokerID,OrderNo):
    OrderInfo=subprocess.check_output([ExecPath+"MatchAccount.exe",BrokerID,OrderNo]).decode('big5').split('\r\n')
    OrderInfo = [ i.split(',') for i in OrderInfo ]
    return OrderInfo
    
#下單並取得帳務回傳
def Order(BrokerID,Product,BS,Price,Qty,OrderType):
    OrderNo=OrderLMT(BrokerID,Product,BS,Price,Qty,OrderType)
    if OrderNo[0:4]!='Fail':
        while 1:
            OrderInfo=GetAccount(BrokerID,OrderNo)
            if OrderInfo[0][0] != 'over':
                return OrderInfo
            else:
                print('尚未成交')
            time.sleep(2)
    else:
        print('下單失敗')
        return False
            
#取消委託
def CancelOrder(BrokerID,OrderNo):
    CancelInfo=subprocess.check_output([ExecPath+"Order.exe",BrokerID,'Delete',OrderNo]).decode('big5').split('\r\n')
    if CancelInfo[0][0:5]=='ERROR':
        print('憑證失效')
        return False
    else:
        print(CancelInfo)
        return True
    
#委託到期刪單
def Order2Cancel(BrokerID,Product,BS,Price,Qty,OrderType,Sec):
    OrderNo=OrderLMT(BrokerID,Product,BS,Price,Qty,OrderType)
    StartTime=time.time()
    if OrderNo[0:4]!='Fail':
        while time.time()-StartTime<Sec:
            time.sleep(2)
            OrderInfo=GetAccount(BrokerID,OrderNo)
            if OrderInfo[0][0] != 'over':
                return OrderInfo   
        if CancelOrder(BrokerID,OrderNo):
            print('刪單成功')
            return 1
        else:
            print('刪單失敗')
            return 2
    else:
        print('下單失敗')
        return False
        
#範圍市價單
def Order2Deal(BrokerID,Product,BS,Price,Qty,OrderType,Tick,Sec,n):
    num=0
    while num<n:
        if BS=='B':
            OrderPrice=str(round(float(Price)+(num*Tick),2))
        elif BS=='S':
            OrderPrice=str(round(float(Price)-(num*Tick),2))
        OrderInfo=Order2Cancel(BrokerID,Product,BS,OrderPrice,Qty,OrderType,Sec)
        if OrderInfo == False:
            print('下單失敗不繼續')
            return False
        if OrderInfo == 1:
            print('再次下單')
            num+=1
        elif OrderInfo == 2:
            print('發生錯誤，不再下單')
            return False
        else:
            return OrderInfo
    print('超過指定次數，不進行下單')
    return False
            
#取得總帳務            
def GetAllAccount(BrokerID):
    AccInfo=subprocess.check_output([ExecPath+"GetAccount.exe",BrokerID,'All']).decode('big5').split('\r\n')
    return AccInfo
                
#取得股票庫存
def GetStock(BrokerID):
    StockInfo=subprocess.check_output([ExecPath+"GetInStock.exe",BrokerID]).decode('big5').split('\r\n')
    return StockInfo
            
