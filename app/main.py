
import streamlit as st

st.set_page_config(
    page_title="Révi’Pote — Ton compagnon de révision",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Identité visuelle
NAVY = "#12345A"
TURQUOISE = "#12B8BE"
YELLOW = "#FFC83D"
BG = "#F5FAFF"

st.markdown(
    f"""
    <style>
        .stApp {{
            background: {BG};
            color: {NAVY};
        }}

        .block-container {{
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        .brand {{
            font-size: 2.7rem;
            font-weight: 850;
            letter-spacing: -1.5px;
            color: {NAVY};
            margin-bottom: 0;
        }}

        .brand span {{
            color: {TURQUOISE};
        }}

        .tagline {{
            font-size: 1.05rem;
            color: {NAVY};
            margin-top: -5px;
            margin-bottom: 2rem;
        }}

        .hero {{
            background: linear-gradient(120deg, #E5F5FF, #FFFFFF);
            border: 1px solid #DCEBFA;
            border-radius: 24px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}

        .robot {{
            font-size: 6rem;
            text-align: center;
            line-height: 1.2;
        }}

        .speech {{
            background: white;
            border-radius: 18px;
            padding: 1rem 1.2rem;
            border: 1px solid #E4EDF8;
        }}

        .feature {{
            background: white;
            border: 1px solid #E4EDF8;
            border-radius: 20px;
            padding: 1.2rem;
            min-height: 185px;
            box-shadow: 0 5px 18px rgba(18, 52, 90, 0.04);
        }}

        .feature-icon {{
            font-size: 2.3rem;
        }}

        .feature h3 {{
            color: {NAVY};
            font-size: 1.25rem;
            margin: 0.5rem 0;
        }}

        .feature p {{
            color: #405979;
            font-size: 0.95rem;
        }}

        .stAlert {{
            border-radius: 16px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# En-tête
st.markdown(
    '<div class="brand">Révi’<span>Pote</span> ✨</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="tagline">Ton compagnon de révision</div>',
    unsafe_allow_html=True,
)

# Accueil
with st.container():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    left, right = st.columns([1, 2], vertical_alignment="center")

    with left:
        st.markdown('<div class="robot">🤖📚</div>', unsafe_allow_html=True)
        st.caption("Ton robot compagnon")

    with right:
        st.title("Salut ! On révise quoi aujourd’hui ?")
        st.write(
            "Des cours clairs, des exercices adaptés et une aide "
            "pour comprendre et progresser à ton rythme."
        )
        st.markdown(
            '<div class="speech">💡 <b>On avance ensemble !</b><br>'
            "Chaque petite étape compte. Tu peux progresser à ton rythme."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

st.info(
    "🚧 **Révi’Pote est en construction.** "
    "Les cours, fiches et exercices seront disponibles dans les prochaines étapes."
)

st.subheader("Ton espace de révision")

features = [
    ("📚", "Cours", "Des explications claires pour bien comprendre."),
    ("🎯", "Exercices", "Pour t’entraîner et vérifier ce que tu as appris."),
    ("📝", "Fiches", "Des résumés simples pour retenir l’essentiel."),
    ("📈", "Mon progrès", "Pour suivre tes progrès au fil du temps."),
]

columns = st.columns(4)

for column, (emoji, title, description) in zip(columns, features):
    with column:
        st.markdown(
            f"""
            <div class="feature">
                <div class="feature-icon">{emoji}</div>
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()
st.caption("Révi’Pote · Comprendre, s’entraîner et progresser ensemble 💙")
