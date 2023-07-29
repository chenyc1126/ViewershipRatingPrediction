import pandas as pd
training_source_events = pd.read_csv("training_source_events.csv")
training_source_events_columns = training_source_events.columns
new_training_source_events = pd.DataFrame()
#new_training_source_events = pd.read_csv("new_training_source_events.csv")

#session_id、device_id刪掉、user_id、title_in_simulcast不更動
new_training_source_events["user_id"] = training_source_events["user_id"]
new_training_source_events["title_in_simulcast"] = training_source_events["title_in_simulcast"]

#played_duration
import math
max_duration = max(list(training_source_events["played_duration"]))
x = round(math.log(0.9) / (math.log(14400 / max_duration)),5)

played_duration = []

for i in range(len(training_source_events["played_duration"])):    
    if training_source_events["played_duration"][i] < 0:
        played_duration.append(0)
    else:
        change1 = round(float(training_source_events["played_duration"][i]/ max_duration),5)
        change2 = round(change1**x,5)
        played_duration.append(change2)
"""
duration 轉換到 0~1 的range。並將其作根號運算，滿足14400(4小時)轉換後為0.9
滿足:
1.在一個slot中看得越久的，代表他越狂熱，未來同一個slot看的機率也越大
2.只看10秒的人，和看1個小時的人應該有顯著的差異
3.看4個小時以上時間彼此間差異應該不大，因此設定在0.9~1的range
"""
new_training_source_events["played_duration"] = played_duration

#event_time
#將其轉換至對應的timeslot
event_time = []
slot = 0
for i in range(len(training_source_events["event_time"])):
    time = (training_source_events["event_time"][i] - 1607878800) % 604800
    day = time // 86400
    hr = (time % 86400) // 3600
    if 0 <= hr <= 7:
        slot = day*4
    elif 8 <= hr <= 15:    
        slot = day*4 + 1
    elif 16 <= hr <= 19: 
        slot = day*4 + 2
    elif 20 <= hr <= 23: 
        slot = day*4 + 3
    event_time.append(slot)
    
new_training_source_events["event_time"] = event_time

#title_id
hot_title_id = []
title_id_set = set(training_source_events["title_id"])
title_id = dict()

for i in title_id_set:
    title_id[i] = 0
    
for i in training_source_events["title_id"]:
    title_id[i] += 1

