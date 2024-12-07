import re
import pandas as pd
from llama_index.llms.ollama import Ollama

def model_test():
    # llm = Ollama(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4", request_timeout=360)
    llm = Ollama(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q8", request_timeout=360)
    print("ask:早安，你覺得我等等晚餐吃啥")
    response = llm.complete("早安，你覺得我等等晚餐吃啥")
    print(f"response:{response}")

def question_one(arg:str, df):
    row = df[df['中文課程名稱'] == arg]
    outputs = []
    if not row.empty:
        rows = row['地點時間'].unique()

        for row_ in rows:
            parts = row_.split() # 五 2-4 本部 教401
            # print(parts)
            day = parts[0]  # 星期
            campus = parts[2]  # 校區（如本部）
            building_room = parts[3]  # 教室與房間號（如教401）
            
            # 拆分教室名稱和房間號
            if building_room.startswith("教"):
                building = "教育大樓"
                room = building_room[1:]+"教室"  # 取出房間號
            elif building_room.startswith("綜"):
                building = "綜合大樓"
                room = building_room[1:]+"教室"  # 取出房間號
            elif building_room.startswith("工") or building_room.startswith("誠") or building_room.startswith("誠"):
                building = building_room+"教室"
                room = ""
            else:
                building = building_room
                room = ""
            
            # 組合成目標格式
            output = f"星期{day} 校{campus} {building}{room}"
            outputs.append(output)

        return ", ".join(outputs)
    
def filtered_question(index, arg:str): # index:問什麼 arg:關鍵字
    df = pd.read_csv("modified_ee.csv")
    if index == 1:
        temp = question_one(arg, df)
        return temp
    if index == 2:
        row = df[df['中文課程名稱'] == arg]
        if not row.empty:
            input_str = row.iloc[0]['地點時間'][0:5]##time
            
            parts = input_str.split()
            day = parts[0]  # 星期
            times = parts[1].split('-')  # 節次範圍
            start = int(times[0])  # 開始節次
            end = int(times[1])  # 結束節次
            duration = end - start + 1  # 總節次數

            # 組合成目標格式
            temp = f"星期{day} 第{start}節課到第{end}節課 總共{duration}小時"
            return temp
    if index == 3:
        row = df[df['中文課程名稱'] == arg]
        if not row.empty:
            return row.iloc[0]['授課教師']
    if index == 4:
        row = df[df['中文課程名稱'] == arg]
        if not row.empty:
            return row.iloc[0]['課程學分數量']
    if index == 5:
        row = df[df['中文課程名稱'] == arg]
        print(row)
        if not row.empty:
            temp = row.iloc[0]['限修條件'] 
            return temp if temp != "無" else f"{arg}這門課,沒有限修條件"
    if index == 6:
        row = df[df['中文課程名稱'] == arg]
        if not row.empty:
            return row.iloc[0]['全英語']
    if index == 7:
        row = df[df['中文課程名稱'] == arg]
        if not row.empty:
            return row.iloc[0]['備註']
    if index == 8:
        arg = arg.replace("老師","")
        arg = arg.replace("教授","")
        
        row = df[df['授課教師'] == arg]
        if not row.empty:
            return row['中文課程名稱'].unique()
    if index == 9:
        row = df[df['地點時間'][0:5] == arg]
        if not row.empty:
            return row['中文課程時間'].unique()
    if index == 10:
        numbers = re.findall(r'\d+', arg) # 去除字串中的"學分"，只留下數字
        row = df[df["課程學分數量"] == int(numbers[0])]["中文課程名稱"]
        if not row.empty:
            return row.unique()
    if index == 11: # 全部轉成阿拉伯數字
        arg = arg.replace("星期", "")
        table = {
            1:"一",
            2:"二",
            3:"三",
            4:"四",
            5:"五",
            6:"六",
            7:"七"
        }
        arg = arg if not isinstance(arg, int) else table.get(arg)
        row = df[df['地點時間'].str.startswith(arg, na=False)]
        if not row.empty:
            return row['中文課程名稱'].unique()
    if index == 12:
        row = df[df['地點時間'].str.contains(arg, na=False)]
        if not row.empty:
            # 在這間教室上的有:[]
            temp = row['中文課程名稱'].unique()
            return "在這間教室上的有:" + " ".join(temp)
        
def semantic_analysis(prompt,_str = ""):
    # llm = Ollama(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4", request_timeout=360)
    llm = Ollama(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q8", request_timeout=360)
    combine_prompt = f"{prompt}\n{_str}"
    
    responce = llm.complete(combine_prompt)
    return str(responce)

def sentence_enhancement(ques,ans):
    llm = Ollama(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q8", request_timeout=360)
    prompt = f"""你是一個熟悉大學課程的語言模型，請根據以下問題和簡答，將簡答改寫為流暢且完整的句子，請不要幫忙主觀回答。你的任務是潤句，不需要提及任何背景資訊和加入主觀內容。請用繁體中文回答。
            問題:「{ques}」
            簡答:「{ans}」
            """

    # print(f"{'*'*10}\nprompt: {prompt}\n{'*'*10}")
    responce = llm.complete(prompt)
    
    return str(responce)



if __name__ == "__main__":
    # model_test()
    semantic_analysis("","早安，你覺得我等等晚餐吃啥")
    # 請問程式設計的上課時間
    # 請問類比積體電路導論的上課時間
    # 請問程式設計的上課地點在哪?
    # 請問類比積體電路導論的限修條件為何