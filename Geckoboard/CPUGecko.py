#remember to install MySQLdb -> sudo apt-get install python-mysqldb

import urllib2
import MySQLdb
import datetime
from time import sleep


#----------------------------------------------------------------------------------------Functions---------------------------------------------------------------------------------------------------------
def pushGecko(url, data):
    urllib2.urlopen(url, data=data)
    
def grabData(hostIP, userName, password, dbName, query):
    db=MySQLdb.connect(host=hostIP,user=userName,passwd=password,db=dbName)
    curse=db.cursor()
    curse.execute(query)
    return curse.fetchall()
    
def jSonParser(resultSet):
    data='{"api_key":"847c8148b44764e86d979aef5cf9caf1","data":{"item": ['
    rawData=''
    labelData=''
    dayOne=resultSet[0][1].day
    firstDay=True
    minVal=100
    maxVal=0
    for rows in resultSet:
        if rows[0] != None:
            rawData=rawData+'"'+str(rows[0])+'",'
            if rows[0]<minVal:
                minVal=rows[0]
            if rows[0]>maxVal:
                maxVal=rows[0]    
        if rows[1] != None:
            day=rows[1].day
            labelData+='"'+str(day)
            if dayOne > day or firstDay == True : 
                labelData+=rows[1].strftime("%b")
                firstDay=False
            labelData+='",'
            dayOne=day
    #trick to delete last troubling comma&quote from rawData and labelData
    rawData=rawData[:-1]
    labelData=labelData[:-1]
    #on axisy is needed to make a label with the MinVal and MaxVal 'cause the value of "data" are not an (x,y) point but just a relative height value
    axisY='"axisy": ["'+str(minVal)+'%",'
    gap=maxVal-minVal
    #if gap is bigger than 10 make some sub-step labels (5)
    if gap>10:
        for i in range(4):
            axisY+='"'+str(minVal+int(gap/5)*(i+1))+'%",'    
    axisY+='"'+str(maxVal)+'%"],'
    data+=rawData+'],"settings": {"axisx": ['+labelData+'],'+axisY+' "colour": "ffff00"}}}'        
    return data        
        
def evaluateAvg(resultSet):
    payLoad=[]
    avg=int(float(resultSet[0][0].rsplit("90;85")[1].rsplit("=")[1][:-2]))
    #'cpu_usagemhz=2030.00Mhz;90;85 cpu_usage=5.76%;90;85'
    cntr=1
    i=1
    while i < len(resultSet):
        #parse the field into an int value
        avg+=int(float(resultSet[i][0].rsplit("90;85")[1].rsplit("=")[1][:-2]))
        if resultSet[i-1][1].day == resultSet[i][1].day and resultSet[i-1][1].month == resultSet[i][1].month :
            #if in the same month keep counting    
            cntr+=1
        else:
            #else elaborate and save
            avg=avg/cntr
            payLoad.append([avg,resultSet[i-1][1]])
            avg=0
            cntr=0
        i+=1
        if i >= len(resultSet):
            #this manage the last set of elaborations 
            payLoad.append([avg/cntr,resultSet[i-1][1]])
    return payLoad


     
#----------------------------------------------------------------------------------------------Main--------------------------------------------------------------------------------------------------------    


url= 'https://push.geckoboard.com/v1/send/24379-fd93945bffb78d095bd82ce40c848629'
ip='localhost'
usr='root'
pw='root'
dbname='icinga'
retry=0
slpTime=5
query='select perfdata,start_time from icinga_servicechecks ,icinga_objects where (icinga_servicechecks.service_object_id =icinga_objects.object_id) and (icinga_objects.name1 = "car-hq-vm-mgt") and (icinga_objects.name2 ="Total Dc cpu usage")and DATE_SUB(CURDATE(),INTERVAL 30 DAY) <= start_time;'

try:
    result=grabData(ip,usr,pw,dbname,query)
    payLoad=evaluateAvg(result)
    pushGecko(url,jSonParser(payLoad))
except urllib2.HTTPError, e:
    while retry < 5:
        retry+=1
        print 'Push failed, another retry will be done in '+str(slpTime)+'s. '+str(5-retry)+' left.'
        sleep(slpTime)



