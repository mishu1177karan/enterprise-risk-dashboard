import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import io
from fpdf import FPDF

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise Risk Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { color: #e0e0e0; font-size: 2.2rem; margin: 0; }
    .main-header p  { color: #a0b4c8; font-size: 1rem; margin: 0.4rem 0 0; }

    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-val  { font-size: 2rem; font-weight: 700; }
    .metric-label{ font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem; }

    .risk-critical { color: #ef4444; }
    .risk-high     { color: #f97316; }
    .risk-medium   { color: #eab308; }
    .risk-low      { color: #22c55e; }

    .section-header {
        font-size: 1.1rem; font-weight: 600;
        border-left: 4px solid #3b82f6;
        padding-left: 0.75rem;
        margin: 1.5rem 0 1rem;
        color: #e2e8f0;
    }
    .stDataFrame { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Session state initialisation ──────────────────────────────────────────────
RISK_CATEGORIES = [
    "Strategic", "Operational", "Financial", "Compliance / Regulatory",
    "Cyber / Technology", "Reputational", "Environmental / CAT",
    "HR / People", "Third-Party / Supply Chain"
]
MITIGATION_STATUS = ["Not Started", "In Progress", "Implemented", "Accepted", "Transferred"]

SAMPLE_RISKS = [
    {"id": "R001", "title": "Data breach via phishing attack", "category": "Cyber / Technology",
     "likelihood": 4, "impact": 5, "owner": "CTO", "mitigation": "In Progress",
     "description": "Employees susceptible to phishing leading to unauthorised data access.",
     "controls": "MFA enabled, phishing simulation training quarterly.", "date_added": "2024-01-15"},
    {"id": "R002", "title": "Regulatory non-compliance (IRDAI guidelines)", "category": "Compliance / Regulatory",
     "likelihood": 2, "impact": 5, "owner": "Chief Compliance Officer", "mitigation": "Implemented",
     "description": "Failure to comply with IRDAI updated regulations on solvency margins.",
     "controls": "Monthly compliance review, dedicated compliance team.", "date_added": "2024-01-20"},
    {"id": "R003", "title": "Key person dependency - actuarial team", "category": "HR / People",
     "likelihood": 3, "impact": 4, "owner": "CHRO", "mitigation": "In Progress",
     "description": "Over-reliance on 2 senior actuaries for reserving and pricing models.",
     "controls": "Succession planning initiated, cross-training programme.", "date_added": "2024-02-01"},
    {"id": "R004", "title": "Catastrophic flood event - Mumbai portfolio", "category": "Environmental / CAT",
     "likelihood": 2, "impact": 5, "owner": "CRO", "mitigation": "Implemented",
     "description": "Concentrated property exposure in Mumbai flood zones.",
     "controls": "Reinsurance treaty, PML limits per zone.", "date_added": "2024-02-10"},
    {"id": "R005", "title": "Third-party claims administrator failure", "category": "Third-Party / Supply Chain",
     "likelihood": 2, "impact": 3, "owner": "COO", "mitigation": "Not Started",
     "description": "Sole TPA unable to process claims, impacting turnaround.",
     "controls": "SLA monitoring in place, backup TPA not yet contracted.", "date_added": "2024-03-01"},
    {"id": "R006", "title": "Adverse claims experience - liability book", "category": "Financial",
     "likelihood": 3, "impact": 4, "owner": "CFO", "mitigation": "In Progress",
     "description": "Unexpected surge in D&O and CGL claims affecting combined ratio.",
     "controls": "Quarterly claims triangles, pricing re-review triggered.", "date_added": "2024-03-15"},
    {"id": "R007", "title": "Brand damage from mis-selling allegation", "category": "Reputational",
     "likelihood": 2, "impact": 4, "owner": "CMO", "mitigation": "Accepted",
     "description": "Social media allegations of policy mis-selling by retail agents.",
     "controls": "Agent training programme, complaint escalation process.", "date_added": "2024-04-01"},
    {"id": "R008", "title": "Core IT system outage", "category": "Operational",
     "likelihood": 3, "impact": 3, "owner": "CTO", "mitigation": "Implemented",
     "description": "Policy admin system downtime affecting policy issuance.",
     "controls": "DR site active, RTO < 4 hours.", "date_added": "2024-04-10"},
]

if "risks" not in st.session_state:
    st.session_state.risks = SAMPLE_RISKS.copy()
if "next_id" not in st.session_state:
    st.session_state.next_id = 9

def get_risk_score(likelihood, impact):
    return likelihood * impact

def get_risk_level(score):
    if score >= 16: return "Critical", "#ef4444"
    if score >= 10: return "High",     "#f97316"
    if score >= 5:  return "Medium",   "#eab308"
    return           "Low",            "#22c55e"

def get_df():
    df = pd.DataFrame(st.session_state.risks)
    df["score"]       = df["likelihood"] * df["impact"]
    df["level"], df["color"] = zip(*df["score"].apply(
        lambda s: get_risk_level(s)))
    return df

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ Risk Register")
    st.markdown("---")
    page = st.radio("Navigate", ["📊 Dashboard", "➕ Add Risk", "📋 Risk Register", "📄 Export Report"])
    st.markdown("---")
    df_all = get_df()
    total      = len(df_all)
    critical_n = len(df_all[df_all["level"] == "Critical"])
    high_n     = len(df_all[df_all["level"] == "High"])
    open_n     = len(df_all[df_all["mitigation"].isin(["Not Started", "In Progress"])])
    st.markdown(f"**Total Risks:** {total}")
    st.markdown(f"🔴 Critical: {critical_n}")
    st.markdown(f"🟠 High: {high_n}")
    st.markdown(f"⚠️ Open Actions: {open_n}")
    st.markdown("---")
    st.caption("Enterprise Risk Management Framework\nv1.0 · NIA Internship Project")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ Enterprise Risk Dashboard</h1>
        <p>Risk Register · Heat Map · Priority Analysis · ERM Framework</p>
    </div>
    """, unsafe_allow_html=True)

    df = get_df()

    # ── KPI Metrics ──
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (len(df), "Total Risks", "#3b82f6"),
        (len(df[df["level"]=="Critical"]), "Critical", "#ef4444"),
        (len(df[df["level"]=="High"]), "High", "#f97316"),
        (len(df[df["level"]=="Medium"]), "Medium", "#eab308"),
        (len(df[df["mitigation"]=="Implemented"]), "Mitigated", "#22c55e"),
    ]
    for col, (val, label, color) in zip([c1,c2,c3,c4,c5], metrics):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Risk Heat Map ──
    col_heat, col_donut = st.columns([3, 2])

    with col_heat:
        st.markdown('<div class="section-header">Risk Heat Map (Likelihood × Impact)</div>', unsafe_allow_html=True)

        # Build 5×5 grid
        grid = [[[] for _ in range(5)] for _ in range(5)]
        for _, row in df.iterrows():
            l_idx = row["likelihood"] - 1
            i_idx = row["impact"] - 1
            grid[l_idx][i_idx].append(row["id"])

        cell_colors = []
        hover_text  = []
        z_vals      = []
        for l in range(5):
            row_colors = []
            row_hover  = []
            row_z      = []
            for i in range(5):
                score = (l+1) * (i+1)
                _, color = get_risk_level(score)
                ids = grid[l][i]
                row_colors.append(score)
                row_hover.append(f"Score: {score}<br>Risks: {', '.join(ids) if ids else 'None'}")
                row_z.append(score)
            cell_colors.append(row_colors)
            hover_text.append(row_hover)
            z_vals.append(row_z)

        fig_heat = go.Figure(data=go.Heatmap(
            z=z_vals,
            text=hover_text,
            hoverinfo="text",
            colorscale=[
                [0.0,  "#166534"], [0.19, "#166534"],
                [0.20, "#854d0e"], [0.39, "#854d0e"],
                [0.40, "#713f12"], [0.63, "#713f12"],
                [0.64, "#7f1d1d"], [1.0,  "#7f1d1d"],
            ],
            showscale=False,
        ))

        # Annotate cells with risk IDs
        annotations = []
        for l in range(5):
            for i in range(5):
                ids = grid[l][i]
                annotations.append(dict(
                    x=i, y=l,
                    text="<br>".join(ids) if ids else "",
                    showarrow=False,
                    font=dict(color="white", size=10),
                ))

        fig_heat.update_layout(
            xaxis=dict(title="Impact ->", tickvals=list(range(5)),
                       ticktext=["1\nInsignificant","2\nMinor","3\nModerate","4\nMajor","5\nCatastrophic"],
                       tickfont=dict(size=10)),
            yaxis=dict(title="↑ Likelihood", tickvals=list(range(5)),
                       ticktext=["1\nRare","2\nUnlikely","3\nPossible","4\nLikely","5\nAlmost Certain"],
                       tickfont=dict(size=10)),
            annotations=annotations,
            height=380,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_donut:
        st.markdown('<div class="section-header">Risk by Category</div>', unsafe_allow_html=True)
        cat_counts = df["category"].value_counts()
        fig_donut = go.Figure(go.Pie(
            labels=cat_counts.index,
            values=cat_counts.values,
            hole=0.55,
            textinfo="label+value",
            textfont=dict(size=10),
            marker=dict(colors=px.colors.qualitative.Set3),
        ))
        fig_donut.update_layout(
            showlegend=False, height=380,
            margin=dict(l=5, r=5, t=5, b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── Priority Ranking ──
    st.markdown('<div class="section-header">Top Priority Risks</div>', unsafe_allow_html=True)
    top_risks = df.sort_values("score", ascending=False).head(8)

    for _, row in top_risks.iterrows():
        level, color = get_risk_level(row["score"])
        bar_pct = int(row["score"] / 25 * 100)
        mit_emoji = {"Not Started": "🔴", "In Progress": "🟡",
                     "Implemented": "🟢", "Accepted": "🔵", "Transferred": "⚪"
                    }.get(row["mitigation"], "")
        col_a, col_b, col_c, col_d, col_e = st.columns([1, 3, 2, 2, 2])
        col_a.markdown(f"**{row['id']}**")
        col_b.markdown(f"{row['title']}")
        col_c.markdown(f"<span style='color:{color}'><b>{level}</b> ({row['score']})</span>", unsafe_allow_html=True)
        col_d.markdown(f"{mit_emoji} {row['mitigation']}")
        col_e.markdown(f"👤 {row['owner']}")
        st.markdown(f"""<div style="background:#1e293b;border-radius:4px;height:6px;margin-bottom:8px">
            <div style="background:{color};width:{bar_pct}%;height:6px;border-radius:4px"></div></div>""",
            unsafe_allow_html=True)

    # ── Mitigation Status Bar ──
    st.markdown('<div class="section-header">Mitigation Status Overview</div>', unsafe_allow_html=True)
    mit_counts = df["mitigation"].value_counts()
    mit_colors = {"Not Started":"#ef4444","In Progress":"#eab308",
                  "Implemented":"#22c55e","Accepted":"#3b82f6","Transferred":"#a855f7"}
    fig_bar = go.Figure(go.Bar(
        x=mit_counts.index,
        y=mit_counts.values,
        marker_color=[mit_colors.get(s,"#94a3b8") for s in mit_counts.index],
        text=mit_counts.values,
        textposition="outside",
    ))
    fig_bar.update_layout(
        height=280, showlegend=False,
        yaxis=dict(title="Count", gridcolor="#334155"),
        xaxis=dict(title=""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD RISK
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Risk":
    st.markdown("## ➕ Add New Risk")
    st.markdown("Use this form to log a new risk to the register.")

    with st.form("add_risk_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            title    = st.text_input("Risk Title *", placeholder="e.g. Cyber ransomware attack")
            category = st.selectbox("Category *", RISK_CATEGORIES)
            owner    = st.text_input("Risk Owner *", placeholder="e.g. CTO / CRO")
        with c2:
            likelihood  = st.slider("Likelihood (1 = Rare, 5 = Almost Certain)", 1, 5, 3)
            impact      = st.slider("Impact (1 = Insignificant, 5 = Catastrophic)", 1, 5, 3)
            mitigation  = st.selectbox("Mitigation Status", MITIGATION_STATUS)

        description = st.text_area("Risk Description", placeholder="Describe the nature and cause of this risk...")
        controls    = st.text_area("Existing Controls", placeholder="List controls already in place...")

        score = likelihood * impact
        level, color = get_risk_level(score)
        st.markdown(f"**Calculated Risk Score:** <span style='color:{color};font-size:1.2rem'>{score} - {level}</span>", unsafe_allow_html=True)

        submitted = st.form_submit_button("➕ Add to Register", use_container_width=True)
        if submitted:
            if not title or not owner:
                st.error("Please fill in all required fields (*).")
            else:
                new_risk = {
                    "id":          f"R{st.session_state.next_id:03d}",
                    "title":       title,
                    "category":    category,
                    "likelihood":  likelihood,
                    "impact":      impact,
                    "owner":       owner,
                    "mitigation":  mitigation,
                    "description": description,
                    "controls":    controls,
                    "date_added":  datetime.today().strftime("%Y-%m-%d"),
                }
                st.session_state.risks.append(new_risk)
                st.session_state.next_id += 1
                st.success(f"✅ Risk **{new_risk['id']} - {title}** added! Navigate to the Dashboard to view it.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: RISK REGISTER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Risk Register":
    st.markdown("## 📋 Full Risk Register")

    df = get_df()

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    cat_filter = fc1.multiselect("Filter by Category", options=df["category"].unique().tolist(), default=[])
    lvl_filter = fc2.multiselect("Filter by Level", options=["Critical","High","Medium","Low"], default=[])
    mit_filter = fc3.multiselect("Filter by Mitigation", options=MITIGATION_STATUS, default=[])

    filtered = df.copy()
    if cat_filter: filtered = filtered[filtered["category"].isin(cat_filter)]
    if lvl_filter: filtered = filtered[filtered["level"].isin(lvl_filter)]
    if mit_filter: filtered = filtered[filtered["mitigation"].isin(mit_filter)]

    display_cols = ["id","title","category","likelihood","impact","score","level","owner","mitigation","date_added"]
    st.dataframe(
        filtered[display_cols].sort_values("score", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=420,
    )

    st.markdown(f"**Showing {len(filtered)} of {len(df)} risks**")

    # Edit / Delete
    st.markdown("### ✏️ Update Risk")
    risk_ids = [r["id"] for r in st.session_state.risks]
    sel_id   = st.selectbox("Select Risk ID to Edit/Delete", risk_ids)
    sel_risk = next((r for r in st.session_state.risks if r["id"] == sel_id), None)

    if sel_risk:
        with st.form("edit_form"):
            ec1, ec2 = st.columns(2)
            new_mit  = ec1.selectbox("Mitigation Status", MITIGATION_STATUS,
                                     index=MITIGATION_STATUS.index(sel_risk["mitigation"]))
            new_like = ec2.slider("Likelihood", 1, 5, sel_risk["likelihood"])
            new_imp  = st.slider("Impact", 1, 5, sel_risk["impact"])
            new_ctrl = st.text_area("Update Controls", value=sel_risk["controls"])
            sb1, sb2 = st.columns(2)
            update = sb1.form_submit_button("💾 Update", use_container_width=True)
            delete = sb2.form_submit_button("🗑️ Delete Risk", use_container_width=True)

            if update:
                for r in st.session_state.risks:
                    if r["id"] == sel_id:
                        r["mitigation"] = new_mit
                        r["likelihood"] = new_like
                        r["impact"]     = new_imp
                        r["controls"]   = new_ctrl
                st.success(f"✅ {sel_id} updated.")
                st.rerun()

            if delete:
                st.session_state.risks = [r for r in st.session_state.risks if r["id"] != sel_id]
                st.success(f"🗑️ {sel_id} deleted.")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EXPORT REPORT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 Export Report":
    st.markdown("## 📄 Export Risk Report")
    st.markdown("Generate a professional PDF risk report for board / management submission.")

    df = get_df()

    org_name    = st.text_input("Organisation Name", value="Aviva India - Risk Management")
    report_date = st.date_input("Report Date", value=datetime.today())
    prepared_by = st.text_input("Prepared By", value="Risk Management Team")
    st.markdown("---")

    # Preview
    st.markdown("### Report Preview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Risks", len(df))
    c2.metric("Critical / High", len(df[df["level"].isin(["Critical","High"])]))
    c3.metric("Open Actions", len(df[df["mitigation"].isin(["Not Started","In Progress"])]))

    st.markdown("**Top 5 Priority Risks:**")
    top5 = df.sort_values("score", ascending=False).head(5)[
        ["id","title","category","score","level","owner","mitigation"]
    ]
    st.dataframe(top5, use_container_width=True)

    if st.button("📥 Generate & Download PDF Report", use_container_width=True):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title page
        pdf.set_fill_color(15, 52, 96)
        pdf.rect(0, 0, 210, 60, "F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_xy(10, 15)
        pdf.cell(190, 12, "ENTERPRISE RISK REPORT", align="C")
        pdf.set_font("Helvetica", "", 13)
        pdf.set_xy(10, 30)
        pdf.cell(190, 8, org_name, align="C")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_xy(10, 42)
        pdf.cell(190, 8, f"Reporting Date: {report_date.strftime('%d %B %Y')}  |  Prepared by: {prepared_by}", align="C")

        pdf.set_text_color(30, 30, 30)
        pdf.set_xy(10, 70)

        # Executive Summary
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(190, 8, "1. Executive Summary", ln=True)
        pdf.set_draw_color(59, 130, 246)
        pdf.set_line_width(0.8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        pdf.set_font("Helvetica", "", 11)
        critical_n = len(df[df["level"]=="Critical"])
        high_n     = len(df[df["level"]=="High"])
        open_n     = len(df[df["mitigation"].isin(["Not Started","In Progress"])])
        summary = (
            f"This report presents the current state of the enterprise risk register as at "
            f"{report_date.strftime('%d %B %Y')}. A total of {len(df)} risks have been identified "
            f"and assessed across {df['category'].nunique()} risk categories. "
            f"Of these, {critical_n} are rated Critical and {high_n} are rated High, "
            f"requiring immediate management attention. {open_n} risks have open mitigation actions."
        )
        pdf.multi_cell(190, 7, summary)
        pdf.ln(5)

        # KPI table
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(190, 8, "2. Risk Summary Metrics", ln=True)
        pdf.set_draw_color(59, 130, 246)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        headers  = ["Metric", "Count"]
        rows_kpi = [
            ("Total Risks Identified", str(len(df))),
            ("Critical Risks (Score >= 16)", str(critical_n)),
            ("High Risks (Score 10-15)", str(high_n)),
            ("Medium Risks (Score 5-9)", str(len(df[df["level"]=="Medium"]))),
            ("Low Risks (Score < 5)", str(len(df[df["level"]=="Low"]))),
            ("Mitigations Implemented", str(len(df[df["mitigation"]=="Implemented"]))),
            ("Open / In-Progress Actions", str(open_n)),
        ]
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(15, 52, 96)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(140, 8, "Metric", border=1, fill=True)
        pdf.cell(50, 8, "Count", border=1, fill=True, ln=True)
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 10)
        for i, (k, v) in enumerate(rows_kpi):
            fill = i % 2 == 0
            pdf.set_fill_color(235, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.cell(140, 7, k, border=1, fill=fill)
            pdf.cell(50, 7, v, border=1, fill=fill, ln=True)
        pdf.ln(6)

        # Top 10 priority risks
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(190, 8, "3. Top Priority Risks", ln=True)
        pdf.set_draw_color(59, 130, 246)
        pdf.set_line_width(0.8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        cols  = ["ID", "Risk Title", "Category", "L", "I", "Score", "Level", "Owner", "Status"]
        widths= [12,  52,            30,          8,   8,   12,      18,      30,      20]
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(15, 52, 96)
        pdf.set_text_color(255, 255, 255)
        for col, w in zip(cols, widths):
            pdf.cell(w, 8, col, border=1, fill=True)
        pdf.ln()

        pdf.set_font("Helvetica", "", 8)
        top10 = df.sort_values("score", ascending=False).head(10)
        level_colors = {"Critical":(127,29,29), "High":(124,45,18),
                        "Medium":(113,63,18), "Low":(20,83,45)}
        for i, row in top10.iterrows():
            fill = (i % 2 == 0)
            pdf.set_fill_color(235,245,255) if fill else pdf.set_fill_color(255,255,255)
            pdf.set_text_color(30,30,30)
            vals = [row["id"], row["title"][:30], row["category"][:18],
                    str(row["likelihood"]), str(row["impact"]), str(row["score"]),
                    row["level"], row["owner"][:18], row["mitigation"][:12]]
            for val, w in zip(vals, widths):
                pdf.cell(w, 7, str(val), border=1, fill=fill)
            pdf.ln()
        pdf.ln(6)

        # Risk descriptions
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(30,30,30)
        pdf.cell(190, 8, "4. Detailed Risk Profiles", ln=True)
        pdf.set_draw_color(59, 130, 246)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        for _, row in df.sort_values("score", ascending=False).iterrows():
            if pdf.get_y() > 240: pdf.add_page()
            level, _ = get_risk_level(row["score"])
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(30, 41, 59)
            pdf.set_text_color(255,255,255)
            pdf.cell(190, 7, f"  {row['id']} | {row['title']} | {level} (Score: {row['score']})", fill=True, ln=True)
            pdf.set_text_color(30,30,30)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(190, 6, f"Category: {row['category']}  |  Owner: {row['owner']}  |  Mitigation: {row['mitigation']}", ln=True)
            if row.get("description"):
                pdf.multi_cell(190, 5.5, f"Description: {row['description']}")
            if row.get("controls"):
                pdf.multi_cell(190, 5.5, f"Controls: {row['controls']}")
            pdf.ln(3)

        # Footer
        pdf.set_y(-25)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120,120,120)
        pdf.cell(190, 5,
            f"CONFIDENTIAL - {org_name} - Enterprise Risk Report - {report_date.strftime('%d %B %Y')}",
            align="C")

        pdf_bytes = bytes(pdf.output())
        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name=f"ERM_Report_{report_date.strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.success("✅ PDF generated! Click above to download.")
