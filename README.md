# ViewershipRatingPrediction
此程式為機器學習概論之期末發表，課堂與KKTV公司合作，希望透過觀察使用者過往的觀影追劇作息，推測使用者在未來的一週內哪些時段看劇，並建立準確的推測模型,  幫助 KKTV 對即將有空暇的用戶，提出適時的推薦。 幫助 KKTV 合理的安排推播提醒，並且避免不必要的打擾推播訊息。。

# 設計Feature
從training_sourse_event.csv取得data處理後得到final_test_sourse_event.csv:
●	建立new_training_sourse_event.csv（39542450*9）
1.	user_id保留、device_id、session_id刪除（認為這兩項影響不大）。
2.	將event time轉換成在一個禮拜中的哪個time_slot，標示為0～27。
3.	將title_id中較熱門的（出現次數前⅓多的）標示為1，其他表示為0。
4.	將played_duration轉換為0～1的數值，以4小時為0.9為基準做根號運算（認為看越久未來同slot觀看機率大，且如0和1小時的機率差異大、4小時以上差異小，故導出我們設定的公式）。
5.	title_in_simulcast、platform、internet_connection_type、action_trigger、title_type五種類別變數保留不處理。
●	建立final_training_sourse_event.csv（896000*36）
*896000對應32000個user_id乘以28個time_slot 》training_target_label.csv
1.	合併user_id和event_time，建立新的一個column”user_slot”，標示為0_0、0_1⋯、0_27、⋯、31999_27共896000項。
2.	建立title_id、played_duration、title_in_simulcast三項column，分別取new_training_sourse_event.csv中同個user_id、同個event_time的所有數值取平均，加入對應的user_slot那一行。
3.	建立platform_0～3、internet_connection_type_0～7、action_trigger_0～13、title_type_0～5共32個columns，分別取new_training_sourse_event.csv中同個user_id、同個event_time的眾數，在對應類別表示為1，其他為0，（例如user_slot=0_0中出現最多的platform是0，在platform_0表示1、platform_1.2.3表示0），最後將四種類別變數32個結果加入對應的user_slot那一行。
test_sourse_event.csv做一樣的處理得到final_test_sourse_event.csv

# 建立Model
以final_training_sourse_event.csv(x,前幾週結果處理統整的歷史資料）和training_target_label.csv（y,最後一週結果）建立model。
1.首先我們依序將資料讀入，隨機分割測試集與訓練集
2.我們使用Sequential()建造網路架構，並add一層神經層，輸入x的項目數，輸出38
3.add 激勵層，使用relu，便於依照資料及模型的特性挑選，且排除負值
4.編譯模型，損失函數選擇binary_crossentropy，optimizer選擇adam
5.以X_train、Y_train分別去訓練model，epoch經我們測試選擇10效果最好


# Prediction 
將final_test_sourse_event.csv以建立好的model預測出接下來一週的結果
將預測結果改成規定的格式匯出成csv 檔
