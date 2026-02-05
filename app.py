import streamlit as st
from PIL import Image
from openai import OpenAI
# from secret_key import OPENAI_API_KEY
from auth import authenticate, create_account
from history import load_history, add_entry
import plotly.express as px
import io
import base64
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    from secret_key import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------- AUTENTIFICARE -----------------

st.sidebar.title("Autentificare")

mode = st.sidebar.radio("Alege actiunea:", ["Login", "Creeaza cont"])

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Parola", type="password")

if mode == "Creeaza cont":
    if st.sidebar.button("Creeaza cont"):
        if not username or not password:
            st.sidebar.error("Completeaza username si parola.")
        else:
            if create_account(username, password):
                st.sidebar.success("Cont creat cu succes! Acum te poti loga.")
            else:
                st.sidebar.error("Username deja existent.")

if mode == "Login":
    if st.sidebar.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state["user"] = user
            st.sidebar.success(f"Autentificat ca: {user}")
        else:
            st.sidebar.error("Date incorecte.")

if "user" not in st.session_state:
    st.warning("Te rog autentifica-te in stanga.")
    st.stop()

current_user = st.session_state["user"]

# ----------------- NAVIGARE PAGINI -----------------

st.sidebar.markdown("---")
page = st.sidebar.radio("Navigare", ["Home", "Istoric", "Statistici", "Profil"])

# ----------------- FUNCTIE AI VISION MULTI-INGREDIENT + MACRO -----------------

def call_vision_model(image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    img_bytes = buf.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    img_url = f"data:image/png;base64,{img_b64}"

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Analyze the food in the image and return ONLY a valid JSON object.\n"
                            "Use STRICT JSON rules:\n"
                            "- Only double quotes.\n"
                            "- No comments.\n"
                            "- No text outside JSON.\n"
                            "Return exactly this structure:\n"
                            "{\n"
                            "  \"ingredients\": [\n"
                            "      {\n"
                            "          \"name\": \"ingredient_name\",\n"
                            "          \"calories\": estimated_kcal,\n"
                            "          \"protein\": grams_of_protein,\n"
                            "          \"carbs\": grams_of_carbs,\n"
                            "          \"fat\": grams_of_fat\n"
                            "      }\n"
                            "  ],\n"
                            "  \"dish_name\": \"general category\",\n"
                            "  \"total_calories\": total_kcal,\n"
                            "  \"total_protein\": total_protein_grams,\n"
                            "  \"total_carbs\": total_carbs_grams,\n"
                            "  \"total_fat\": total_fat_grams\n"
                            "}\n"
                            "Be realistic with estimates. Output ONLY the JSON."
                        )
                    },
                    {"type": "input_image", "image_url": img_url}
                ]
            }
        ]
    )

    return response.output_text

# ----------------- DEFAULT SETARI CALORII -----------------

if "min_daily" not in st.session_state:
    st.session_state.min_daily = 1800

if "max_daily" not in st.session_state:
    st.session_state.max_daily = 2500

if "min_weekly" not in st.session_state:
    st.session_state.min_weekly = 12000

if "max_weekly" not in st.session_state:
    st.session_state.max_weekly = 17500

if "week_offset" not in st.session_state:
    st.session_state.week_offset = 0







# ----------------- PAGINA: HOME -----------------

