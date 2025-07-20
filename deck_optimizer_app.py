import streamlit as st
from itertools import combinations
from collections import Counter

# --- UI: デッキサイズ選択 ---
deck_size = st.radio("🧩 デッキの枚数を選んでください", [6, 7], index=1)

# --- カードと特性 ---
cards = [
    ("ナイト", ["エリート", "タンク"]),
    ("アーチャー", ["クラン", "シューター"]),
    ("ゴブリン", ["ゴブリン", "アサシン"]),
    ("槍ゴブリン", ["ゴブリン", "スローワー"]),
    ("ボンバー", ["アンデット", "スローワー"]),
    ("バーバリアン", ["クラン", "ファイター"]),
    ("バルキリー", ["クラン", "アベンジャー"]),
    ("P.E.K.K.A", ["エース", "タンク"]),
    ("プリンス", ["エリート", "ファイター"]),
    ("巨大スケルトン", ["アンデット", "ファイター"]),
    ("吹き矢ゴブリン", ["ゴブリン", "シューター"]),
    ("執行人ファルチェ", ["エース", "スローワー"]),
    ("プリンセス", ["エリート", "シューター"]),
    ("メガナイト", ["エース", "ファイター"]),
    ("ロイヤルゴースト", ["アンデット", "アサシン"]),
    ("アサシンユーノ", ["エース", "アベンジャー"]),
    ("ゴブリンマシン", ["ゴブリン", "タンク"]),
    ("スケルトンキング", ["アンデット", "タンク"]),
    ("ゴールドナイト", ["エリート", "アサシン"]),
    ("アーチャークイーン", ["クラン", "アベンジャー"]),
]

category_2_4 = {"エース", "ファイター", "クラン", "ゴブリン", "タンク", "エリート", "アンデット"}
category_3 = {"スローワー", "シューター", "アベンジャー", "アサシン"}

def calculate_score(deck_cards):
    traits = []
    for _, t in deck_cards:
        traits.extend(t)
    count = Counter(traits)
    score = 0
    for t in category_2_4:
        if count[t] >= 4:
            score += 4
        elif count[t] >= 2:
            score += 2
    for t in category_3:
        if count[t] == 3:
            score += 3
    return score

st.title("🃏 デッキ最適化アプリ")

# --- 1枚目選択 ---
card_names = [name for name, _ in cards]
must_card_1 = st.selectbox("① 1枚目のカードを選択してください", card_names)

if must_card_1:
    must_card_data = next(c for c in cards if c[0] == must_card_1)
    remaining_cards = [c for c in cards if c[0] != must_card_1]
    num_to_choose = deck_size - 1
    candidates = [combo + (must_card_data,) for combo in combinations(remaining_cards, num_to_choose)]
    scored = [(deck, calculate_score(deck)) for deck in candidates]
    max_score = max(score for _, score in scored)
    top_decks = [deck for deck, score in scored if score == max_score]

    # --- 最大スコア構成に含まれる2枚目候補を抽出 ---
    second_card_counter = Counter()
    for deck in top_decks:
        for name, _ in deck:
            if name != must_card_1:
                second_card_counter[name] += 1
    sorted_second_cards = [name for name, _ in second_card_counter.most_common()]

    # --- 2枚目選択（最大スコアに含まれるカードのみ） ---
    must_card_2 = st.selectbox("② 2枚目のカードを選択してください（1枚目と同時に含まれる）", sorted_second_cards)

    if must_card_2:
        st.markdown(f"### 🔍 『{must_card_1}』 + 『{must_card_2}』 の最大スコア構成")
        st.write(f"🎯 最大スコア: **{max_score}点**")
        count = 0
        for deck in top_decks:
            names = [name for name, _ in deck]
            if must_card_1 in names and must_card_2 in names:
                count += 1
                st.write(f"・{'、'.join(names)}")
        if count == 0:
            st.warning("この2枚では最大スコアの構成は見つかりませんでした。")

