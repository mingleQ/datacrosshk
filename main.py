from zhipuai import ZhipuAI
import gradio as gr
import os
import logging
from neo4j_sc import search
from embedding.search_vector import search_from_vector
from dotenv import load_dotenv
from difflib import SequenceMatcher

load_dotenv()
api_id = os.getenv('ZHIPU_API_ID')
# 初始化ZhipuAI客户端
client = ZhipuAI(api_key=api_id)  # 请填写自己的APIKey

# 知识图谱和向量检索开关
neo4j_flag = -1
vector_flag = -1
country = ''

def is_country(content):
    country_list = ['中国','英国','菲律宾','韩国','日本','香港','美国','欧盟']
    for c in country_list:
        if c in content:
            return c 
    return ''

# def neo4j_resp(user_input, country):
#     input_country = is_country(user_input)
#     if input_country != '':
#         country = input_country
    
#     neo4j_content = ''
    
#     neo4j_content_dict = search.search_from_neo4j(user_input=user_input, country=country)
    
#     if len(neo4j_content_dict) > 0:
#         if len(country) > 0:
#             neo4j_content = f'知识图谱提供的关于{country}在这个问题上的背景知识：'
#         else:
#             neo4j_content = f'知识图谱提供的背景知识：'
#         for k, v in neo4j_content_dict.items():
#             neo4j_content += k + ':' + v + '\n'
    
#     logging.info(f"neo4j resp:{neo4j_content}")
#     return neo4j_content

def neo4j_resp(user_input, country):
    input_country = is_country(user_input)
    if input_country != '':
        country = input_country
    
    neo4j_content = ''
    
    neo4j_content_dict = search.search_from_neo4j(user_input=user_input, country=country)
    
    if len(neo4j_content_dict) > 0:
        if len(country) > 0:
            neo4j_content = f'知识图谱提供的关于{country}在这个问题上的背景知识：'
        else:
            neo4j_content = f'知识图谱提供的背景知识：'
        
        # 计算每个 value 与 user_input 的相似度
        similarity_scores = [(k, v, SequenceMatcher(None, user_input, v).ratio()) for k, v in neo4j_content_dict.items()]
        
        # 按相似度排序并选择前 3 个
        top_related_content = sorted(similarity_scores, key=lambda x: x[2], reverse=True)[:3]
        
        for k, v, _ in top_related_content:
            neo4j_content += k + ':' + v + '\n'
    
    logging.info(f"neo4j resp:{neo4j_content}")
    return neo4j_content


def vector_resp(user_input):
    vector_content = search_from_vector(user_input, k=3)
    logging.info(f"vector resp:{vector_content}")
    return f'向量知识库提供的背景知识：{vector_content}'

# 定义一个生成器函数，用于与模型进行流式交互
def chat_with_model_stream(chat_history):

    messages = [{"role":"system", "content":"假设你数据跨境小助手，帮助用户解答数据跨境相关的问题"}]
    for role, content in chat_history:
        if role == "user":
            messages.append({"role": "user", "content": content})
        elif role == "assistant":
            messages.append({"role": "assistant", "content": content})

    print("message:", messages)

    response = client.chat.completions.create(
        model="glm-4",  
        messages=messages,
        stream=True,  # 启用流式输出
    )
    
    full_response = ""
    for chunk in response:
        delta = chunk.choices[0].delta.content  
        full_response += delta
        yield full_response