if page == "Home":
    st.title("🍽️ Aplicatia de recunoastere a alimentelor")
    
    st.write("Incarca o poza cu mancare si iti dau o estimare detaliata de calorii si macronutrienti.")

    uploaded = st.file_uploader("Incarca o imagine", type=["jpg", "jpeg", "png"])

    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="Imagine incarcata", use_container_width=True)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_bytes = buf.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        result = call_vision_model(img)

        import ast
        try:
            data = json.loads(result)
        except Exception:
            try:
                data = ast.literal_eval(result)
            except Exception:
                st.error("AI a returnat un format invalid.")
                st.write(result)
                st.stop()

        ingredients = data.get("ingredients", [])
        dish_name = data.get("dish_name", "unknown dish")
        total_cal = data.get("total_calories", 0)
        total_protein = data.get("total_protein", 0)
        total_carbs = data.get("total_carbs", 0)
        total_fat = data.get("total_fat", 0)

        add_entry(
            current_user,
            dish_name,
            total_cal,
            total_protein,
            total_carbs,
            total_fat,
            img_b64,
            ingredients
        )

        st.subheader(f"Preparat detectat: {dish_name}")
        st.success(f"Total calorii estimate: {total_cal} kcal")

        st.subheader("Macronutrienti totali:")
        st.write(f"Proteine: {total_protein} g")
        st.write(f"Carbohidrati: {total_carbs} g")
        st.write(f"Grasimi: {total_fat} g")

        st.subheader("Ingrediente detectate (tabel):")
        if ingredients:
            df_ing = pd.DataFrame([
                {
                    "Ingredient": ing.get("name", "unknown"),
                    "Calorii (kcal)": ing.get("calories", 0),
                    "Proteine (g)": ing.get("protein", 0),
                    "Carbohidrati (g)": ing.get("carbs", 0),
                    "Grasimi (g)": ing.get("fat", 0)
                }
                for ing in ingredients
            ])
            st.table(df_ing)
        else:
            st.info("Nu au fost detectate ingrediente in mod clar.")






# ----------------- PAGINA: ISTORIC -----------------

elif page == "Istoric":
    st.title("Istoricul tau")

    history = load_history()
    user_history = history.get(current_user, [])

    if not user_history:
        st.info("Nu ai inca istoric.")
        st.stop()

    # ----------------- CONSTRUIM TABELUL -----------------
    rows = []
    for entry in reversed(user_history):
        rows.append({
            "Data": entry.get("timestamp", ""),
            "Preparat": entry.get("dish_name", "unknown"),
            "Calorii": entry.get("total_calories", 0),
            "Proteine": entry.get("total_protein", 0),
            "Carbohidrati": entry.get("total_carbs", 0),
            "Grasimi": entry.get("total_fat", 0),
            "Image": entry.get("image_b64")
        })

    df = pd.DataFrame(rows)

    # Convertim Data în datetime
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    # ----------------- FILTRE -----------------
    st.subheader("Filtre")

    col1, col2 = st.columns(2)

    # Filtru dupa numele preparatului
    with col1:
        filter_name = st.text_input("Cauta dupa numele preparatului")

    # Filtru dupa interval de date
    with col2:
        valid_dates = df["Data"].dropna()

        if len(valid_dates) > 0:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
        else:
            today = datetime.now().date()
            min_date = today
            max_date = today

        date_range = st.date_input(
            "Alege intervalul de date",
            value=(min_date, max_date)
        )

    # ----------------- APLICAM FILTRE -----------------

    # Filtru dupa nume
    if filter_name:
        df = df[df["Preparat"].str.contains(filter_name, case=False, na=False)]

    # Filtru dupa data
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        df = df[
            (df["Data"].dt.date >= start) &
            (df["Data"].dt.date <= end)
        ]

    # ----------------- TABEL FINAL -----------------
    st.subheader("Tabel istoric filtrat")
    st.dataframe(df.drop(columns=["Image"]), use_container_width=True)

    # ----------------- IMAGINI LA CERERE -----------------
    st.subheader("Vizualizare imagini")

    for idx, row in df.iterrows():
        with st.expander(f"📸 Vezi imaginea pentru: {row['Preparat']}"):
            if row["Image"]:
                st.image(
                    f"data:image/png;base64,{row['Image']}",
                    caption=row["Preparat"],
                    use_container_width=True
                )
            else:
                st.info("Nu exista imagine salvata pentru aceasta intrare.")



# ----------------- PAGINA: STATISTICI -----------------

