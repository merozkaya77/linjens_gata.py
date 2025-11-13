import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random
import re

st.set_page_config(page_title="Linjens gåta", page_icon="🎯", layout="centered")

st.title("🎯 Linjens gåta – Tvåspelarläge")
st.write("Två spelare turas om att gissa ekvationen y = kx + m. Först till 10 poäng vinner.")

# ---------- Initiera session state ----------
if "score1" not in st.session_state:
    st.session_state.score1 = 0
if "score2" not in st.session_state:
    st.session_state.score2 = 0
if "turn" not in st.session_state:
    st.session_state.turn = 1  # 1 eller 2
if "k" not in st.session_state:
    # undvik k=0 om du vill ha intressanta linjer - men här tillåter vi 0 också
    st.session_state.k = random.randint(-4, 4)
if "m" not in st.session_state:
    st.session_state.m = random.randint(-5, 5)
if "message" not in st.session_state:
    st.session_state.message = ""  # pedagogisk feedback
if "guess_input" not in st.session_state:
    st.session_state.guess_input = ""  # för att kunna rensa inmatning

# ---------- Funktion för att tolka gissning ----------
def parse_guess(guess: str):
    """
    Acceptabla format:
      y = 2x + 1
      y=2x-3
      y = -x + 2  (tolkar -x som -1x)
      y = x + 1   (tolkar x som 1x)
    Returnerar (k, m) som floats eller (None, None) om fel format.
    """
    guess = guess.replace(" ", "")
    pattern = r"^y=([+\-]?\d*\.?\d*)x([+\-]?\d*\.?\d*)$"
    m = re.match(pattern, guess)
    if not m:
        # även stöd för fall där m saknas, t.ex. "y=2x"
        pattern2 = r"^y=([+\-]?\d*\.?\d*)x$"
        m2 = re.match(pattern2, guess)
        if m2:
            k_str = m2.group(1)
            if k_str in ["", "+"]:
                k = 1.0
            elif k_str == "-":
                k = -1.0
            else:
                k = float(k_str)
            return k, 0.0
        return None, None

    k_str = m.group(1)
    m_str = m.group(2)

    # tolka k
    if k_str in ["", "+"]:
        k = 1.0
    elif k_str == "-":
        k = -1.0
    else:
        k = float(k_str)

    # tolka m
    if m_str in ["", "+"]:
        m_val = 0.0
    else:
        m_val = float(m_str)

    return k, m_val

# ---------- Rita grafen med rutnät och två markerade punkter ----------
def draw_line(k, m):
    x = np.linspace(-10, 10, 400)
    y = k * x + m
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(x, y, linewidth=2)
    ax.axhline(0, color="black", linewidth=1.2)
    ax.axvline(0, color="black", linewidth=1.2)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_xticks(np.arange(-10, 11, 1))
    ax.set_yticks(np.arange(-10, 11, 1))
    ax.grid(True, which='both', linewidth=0.5, linestyle='--')
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Gissa linjens ekvation (y = kx + m)")

    # Markera två heltals-punkter på linjen för hjälp (inte för att ge bort k och m direkt)
    # Välj två x-värden och markera
    x1, x2 = -3, 2
    y1, y2 = k * x1 + m, k * x2 + m
    ax.scatter([x1, x2], [y1, y2], s=40)
    ax.annotate(f"({x1},{round(y1,1)})", (x1, y1), textcoords="offset points", xytext=(5,5))
    ax.annotate(f"({x2},{round(y2,1)})", (x2, y2), textcoords="offset points", xytext=(5,5))

    return fig

# ---------- Visa graf ----------
fig = draw_line(st.session_state.k, st.session_state.m)
st.pyplot(fig)

# ---------- Visa spelstatus ----------
st.markdown("---")
st.subheader("Poängställning")
st.write(f"Spelare 1: **{st.session_state.score1}**")
st.write(f"Spelare 2: **{st.session_state.score2}**")

# Vem har tur nu?
current_player = st.session_state.turn
st.markdown(f"### Det är Spelare {current_player}s tur!")

