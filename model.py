from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"


print("Loading Qwen model...")


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)


model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)


print("Model loaded")



def generate_response(text):

    try:

        prompt = f"""
Summarize the following PDF text:

{text}

Provide a clear and short summary.
"""


        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=8000
        )


        inputs = {
            k:v.to(model.device)
            for k,v in inputs.items()
        }



        output = model.generate(

            **inputs,

            max_new_tokens=400,

            temperature=0.7,

            do_sample=True

        )


        result = tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )


        return result



    except Exception as e:

        print("AI ERROR:",e)

        return None





def generate_normal_response(text):


    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True
    )


    inputs = {
        k:v.to(model.device)
        for k,v in inputs.items()
    }


    output=model.generate(
        **inputs,
        max_new_tokens=250
    )


    return tokenizer.decode(
        output[0],
        skip_special_tokens=True
    )