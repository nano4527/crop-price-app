import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os

st.set_page_config(page_title="작물 가격 예측기", page_icon="🌽")
st.title("🌾 작물 가격 예측 및 돌연변이 계산기")

# 📁 샘플 저장 파일 초기화
SAMPLE_FILE = "samples.csv"

if not os.path.exists(SAMPLE_FILE):
    pd.DataFrame(columns=["작물", "kg", "기준가격", "날짜"]).to_csv(SAMPLE_FILE, index=False)

# 🔹 사용자 입력: 작물 이름
crop_name = st.text_input("작물 이름을 입력하세요 (예: 감자, 토마토)").strip()

# 🔹 사용자 입력: kg (소수점 허용)
kg = st.number_input("kg 수량을 입력하세요", min_value=0.01, step=0.01, format="%.2f")

# 🔹 성장 변이 선택
mutation_type = st.radio("성장 변이를 선택하세요", ["일반", "골드", "레인보우"])
mutation_multiplier = {"일반": 1, "골드": 20, "레인보우": 50}[mutation_type]

# 🔹 돌연변이 선택
st.markdown("### ✅ 붙어있는 돌연변이를 선택하세요")
mutation_data = [
    ("wet", "웻", 1),
    ("Chilled", "칠드", 1),
    ("Frozen", "프로즌", 9),
    ("Shocked", "쇼크드", 99),
    ("Moonlit", "문라이트", 1),
    ("Choc", "초코", 1),
    ("Disco", "디스코", 124),
    ("Bloodlit", "블러드라이트", 3),
    ("Celestial", "셀레스티얼", 119),
    ("Zombified", "좀비", 24),
    ("Plasma", "플라즈마", 4),
    ("Voidtouched", "보이드터치", 134),
    ("pollinated", "수분받음", 2),
    ("HoneyGlazed", "허니글레이즈", 4),
    ("Heavenly", "헤븐리", 4),
    ("Dawnbound", "던바운드", 149),
    ("Molten", "몰튼", 24),
    ("Meteoric", "메테오릭", 124),
    ("Burnt", "번트", 3),
    ("Cooked", "구워진", 9)
]

weather_multiplier = 1
selected_mutations = []

for eng, kor, bonus in mutation_data:
    if st.checkbox(f"{kor} ({eng}) : +{bonus}"):
        weather_multiplier += bonus
        selected_mutations.append((kor, bonus))

# 🔹 예측 사용 여부 체크박스
use_prediction = st.checkbox("📈 가격 예측 기능 사용 (작물별 3개 이상 샘플 필요)")

# 🔹 기존 데이터 불러오기
df = pd.read_csv(SAMPLE_FILE)
crop_samples = df[df["작물"] == crop_name]

# 🔹 예측 여부 판단
predict_price = None
use_model = False

if use_prediction == "가격 예측 사용":
    if len(crop_samples) >= 3:
        coef = np.polyfit(crop_samples["kg"], crop_samples["기준가격"], 2)
        predict_price = np.polyval(coef, kg)
        use_model = True
    else:
        st.warning("⚠️ 예측 가능한 기준 가격이 없습니다 (샘플 3개 이상 필요).")
elif use_prediction == "직접 가격 입력":
    predict_price = st.number_input("직접 입력할 기준 가격", min_value=0, step=100)
    use_model = True  # 수동 입력도 곧바로 계산으로 사용

# 🔹 최종 배수 계산
total_multiplier = mutation_multiplier * weather_multiplier

# 🔹 가격 출력
if use_model:
    final_price = predict_price * total_multiplier
    st.markdown("### 💰 예측 결과")
    st.write(f"📦 기준 가격 (예측): {predict_price:,.0f} 원")
    st.write(f"🔁 적용 배수: {total_multiplier}배")
    st.write(f"💰 최종 가격: **{final_price:,.0f} 원**")
elif crop_name:
    st.warning("⚠️ 예측 가능한 기준 가격이 없습니다 (샘플 3개 이상 필요).")

# 🔹 실제 가격 입력
st.markdown("### 📥 실제 가격을 입력해 주세요")
actual_price = st.number_input("실제 판매 가격", min_value=0, step=100)

# 🔹 실제 가격 저장 버튼
if st.button("✅ 실제 가격 저장"):
    if actual_price > 0 and kg > 0 and crop_name:
        inferred_base = actual_price / total_multiplier
        new_row = pd.DataFrame({
            "작물": [crop_name],
            "kg": [kg],
            "기준가격": [inferred_base],
            "날짜": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M")]
        })
        new_row.to_csv(SAMPLE_FILE, mode='a', index=False, header=False)
        st.success(f"📌 저장 완료! 기준 가격 추정: {inferred_base:,.0f} 원")
    else:
        st.error("❌ 작물명, kg, 실제 가격을 모두 정확히 입력해주세요.")
