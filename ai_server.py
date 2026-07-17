import modal


app = modal.App("qwen-notefinder")


image = (
    modal.Image.debian_slim()
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "fastapi"
    )
)


@app.cls(
    image=image,
    gpu="T4",
    scaledown_window=300
)
class QwenModel:


    @modal.enter()
    def load_model(self):

        from transformers import (
            AutoTokenizer,
            AutoModelForCausalLM
        )

        import torch


        model_name = "Qwen/Qwen2-1.5B-Instruct"


        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )


        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )


    @modal.method()
    def generate(self, text):

        import torch


        prompt = f"""
Summarize the following PDF text:

{text}
"""


        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096
        )


        inputs = {
            k: v.to(self.model.device)
            for k, v in inputs.items()
        }


        with torch.no_grad():

            output = self.model.generate(
                **inputs,
                max_new_tokens=400,
                temperature=0.7
            )


        result = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )


        return result



# HTTP API
@app.function(
    image=image,
    gpu="T4"
)
@modal.fastapi_endpoint(method="POST")
def summarize(data: dict):

    model = QwenModel()

    result = model.generate.remote(
        data["text"]
    )

    return {
        "summary": result
    }