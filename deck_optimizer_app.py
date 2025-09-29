import streamlit as st
import itertools
import pandas as pd

# ------------------------
# カードデータと特性設定（最新版）
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

traits_2_or_4_or_6 = {"クラン", "ゴブリン", "エース", "ファイター", "シューター", "アサシン", "ブラスター", "タンク", "アベンジャー", "エリート", "アンデット"}
traits_2_only = {"ファイア", "エレクトリック", "メイジ"}

def calculate_score(deck, mode="normal", dummy_traits=None):
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
            if mode == "ultimate" and trait in {"エリート", "アンデット"}:
                if n >= 6:
                    score += 6
                    breakdown.append((trait, 6, list(card_set)))
                elif n >= 4:
                    score += 4
                    breakdown.append((trait, 4, list(card_set)))
                elif n >= 2:
                    score += 2
                    breakdown.append((trait, 2, list(card_set)))
            else:
                if n >= 4:
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

st.title("カードデッキ最適化アプリ")

mode = st.radio("ゲームモードを選択", ["通常モード", "究極の種族モード", "特性ダミーモード", "スコアお手本出力"])

# 停止ボタン（チェック）を上部に設置
stop_search = st.checkbox("🔴 検索を中止する")

if mode == "スコアお手本出力":
    st.subheader("全モードでの最適デッキを探索中...")
    modes_to_run = [
        ("通常モード", [], 6, "normal"),
        ("究極の種族モード", ["エリート", "アンデット"], 7, "ultimate"),
    ]
    all_traits = sorted({trait for traits in cards.values() for trait in traits})
    for trait1 in all_traits:
        for trait2 in all_traits:
            if trait1 != trait2:
                modes_to_run.append((f"特性ダミーモード: {trait1} + {trait2}", [trait1, trait2], 7, "normal"))

    for label, dummy_traits, deck_size, mode_flag in modes_to_run:
        if stop_search:
            st.warning("検索が中断されました。")
            break

        all_card_names = list(cards.keys())
        combinations = list(itertools.combinations(all_card_names, deck_size - (1 if dummy_traits else 0)))
        results = []
        for combo in combinations:
            if stop_search:
                st.warning("検索が中断されました。")
                break

            score, breakdown = calculate_score(combo, mode=mode_flag, dummy_traits=dummy_traits)
            results.append({"deck": combo, "score": score, "breakdown": breakdown})

        if results:
            max_score = max(r["score"] for r in results)
            top_decks = [r for r in results if r["score"] == max_score]

            st.markdown(f"## {label} — 最大スコア: {max_score}点 （{len(top_decks)}通り）")
            if len(top_decks) <= 20:
                for idx, r in enumerate(top_decks, 1):
                    st.markdown(f"### デッキ {idx}")
                    st.write(", ".join(r["deck"]))
                    for trait, score_part, members in r["breakdown"]:
                        st.write(f"- {trait}: {score_part}点（{', '.join(members)}）")
            else:
                st.info("最適デッキが20通りを超えるため、構成は省略します。")
    st.stop()

if mode == "特性ダミーモード":
    all_traits = sorted({trait for traits in cards.values() for trait in traits})
    dummy_trait_1 = st.selectbox("ダミーユニット特性①を選択", all_traits, index=0)
    dummy_trait_2 = st.selectbox("ダミーユニット特性②を選択", [t for t in all_traits if t != dummy_trait_1], index=1)
    dummy_traits = [dummy_trait_1, dummy_trait_2]
    deck_size = 7
elif mode == "究極の種族モード":
    dummy_traits = ["エリート", "アンデット"]
    deck_size = 7
else:
    dummy_traits = []
    deck_size = 6

st.write(f"このモードでは {deck_size} 枚のデッキを構成します。")

all_card_names = list(cards.keys())
selected_cards = st.multiselect("固定するカードを最大5枚まで選択:", all_card_names, max_selections=5)

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

    for combo in combinations:
        if stop_search:
            st.warning("検索が中断されました。")
            break

        full_deck = list(selected_cards) + list(combo)
        score, breakdown = calculate_score(full_deck, mode=mode_flag, dummy_traits=dummy_traits)
        results.append({"deck": full_deck, "score": score, "breakdown": breakdown})

    if results:
        max_score = max(r["score"] for r in results)
        top_decks = [r for r in results if r["score"] == max_score]

        st.success(f"最大スコア: {max_score}点 （{len(top_decks)}通り）")

        if len(top_decks) <= 10:
            for idx, r in enumerate(top_decks, 1):
                st.markdown(f"### デッキ候補 {idx}")
                st.write(", ".join(r["deck"]))
                st.markdown("**スコア内訳:**")
                for trait, score_part, members in r["breakdown"]:
                    st.write(f"- {trait}: {score_part}点（{', '.join(members)}）")
        else:
            st.info("表示件数が多いため、構成は省略します。")
    else:
        st.warning("該当するデッキが見つかりませんでした。")