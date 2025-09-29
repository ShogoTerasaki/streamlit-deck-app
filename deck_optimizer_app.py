import streamlit as st
import itertools
import pandas as pd

# ------------------------
# カードデータと特性設定（更新後）
# ------------------------
cards = {
    "バーバリアン": ["クラン", "ファイター"],
    "アーチャー": ["クラン", "シューター"],
    "バルキリー": ["クラン", "タンク"],
    "アーチャークイーン": ["クラン", "アベンジャー"],
    "プリンス": ["エリート", "ファイター"],
    "プリンセス": ["エリート", "シューター"],
    "ゴールドナイト": ["エリート", "アサシン"],
    "マスケット銃士": ["エリート", "ブラスター"],
    "ナイト": ["エリート", "タンク"],
    "吹き矢ゴブリン": ["ゴブリン", "シューター"],
    "ゴブリン": ["ゴブリン", "アサシン"],
    "槍ゴブリン": ["ゴブリン", "ブラスター"],
    "ゴブリンマシン": ["ゴブリン", "タンク"],
    "巨大スケルトン": ["アンデット", "ファイター"],
    "スケルトンドラゴン": ["アンデット", "シューター"],
    "ロイヤルゴースト": ["アンデット", "アサシン"],
    "スケルトンキング": ["アンデット", "タンク"],
    "ネクロマンサー": ["アンデット", "アベンジャー"],
    "メガナイト": ["エース", "ファイター"],
    "アサシンユーノ": ["エース", "アサシン"],
    "執行人ファルチェ": ["エース", "ブラスター"],
    "P.E.K.K.A": ["エース", "アベンジャー"],
    "ベビードラゴン": ["ファイア", "ブラスター"],
    "ウィザード": ["ファイア", "メイジ"],
    "エレクトロジャイアント": ["エレクトリック", "アベンジャー"],
    "エレクトロウィザード": ["エレクトリック", "メイジ"]
}

# 通常モード用特性ルール
traits_2_or_4 = {"クラン", "ゴブリン", "エース", "ファイター", "シューター", "アサシン", "ブラスター", "タンク", "アベンジャー"}
traits_2_only = {"ファイア", "エレクトリック", "メイジ"}

# ------------------------
# スコア計算関数
# ------------------------
def calculate_score(deck, mode="normal"):
    trait_counts = {}
    for card in deck:
        for trait in cards[card]:
            trait_counts.setdefault(trait, set()).add(card)

    score = 0
    breakdown = []
    for trait, card_set in trait_counts.items():
        n = len(card_set)
        if trait in traits_2_or_4 or (mode == "ultimate" and trait in {"エリート", "アンデット"}):
            if n >= 6:
                score += 6
                breakdown.append((trait, 6, list(card_set)))
            elif n >= 4:
                score += 4
                breakdown.append((trait, 4, list(card_set)))
            elif n >= 2:
                score += 2
                breakdown.append((trait, 2, list(card_set)))
        elif trait in traits_2_only:
            if n >= 2:
                score += 2
                breakdown.append((trait, 2, list(card_set)))
    return score, breakdown

# ------------------------
# Streamlit アプリ本体
# ------------------------
st.title("カードデッキ最適化アプリ")

mode = st.radio("ゲームモードを選択", ["通常モード", "究極の種族モード", "特性ダミーモード"])

all_card_names = list(cards.keys())
selected_cards = st.multiselect("固定するカードを最大5枚まで選択:", all_card_names, max_selections=5)

if mode == "通常モード":
    deck_size = 6
    st.write("\n\n通常モードでは6体構成でスコアを最大化します。")
else:
    deck_size = 7
    st.write("\n\nこのモードではダミーユニットを含め7体構成でスコアを最大化します。")

if len(selected_cards) > deck_size:
    st.error("選択カードがデッキサイズを超えています！")
    st.stop()

if st.button("最適デッキを探索"):
    remaining_cards = [card for card in all_card_names if card not in selected_cards]
    comb_size = deck_size - len(selected_cards)

    combinations = list(itertools.combinations(remaining_cards, comb_size))
    results = []

    mode_flag = "normal"
    if mode == "究極の種族モード":
        mode_flag = "ultimate"
    elif mode == "特性ダミーモード":
        mode_flag = "normal"

    for combo in combinations:
        full_deck = list(selected_cards) + list(combo)
        score, breakdown = calculate_score(full_deck, mode=mode_flag)
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
