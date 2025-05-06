
import streamlit as st
from PIL import Image
import io
import zipfile
import math

st.set_page_config(page_title="画像分割ツール", layout="wide")
st.title("📄 画像分割ツール（分割数選択＆横並びプレビュー）")

uploaded_file = st.file_uploader("画像をアップロードしてください（拡張子制限なし）", type=None)

if uploaded_file:
    st.write(f"受け取ったファイル名: `{uploaded_file.name}`")
    try:
        img = Image.open(uploaded_file).convert("RGB")

        num_splits = st.slider("分割数を選択してください", min_value=1, max_value=10, value=3)

        # 分割処理
        chunk_height = math.ceil(img.height / num_splits)
        chunks = []

        st.markdown("### 🔍 分割画像プレビュー")
        cols = st.columns(num_splits)

        for i in range(num_splits):
            top = i * chunk_height
            bottom = min((i + 1) * chunk_height, img.height)
            box = (0, top, img.width, bottom)
            chunk = img.crop(box)
            chunks.append(chunk)
            with cols[i]:
                st.image(chunk, caption=f"{i+1}枚目", use_column_width=True)

        # ZIPにまとめてダウンロード
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for idx, chunk in enumerate(chunks):
                img_byte_arr = io.BytesIO()
                chunk.save(img_byte_arr, format="PNG")
                zip_file.writestr(f"chunk_{idx+1}.png", img_byte_arr.getvalue())

        st.download_button(
            label="📦 分割画像をZIPで一括ダウンロード",
            data=zip_buffer.getvalue(),
            file_name="split_images.zip",
            mime="application/zip"
        )

    except Exception as e:
        st.error("画像の読み込みに失敗しました。対応形式の画像をアップロードしてください。")
        st.stop()