title_id_key = list(title_id.keys())
title_id_value = list(title_id.values())
title_id_value_sort = sorted(title_id_value,reverse = True)
hot_title_id_value = title_id_value_sort[len(title_id_value_sort)//3]

for i in range(len(title_id_key)):
    if title_id_value[i] >= hot_title_id_value:
        title_id[title_id_key[i]] = 1
    else:
        title_id[title_id_key[i]] = 0

for i in range(len(training_source_events["title_id"])):
    hot_title_id.append(title_id[training_source_events["title_id"][i]])
    
new_training_source_events["title_id"] = hot_title_id

#剩餘變數屬類別變數,不更動
new_training_source_events["platform"] = training_source_events["platform"]
new_training_source_events["internet_connection_type"] = training_source_events["internet_connection_type"]
new_training_source_events["action_trigger"] = training_source_events["action_trigger"]
new_training_source_events["title_type"] = training_source_events["title_type"]
#存檔成csv
new_training_source_events.to_csv("new_training_source_events.csv")


#收集同個使用者同個timeslot的index
import pandas as pd
new_training_source_events = pd.read_csv("new_training_source_events.csv")
new_training_source_events_columns = new_training_source_events.columns

Index = dict()

for i in range(0,32000):
    for j in range(0,28):
        Index.setdefault(str(i)+"_"+str(j),[])
        
for i in range(len(new_training_source_events["user_id"])):
    userid = new_training_source_events["user_id"][i]
    eventtime = new_training_source_events["event_time"][i]
    
    Index[str(userid)+"_"+str(eventtime)].append(i)
    
#建立最終training_source_events的csv

final_training_source_events = pd.DataFrame()
final_training_source_events_columns = final_training_source_events.columns
#final_training_source_events = pd.read_csv("final_training_source_events.csv")

#user_slot
user_slot_list = []
for i in Index.keys():
    user_slot_list.append(i)

final_training_source_events["user_slot"] = user_slot_list

#非類別變數,取同使用者同slot的平均
new_played_duration = []
new_title_id = []
new_title_in_simulcast = []

import numpy
for i in Index.keys():
    played_duration_list = []
    title_id_list = []
    title_in_simulcast_list = []
    
    for k in Index[i]:
        
        played_duration_list.append(new_training_source_events["played_duration"][k])
        title_id_list.append(new_training_source_events["title_id"][k])
        title_in_simulcast_list.append(new_training_source_events["title_in_simulcast"][k])

    if played_duration_list == []:
        new_played_duration.append(float(0))
    else:
        new_played_duration.append(float(numpy.mean(played_duration_list)))
        
    if title_id_list == []:
        new_title_id.append(0)
    else:
        new_title_id.append(numpy.mean(title_id_list))
        
    if title_in_simulcast_list == []:
        new_title_in_simulcast.append(0)
    else:
        new_title_in_simulcast.append(numpy.mean(title_in_simulcast_list))

final_training_source_events["played_duration"] = new_played_duration
final_training_source_events["title_id"] = new_title_id
final_training_source_events["title_in_simulcast"] = new_title_in_simulcast
final_training_source_events.to_csv("final_training_source_events.csv")

#類別變數,取同使用者同slot的眾數
new_platform  = []
new_internet_connection_type = []
new_action_trigger = []
new_title_type  = []
       
for i in Index.keys():
    platform_list = []
    internet_connection_type_list = []
    action_trigger_list = []
    title_type_list = []
    
    for k in Index[i]:

        platform_list.append(new_training_source_events["platform"][k])
        internet_connection_type_list.append(new_training_source_events["internet_connection_type"][k])
        action_trigger_list.append(new_training_source_events["action_trigger"][k])
        title_type_list.append(new_training_source_events["title_type"][k])
        
    if platform_list == []:
        new_platform.append(-1)
    else:
        x = pd.Series(data = platform_list)
        new_platform.append(int(x.mode()[0]))
        
    if internet_connection_type_list == []:
        new_internet_connection_type.append(-1)
    else:
        x = pd.Series(data = internet_connection_type_list)
        new_internet_connection_type.append(int(x.mode()[0]))
        
    if action_trigger_list == []:
        new_action_trigger.append(-1)
    else:
        x = pd.Series(data = action_trigger_list)
        new_action_trigger.append(int(x.mode()[0]))
        
    if title_type_list == []:
        new_title_type.append(-1)
    else:
        x = pd.Series(data = title_type_list)
        new_title_type.append(int(x.mode()[0]))

#platform
platform_dict = dict()
for i in range(0,4):
    platform_dict["platform_%d"%i] = []
    
for i in new_platform:
    if i == -1:
        for j in range(0,4):
            platform_dict["platform_%d"%j].append(0)
    else:
        for j in range(0,4):
            if i == j:
                platform_dict["platform_%d"%j].append(1)
            else:
                platform_dict["platform_%d"%j].append(0)

for i in range(0,4):
    final_training_source_events["platform_%d"%i] = platform_dict["platform_%d"%i]

final_training_source_events.to_csv("final_training_source_events.csv")

#internet_connection_type
internet_connection_type_dict = dict()
for i in range(0,8):
    internet_connection_type_dict["internet_connection_type_%d"%i] = []
    
for i in new_internet_connection_type:
    if i == -1:
        for j in range(0,8):
            internet_connection_type_dict["internet_connection_type_%d"%j].append(0)
    else:
        for j in range(0,8):
            if i == j:
                internet_connection_type_dict["internet_connection_type_%d"%j].append(1)
            else:
                internet_connection_type_dict["internet_connection_type_%d"%j].append(0)
                
for i in range(0,8):
    final_training_source_events["internet_connection_type_%d"%i] = internet_connection_type_dict["internet_connection_type_%d"%i]

final_training_source_events.to_csv("final_training_source_events.csv")

#action_trigger
action_trigger_dict = dict()
for i in range(0,14):
    action_trigger_dict["action_trigger_%d"%i] = []
    
for i in new_action_trigger:
    if i == -1:
        for j in range(0,14):
            action_trigger_dict["action_trigger_%d"%j].append(0)
    else:
        for j in range(0,14):
            if i == j:
                action_trigger_dict["action_trigger_%d"%j].append(1)
            else:
                action_trigger_dict["action_trigger_%d"%j].append(0)

for i in range(0,14):
    final_training_source_events["action_trigger_%d"%i] = action_trigger_dict["action_trigger_%d"%i]

final_training_source_events.to_csv("final_training_source_events.csv")

#title_type
title_type_dict = dict()
for i in range(0,6):
    title_type_dict["title_type_%d"%i] = []
    
for i in new_title_type:
    if i == -1:
        for j in range(0,6):
            title_type_dict["title_type_%d"%j].append(0)
    else:
        for j in range(0,6):
            if i == j:
                title_type_dict["title_type_%d"%j].append(1)
            else:
                title_type_dict["title_type_%d"%j].append(0)

for i in range(0,6):
    final_training_source_events["title_type_%d"%i] = title_type_dict["title_type_%d"%i]

final_training_source_events.to_csv("final_training_source_events.csv")
