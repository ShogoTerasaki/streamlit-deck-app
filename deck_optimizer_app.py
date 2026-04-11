import streamlit as st
import itertools

# =========================
# カード定義
# =========================

cards = {
    "ナイト": ["エリート", "ディフェンダー"],
    "アーチャー": ["クラン", "マークスマン"],
    "ゴブリン": ["ゴブリン", "アサシン"],
    "バーバリアン": ["クラン", "ウォーリア"],
    "スケルトンドラゴン": ["アンデット", "ドラゴン"],
    "ウィザード": ["ファイア", "サボタージュ"],
    "吹き矢ゴブリン": ["ゴブリン", "マークスマン"],
    "ジャイアント": ["ジャイアント", "スーパースター"],
    "マスケット銃士": ["エリート", "マークスマン"],
    "バルキリー": ["クラン", "ディフェンダー"],
    "ロイヤルジャイアント": ["ジャイアント", "マークスマン"],
    "巨大スケルトン": ["アンデット", "ディフェンダー"],
    "ダイナマイトゴブリン": ["ゴブリン", "ウォーリア"],
    "P.E.E.K.A": ["エース", "スーパースター"],
    "ネクロマンサー": ["アンデット", "サボタージュ"],
    "ベビードラゴン": ["ファイア", "ドラゴン"],
    "プリンス": ["エリート", "ウォーリア"],
    "ゴブリンマシン": ["ゴブリン", "スーパースター"],
    "スケルトンキング": ["アンデット", "ウォーリア"],
    "ゴールドナイト": ["エリート", "アサシン"],
    "アーチャークイーン": ["クラン", "スーパースター"],
    "モンク": ["エース", "ディフェンダー"],

    # 追加4体
    "執行人ファルチェ": ["エース", "サボタージュ"],
    "ロイヤルゴースト": ["アンデット", "アサシン"],
    "アサシンユーノ": ["エース", "アサシン"],
    "プリンセス": ["エリート", "サボタージュ"],
}

# =========================
# 特性発動ルール
# =========================

# 2枚のみ発動
traits_2_only = {
    "ドラゴン",
    "ファイア",
    "ジャイアント",
}

# 2枚 or 4枚発動
traits_2_or_4 = {
    "マークスマン",
    "ディフェンダー",
    "ウォーリア",
    "クラン",
    "ゴブリン",
    "エリート",
    "アンデット",
    "スーパースター",
    "エース",
    "アサシン",
    "サボタージュ",
}

# 究極の種族モードでのみ 2 / 4 / 6 発動
traits_2_or_4_or_6_ultimate = {
    "エリート",
    "アンデット",
}

# =========================
# スコア計算
# =========================

def calculate_score(deck, mode="通常モード", dummy_traits=None):
    trait_members = {}

    for card in deck:
        for trait in cards[card]:
            trait_members.setdefault(trait, []).append(card)

    if dummy_traits:
        for trait in dummy_traits:
            trait_members.setdefault(trait, []).append("ダミーユニット")

    score = 0
    breakdown = []

    for trait, members in trait_members.items():
        n = len(members)

        # 究極の種族モード専用
        if mode == "究極の種族モード" and trait in traits_2_or_4_or_6_ultimate:
            if n >= 6:
                score += 6
                breakdown.append((trait, 6, members))
            elif n >= 4:
                score += 4
                breakdown.append((trait, 4, members))
            elif n >= 2:
                score += 2
                breakdown.append((trait, 2, members))

        # 2枚のみ
        elif trait in traits_2_only:
            if n >= 2:
                score += 2
                breakdown.append((trait, 2, members))

        # 2枚 or 4枚
        elif trait in traits_2_or_4:
            if n >= 4:
                score += 4
                breakdown.append((trait, 4, members))
            elif n >= 2:
                score += 2
                breakdown.append((trait, 2, members))

    return score, breakdown


# =========================
# Streamlit UI
# =========================

st.title("カードデッキ最適化アプリ")

mode = st.radio(
    "ゲームモードを選択",
    ["通常モード", "究極の種族モード"]
)

# 通常モードは6体
# 究極の種族モードは「6体 + ダミー1体」で計7体
if mode == "究極の種族モード":
    deck_size = 6
    dummy_traits = ["エリート", "アンデット"]
    st.write("このモードでは 6体 + ダミーユニット1体 の計7体で構成します。")
else:
    deck_size = 6
    dummy_traits = []
    st.write("このモードでは 6体で構成します。")

selected_cards = st.multiselect(
    "固定するカード（最大5枚）",
    list(cards.keys()),
    max_selections=5
)

if len(selected_cards) > deck_size:
    st.error("固定カードが多すぎます")
    st.stop()

if st.button("最適デッキを探索"):
    remaining = [c for c in cards.keys() if c not in selected_cards]
    comb_size = deck_size - len(selected_cards)

    all_combos = list(itertools.combinations(remaining, comb_size))

    results = []
    for combo in all_combos:
        deck = selected_cards + list(combo)
        score, breakdown = calculate_score(
            deck,
            mode=mode,
            dummy_traits=dummy_traits
        )
        results.append((deck, score, breakdown))

    if not results:
        st.warning("構成が見つかりませんでした")
    else:
        max_score = max(r[1] for r in results)
        best = [r for r in results if r[1] == max_score]

        st.success(f"最大スコア：{max_score}点（{len(best)}通り）")

        if len(best) <= 10:
            for i, (deck, score, breakdown) in enumerate(best, 1):
                st.markdown(f"### デッキ{i}")
                if mode == "究極の種族モード":
                    st.write(", ".join(deck) + " + ダミーユニット")
                else:
                    st.write(", ".join(deck))

                st.markdown("**スコア内訳**")
                for trait, pts, mem in breakdown:
                    st.write(f"- {trait}：{pts}点（{', '.join(mem)}）")
        else:
            st.info("最適構成が多いため詳細は省略しました。")
