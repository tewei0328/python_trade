# 載入必要套件
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from haohaninfo.MicroTest import microtest_db
import numpy as np
import haohaninfo,time

# 下單部位管理物件
class Record():
    def __init__(self ):
        # 儲存績效
        self.Profit=[]
        # 未平倉
        self.OpenInterestQty=0
        self.OpenInterest=[]
        # 交易紀錄總計
        self.TradeRecord=[]
    # 進場紀錄
    def Order(self, BS,Product,OrderTime,OrderPrice,OrderQty):
        if BS=='B' or BS=='Buy':
            for i in range(OrderQty):
                self.OpenInterest.append([1,Product,OrderTime,OrderPrice])
                self.OpenInterestQty +=1
        elif BS=='S' or BS=='Sell':
            for i in range(OrderQty):
                self.OpenInterest.append([-1,Product,OrderTime,OrderPrice])
                self.OpenInterestQty -=1
    # 出場紀錄(買賣別需與進場相反，多單進場則空單出場)
    def Cover(self, BS,Product,CoverTime,CoverPrice,CoverQty):
        if BS=='S' or BS=='Sell':
            for i in range(CoverQty):
                # 取得多單未平倉部位
                TmpInterest=[ i for i in self.OpenInterest if i[0]==1 ][0]
                if TmpInterest != []:
                    # 清除未平倉紀錄
                    self.OpenInterest.remove(TmpInterest)
                    self.OpenInterestQty -=1
                    # 新增交易紀錄
                    self.TradeRecord.append(['B',TmpInterest[1],TmpInterest[2],TmpInterest[3],CoverTime,CoverPrice])
                    self.Profit.append(CoverPrice-TmpInterest[3])
                else:
                    print('尚無進場')
        elif BS=='B' or BS=='Buy':
            for i in range(CoverQty):
                # 取得空單未平倉部位
                TmpInterest=[ i for i in self.OpenInterest if i[0]==-1 ][0]
                if TmpInterest != []:
                    # 清除未平倉紀錄
                    self.OpenInterest.remove(TmpInterest)
                    self.OpenInterestQty +=1
                    # 新增交易紀錄
                    self.TradeRecord.append(['S',TmpInterest[1],TmpInterest[2],TmpInterest[3],CoverTime,CoverPrice])
                    self.Profit.append(TmpInterest[3]-CoverPrice)
                else:
                    print('尚無進場')
    # 取得當前未平倉量
    def GetOpenInterest(self):               
        # 取得未平倉量
        return self.OpenInterestQty
    # 取得交易紀錄
    def GetTradeRecord(self):               
        # 取得未平倉量
        return self.TradeRecord   
    # 取得交易績效
    def GetProfit(self):       
        return self.Profit  
    # 取得交易績效
    def GetTotalProfit(self):  
        return sum(self.Profit)
    # 取得平均交易績效
    def GetAverageProfit(self): 
        if len(self.Profit)>0: 
            return sum(self.Profit)/len(self.Profit)
        else:
            return None
    # 取得勝率
    def GetWinRate(self):
        if len(self.Profit)>0:  
            WinProfit = [ i for i in self.Profit if i > 0 ]
            return len(WinProfit)/len(self.Profit)
        else:
            return None
    # 最大連續虧損
    def GetAccLoss(self):
        AccLoss = 0
        MaxAccLoss = 0
        for p in self.Profit:
            if p <= 0:
                AccLoss+=p
                if AccLoss < MaxAccLoss:
                    MaxAccLoss=AccLoss
            else:
                AccLoss=0
        return MaxAccLoss
    # 最大資金回落(MDD)
    def GetMDD(self):
        MDD,Capital,MaxCapital = 0,0,0
        for p in self.Profit:
            Capital += p
            MaxCapital = max(MaxCapital,Capital)
            DD = MaxCapital - Capital
            MDD = max(MDD,DD)
        return MDD
    # 平均獲利 
    def GetAverEarn(self):
        if len( [ i for i in self.Profit if i > 0 ] )>0:  
            WinProfit = [ i for i in self.Profit if i > 0 ]
            return sum(WinProfit)/len(WinProfit)
        else:
            return None
    # 平均虧損
    def GetAverLoss(self):
        if len( [ i for i in self.Profit if i < 0 ] )>0:  
            FailProfit = [ i for i in self.Profit if i < 0 ]
            return sum(FailProfit)/len(FailProfit)
        else:
            return None
    # 產出交易績效圖
    def GeneratorProfitChart(self,StrategyName='Strategy'):
        # 定義圖表
        ax1 = plt.subplot(111)
        # 計算累計績效
        TotalProfit=[0]
        for i in self.Profit:
            TotalProfit.append(TotalProfit[-1]+i)
        # 繪製圖形
        ax1.plot( TotalProfit  , '-', linewidth=1 )
        #定義標頭
        ax1.set_title('Profit')
        plt.show()    # 顯示繪製圖表
        # plt.savefig(StrategyName+'.png') #儲存繪製圖表
    
    
