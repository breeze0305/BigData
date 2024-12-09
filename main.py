import pandas as pd
import opencc
import re
import os
import random
import string
import pandas as pd
from datetime import datetime

from llama_custom import semantic_analysis,sentence_enhancement,filtered_question

def logging_to_csv(label, type, question, message="N/A", details=None):
    # 構建當前記錄的 DataFrame
    log_entry = pd.DataFrame([{
        "label": label,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": type,
        "question": question,
        "message": message,
        "details": str(details) if details else ""
    }])

    log_file = "log.csv"
    write_header = not os.path.exists(log_file)
    
    # 追加寫入 CSV 文件
    log_entry.to_csv(log_file, mode='a', index=False, header=write_header, encoding='utf-8')



def get_preprompts():
    prompt = """
    上面是我的問題，你是一個問題分類器,請根據下面的規則,依照格式輸出問題中的關鍵字,請不要回答其他的問題,
    如果是透過"課程名稱"去詢問上課地點的,請幫我回答"1/該問題的課程名稱";
    例如詢問"數位系統"的上課地點,請幫我回答"1/數位系統";
    如果是透過"課程名稱"去詢問上課時間的,請幫我回答"2/該問題的課程名稱";
    如果是透過"課程名稱"去詢問授課教授是誰,請幫我回答"3/該問題的課程名稱";
    如果是透過"課程名稱"去詢問課程的學分數,請幫我回答"4/該問題的課程名稱";
    如果是透過"課程名稱"去詢問限修條件,請幫我回答"5/該問題的課程名稱";
    如果是透過"課程名稱"去詢問是否為全英文授課,請幫我回答"6/該問題的課程名稱";
    如果是透過"課程名稱"去詢問這門課有沒有備註,請幫我回答"7/該問題的課程名稱";
    如果是透過"老師名稱"去詢問這個老師總共有開哪一些課程,請幫我回答"8/該問題的老師的名稱";
    如果是透過"上課時段"去詢問這個時間有開哪一些課程,請幫我回答"9/該問題的時段";
    如果是透過"學分數"去詢問有哪一些課程符合,請幫我回答"10/學分數";
    如果是透過"星期幾"去詢問有哪一些課程符合,請幫我回答"11/星期幾";
    如果是透過"上課地點"去詢問有哪一些課程符合,請幫我回答"12/上課地點";
    如果是透過"課程名稱"去詢問限修人數,請幫我回答"13/該問題的課程名稱";
    
    """
    # 如果問題與上述的內容都不相關,則直接回傳 "0/不支援的問題" 
    return prompt

def check_format(input_str: str) -> bool:
    # 使用正則表達式來匹配格式
    pattern = r'^\d+/.+$'  # 數字開頭, 之後是 `/` 和文字
    return bool(re.match(pattern, input_str))

def is_exact_match(input_str):
    input_str = input_str.split("/")[-1]
    specific_strings = [
        "該問題的課程名稱",
        "該問題的老師的名稱",
        "該問題的時段",
        "學分數",
        "星期幾",
        "上課地點"
    ]
    return not (input_str in specific_strings)

def main_process(question):
    # question = question + ",請用中文回答"
    random_label = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    preprompt = get_preprompts()
    MAX_ATTEMPTS = 5
    attempts = 1
    CC = opencc.OpenCC('s2t.json')
    
    while True:
        parameters = semantic_analysis(preprompt,question)
        logging_to_csv(random_label, '語意拆解', question, message=parameters, details=None)
        
        if check_format(parameters):
            # 格式正確,但是不符合規則 (ex: 1/該問題的課程名稱) -> (ex: 1/數位系統)
            while True:
                if is_exact_match(parameters): # 篩選掉"直接複製"我的模板的問題
                    break
                prompt2 = f"""
                            下面是我的問題,我希望你可以幫我把問題中的關鍵字填入"/"後面,
                            問題:{question}。模板:{parameters}。
                            """
                parameters = semantic_analysis(prompt2)
                logging_to_csv(random_label, '去除直接複製模板的答案', question, message=parameters, details=None)
                
            break
        elif attempts >= MAX_ATTEMPTS:
            print("超過最大次數")
            logging_to_csv(random_label, '超過最大次數(error)', question, message='', details=None)
            return "不好意思，我無法回答這個問題"
        else:
            attempts += 1
            logging_to_csv(random_label, '回答不符合 </>的格式 ', question, message=parameters, details=None)
            
    print(f"source response({attempts}):{parameters}")
    
    index, args = parameters.split("/")
    print(f"index: {index}, args: {args}")
    
    normalize_answer = filtered_question(int(index), args)
    logging_to_csv(random_label, 'normalize_answer', question, message=normalize_answer, details=None)
    print(f"normalize_answer: {normalize_answer}")
    
    perfect_ansewr = sentence_enhancement(question,normalize_answer)
    logging_to_csv(random_label, 'perfect_ansewr', question, message=perfect_ansewr, details=None)
    print(f"perfect_ansewr: {perfect_ansewr}")
    
    return CC.convert(perfect_ansewr)
    
def main():
    question = input("請輸入問題: ")
    main_process(question)
    
if __name__ == "__main__":
    main()
    