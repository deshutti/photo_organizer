import os
import streamlit as st
from organizer import sortiere_medien

st.set_page_config(page_title="Medien-Organizer", layout="wide")

st.markdown("<h1 style='text-align: center;'>📁 Medien-Organizer</h1>", unsafe_allow_html=True)

# 2 Spalten anlegen: links für Ordnerpfade, rechts für Buttons
col1, col2 = st.columns([2, 3])  # 3:2 Breite Verhältnis

with col1:
    st.markdown(
        "<h3 style='text-align: center; width: 100%;'>📂 Ordnerpfade</h3>",
        unsafe_allow_html=True
    )
    quellordner = st.text_input("Quellordner", placeholder="/Pfad/zu/Quellordner")
    zielordner = st.text_input("Zielordner", placeholder="/Pfad/zu/Zielordner")
    duplikat_ordner = st.text_input("Duplikat-Ordner (optional)", placeholder="/Pfad/zu/Duplikate")

with col2:
    # Zwei Spalten für Toggle und Start-Button nebeneinander
    btn_col1, btn_col2 = st.columns([2, 1])

    with btn_col1:
        nur_kopieren = st.toggle("Nur kopieren (statt verschieben)", value=False)
    with btn_col2:
        start_clicked = st.button("▶️ Starten", key="start_button")

    progress = st.progress(0)
    logfenster = st.empty()

# Validierung der Ordnerpfade
valid_quellordner = os.path.isdir(quellordner)
valid_zielordner = os.path.isdir(zielordner)
valid_duplikat_ordner = duplikat_ordner == "" or os.path.isdir(duplikat_ordner)

if not valid_quellordner and quellordner != "":
    st.warning("⚠️ Quellordner existiert nicht oder ist kein Ordner.")
if not valid_zielordner and zielordner != "":
    st.warning("⚠️ Zielordner existiert nicht oder ist kein Ordner.")
if duplikat_ordner and not valid_duplikat_ordner:
    st.info("ℹ️ Duplikat-Ordner wird optional verwendet, Pfad aber ungültig.")

if start_clicked:
    if valid_quellordner and valid_zielordner and valid_duplikat_ordner:
        log_output = []

        def print_fn(msg):
            log_output.append(msg)
            logfenster.code("\n".join(log_output), language='text')

        def progress_fn(percent):
            progress.progress(int(percent * 100))

        sortiere_medien(
            quellordner=quellordner,
            zielordner=zielordner,
            duplikat_ordner=duplikat_ordner or None,
            nur_kopieren=nur_kopieren,
            print_fn=print_fn,
            progress_fn=progress_fn
        )
    else:
        st.error("Bitte valide Ordnerpfade eingeben, bevor Sie starten.")