elif page == "Statistici":
    st.title("📊 Dashboard calorii")

    st.subheader("Alege ce grafice vrei sa vezi")

    show_daily = st.checkbox("Calorii pe zile", value=True)
    show_last_30 = st.checkbox("Calorii pe ultimele 30 de zile")
    show_trend = st.checkbox("Linie de trend")
    show_pie_month = st.checkbox("Pie chart — raport lunar")
    show_macros_bar = st.checkbox("Bar chart — evolutia macronutrientilor")
    show_table = st.checkbox("Afiseaza tabelul cu date brute")

    history = load_history()
    user_history = history.get(current_user, [])

    # st.subheader("Grafice principale")

    if not user_history:
        st.info("Nu exista date pentru grafice.")
        st.stop()

    # ----------------- PRELUCRARE DATE -----------------

    calories_per_day = {}

    for entry in user_history:
        date = entry["date"]
        cal = entry.get("total_calories", 0) or 0
        calories_per_day[date] = calories_per_day.get(date, 0) + cal

    sorted_dates = sorted(calories_per_day.keys())
    values = [calories_per_day[d] for d in sorted_dates]

    # ----------------- METRICI PRINCIPALE -----------------

    st.markdown("---")
    st.subheader("📌 Rezumat rapid")

    total_all = sum(values)
    avg_all = total_all / len(values)
    max_day = max(calories_per_day, key=calories_per_day.get)

    colA, colB, colC = st.columns(3)
    colA.metric("Total inregistrat", f"{total_all} kcal")
    colB.metric("Media zilnica", f"{avg_all:.1f} kcal")
    colC.metric("Zi maxima", f"{calories_per_day[max_day]} kcal", max_day)

    # ----------------- CALENDAR SAPTAMANAL -----------------

    st.markdown("---")
    st.subheader("📅 Calendar saptamanal calorii")

    col_prev, _, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("◀ Saptamana anterioara"):
            st.session_state.week_offset -= 1

    with col_next:
        if st.button("Saptamana urmatoare ▶"):
            st.session_state.week_offset += 1

    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(days=7 * st.session_state.week_offset)

    week_days = [(start_of_week + timedelta(days=i)) for i in range(7)]
    week_days_str = [d.strftime("%Y-%m-%d") for d in week_days]
    week_days_pretty = [d.strftime("%d %b") for d in week_days]
    week_values = [calories_per_day.get(day, 0) for day in week_days_str]

    day_names = ["L", "M", "M", "J", "V", "S", "D"]
    today_str = today.strftime("%Y-%m-%d")

    cols = st.columns(7)

    for i, c in enumerate(cols):
        day = week_days_str[i]
        kcal = week_values[i]
        date_pretty = week_days_pretty[i]

        if day == today_str:
            bg = "#FFFDF5"
            border = "2px solid #E0C080"
            star = "⭐"
        elif kcal > st.session_state.max_daily:
            bg = "#FFF6F6"
            border = "1px solid #E0A0A0"
            star = "🔥"
        elif kcal < st.session_state.min_daily and kcal > 0:
            bg = "#F7FFF7"
            border = "1px solid #A8D5A8"
            star = "🟢"
        elif kcal == 0:
            bg = "#FAFAFA"
            border = "1px solid #DDD"
            star = ""
        else:
            bg = "#F5F5F5"
            border = "1px solid #CCC"
            star = ""

        c.markdown(
            f"""
            <div style="
                background-color:{bg};
                border:{border};
                border-radius:12px;
                padding:16px;
                text-align:center;
                font-size:15px;
                color:#111;
                box-shadow:0 1px 3px rgba(0,0,0,0.04);
            ">
                <b style="font-size:19px;">{day_names[i]}</b><br>
                <span style="font-size:13px; opacity:0.7;">{date_pretty}</span><br>
                <b style="font-size:17px;">{star} {kcal} kcal</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ----------------- RAPORT SAPTAMANAL -----------------

    st.markdown("---")
    st.subheader("📊 Raport automat saptamanal")

    week_total = sum(week_values)
    week_avg = week_total / 7

    days_under = sum(1 for v in week_values if v < st.session_state.min_daily and v > 0)
    days_over = sum(1 for v in week_values if v > st.session_state.max_daily)
    days_zero = sum(1 for v in week_values if v == 0)

    max_value = max(week_values)
    max_index = week_values.index(max_value)
    max_day_name = day_names[max_index]
    max_day_date = week_days_pretty[max_index]

    if week_total == 0:
        verdict = "Nu exista date pentru aceasta saptamana."
        verdict_color = "gray"
    elif days_over >= 3:
        verdict = "Ai depasit limita in mai multe zile. Atentie!"
        verdict_color = "red"
    elif days_over in [1, 2]:
        verdict = "Ai avut cateva zile peste limita. Incearca sa echilibrezi."
        verdict_color = "orange"
    elif days_under >= 4:
        verdict = "Excelent! Majoritatea zilelor sunt sub limita."
        verdict_color = "green"
    else:
        verdict = "Saptamana echilibrata."
        verdict_color = "blue"

    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Total saptamana", f"{week_total} kcal")
    col_r2.metric("Media zilnica", f"{week_avg:.1f} kcal")
    col_r3.metric("Zile fara date", f"{days_zero}")

    col_r4, col_r5 = st.columns(2)
    col_r4.metric("Zile sub limita", f"{days_under}")
    col_r5.metric("Zile peste limita", f"{days_over}")

    st.markdown(
        f"""
        <div style="
            margin-top:18px;
            padding:18px;
            border-radius:12px;
            background-color:#FFFFFF;
            border-left:6px solid {verdict_color};
            color:#111;
            box-shadow:0 1px 4px rgba(0,0,0,0.06);
        ">
            <b style="font-size:19px;">Verdict saptamanal:</b><br>
            <span style="font-size:17px; color:{verdict_color}; font-weight:600;">
                {verdict}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )



