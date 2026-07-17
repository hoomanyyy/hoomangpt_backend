from transformers import AutoModelForCausalLM, AutoTokenizer
from pdf_reader import read_pdf
import torch

MODEL_PATH = "./model"

print("loading ai model")

model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

print(model)

def generate_response(text):
    try:

        prompt = f"""
Summarize the following text:

{text}
"""


        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True
        ).to(model.device)


        output = model.generate(
            **inputs,
            max_new_tokens=400
        )


        result = tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )


        print(result)

        return result


    except Exception as e:
        print("Error:", e)
        return None
    
    
def generate_normal_response(text):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True
    )

    print(model.config._name_or_path)
    print(model.config.model_type)
    print(model.config.architectures)
    print(model.generation_config)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    output = model.generate(
        **inputs,
        max_new_tokens=250
    )

    result = tokenizer.decode(
        output[0],
        skip_special_tokens=True
    )

    return result