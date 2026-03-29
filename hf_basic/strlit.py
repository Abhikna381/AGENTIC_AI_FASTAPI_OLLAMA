import streamlit as st
import torch
from PIL import Image
from transformers import (
    AutoProcessor, 
    AutoModelForImageTextToText, 
    BitsAndBytesConfig
)

# --- Page Configuration ---
st.set_page_config(page_title="Gemma 3 Vision Lab", layout="wide")

# --- Sidebar: Model Parameters ---
with st.sidebar:
    st.header("⚙️ Model Settings")
    temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
    max_tokens = st.number_input("Max New Tokens", min_value=64, max_value=1024, value=256)
    
    st.divider()
    if st.button("🗑️ Clear Conversation"):
        if "prediction" in st.session_state:
            del st.session_state["prediction"]
        st.rerun()

st.title("📸 Gemma 3: GPU Accelerated")
st.info(f"Connected to: {torch.cuda.get_device_name(0)}")

# --- Model Loading (Cached) ---
@st.cache_resource
def load_model():
    model_id = "google/gemma-3-4b-it"
    
    # 1. 4-bit Quantization (Reduces VRAM usage significantly)
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True
    )
    
    processor = AutoProcessor.from_pretrained(model_id,backend="torchvision")
    
    # 2. Load model directly to GPU
    model = AutoModelForImageTextToText.from_pretrained(
        model_id,
        quantization_config=quant_config,
        device_map={"": 0}, # Force to the first GPU
        trust_remote_code=True,
        attn_implementation="eager"
    )
    return processor, model

# Load the heavy hitters
processor, model = load_model()

# --- User Interface ---
col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    user_query = st.text_input("Ask Gemma:", placeholder="Describe what's happening here...")
    generate_btn = st.button("Generate Answer", type="primary")

with col2:
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        # 2026 standard for full-width images
        st.image(image, caption="Current Context", width="stretch")

        if generate_btn and user_query:
            with st.spinner("Processing with CUDA..."):
                # 1. Build Message
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image"},
                            {"type": "text", "text": user_query}
                        ]
                    },
                ]

                # 2. Prompt Prep
                prompt = processor.apply_chat_template(
                    messages, 
                    add_generation_prompt=True, 
                    tokenize=False
                )
                
                # 3. Tensor Preparation
                inputs = processor(
                    text=[prompt], 
                    images=[image], 
                    return_tensors="pt",
                    padding=True
                ).to("cuda") # Explicitly move to GPU

                # 4. Inference
                try:
                    with torch.inference_mode():
                        outputs = model.generate(
                            **inputs, 
                            max_new_tokens=max_tokens,
                            do_sample=True if temp > 0 else False,
                            temperature=temp if temp > 0 else None,
                        )
                    
                    # 5. Decode
                    input_len = inputs["input_ids"].shape[-1]
                    st.session_state["prediction"] = processor.decode(
                        outputs[0][input_len:], 
                        skip_special_tokens=True
                    )
                except Exception as e:
                    st.error(f"Inference Error: {e}")

    # Display Answer
    if "prediction" in st.session_state:
        st.success("### Answer:")
        st.write(st.session_state["prediction"])