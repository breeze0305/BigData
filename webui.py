import gradio as gr

from main import main_process

def checker(id, password):
    return True


def feed_back(message, chat_history):
    response = main_process(message)
    response = str(response)
    chat_history.append((message, response))
    return "", chat_history


def launch(debug: bool): 
    with gr.Blocks() as demo:
        with gr.Column():
            chatbot = gr.Chatbot()
            msg = gr.Textbox()
            clear = gr.ClearButton([msg, chatbot])

            msg.submit(feed_back, [msg, chatbot], [msg, chatbot])

    if debug:
        demo.launch(server_port=8000)
    else:
        demo.launch(share=True, auth=checker, server_port=8000)


if __name__ == "__main__":
    debug = True

    launch(debug)
