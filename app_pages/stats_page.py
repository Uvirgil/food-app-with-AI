from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from core.history_manager import HistoryManager
from core.calorie_settings import CalorieSettings


class StatsPage:
    def __init__(self, history_manager: HistoryManager, settings: CalorieSettings):
        # Salvam managerul de istoric si setarile calorice
        self.history = history_manager
        self.settings = settings

    def render(self):
        # Titlul principal al paginii de statistici
        st.title("📊 Dashboard calorii")

        # Optiuni pentru afisarea diferitelor grafice
        st.subheader("Alege ce grafice vrei sa vezi")
        show_daily = st.checkbox("Calorii pe zile", value=True)
        show_last_30 = st.checkbox("Calorii pe ultimele 30 de zile")
        show_trend = st.checkbox("Linie de trend")
        show_pie_month = st.checkbox("Pie chart — raport lunar")
        show_macros_bar = st.checkbox("Bar chart — evolutia macronutrientilor")
        show_table = st.checkbox("Afiseaza tabelul cu date brute")

        # Preluam istoricul utilizatorului
        user_history = self.history.get_user_history()
        if not user_history:
            st.info("Nu exista date pentru grafice.")
            return

        # Construim un dictionar cu totalul de calorii pe fiecare zi
        calories_per_day = {}
        for entry in user_history:
            date = entry["date"]
            cal = entry.get("total_calories", 0) or 0
            calories_per_day[date] = calories_per_day.get(date, 0) + cal

        # Sortam datele pentru afisare corecta
        sorted_dates = sorted(calories_per_day.keys())
        values = [calories_per_day[d] for d in sorted_dates]

        # Sectiune de rezumat rapid
        st.markdown("---")
        st.subheader("📌 Rezumat rapid")

        total_all = sum(values)  # total calorii inregistrate
        avg_all = total_all / len(values)  # media zilnica
        max_day = max(calories_per_day, key=calories_per_day.get)  # ziua cu cele mai multe calorii

        # Afisam 3 metrici rapide
        colA, colB, colC = st.columns(3)
        colA.metric("Total inregistrat", f"{total_all} kcal")
        colB.metric("Media zilnica", f"{avg_all:.1f} kcal")
        colC.metric("Zi maxima", f"{calories_per_day[max_day]} kcal", max_day)

        # Afisam calendarul saptamanal si raportul saptamanal
        self._render_week_calendar(calories_per_day)
        self._render_week_report(calories_per_day)

        # Afisam graficele selectate de utilizator
        if show_daily:
            self._render_daily_bar(sorted_dates, values)

        if show_last_30:
            self._render_last_30(calories_per_day)

        if show_trend:
            self._render_trend(sorted_dates, values)

        if show_pie_month:
            self._render_pie_month(calories_per_day, sorted_dates)

        if show_macros_bar:
            self._render_macros_bar(user_history, sorted_dates)

        # Afisam tabelul brut daca utilizatorul a bifat optiunea
        if show_table:
            st.markdown("---")
            st.subheader("📄 Date brute")
            st.write(calories_per_day)

    def _render_week_calendar(self, calories_per_day):
        # Sectiune pentru calendarul saptamanal
        st.markdown("---")
        st.subheader("📅 Calendar saptamanal calorii")

        # Butoane pentru navigarea intre saptamani
        col_prev, _, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.button("◀ Saptamana anterioara"):
                self.settings.week_offset = self.settings.week_offset - 1

        with col_next:
            if st.button("Saptamana urmatoare ▶"):
                self.settings.week_offset = self.settings.week_offset + 1

        # Calculam inceputul saptamanii curente (luni)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(
            days=7 * self.settings.week_offset
        )

        # Generam lista celor 7 zile ale saptamanii
        week_days = [start_of_week + timedelta(days=i) for i in range(7)]
        week_days_str = [d.strftime("%Y-%m-%d") for d in week_days]
        week_days_pretty = [d.strftime("%d %b") for d in week_days]

        # Preluam caloriile pentru fiecare zi
        week_values = [calories_per_day.get(day, 0) for day in week_days_str]

        # Numele scurte ale zilelor
        day_names = ["L", "M", "M", "J", "V", "S", "D"]
        today_str = today.strftime("%Y-%m-%d")

        # Afisam fiecare zi in cate o coloana
        cols = st.columns(7)
        for i, c in enumerate(cols):
            day = week_days_str[i]
            kcal = week_values[i]
            date_pretty = week_days_pretty[i]

            # Stilizare in functie de situatie
            if day == today_str:
                bg = "#FFFDF5"
                border = "2px solid #E0C080"
                star = "⭐"
            elif kcal > self.settings.max_daily:
                bg = "#FFF6F6"
                border = "1px solid #E0A0A0"
                star = "🔥"
            elif kcal < self.settings.min_daily and kcal > 0:
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

            # Afisam casuta zilei
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
                unsafe_allow_html=True,
            )

        # Salvam contextul saptamanii pentru raportul saptamanal
        self._week_context = (week_values, week_days, day_names, week_days_pretty)

    def _render_week_report(self, calories_per_day):
        # Preluam datele generate in calendar
        week_values, week_days, day_names, week_days_pretty = self._week_context

        st.markdown("---")
        st.subheader("📊 Raport automat saptamanal")

        # Calculam statistici saptamanale
        week_total = sum(week_values)
        week_avg = week_total / 7

        days_under = sum(
            1 for v in week_values if v < self.settings.min_daily and v > 0
        )
        days_over = sum(1 for v in week_values if v > self.settings.max_daily)
        days_zero = sum(1 for v in week_values if v == 0)

        # Cautam ziua cu cele mai multe calorii
        max_value = max(week_values)
        max_index = week_values.index(max_value)
        max_day_name = day_names[max_index]
        max_day_date = week_days_pretty[max_index]

        # Generam verdictul saptamanii
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

        # Afisam metricile saptamanii
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Total saptamana", f"{week_total} kcal")
        col_r2.metric("Media zilnica", f"{week_avg:.1f} kcal")
        col_r3.metric("Zile fara date", f"{days_zero}")

        col_r4, col_r5 = st.columns(2)
        col_r4.metric("Zile sub limita", f"{days_under}")
        col_r5.metric("Zile peste limita", f"{days_over}")

        # Afisam verdictul stilizat
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
            unsafe_allow_html=True,
        )

    def _render_daily_bar(self, sorted_dates, values):
        # Sectiune pentru graficul de calorii pe zile
        st.subheader("📅 Calorii pe zile")

        # Construim DataFrame cu datele sortate
        df_daily = pd.DataFrame(
            {
                "date": [pd.to_datetime(d).date() for d in sorted_dates],
                "calories": values,
            }
        ).sort_values("date")

        # Etichete scurte pentru zilele saptamanii
        day_labels = ["lun", "mar", "mie", "joi", "vin", "sam", "dum"]
        df_daily["day"] = [day_labels[d.weekday()] for d in df_daily["date"]]

        # Grafic bar pentru calorii pe zile
        fig_daily = px.bar(
            df_daily,
            x="day",
            y="calories",
            labels={"day": "Zi", "calories": "Calorii"},
            color_discrete_sequence=["#3A7BD5"],
        )

        # Stilizare bare
        fig_daily.update_traces(width=0.55, marker=dict(opacity=0.95, cornerradius=10))
        fig_daily.update_layout(bargap=0.35)

        # Linie pentru limita minima zilnica
        fig_daily.add_hline(
            y=self.settings.min_daily,
            line_dash="dot",
            line_color="#2ECC71",
            annotation_text="Minim",
            annotation_position="top left",
            annotation_font_color="#2ECC71",
        )

        # Linie pentru limita maxima zilnica
        fig_daily.add_hline(
            y=self.settings.max_daily,
            line_dash="dot",
            line_color="#E74C3C",
            annotation_text="Maxim",
            annotation_position="bottom left",
            annotation_font_color="#E74C3C",
        )

        # Ajustam axa Y pentru a lasa spatiu vizual
        max_val = max(df_daily["calories"])
        fig_daily.update_yaxes(
            range=[0, max_val + 500],
            showline=True,
            linewidth=2,
            linecolor="#222",
            gridcolor="rgba(0,0,0,0.12)",
            tickfont=dict(size=15, color="#111"),
        )

        # Stilizare axa X
        fig_daily.update_xaxes(
            showline=True,
            linewidth=2,
            linecolor="#222",
            tickfont=dict(size=15, color="#111"),
            showgrid=False,
        )

        # Stilizare generala a graficului
        fig_daily.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=30, r=30, t=20, b=20),
            font=dict(color="#111", size=15),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#F2F2F2", font_size=14, font_color="#111"
            ),
        )

        # Afisam graficul
        st.plotly_chart(fig_daily, use_container_width=True)

    def _render_last_30(self, calories_per_day):
        # Sectiune pentru ultimele 30 de zile
        st.subheader("📆 Calorii pe ultimele 30 de zile")

        today = datetime.now().date()
        last_30_days = [today - timedelta(days=i) for i in range(29, -1, -1)]

        # Construim DataFrame cu datele ultimei luni
        df_30 = pd.DataFrame(
            {
                "date": last_30_days,
                "calories": [
                    calories_per_day.get(d.strftime("%Y-%m-%d"), 0)
                    for d in last_30_days
                ],
            }
        )

        # Grafic linie pentru ultimele 30 de zile
        fig30 = px.line(
            df_30,
            x="date",
            y="calories",
            markers=True,
            labels={"date": "Data", "calories": "Calorii"},
            color_discrete_sequence=["#3A7BD5"],
        )

        # Stilizare linie si markere
        fig30.update_traces(
            line=dict(width=3, shape="spline"),
            marker=dict(
                size=7, color="#3A7BD5", line=dict(width=1, color="#1B4F72")
            ),
        )

        # Linie limita minima
        fig30.add_hline(
            y=self.settings.min_daily,
            line_dash="dot",
            line_color="#2ECC71",
            annotation_text="Minim",
            annotation_position="top left",
            annotation_font_color="#2ECC71",
        )

        # Linie limita maxima
        fig30.add_hline(
            y=self.settings.max_daily,
            line_dash="dot",
            line_color="#E74C3C",
            annotation_text="Maxim",
            annotation_position="bottom left",
            annotation_font_color="#E74C3C",
        )

        # Ajustam axa Y
        max_val = max(df_30["calories"])
        fig30.update_yaxes(
            range=[0, max_val + 500],
            showline=True,
            linewidth=2,
            linecolor="#222",
            gridcolor="rgba(0,0,0,0.12)",
            tickfont=dict(size=14, color="#111"),
        )

        # Stilizare axa X
        fig30.update_xaxes(
            showline=True,
            linewidth=2,
            linecolor="#222",
            tickfont=dict(size=13, color="#111"),
            showgrid=False,
            tickformat="%d %b",
        )

        # Stilizare generala
        fig30.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=30, r=30, t=20, b=20),
            font=dict(color="#111", size=15),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#F2F2F2", font_size=14, font_color="#111"
            ),
        )

        st.plotly_chart(fig30, use_container_width=True)

    def _render_trend(self, sorted_dates, values):
        # Sectiune pentru linia de trend
        st.subheader("📉 Linie de trend")

        # Avem nevoie de cel putin 2 valori pentru a calcula trendul
        if len(values) < 2:
            st.info("Nu exista suficiente date pentru trend.")
            return

        # Pregatim datele pentru regresie liniara
        x = np.arange(len(values))
        y = np.array(values)

        # Calculam panta (m) si intersectia (b)
        m, b = np.polyfit(x, y, 1)
        trendline = m * x + b

        # Construim DataFrame pentru grafic
        df_trend = pd.DataFrame(
            {
                "date": [pd.to_datetime(d).date() for d in sorted_dates],
                "calories": values,
                "trend": trendline,
            }
        )

        # Afisam graficul
        fig_trend = px.line(df_trend, x="date", y=["calories", "trend"])
        st.plotly_chart(fig_trend)

        # Interpretam trendul
        if m > 0:
            st.error("Trend crescator")
        elif m < 0:
            st.success("Trend descrescator")
        else:
            st.info("Trend stabil")

    def _render_pie_month(self, calories_per_day, sorted_dates):
        # Sectiune pentru raportul lunar
        st.markdown("---")
        st.subheader("📆 Raport lunar")

        today = datetime.now().date()
        last_month = today - timedelta(days=30)

        # Filtram doar datele din ultimele 30 de zile
        monthly_data = {
            d: calories_per_day[d]
            for d in sorted_dates
            if datetime.strptime(d, "%Y-%m-%d").date() >= last_month
        }

        # Daca exista date, afisam pie chart
        if monthly_data:
            df_month = pd.DataFrame(
                {"Zi": list(monthly_data.keys()), "Calorii": list(monthly_data.values())}
            )
            st.plotly_chart(px.pie(df_month, names="Zi", values="Calorii"))
        else:
            st.info("Nu exista date pentru ultimele 30 de zile.")

    def _render_macros_bar(self, user_history, sorted_dates):
        # Sectiune pentru evolutia macronutrientilor
        st.markdown("---")
        st.subheader("💪 Evolutia macronutrientilor")

        # Dictionare pentru macronutrienti pe zi
        protein_per_day = {}
        carbs_per_day = {}
        fat_per_day = {}

        # Agregam macronutrientii pentru fiecare zi
        for entry in user_history:
            date = entry["date"]
            protein_per_day[date] = protein_per_day.get(date, 0) + entry.get("total_protein", 0)
            carbs_per_day[date] = carbs_per_day.get(date, 0) + entry.get("total_carbs", 0)
            fat_per_day[date] = fat_per_day.get(date, 0) + entry.get("total_fat", 0)

        # Construim DataFrame pentru grafic
        df_macros = pd.DataFrame(
            {
                "date": sorted_dates,
                "Proteine": [protein_per_day.get(d, 0) for d in sorted_dates],
                "Carbohidrati": [carbs_per_day.get(d, 0) for d in sorted_dates],
                "Grasimi": [fat_per_day.get(d, 0) for d in sorted_dates],
            }
        )

        # Afisam bar chart grupat
        st.plotly_chart(
            px.bar(
                df_macros,
                x="date",
                y=["Proteine", "Carbohidrati", "Grasimi"],
                barmode="group",
            )
        )