#     # ----------------- GRAFICE PRINCIPALE -----------------
# elif page == "Grafice principale":
#     st.title("📊 Grafice principale")

#     history = load_history()
#     user_history = history.get(current_user, [])

#     if not user_history:
#         st.info("Nu exista date pentru grafice.")
#         st.stop()

#     # ----------------- CONSTRUIM DATAFRAME -----------------
#     rows = []
#     for entry in user_history:
#         rows.append({
#             "Data": entry.get("timestamp", ""),
#             "Calorii": entry.get("total_calories", 0),
#             "Proteine": entry.get("total_protein", 0),
#             "Carbohidrati": entry.get("total_carbs", 0),
#             "Grasimi": entry.get("total_fat", 0)
#         })

#     df = pd.DataFrame(rows)

#     # Convertim Data in datetime
#     df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

#     # Eliminam date invalide
#     df = df.dropna(subset=["Data"])

#     # Grupam pe zile
#     df_daily = df.groupby(df["Data"].dt.date).sum().reset_index()
#     df_daily = df_daily.sort_values("Data")

#     # ----------------- VERDICT SAPTAMANAL -----------------
#     st.subheader("📅 Verdict saptamanal")

#     LIMIT = 2500  # limita calorica recomandata

#     last_7 = df_daily.tail(7)
#     days_over = (last_7["Calorii"] > LIMIT).sum()

#     if days_over == 0:
#         st.success("Ai avut o saptamana excelenta, toate zilele sub limita.")
#     elif days_over <= 2:
#         st.warning("Ai avut cateva zile peste limita. Incearca sa echilibrezi.")
#     else:
#         st.error("Ai depasit limita in mai multe zile. Atentie la aportul caloric.")

#     # ----------------- GRAFIC CALORII PE ZILE -----------------
#     st.subheader("🔥 Calorii pe zile")

#     chart_data = pd.DataFrame({
#         "Data": df_daily["Data"],
#         "Calorii": df_daily["Calorii"]
#     })

#     st.bar_chart(chart_data, x="Data", y="Calorii", use_container_width=True)

#     # ----------------- GRAFIC MACRONUTRIENTI -----------------
#     st.subheader("🍗 Macronutrienti pe zile")

#     macro_data = df_daily[["Data", "Proteine", "Carbohidrati", "Grasimi"]]

#     st.line_chart(macro_data, x="Data", use_container_width=True)

#     # ----------------- TOTALURI -----------------
#     st.subheader("📦 Totaluri generale")

