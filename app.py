
import streamlit as st
from PIL import Image
import io
import zipfile
import math

st.set_page_config(page_title="画像分割ツール", layout="wide")
st.title("📄 画像分割ツール")

# CSS for true horizontal button layout
st.markdown(
    """
    <style>
    .button-container {
        display: flex;
        flex-wrap: nowrap;
        gap: 10px;
        margin-bottom: 20px;
    }
    .button-container form {
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("画像をアップロードしてください（拡張子制限なし）", type=None)

if uploaded_file:
    st.write(f"受け取ったファイル名: `{uploaded_file.name}`")
    try:
        img = Image.open(uploaded_file).convert("RGB")

        left_col, right_col = st.columns(2)

        if "num_splits" not in st.session_state:
            st.session_state.num_splits = 3

        with right_col:
            st.markdown("### 🔢 分割数を選択")
            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            for splits in range(2, 8):
                if st.form(key=f"form_{splits}").form_submit_button(f"{splits}分割"):
                    st.session_state.num_splits = splits
            st.markdown('</div>', unsafe_allow_html=True)

        num_splits = st.session_state.num_splits

        chunk_height = math.ceil(img.height / num_splits)
        chunks = []

        with left_col:
            st.markdown(f"### 🔍 {num_splits}分割プレビュー")
            preview_cols = st.columns(num_splits)
            for i in range(num_splits):
                top = i * chunk_height
                bottom = min((i + 1) * chunk_height, img.height)
                box = (0, top, img.width, bottom)
                chunk = img.crop(box)
                chunks.append(chunk)
                with preview_cols[i]:
                    st.image(chunk, caption=f"{i+1}枚目", use_container_width=True)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for idx, chunk in enumerate(chunks):
                img_byte_arr = io.BytesIO()
                chunk.save(img_byte_arr, format="PNG")
                zip_file.writestr(f"chunk_{idx+1}.png", img_byte_arr.getvalue())

        with right_col:
            st.markdown("### 📥 ダウンロード")
            st.download_button(
                label="📦 分割画像をZIPで一括ダウンロード",
                data=zip_buffer.getvalue(),
                file_name="split_images.zip",
                mime="application/zip"
            )

    except Exception as e:
        st.error("画像の読み込みに失敗しました。対応形式の画像をアップロードしてください。")
        st.stop()
