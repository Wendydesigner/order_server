#encoding:utf-8
#!/usr/bin/env python3

import json, sys, ast
import flask, flask_cors
from flask import request,make_response,jsonify
from flask_cors import CORS

def divide_set(L,k):#把L分成k组
    if k==0:return [[[]]]
    if k==1:return [[L]]
    L1=[];L2=[]
    if len(L)-1>=k:
        L2=divide_set(L[1:],k)  #把除了第一个元素之外的分成k组，第一个元素插入到其中
        #print(L2)
    if len(L)>=k:
        L1=divide_set(L[1:],k-1)#把第一个元素作为一组，其他分成k-1组
        #print(L1)
    R=[]#R是三重列表
    
    #把L[0]插入到L2中
    for t in L2:  #遍历L2中每个二重列表，一个二重列表代表一个分组集合
        for i in range(0,len(t)):
            x=t[:i]+[[L[0]]+t[i]]+t[i+1:]#把L[0]拼接到一个集合中的第i个分组中，x是二重列表
            R.append(x)
    
    #把L[0]添加到集合中L1中  
    for e in L1:  #遍历L1的每个元素，e是二重列表，代表一个集合
        e.append([L[0]])
        R.append(e)
    return R

def accurate_price(n,d,f):
    l = []
    minPrice=float("inf")
    for k in range(1, len(n)+1):
        R=divide_set(n,k)
        # R为数组n分成k组得到结果 R=[[1,2],[3]]
        for i in range(len(R)):
            # 计算每单的金额 m = [1,2]
            total=[]
            for m in R[i]:
                s = sum(m)
                # 进行满减
                for p in range(len(d)):
                    if (p==0 and s < d[0][0]): 
                        break
                    if (p==len(d)-1 and s >= d[p][0]):
                        s = s - d[p][1]
                        break
                    if (d[p-1][0]<=s and d[p][0]>s):
                        s = s - d[p-1][1]
                        break
                s = s + f
                total.append(s)
            if (sum(total)<minPrice):
                l=R[i]
                minPrice=sum(total)
    return [l, minPrice]

server = flask.Flask(__name__)
CORS(server, resources=r'/*')
@server.route('/', methods=['get', 'post'])
def main():
    data = request.stream.read()
    data = json.loads(data)
    # data = ast.literal_eval(sys.argv[1])
    # 商品和金额以及数量的对应关系字典型
    products=data["products"]
    # 满减优惠
    d=data["discount"]
    # 配送费
    f=data["deliveryFee"]
    n=[]
    for i in products:
        n+=[(products[i]["price"]+products[i]["packageFee"]) for x in range(products[i]["num"])]
    # 满减优惠列表并排序
    if len(d)==1 and len(d[0])==0:
        d = []
    else:
        d=sorted(d,key=(lambda x:x[0]))
    # 价格组合和最优惠价格
    l, minPrice = accurate_price(n,d,f)
    rep = []
    for m in l:
        repItem=[]
        for x in m:
            for key in products:
                if((products[key]["price"]+products[key]["packageFee"])==x and products[key]["num"]!=0):
                    repItem+=[key]
                    products[key]["num"]-=1
                    break
        rep+=[repItem]
    # 返回物品组合，最小总金额
    response = make_response(jsonify({
        "list": rep,
        "minprice": minPrice
    }))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'

    return response

if __name__ == '__main__':
    # x=main()
    # print x
    server.run(debug=True, port=8888, host='127.0.0.1')