#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Total calorii", int(df["Calorii"].sum()))
#     col2.metric("Total proteine", int(df["Proteine"].sum()))
#     col3.metric("Total carbohidrati", int(df["Carbohidrati"].sum()))
#     col4.metric("Total grasimi", int(df["Grasimi"].sum()))

    # ----------------- CALORII PE ZILE -----------------

    if show_daily:
        st.subheader("📅 Calorii pe zile")

        df_daily = pd.DataFrame({
            "date": [pd.to_datetime(d).date() for d in sorted_dates],
            "calories": values
        }).sort_values("date")

        day_labels = ["lun", "mar", "mie", "joi", "vin", "sam", "dum"]
        df_daily["day"] = [day_labels[d.weekday()] for d in df_daily["date"]]

        fig_daily = px.bar(
            df_daily,
            x="day",
            y="calories",
            labels={"day": "Zi", "calories": "Calorii"},
            color_discrete_sequence=["#3A7BD5"]
        )

        fig_daily.update_traces(
            width=0.55,
            marker=dict(opacity=0.95, cornerradius=10)
        )

        fig_daily.update_layout(bargap=0.35)

        fig_daily.add_hline(
            y=st.session_state.min_daily,
            line_dash="dot",
            line_color="#2ECC71",
            annotation_text="Minim",
            annotation_position="top left",
            annotation_font_color="#2ECC71"
        )

        fig_daily.add_hline(
            y=st.session_state.max_daily,
            line_dash="dot",
            line_color="#E74C3C",
            annotation_text="Maxim",
            annotation_position="bottom left",
            annotation_font_color="#E74C3C"
        )

        max_val = max(df_daily["calories"])
        fig_daily.update_yaxes(
            range=[0, max_val + 500],
            showline=True,
            linewidth=2,
            linecolor="#222",
            gridcolor="rgba(0,0,0,0.12)",
            tickfont=dict(size=15, color="#111")
        )

        fig_daily.update_xaxes(
            showline=True,
            linewidth=2,
            linecolor="#222",
            tickfont=dict(size=15, color="#111"),
            showgrid=False
        )

        fig_daily.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=30, r=30, t=20, b=20),
            font=dict(color="#111", size=15),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#F2F2F2",
                font_size=14,
                font_color="#111"
            )
        )

        st.plotly_chart(fig_daily, use_container_width=True)



    # ----------------- CALORII PE ULTIMELE 30 DE ZILE -----------------

    if show_last_30:
        st.subheader("📆 Calorii pe ultimele 30 de zile")

        today = datetime.now().date()
        last_30_days = [(today - timedelta(days=i)) for i in range(29, -1, -1)]

        df_30 = pd.DataFrame({
            "date": last_30_days,
            "calories": [calories_per_day.get(d.strftime("%Y-%m-%d"), 0) for d in last_30_days]
        })

        fig30 = px.line(
            df_30,
            x="date",
            y="calories",
            markers=True,
            labels={"date": "Data", "calories": "Calorii"},
            color_discrete_sequence=["#3A7BD5"]
        )

        fig30.update_traces(
            line=dict(width=3, shape="spline"),
            marker=dict(size=7, color="#3A7BD5", line=dict(width=1, color="#1B4F72"))
        )

        fig30.add_hline(
            y=st.session_state.min_daily,
            line_dash="dot",
            line_color="#2ECC71",
            annotation_text="Minim",
            annotation_position="top left",
            annotation_font_color="#2ECC71"
        )

        fig30.add_hline(
            y=st.session_state.max_daily,
            line_dash="dot",
            line_color="#E74C3C",
            annotation_text="Maxim",
            annotation_position="bottom left",
            annotation_font_color="#E74C3C"
        )

        max_val = max(df_30["calories"])
        fig30.update_yaxes(
            range=[0, max_val + 500],
            showline=True,
            linewidth=2,
            linecolor="#222",
            gridcolor="rgba(0,0,0,0.12)",
            tickfont=dict(size=14, color="#111")
        )

        fig30.update_xaxes(
            showline=True,
            linewidth=2,
            linecolor="#222",
            tickfont=dict(size=13, color="#111"),
            showgrid=False,
            tickformat="%d %b"
        )

        fig30.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=30, r=30, t=20, b=20),
            font=dict(color="#111", size=15),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#F2F2F2",
                font_size=14,
                font_color="#111"
            )
        )

        st.plotly_chart(fig30, use_container_width=True)

    # ----------------- LINIE DE TREND -----------------

    if show_trend:
        st.subheader("📉 Linie de trend")

        if len(values) >= 2:
            x = np.arange(len(values))
            y = np.array(values)
            m, b = np.polyfit(x, y, 1)
            trendline = m * x + b

            df_trend = pd.DataFrame({
                "date": [pd.to_datetime(d).date() for d in sorted_dates],
                "calories": values,
                "trend": trendline
            })

            fig_trend = px.line(df_trend, x="date", y=["calories", "trend"])
            st.plotly_chart(fig_trend)

            if m > 0:
                st.error("Trend crescator")
            elif m < 0:
                st.success("Trend descrescator")
            else:
                st.info("Trend stabil")
        else:
            st.info("Nu exista suficiente date pentru trend.")

    # ----------------- PIE CHART LUNAR -----------------

    if show_pie_month:
        st.markdown("---")
        st.subheader("📆 Raport lunar")

        today = datetime.now().date()
        last_month = today - timedelta(days=30)

        monthly_data = {
            d: calories_per_day[d]
            for d in sorted_dates
            if datetime.strptime(d, "%Y-%m-%d").date() >= last_month
        }

        if monthly_data:
            df_month = pd.DataFrame({
                "Zi": list(monthly_data.keys()),
                "Calorii": list(monthly_data.values())
            })

            st.plotly_chart(px.pie(df_month, names="Zi", values="Calorii"))
        else:
            st.info("Nu exista date pentru ultimele 30 de zile.")

    # ----------------- MACRONUTRIENTI -----------------

    if show_macros_bar:
        st.markdown("---")
        st.subheader("💪 Evolutia macronutrientilor")

        protein_per_day = {}
        carbs_per_day = {}
        fat_per_day = {}

        for entry in user_history:
            date = entry["date"]
            protein_per_day[date] = protein_per_day.get(date, 0) + entry.get("total_protein", 0)
            carbs_per_day[date] = carbs_per_day.get(date, 0) + entry.get("total_carbs", 0)
            fat_per_day[date] = fat_per_day.get(date, 0) + entry.get("total_fat", 0)

        df_macros = pd.DataFrame({
            "date": sorted_dates,
            "Proteine": [protein_per_day.get(d, 0) for d in sorted_dates],
            "Carbohidrati": [carbs_per_day.get(d, 0) for d in sorted_dates],
            "Grasimi": [fat_per_day.get(d, 0) for d in sorted_dates]
        })

        st.plotly_chart(
            px.bar(df_macros, x="date", y=["Proteine", "Carbohidrati", "Grasimi"], barmode="group")
        )

    # ----------------- TABEL DATE BRUTE -----------------

    if show_table:
        st.markdown("---")
        st.subheader("📄 Date brute")
        st.write(calories_per_day)




# ----------------- PAGINA: PROFIL -----------------

elif page == "Profil":
    st.title("Profil utilizator")
    st.write(f"Username: **{current_user}**")

    st.markdown("---")
    st.subheader("Setari calorii")

    st.info("Ajusteaza limitele zilnice si saptamanale. Acestea sunt folosite in calendar si in raportul saptamanal.")

    st.session_state.min_daily = st.number_input(
        "Limita minima (kcal/zi)",
        min_value=0,
        max_value=5000,
        value=st.session_state.min_daily
    )

    st.session_state.max_daily = st.number_input(
        "Limita maxima (kcal/zi)",
        min_value=0,
        max_value=5000,
        value=st.session_state.max_daily
    )

    st.session_state.min_weekly = st.number_input(
        "Limita minima (kcal/saptamana)",
        min_value=0,
        max_value=50000,
        value=st.session_state.min_weekly
    )

    st.session_state.max_weekly = st.number_input(
        "Limita maxima (kcal/saptamana)",
        min_value=0,
        max_value=50000,
        value=st.session_state.max_weekly
    )

    st.success("Setarile au fost salvate.")