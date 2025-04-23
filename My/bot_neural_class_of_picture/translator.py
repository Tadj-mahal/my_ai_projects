def translate(sample_text):

    from transformers import AutoTokenizer, MarianMTModel

    src = "en"  # source language
    trg = "ru"  # target language

    model_name = f"Helsinki-NLP/opus-mt-{src}-{trg}"
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    batch = tokenizer([sample_text], return_tensors="pt")

    generated_ids = model.generate(**batch)
    output = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return output