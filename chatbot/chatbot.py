# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: MIT

from transformers import AutoModel, AutoTokenizer
import gradio as gr
import mdtex2html
import redis
import torch
import struct


def postprocess(self, y):
    if y is None:
        return []
    for i, (message, response) in enumerate(y):
        y[i] = (
            None if message is None else mdtex2html.convert((message)),
            None if response is None else mdtex2html.convert(response),
        )
    return y


gr.Chatbot.postprocess = postprocess


def parse_text(text):
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split("`")
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f"<br></code></pre>"
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>" + line
    text = "".join(lines)
    return text


def reset_user_input():
    return gr.update(value="")


def reset_state():
    return [], [], None


def numpy_to_vector_byte(floats):
    return struct.pack("<" + "f" * len(floats), *floats)


PROMPT_TEMPLATE_SESSION = """
User's previously asked questions:
{context}
Based on the known information above, answer the user's question. If you cannot derive the answer from it, answer the question on your own. Please respond in Chinese. Question: {question}
"""


class RedisClient:
    def __init__(self, host="127.0.0.1", port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)
        self.text2vec_tokenizer = AutoTokenizer.from_pretrained(
            "GanymedeNil/text2vec-large-chinese"
        )
        self.text2vec_model = AutoModel.from_pretrained(
            "GanymedeNil/text2vec-large-chinese"
        ).cpu()

    def get_embedding(self, text):
        inputs = self.text2vec_tokenizer(
            text, return_tensors="pt", padding=True, truncation=True
        )
        with torch.no_grad():
            outputs = self.text2vec_model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return numpy_to_vector_byte(embeddings.cpu().numpy()[0])

    def create_index(self, session_id, field_name="chatinfo"):
        args = [
            "FT.CREATE",
            session_id,
            "SCHEMA",
            field_name,
            "VECTOR",
            "HNSW",
            "10",  # number of remaining arguments
            "TYPE",
            "FLOAT32",
            "DIM",
            1024,
            "DISTANCE_METRIC",
            "L2",
            "M",
            16,
            "EF_CONSTRUCTION",
            200,
        ]
        self.client.execute_command(*args)

    def similarity_search(self, session_id, query, topK=5, field_name="chatinfo"):
        v = self.get_embedding(query)
        q = [
            "FT.SEARCH",
            session_id,
            f"*=>[KNN {topK} @{field_name} $BLOB EF_RUNTIME 200]",
            "NOCONTENT",  # Only return keys in the results
            "LIMIT",
            "0",
            str(topK),
            "PARAMS",
            "2",
            "BLOB",
            v,
            "DIALECT",
            "2",
        ]
        res = self.client.execute_command(*q)
        return res

    def insert_text(self, text, field_name="chatinfo"):
        v = self.get_embedding(text)
        self.client.hset(text, field_name, v)


class ChatBot:
    def __init__(self, session_id):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "THUDM/chatglm2-6b", trust_remote_code=True
        )
        self.llm_model = AutoModel.from_pretrained(
            "THUDM/chatglm2-6b", trust_remote_code=True
        ).cpu()
        self.llm_model = self.llm_model.eval()
        self.session_id = session_id
        self.redis_client = RedisClient()

    def get_prompt_by_session(self, query):
        # Fetch the user's session history and answer based on past prompts
        results = self.redis_client.similarity_search(self.session_id, query)

        if results[0] == 0:
            prompt = query
        else:
            context = "\n".join([result.decode("utf-8") for result in results[1:]])
            prompt = PROMPT_TEMPLATE_SESSION.format(context=context, question=query)
        return prompt

    def predict(self, input, chatbot, max_length, top_p, temperature, history, past_key_values):
        # Fetch the user's session history and answer based on past prompts
        prompt = self.get_prompt_by_session(input)
        chatbot.append((parse_text(input), ""))
        for response, history, past_key_values in self.llm_model.stream_chat(
            self.tokenizer,
            prompt,
            history,
            past_key_values=past_key_values,
            return_past_key_values=True,
            max_length=max_length,
            top_p=top_p,
            temperature=temperature,
        ):
            chatbot[-1] = (parse_text(input), parse_text(response))

            yield chatbot, history, past_key_values

        # Add the user's current prompt into the index
        self.redis_client.insert_text(input)


if __name__ == "__main__":

    # A user's session_id
    session_id = 12345678

    # Initialize chatbot
    bot = ChatBot(session_id)
    # Initialize vector index
    bot.redis_client.create_index(session_id)

    with gr.Blocks() as demo:
        gr.HTML("""<h1 align="center">ChatGLM2-6B</h1>""")

        with gr.Column(scale=6):
            chatbot = gr.Chatbot(height=600)
        with gr.Row():
            with gr.Column(scale=4):
                with gr.Column(scale=12):
                    user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=3)
                with gr.Column(min_width=32, scale=1):
                    submitBtn = gr.Button("Submit", variant="primary")
            with gr.Column(scale=1):
                emptyBtn = gr.Button("Clear History")
                max_length = gr.Slider(
                    0, 32768, value=8192, step=1.0, label="Maximum length", interactive=True
                )
                top_p = gr.Slider(0, 1, value=0.8, step=0.01, label="Top P", interactive=True)
                temperature = gr.Slider(
                    0, 1, value=0.95, step=0.01, label="Temperature", interactive=True
                )

        history = gr.State([])
        past_key_values = gr.State(None)

        submitBtn.click(
            bot.predict,
            [user_input, chatbot, max_length, top_p, temperature, history, past_key_values],
            [chatbot, history, past_key_values],
            show_progress=True,
        )
        submitBtn.click(reset_user_input, [], [user_input])

        emptyBtn.click(reset_state, outputs=[chatbot, history, past_key_values], show_progress=True)

    demo.queue().launch(share=False, inbrowser=True)