def chat_interface(user_input, chat_history=[], chat_history_show=[]):
    global country
    if len(chat_history) > 6:
        chat_history = chat_history[-6:]
        country = ''
    
    for role, content in chat_history:
        if role == 'user':
            country = is_country(content)

    if neo4j_flag < 0 and vector_flag < 0:
        chat_history.append(("user", user_input))
        chat_history_show.append(("user", user_input))
    else:
        user_input_with_context = user_input
        if neo4j_flag > 0:
            user_input_with_context += '\n' + neo4j_resp(user_input, country)
        if vector_flag > 0:
            user_input_with_context += '\n' + vector_resp(user_input)
        chat_history.append(("user", user_input_with_context))
        chat_history_show.append(("user", user_input))

    bot_response = ""
    for partial_response in chat_with_model_stream(chat_history):
        bot_response = partial_response
        if len(chat_history_show) > 1 and chat_history_show[-1][0] == "assistant":
            chat_history_show[-1] = ("assistant", bot_response)  # 更新最后一条记录
        else:
            chat_history_show.append(("assistant", bot_response))  # 添加新的记录

        formatted_chat_history = [(content, None) if role == "user" else (None, content) for role, content in chat_history_show]
        yield formatted_chat_history, chat_history, chat_history_show

def clear_input():
    # 清空输入框
    return ""

def btn_neo4j_click(neo4j_state, chat_history=[], chat_history_show=[]):
    global neo4j_flag
    neo4j_flag = 1 if neo4j_state else -1
    chat_history_cp = chat_history[:]
    chat_history_show_cp = chat_history_show[:]
    if neo4j_flag > 0:
        print("知识图谱开启")
        # chat_history_cp.append(("assistant", "知识图谱开启"))
        chat_history_show_cp.append(("assistant", "知识图谱开启"))
    else:
        print("知识图谱关闭")
        # chat_history_cp.append(("assistant", "知识图谱关闭"))
        chat_history_show_cp.append(("assistant", "知识图谱关闭"))

    formatted_chat_history = [(content, None) if role == "user" else (None, content) for role, content in chat_history_show_cp]
    return formatted_chat_history, chat_history_cp, chat_history_show_cp

def btn_vector_click(vector_state, chat_history=[], chat_history_show=[]):
    global vector_flag
    vector_flag = 1 if vector_state else -1
    chat_history_cp = chat_history[:]
    chat_history_show_cp = chat_history_show[:]
    if vector_flag > 0:
        print("向量检索开启")
        # chat_history_cp.append(("assistant", "向量检索开启"))
        chat_history_show_cp.append(("assistant", "向量检索开启"))
    else:
        print("向量检索关闭")
        # chat_history_cp.append(("assistant", "向量检索关闭"))
        chat_history_show_cp.append(("assistant", "向量检索关闭"))

    formatted_chat_history = [(content, None) if role == "user" else (None, content) for role, content in chat_history_show_cp]
    return formatted_chat_history, chat_history_cp, chat_history_show_cp

# 创建Gradio界面
with gr.Blocks() as demo:
    chat_history = gr.State([])
    chat_history_show = gr.State([])

    chatbot = gr.Chatbot(
        [],
        elem_id="AI助手",
        height="80vh",
        bubble_full_width=False,
        avatar_images=(None, os.path.join(os.path.dirname(__file__), "liantong.jpg")),
    )

    with gr.Row():
        user_input = gr.Textbox(scale=4, show_label=False, placeholder="我是数据跨境小助手，输入你的问题...")
        submit_btn = gr.Button("发送")
        neo4j_switch = gr.Checkbox(label="开关知识图谱", value=False)
        vector_switch = gr.Checkbox(label="开关向量检索", value=False)

    submit_btn.click(chat_interface, inputs=[user_input, chat_history, chat_history_show], outputs=[chatbot, chat_history, chat_history_show]).then(clear_input, inputs=[], outputs=[user_input])
    user_input.submit(chat_interface, inputs=[user_input, chat_history, chat_history_show], outputs=[chatbot, chat_history, chat_history_show]).then(clear_input, inputs=[], outputs=[user_input])
    neo4j_switch.change(btn_neo4j_click, inputs=[neo4j_switch, chat_history, chat_history_show], outputs=[chatbot, chat_history, chat_history_show], queue=False)
    vector_switch.change(btn_vector_click, inputs=[vector_switch, chat_history, chat_history_show], outputs=[chatbot, chat_history, chat_history_show], queue=False)

# 启动Gradio应用
demo.launch()