# Visa eventuell feedback från föregående gissning
if st.session_state.message:
    st.info(st.session_state.message)

# ---------- Vinnarkontroll ----------
if st.session_state.score1 >= 10 or st.session_state.score2 >= 10:
    winner = 1 if st.session_state.score1 >= 10 else 2
    st.balloons()
    st.success(f"🏆 Spelare {winner} vinner! Först till 10 poäng.")
    if st.button("Starta om spelet"):
        # nollställ allt
        st.session_state.score1 = 0
        st.session_state.score2 = 0
        st.session_state.turn = 1
        st.session_state.k = random.randint(-4, 4)
        st.session_state.m = random.randint(-5, 5)
        st.session_state.message = ""
        st.session_state.guess_input = ""
        st.rerun()
    st.stop()  # stoppa resten av appen så man inte kan gissa efter vinst

# ---------- Inmatning för gissning ----------
# Använd en key så att vi kan rensa textfältet efter varje gissning
st.session_state.guess_input = st.text_input("Skriv din gissning (t.ex. y = 2x + 1):", value=st.session_state.guess_input, key="guess")

if st.button("Gissa!"):
    raw = st.session_state.guess_input
    k_guess, m_guess = parse_guess(raw)

    if k_guess is None:
        st.session_state.message = "⚠️ Fel format. Skriv så här: **y = 2x + 1** eller **y = -x - 2**. Prova igen."
        # behåll turen hos samma spelare (de skrev fel format)
        st.rerun()

    # Kontrollera om gissningen är korrekt (tolerans för flyttal)
    tol = 0.01
    if abs(k_guess - st.session_state.k) < tol and abs(m_guess - st.session_state.m) < tol:
        # Rätt gissat
        st.session_state.message = f"🎉 Rätt! Spelare {current_player} får 1 poäng."
        if current_player == 1:
            st.session_state.score1 += 1
        else:
            st.session_state.score2 += 1

        # Generera ny linje
        st.session_state.k = random.randint(-4, 4)
        st.session_state.m = random.randint(-5, 5)

        # Växla tur till andra spelaren för nästa runda (de turas om)
        st.session_state.turn = 2 if current_player == 1 else 1

        # Rensa inmatningsfältet
        st.session_state.guess_input = ""
        st.rerun()

    else:
        # Fel gissat -> pedagogisk feedback, byt tur till andra spelaren, samma linje kvar
        tips = []
        if k_guess < st.session_state.k:
            tips.append("➡️ Linjen är **brantare** än du gissade. Prova ett högre värde på k.")
        elif k_guess > st.session_state.k:
            tips.append("➡️ Linjen är **mindre brant** än du gissade. Prova ett lägre värde på k.")
        else:
            tips.append("➡️ Din uppskattning av lutningen (k) är korrekt eller nära.")

        if m_guess < st.session_state.m:
            tips.append("➡️ Linjen skär y-axeln **högre upp** än du gissade. Prova ett högre värde på m.")
        elif m_guess > st.session_state.m:
            tips.append("➡️ Linjen skär y-axeln **lägre** än du gissade. Prova ett lägre värde på m.")
        else:
            tips.append("➡️ Din uppskattning av skärningen (m) är korrekt eller nära.")

        # Kombinera feedback till ett meddelande
        st.session_state.message = "❌ Fel gissat! Här kommer några ledtrådar:\n\n" + "\n\n".join(tips)

        # Byt tur
        st.session_state.turn = 2 if current_player == 1 else 1

        # Rensa inmatningsfältet för nästa spelare
        st.session_state.guess_input = ""
        st.rerun()

# ---------- Starta om-knapp om man vill nollställa manuellt ----------
st.markdown("---")
if st.button("Starta om spelet (nollställ poäng)"):
    st.session_state.score1 = 0
    st.session_state.score2 = 0
    st.session_state.turn = 1
    st.session_state.k = random.randint(-4, 4)
    st.session_state.m = random.randint(-5, 5)
    st.session_state.message = ""
    st.session_state.guess_input = ""
    st.rerun()
