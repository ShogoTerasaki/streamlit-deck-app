import streamlit as st
import itertools
import pandas as pd

# ------------------------
# カードデータと特性設定
# ------------------------
cards = {
    "ナイト": ["エリート", "タンク"],
    "アーチャー": ["クラン", "シューター"],
    "ゴブリン": ["ゴブリン", "アサシン"],
    "槍ゴブリン": ["ゴブリン", "スローワー"],
    "ボンバー": ["アンデット", "スローワー"],
    "バーバリアン": ["クラン", "ファイター"],
    "バルキリー": ["クラン", "アベンジャー"],
    "P.E.K.K.A": ["エース", "タンク"],
    "プリンス": ["エリート", "ファイター"],
    "巨大スケルトン": ["アンデット", "ファイター"],
    "吹き矢ゴブリン": ["ゴブリン", "シューター"],
    "執行人ファルチェ": ["エース", "スローワー"],
    "プリンセス": ["エリート", "シューター"],
    "メガナイト": ["エース", "ファイター"],
    "ロイヤルゴースト": ["アンデット", "アサシン"],
    "アサシンユーノ": ["エース", "アベンジャー"],
    "ゴブリンマシン": ["ゴブリン", "タンク"],
    "スケルトンキング": ["アンデット", "タンク"],
    "ゴールドナイト": ["エリート", "アサシン"],
    "アーチャークイーン": ["クラン", "アベンジャー"]
}

traits_2_or_4 = {"エース", "ファイター", "クラン", "ゴブリン", "タンク", "エリート", "アンデット"}
traits_3_only = {"スローワー", "シューター", "アベンジャー", "アサシン"}

# ------------------------
# スコア計算関数
# ------------------------
def calculate_score(deck):
    trait_counts = {}
    for card in deck:
        for trait in cards[card]:
            trait_counts.setdefault(trait, set()).add(card)
    score = 0
    breakdown = []
    for trait, card_set in trait_counts.items():
        n = len(card_set)
        if trait in traits_2_or_4:
            if n >= 4:
                score += 4
                breakdown.append((trait, 4, list(card_set)))
            elif n >= 2:
                score += 2
                breakdown.append((trait, 2, list(card_set)))
        elif trait in traits_3_only:
            if n >= 3:
                score += 3
                breakdown.append((trait, 3, list(card_set)))
    return score, breakdown

# ------------------------
# Streamlit アプリ本体
# ------------------------
st.title("カードデッキ最適化アプリ")
st.write("3枚までカードを固定して、スコアが最大となるデッキを探索します。")

all_card_names = list(cards.keys())
selected_cards = st.multiselect("固定するカードを最大3枚まで選択:", all_card_names, max_selections=3)

deck_size = st.selectbox("デッキの枚数を選択", [6, 7], index=1)

if len(selected_cards) > deck_size:
    st.error("選択カードがデッキサイズを超えています！")
    st.stop()

if st.button("デッキを最適化"):
    remaining_cards = [card for card in all_card_names if card not in selected_cards]
    comb_size = deck_size - len(selected_cards)

    combinations = list(itertools.combinations(remaining_cards, comb_size))
    results = []

    for combo in combinations:
        full_deck = list(selected_cards) + list(combo)
        score, breakdown = calculate_score(full_deck)
        results.append({"deck": full_deck, "score": score, "breakdown": breakdown})

    if results:
        max_score = max(r["score"] for r in results)
        top_decks = [r for r in results if r["score"] == max_score]

        st.success(f"最大スコア: {max_score}点 （{len(top_decks)}通り）")

        for idx, r in enumerate(top_decks, 1):
            st.markdown(f"### デッキ候補 {idx}")
            st.write(", ".join(r["deck"]))
            st.markdown("**スコア内訳:**")
            for trait, score_part, members in r["breakdown"]:
                st.write(f"- {trait}: {score_part}点（{', '.join(members)}）")
    else:
        st.warning("該当するデッキが見つかりませんでした。")