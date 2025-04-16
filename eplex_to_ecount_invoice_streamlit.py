
import streamlit as st
import pandas as pd
import io

# 쇼핑몰/배송방법 매핑
SHOP_CODE_MAP = {
    '쿠팡': ('00004', 'CJGLS'),
    '11번가': ('00002', '00034'),
    '롯데온': ('00003', '00034'),
    '롯데ON': ('00003', '00034'),
}

# 이카운트 열 순서 고정
ECOUNT_COLUMNS = ['쇼핑몰코드', '주문번호', '묶음주문번호', '배송방법코드', '송장번호']

def convert_excel(file):
    df = pd.read_excel(file, dtype=str)

    # 필수 컬럼 확인
    required_columns = ['판매채널', '주문번호', '운송장번호', '묶음배송번호']
    if not all(col in df.columns for col in required_columns):
        st.error("주문현황 파일에 필수 컬럼이 없습니다.")
        return None

    output_data = []
    for _, row in df.iterrows():
        channel = row['판매채널']
        if channel not in SHOP_CODE_MAP:
            continue

        shop_code, delivery_code = SHOP_CODE_MAP[channel]

        output_data.append({
            '쇼핑몰코드': shop_code,
            '배송방법코드': delivery_code,
            '묶음주문번호': row['주문번호'],
            '송장번호': row['운송장번호'],
            '주문번호': row['묶음배송번호'],
        })

    if not output_data:
        st.warning("유효한 판매채널의 데이터가 없습니다.")
        return None

    result_df = pd.DataFrame(output_data)

    for col in ECOUNT_COLUMNS:
        if col not in result_df.columns:
            result_df[col] = ""

    result_df = result_df[ECOUNT_COLUMNS]
    return result_df

st.title("이플렉스 → 이카운트 송장전송양식 변환기")

uploaded_file = st.file_uploader("이플렉스 주문현황 엑셀 업로드", type=["xlsx"])

if uploaded_file is not None:
    result = convert_excel(uploaded_file)

    if result is not None:
        st.success("✅ 변환 완료!")
        st.dataframe(result)

        output = io.BytesIO()
        result.to_excel(output, index=False)
        st.download_button(
            label="📥 변환된 파일 다운로드",
            data=output.getvalue(),
            file_name="이카운트_송장전송양식.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
