
import pandas as pd
import streamlit as st
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

def convert_excel(order_file, ecount_file):
    try:
        # 주문현황
        order_df = pd.read_excel(order_file, dtype=str)

        # 이카운트 기준 엑셀 (2행부터 실제 헤더)
        ecount_df = pd.read_excel(ecount_file, skiprows=1, dtype=str)

        # 공백 제거하여 매핑 안정화
        ecount_df['주문번호'] = ecount_df['주문번호'].str.strip()
        ecount_df['묶음주문번호'] = ecount_df['묶음주문번호'].str.strip()

        mapping_dict = dict(zip(ecount_df['주문번호'], ecount_df['묶음주문번호']))

        required_columns = ['판매채널', '주문번호', '운송장번호', '묶음배송번호']
        if not all(col in order_df.columns for col in required_columns):
            st.error("주문현황 파일에 필수 컬럼이 없습니다.")
            return None

        output_data = []
        for _, row in order_df.iterrows():
            판매채널 = row['판매채널']
            묶음배송번호 = row['묶음배송번호']
            송장번호 = row['운송장번호']

            if 판매채널 not in SHOP_CODE_MAP:
                continue

            쇼핑몰코드, 배송방법코드 = SHOP_CODE_MAP[판매채널]

            묶음주문번호 = mapping_dict.get(묶음배송번호)
            if not 묶음주문번호:
                continue  # 매핑 실패 시 제외

            output_data.append({
                '쇼핑몰코드': 쇼핑몰코드,
                '주문번호': 묶음배송번호,
                '묶음주문번호': 묶음주문번호,
                '배송방법코드': 배송방법코드,
                '송장번호': 송장번호,
            })

        if not output_data:
            st.warning("유효한 매핑 결과가 없습니다.")
            return None

        result_df = pd.DataFrame(output_data)

        for col in ECOUNT_COLUMNS:
            if col not in result_df.columns:
                result_df[col] = ""
        result_df = result_df[ECOUNT_COLUMNS]

        return result_df

    except Exception as e:
        st.error(f"오류 발생: {e}")
        return None

# Streamlit UI
st.title("이플렉스 → 이카운트 송장전송양식 변환기")

order_file = st.file_uploader("이플렉스 주문현황 엑셀 업로드", type=["xlsx"])
ecount_file = st.file_uploader("이카운트 주문 엑셀 업로드", type=["xlsx"])

if order_file and ecount_file:
    result_df = convert_excel(order_file, ecount_file)

    if result_df is not None:
        st.success("✅ 변환 완료!")
        st.dataframe(result_df)

        output = io.BytesIO()
        result_df.to_excel(output, index=False)
        st.download_button(
            label="📥 결과 파일 다운로드",
            data=output.getvalue(),
            file_name="이카운트_송장전송양식_.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
