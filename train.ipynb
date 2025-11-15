# train_qora.py
import os
import json
from datasets import load_dataset
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# === CONFIG ===
BASE_MODEL = os.getenv("BASE_MODEL", "Qwen/Qwen1.5-1.8B-Chat")   # <-- FINAL MODEL
DATA_PATH = os.getenv("DATA_PATH", "dataset.jsonl")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "qora_finetune")

# Adjusted for 4GB GPU
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "4"))
MICRO_BATCH = int(os.getenv("MICRO_BATCH", "1"))

EPOCHS = int(os.getenv("EPOCHS", "3"))
LEARNING_RATE = float(os.getenv("LR", "2e-4"))
LR_WARMUP_STEPS = int(os.getenv("WARMUP", "100"))

MAX_LENGTH = int(os.getenv("MAX_LEN", "256"))  # small seq helps avoid OOM

LORA_R = int(os.getenv("LORA_R", "16"))
LORA_ALPHA = int(os.getenv("LORA_ALPHA", "32"))
LORA_DROPOUT = float(os.getenv("LORA_DROPOUT", "0.05"))

print(f"Using model: {BASE_MODEL}")

# === LOAD DATASET ===
dataset = load_dataset("json", data_files=DATA_PATH, split="train")

# === TOKENIZER ===
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)

# Ensure pad token
if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token

def format_example(example):
    instr = example["instruction"].strip()
    resp = example["response"]
    target_json = json.dumps(resp, ensure_ascii=False)

    prompt = f"### Instruction:\n{instr}\n### Response:\n"
    full = prompt + target_json

    return tokenizer(
        full,
        truncation=True,
        max_length=MAX_LENGTH
    )

dataset = dataset.map(lambda ex: format_example(ex), remove_columns=dataset.column_names)
dataset.set_format(type="torch", columns=["input_ids", "attention_mask"])

# === LOAD MODEL (QWEN 1.8B) with 4-BIT QLoRA ===
from transformers import BitsAndBytesConfig

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    device_map="auto",
    quantization_config=quant_config
)

# Prepare for QLoRA
model = prepare_model_for_kbit_training(model)

# LoRA target modules for QWEN
lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    target_modules=["c_attn", "c_proj"],   # <-- Correct Qwen LoRA modules
    lora_dropout=LORA_DROPOUT,
    bias="none"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# === TRAINING ===
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=MICRO_BATCH,
    gradient_accumulation_steps=BATCH_SIZE // MICRO_BATCH,
    num_train_epochs=EPOCHS,
    learning_rate=LEARNING_RATE,
    fp16=True,
    logging_steps=50,
    save_total_limit=3,
    warmup_steps=LR_WARMUP_STEPS,
    evaluation_strategy="no",
    save_strategy="epoch",
    report_to="none"
)

data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=data_collator
)

trainer.train()

trainer.save_model(OUTPUT_DIR)
print("✔ TRAINING COMPLETE — Model saved to:", OUTPUT_DIR)
