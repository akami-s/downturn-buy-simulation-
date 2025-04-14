import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# タイトル
st.markdown("""
<h1 style='font-size: 1.8em; line-height: 1.3; text-align: center;'>
📉<br>下落局面の<br>買付シミュレーション
</h1>
""", unsafe_allow_html=True)


# 入力フォーム
initial_price = st.number_input("初期株価（円）", value=100)
recovery_price = st.number_input("回復時の株価（円）", value=100)
initial_investment = st.number_input("初期投資額（円）", value=1000000)
drop_step = st.number_input("下落ステップ（%ごと）", value=10)
max_drop = st.number_input("最大下落率（%）", value=50)

# 買付金額の決め方
buy_mode = st.radio("買付金額の決め方", ["金額を指定する", "手元資金から自動計算する"])

if buy_mode == "金額を指定する":
    buy_amount = st.number_input("1回あたりの買付額（円）", value=1000000)
else:
    total_capital = st.number_input("手元資金の合計（円）", value=6000000)
    buy_count = int(max_drop / drop_step) + 1
    st.write(f"買付回数: {buy_count} 回")

# 買付方式
buy_type = st.radio("買付方式", ["固定額（毎回同じ金額）", "下落に応じて増額"])

if buy_mode == "手元資金から自動計算する":
    if buy_type == "固定額（毎回同じ金額）":
        buy_amount = total_capital / buy_count
        st.write(f"1回あたりの買付額は **{int(buy_amount):,} 円** になります。\n\n（計算式：買付額 = 手元資金 ÷ 買付回数）")
    else:
        coef_list = [round(1 + 0.2 * i, 1) for i in range(buy_count)]
        coef_formula = " + ".join(map(str, coef_list))
        coef_sum = sum(coef_list)
        buy_amount = total_capital / coef_sum
        st.write(f"増額方式に基づく初回の買付額は **{int(buy_amount):,} 円** になります。")
        st.write(f"（増額係数の合計 = {coef_formula} = {coef_sum}）")

# シミュレーション
if st.button("シミュレーション開始"):
    prices = []
    buy_amounts = []
    buy_units = []
    accumulated_units = []
    total_cost = 0
    total_units = 0

    step_labels = []
    drop_rates_list = []
    amount_list = []

    buy_count = int(max_drop / drop_step) + 1

    for i in range(0, int(max_drop + drop_step), int(drop_step)):
        drop_rate = i / 100
        price = initial_price * (1 - drop_rate)

        if buy_type == "固定額（毎回同じ金額）":
            amount = buy_amount
        else:
            step = i // drop_step
            amount = buy_amount * (1 + 0.2 * step)
            step_labels.append(f"{step + 1} Step")
            drop_rates_list.append(f"-{i}%")
            amount_list.append(int(amount))

        units = amount / price
        total_units += units
        total_cost += amount

        prices.append(price)
        buy_amounts.append(amount)
        buy_units.append(units)
        accumulated_units.append(total_units)

    if buy_type == "下落に応じて増額":
        st.subheader("📋 Buy Amount per Step (Increase Rule)")
        df = pd.DataFrame({
            "Step": step_labels,
            "Drop Rate": drop_rates_list,
            "Buy Amount (JPY)": amount_list
        })
        st.dataframe(df, use_container_width=True)

    # 回復時の評価
    final_value = total_units * recovery_price
    profit = final_value - total_cost
    profit_rate = profit / total_cost * 100

    # 一括投資
    lump_units = total_cost / initial_price
    lump_final_value = lump_units * recovery_price
    lump_profit = lump_final_value - total_cost
    lump_profit_rate = lump_profit / total_cost * 100

    st.subheader("📊 段階投資のシミュレーション結果")
    st.write(f"**総投資額**: {int(total_cost):,} 円")
    st.write(f"**総取得株数**: {total_units:.2f} 株")
    st.write(f"**平均取得単価**: {total_cost / total_units:.2f} 円")
    st.write(f"**回復時の評価額**: {int(final_value):,} 円")
    st.write(f"**リターン**: {profit_rate:.2f} %")

    st.subheader("📊 一括投資との比較")
    st.write(f"**一括投資時の平均取得単価**: {initial_price} 円")
    st.write(f"**同じ金額を一括投資した場合の評価額**: {int(lump_final_value):,} 円")
    st.write(f"**リターン（%）**: {lump_profit_rate:.2f} %")

    fig, ax = plt.subplots()
    ax.bar(['Step Buy', 'Lump Sum'], [profit_rate, lump_profit_rate], color=['skyblue', 'orange'])
    ax.set_ylabel("Return (%)")
    ax.set_title("Step Buy vs Lump Sum: Return Comparison")
    st.pyplot(fig)

    fig2, ax2 = plt.subplots()
    ax2.plot(prices, accumulated_units, marker='o')
    ax2.set_title('Price Decline vs Accumulated Shares')
    ax2.set_xlabel('Stock Price (after decline)')
    ax2.set_ylabel('Accumulated Shares')
    ax2.grid(True)
    ax2.invert_xaxis()
    st.pyplot(fig2)
