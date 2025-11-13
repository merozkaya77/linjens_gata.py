import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random
import re

# --- Grundinställningar ---
st.set_page_config(page_title="Linjens gåta", page_icon="🎯", layout="centered")

st.title("🎯 Linjens gåta – Mattespel om y = kx + m")
st.write("Två spelare turas om att gissa linjens ekvation. Rätt gissning ger ett poäng!")

# --- Speldata i session ---
if "score1" not in st.session_state:
    st.session_state.score1 = 0
if "score2" not in st.session_state:
    st.session_state.score2 = 0
if "turn" not in st.session_state:
    st.session_state.turn = 1
if "k" not in st.session_state:
    st.session_state.k = random.randint(-4, 4)
if "m" not in st.session_state:
    st.session_state.m = random.randint(-5, 5)

# --- Rita graf ---
x = np.linspace(-10, 10, 200)
y = st.session_state.k * x + st.session_state.m
fig, ax = plt.subplots()
ax.plot(x, y, label=f"Linjens gåta")
ax.axhline(0, color='black', linewidth=0.8)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_ylim(-10, 10)
ax.legend()
st.pyplot(fig)

st.markdown("### Gissa ekvationen för linjen ovan!")

# --- Turhantering ---
spelare = "Spelare 1" if st.session_state.turn == 1 else "Spelare 2"
st.subheader(f"Det är {spelare}s tur!")

gissning = st.text_input("Skriv din gissning (ex: y = 2x + 1)").replace(" ", "")

def parse_guess(guess):
    """Tolkar elevens gissning och plockar ut k och m"""
    pattern = r"y=([\-]?\d*\.?\d*)x([\+\-]?\d+\.?\d*)?"
    match = re.match(pattern, guess)
    if match:
        k = float(match.group(1)) if match.group(1) not in ["", "-", "+"] else (1.0 if match.group(1) != "-" else -1.0)
        m = float(match.group(2)) if match.group(2) else 0.0
        return k, m
    return None, None

if st.button("Gissa!"):
    k_guess, m_guess = parse_guess(gissning)
    if k_guess is None:
        st.warning("Fel format! Skriv t.ex. y = 2x + 1")
    else:
        if abs(k_guess - st.session_state.k) < 0.01 and abs(m_guess - st.session_state.m) < 0.01:
            st.success(f"Rätt! {spelare} får 1 poäng 🎉")
            if st.session_state.turn == 1:
                st.session_state.score1 += 1
            else:
                st.session_state.score2 += 1
            # Ny linje
            st.session_state.k = random.randint(-4, 4)
            st.session_state.m = random.randint(-5, 5)
        else:
            # Ledtråd (AI-inspirerad feedback)
            tip = "Lutningen är större" if k_guess < st.session_state.k else "Lutningen är mindre"
            tip_m = "Skärningen är högre" if m_guess < st.session_state.m else "Skärningen är lägre"
            st.info(f"Fel! Tips: {tip}, {tip_m}. Nu är det den andra spelarens tur.")
            st.session_state.turn = 2 if st.session_state.turn == 1 else 1

# --- Poängställning ---
st.markdown("---")
st.subheader("Poängställning:")
st.write(f"Spelare 1: **{st.session_state.score1}** poäng")
st.write(f"Spelare 2: **{st.session_state.score2}** poäng")

# --- Återställ ---
if st.button("Starta om spelet"):
    st.session_state.score1 = 0
    st.session_state.score2 = 0
    st.session_state.turn = 1
    st.session_state.k = random.randint(-4, 4)
    st.session_state.m = random.randint(-5, 5)
    st.experimental_rerun()
