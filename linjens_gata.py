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
# --- Rita graf med rutnät ---
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot(x, y, label=f"Linjens gåta", linewidth=2)

# Rita koordinataxlar
ax.axhline(0, color='black', linewidth=1.2)
ax.axvline(0, color='black', linewidth=1.2)

# Rutnät
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_xticks(np.arange(-10, 11, 1))
ax.set_yticks(np.arange(-10, 11, 1))
ax.grid(True, which='both', color='gray', linewidth=0.5, linestyle='--')

# Gör rutorna fyrkantiga (lika skalning på axlarna)
ax.set_aspect('equal', adjustable='box')

# Etiketter och titel
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Gissa linjens ekvation")
ax.legend()

st.pyplot(fig)


st.markdown("### Gissa ekvationen för linjen ovan!")

# --- Turhantering ---
spelare = "Spelare 1" if st.session_state.turn == 1 else "Spelare 2"
st.subheader(f"Det är {spelare}s tur!")

st.markdown("### Gissa ekvationen för linjen ovan!")

spelare = "Spelare 1" if st.session_state.turn == 1 else "Spelare 2"
st.subheader(f"Det är {spelare}s tur!")

gissning = st.text_input("Skriv din gissning (t.ex. y = 2x + 1)").replace(" ", "")

def parse_guess(guess):
    pattern = r"y=([\-]?\d*\.?\d*)x([\+\-]?\d+\.?\d*)?"
    match = re.match(pattern, guess)
    if match:
        k = match.group(1)
        m = match.group(2)
        k = float(k) if k not in ["", "+", "-"] else (1.0 if k != "-" else -1.0)
        m = float(m) if m else 0.0
        return k, m
    return None, None

if st.button("Gissa!"):
    k_guess, m_guess = parse_guess(gissning)

    if k_guess is None:
        st.warning("⚠️ Formatet känns fel. Skriv exempelvis: **y = 2x + 1**")
    else:
        # Kontrollera rätt svar
        if abs(k_guess - st.session_state.k) < 0.01 and abs(m_guess - st.session_state.m) < 0.01:
            st.success(f"🎉 RÄTT! {spelare} får 1 poäng!")

            # Ge poäng
            if st.session_state.turn == 1:
                st.session_state.score1 += 1
            else:
                st.session_state.score2 += 1

            # Generera ny linje automatiskt
            st.session_state.k = random.randint(-4, 4)
            st.session_state.m = random.randint(-5, 5)

            # Visa direkt uppdaterad linje
            st.rerun()

        else:
            # Pedagogisk feedback
            feedback = []

            # L lutning
            if k_guess < st.session_state.k:
                feedback.append("➡️ **Linjen är brantare än du tror. Prova ett större värde på k.**")
            elif k_guess > st.session_state.k:
                feedback.append("➡️ **Linjen är mindre brant än du tror. Prova ett mindre värde på k.**")

            # m skärning
            if m_guess < st.session_state.m:
                feedback.append("➡️ **Linjen skär y-axeln högre upp. Prova ett större värde på m.**")
            elif m_guess > st.session_state.m:
                feedback.append("➡️ **Linjen skär y-axeln längre ned. Prova ett mindre värde på m.**")

            st.info("❌ **Fel gissat!** Här kommer en ledtråd:")
            for tip in feedback:
                st.write(tip)

            # Byt spelare
            st.session_state.turn = 2 if st.session_state.turn == 1 else 1