try:
    GOC = haohaninfo.GOrder.GOCommand()
    GOQ = haohaninfo.GOrder.GOQuote()
except:
    print('GOrder尚未啟動，請確認程式運作情況，否則下單指令無法運作')
    
# 下單委託單取得成交回報
def OrderAndMatch(Broker,Product,BS,Price,Qty,TradeType,OrderType):
    # 送出交易委託
    # print(Broker, Product, BS, Price, Qty, TradeType, OrderType)
    OrderNo=GOC.Order(Broker, Product, BS, Price, Qty, TradeType, OrderType)
    # print(OrderNo)
    # 判斷是否委託成功(這邊以群益證為例)
    if OrderNo[:4] != 'Fail':
        while True:
            # 取得成交帳務
            MatchInfo=GOC.MatchAccount(Broker,OrderNo)
            # 判斷是否成交
            if MatchInfo != []:
                # 成交則回傳
                return MatchInfo[0].split(',')
            # 稍等0.5秒
            time.sleep(0.5)
    else:
        return False
            
# 限價委託單到期刪單(N秒尚未成交刪單[預設10])
def OrderAndDelete(Broker,Product,BS,Price,Qty,TradeType,OrderType,Wait=10):
    # 送出交易委託
    # print(Broker, Product, BS, Price, Qty, TradeType, OrderType)
    OrderNo=GOC.Order(Broker, Product, BS, Price, Qty, TradeType, OrderType)
    # 設定刪單時間
    EndTime=time.time()+Wait
    # 判斷是否委託成功(這邊以群益證為例)
    if OrderNo != '委託失敗':
        # 若大於刪單時間則跳出迴圈
        while time.time() < EndTime:
            # 取得成交帳務
            MatchInfo=GOC.MatchAccount(Broker,OrderNo)
            # 判斷是否成交
            if MatchInfo != []:
                # 成交則回傳
                return MatchInfo[0].split(',')
            # 稍等0.5秒
            time.sleep(0.5)
            print(OrderNo,'尚未成交')
        # 刪單並確認委託成功刪除
        GOC.Delete(Broker,OrderNo)
        GOC.GetAccount(Broker,OrderNo)
        print('到期刪單')
        return False
    else:
        return False            

# 取得股票價格跳動點陣列(用來計算當前股價相對N Tick的值)
StockPriceList=[]
StockPriceList.extend([ i/100 for i in range(1,1001,1) ])
StockPriceList.extend([ i/100 for i in range(1005,5005,5) ])
StockPriceList.extend([ i/10 for i in range(501,1001,1) ])
StockPriceList.extend([ i/10 for i in range(1005,5005,5) ])
StockPriceList.extend([ i for i in range(501,1001,1) ])
StockPriceList.extend([ i for i in range(1005,10005,5) ])

# 範圍市價單(掛上下N Tick價[預設3]、N秒尚未成交刪單[預設10])
def OrderRangeMKT(Broker,Product,BS,Qty,TradeType,OrderType,OrderDiffTick=3,Wait=10): 
    # 新增訂閱要下單的商品，預防沒有取到該商品報價
    GOC.AddQuote(Broker,Product,True)
    # 取得委託商品的成交資訊
    MatchInfo=GOQ.SubscribeLast(Broker,'match',Product)
    MatchPrice=float(MatchInfo[2])
    # 成交價正負N Tick計算
    OrderPoint=StockPriceList[StockPriceList.index(MatchPrice)+OrderDiffTick]
    # 顯示交易委託參數
    print(Broker, Product, BS, OrderPoint, Qty, TradeType, OrderType)
    # 限價委託單到期刪單
    OrderInfo=OrderAndDelete(Broker,Product,BS,str(OrderPoint),Qty,TradeType,OrderType,Wait=10)
    return OrderInfo

# 範圍市價單(預設非當沖、倉別自動、掛上下N檔價1-5[預設3]、N秒尚未成交刪單[預設10])
def RangeMKTDeal(Broker,Product,BS, Qty,TradeType,OrderType,OrderDiffTick=3,Wait=10):
    # 防止例外狀況，最多下三次單
    for i in range(1,4):
        # 顯示第幾次執行
        print('第',i,'次執行委託',Broker,Product,BS,Qty,TradeType,OrderType,OrderDiffTick,Wait)
        # 執行範圍市價單
        OrderInfo=OrderRangeMKT(Broker,Product,BS,Qty,TradeType,OrderType,OrderDiffTick,Wait)
        if OrderInfo != False:
            return OrderInfo
    # 三次委託皆失敗，建議當日不做交易
    return False
