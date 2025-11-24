import streamlit as st
import itertools
import pandas as pd

# ------------------------
# カードデータと特性設定（最新版）
# ------------------------
cards = {
    "バーバリアン": ["クラン", "ファイター"],
    "バルキリー": ["クラン", "ブルータリスト"],
    "アーチャークイーン": ["クラン", "シューター"],
    "プリンス": ["エリート", "ファイター"],
    "プリンセス": ["エリート", "ブラスター"],
    "ゴールドナイト": ["エリート", "アサシン"],
    "マスケット銃士": ["エリート", "スーパースター"],
    "吹き矢ゴブリン": ["ゴブリン", "シューター"],
    "ゴブリン": ["ゴブリン", "アサシン"],
    "槍ゴブリン": ["ゴブリン", "ブラスター"],
    "ゴブリンマシン": ["ゴブリン", "ブルータリスト"],
    "スケルトンドラゴン": ["アンデット", "シューター"],
    "ロイヤルゴースト": ["アンデット", "アサシン"],
    "スケルトンキング": ["アンデット", "ブルータリスト"],
    "ネクロマンサー": ["アンデット", "スーパースター"],
    "メガナイト": ["エース", "ファイター"],
    "アサシンユーノ": ["エース", "アサシン"],
    "執行人ファルチェ": ["エース", "ブラスター"],
    "P.E.K.K.A": ["P.E.E.K.A", "ファイター"],
    "ウィザード": ["クラン", "ブラスター"],
    "エレクトロジャイアント": ["ジャイアント", "スーパースター"],
    # 新規追加
    "ミニP.E.K.K.A": ["P.E.E.K.A", "ブルータリスト"],
    "ロイヤルジャイアント": ["ジャイアント", "シューター"],
    "モンク": ["エース", "スーパースター"],
}

traits_2_or_4_or_6 = {
    "クラン", "ゴブリン", "エース", "ファイター", "シューター",
    "アサシン", "ブラスター", "ブルータリスト", "スーパースター",
    "エリート", "アンデット"
}
traits_2_only = {"ジャイアント", "P.E.E.K.A"}

def calculate_score(deck, dummy_traits=None):
    trait_counts = {}
    for card in deck:
        for trait in cards[card]:
            trait_counts.setdefault(trait, set()).add(card)
    if dummy_traits:
        for trait in dummy_traits:
            trait_counts.setdefault(trait, set()).add("ダミーユニット")

    score = 0
    breakdown = []
    for trait, card_set in trait_counts.items():
        n = len(card_set)
        if trait in traits_2_or_4_or_6:
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

mode = st.radio("ゲームモードを選択", ["通常モード", "特性ダミーモード", "スコアお手本出力"])

# 停止ボタン（チェック）
stop_search = st.checkbox("🔴 検索を中止する")

# 特性ダミーモード設定
if mode == "特性ダミーモード":
    all_traits = sorted({trait for traits in cards.values() for trait in traits})
    dummy_trait_1 = st.selectbox("ダミーユニット特性①", all_traits, index=0)
    dummy_trait_2 = st.selectbox("ダミーユニット特性②", [t for t in all_traits if t != dummy_trait_1], index=1)
    dummy_traits = [dummy_trait_1, dummy_trait_2]
    deck_size = 6
else:
    dummy_traits = []
    deck_size = 6

st.write(f"このモードでは {deck_size + (1 if dummy_traits else 0)} 枚のデッキを構成します。")

# 固定カード選択
all_card_names = list(cards.keys())
selected_cards = st.multiselect("固定するカード（最大5枚）", all_card_names, max_selections=5)

if len(selected_cards) > deck_size:
    st.error("選択カードが多すぎます！")
    st.stop()

# 最適化ボタン
if st.button("最適デッキを探索"):
    remaining_cards = [card for card in all_card_names if card not in selected_cards]
    comb_size = deck_size - len(selected_cards)
    combinations = list(itertools.combinations(remaining_cards, comb_size))

    results = []
    for combo in combinations:
        if stop_search:
            st.warning("検索が中断されました。")
            break
        full_deck = list(selected_cards) + list(combo)
        score, breakdown = calculate_score(full_deck, dummy_traits)
        results.append({"deck": full_deck, "score": score, "breakdown": breakdown})

    if results:
        max_score = max(r["score"] for r in results)
        top_decks = [r for r in results if r["score"] == max_score]

        st.success(f"最大スコア: {max_score}点（{len(top_decks)}通り）")
        if len(top_decks) <= 10:
            for idx, r in enumerate(top_decks, 1):
                st.markdown(f"### デッキ {idx}")
                st.write(", ".join(r["deck"]))
                st.markdown("**スコア内訳:**")
                for trait, pts, mems in r["breakdown"]:
                    st.write(f"- {trait}: {pts}点（{', '.join(mems)}）")
        else:
            st.info("最適構成が多いため構成は省略します。")
    else:
        st.warning("条件に合う構成が見つかりませんでした。")

# お手本出力
if mode == "スコアお手本出力":
    st.subheader("全パターン最適スコアを探索中...")
    all_traits = sorted({trait for traits in cards.values() for trait in traits})
    mode_configs = [(f"通常モード", [], 6)]

    for t1 in all_traits:
        for t2 in all_traits:
            if t1 != t2:
                mode_configs.append((f"{t1}+{t2}", [t1, t2], 6))

    for label, dummy_traits, deck_size in mode_configs:
        if stop_search:
            st.warning("中断されました。")
            break

        combinations = list(itertools.combinations(all_card_names, deck_size))
        results = []
        for combo in combinations:
            if stop_search:
                st.warning("中断されました。")
                break
            score, breakdown = calculate_score(combo, dummy_traits)
            results.append({"deck": combo, "score": score, "breakdown": breakdown})

        if results:
            max_score = max(r["score"] for r in results)
            top_decks = [r for r in results if r["score"] == max_score]

            st.markdown(f"## {label} — 最大スコア: {max_score}点（{len(top_decks)}通り）")
            if len(top_decks) <= 20:
                for idx, r in enumerate(top_decks, 1):
                    st.write(", ".join(r["deck"]))
                    for trait, pts, mems in r["breakdown"]:
                        st.write(f"- {trait}: {pts}点（{', '.join(mems)}）")
            else:
                st.info("構成が多いため省略します。")
