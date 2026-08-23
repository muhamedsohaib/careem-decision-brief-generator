from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from analysis_engine import DataInputError, analyze_dataframe, build_reasoning_prompt, read_csv_safely


APP_TITLE = "Decision Brief Generator"
SAMPLE_PATH = Path(__file__).with_name("sample_amazon_operations.csv")


def format_value(value, kind: str | None, currency: str | None = None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    if kind == "currency":
        prefix = f"{currency} " if currency else ""
        return f"{prefix}{value:,.{decimals}f}"
    if kind == "ratio":
        return f"{value:,.{decimals}f}"
    if kind == "quantity":
        return f"{value:,.0f}"
    return f"{value:,.{decimals}f}"


def brief_text(result: dict, source_label: str) -> str:
    lines = [
        "DECISION BRIEF",
        f"Source: {source_label}",
        f"Analysis mode: {result['mode']}",
        f"Primary KPI: {result.get('primary_kpi') or 'Unavailable'}",
        f"Confidence: {result['confidence']}",
        "",
        "OBSERVED FACTS",
    ]
    lines.extend(f"- {item}" for item in result["facts"])
    lines.extend(["", "HYPOTHESES"])
    lines.extend(f"- {item}" for item in result["hypotheses"] or ["None supported by the supplied data."])
    lines.extend(["", "RECOMMENDED ACTIONS"])
    lines.extend(f"- {item}" for item in result["actions"] or ["Blocked pending data-quality resolution."])
    lines.extend(["", "RISKS & UNKNOWNS"])
    lines.extend(f"- {item}" for item in result["unknowns"] or ["No additional unknowns recorded."])
    return "\n".join(lines)


def load_sample() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_PATH)


st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
st.markdown(
    """
    <style>
      [data-testid="stAppViewContainer"] { background: #f8fafc; }
      [data-testid="stSidebar"] { background: #ffffff; }
      h1, h2, h3, h4 { color: #19163d; }
      .eyebrow { font-size: .78rem; letter-spacing: .12em; font-weight: 700; color: #6366f1; }
      .mode-pill {
        display:inline-block; padding:.28rem .62rem; border-radius:999px;
        background:#eef2ff; color:#4338ca; font-size:.8rem; font-weight:700;
      }
      .guardrail {
        padding:.8rem 1rem; border:1px solid #cbd5e1; border-radius:12px;
        background:#fff; margin:.4rem 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">EVIDENCE-FIRST OPERATIONS INTELLIGENCE</div>', unsafe_allow_html=True)
st.title(APP_TITLE)
st.caption(
    "Turn raw operational data into facts, hypotheses and actions without letting the narrative invent the evidence."
)

st.sidebar.markdown("### Data input")
source_choice = st.sidebar.radio(
    "Source",
    ["Sanitized Amazon operations sample", "Upload CSV"],
    help=(
        "The built-in sample preserves a representative operating pattern, but identifiers and numerical values "
        "have been transformed and are not original commercial figures."
    ),
)

df = None
source_label = ""
input_error = None

if source_choice == "Sanitized Amazon operations sample":
    df = load_sample()
    source_label = "Sanitized representative Amazon operations sample"
    inject_conflict = st.sidebar.toggle(
        "Demonstrate safety gate",
        value=False,
        help="Adds a conflicting duplicate record so the engine must refuse to recommend an operational action.",
    )
    if inject_conflict:
        conflict = df.iloc[[1]].copy()
        conflict["current_stock"] = 99
        df = pd.concat([df, conflict], ignore_index=True)
        source_label += " + injected conflicting record"
else:
    uploaded = st.sidebar.file_uploader(
        "CSV file",
        type=["csv"],
        help=(
            "Maximum 5 MB. Uploaded data is processed in the active Streamlit server session. "
            "Do not upload confidential or personally identifiable information to a public deployment."
        ),
    )
    if uploaded is not None:
        try:
            df = read_csv_safely(uploaded)
            source_label = f"Uploaded CSV: {uploaded.name}"
        except DataInputError as exc:
            input_error = str(exc)

if input_error:
    st.error(input_error)

if df is None:
    st.info("Upload a CSV to begin, or select the sanitized sample.")
    st.stop()

initial = analyze_dataframe(df)
numeric_columns = initial["numeric_columns"]

st.sidebar.markdown("### Analysis controls")
if numeric_columns:
    default_index = numeric_columns.index(initial["primary_kpi"]) if initial["primary_kpi"] in numeric_columns else 0
    selected_kpi = st.sidebar.selectbox("Primary KPI", numeric_columns, index=default_index)
else:
    selected_kpi = None

result = analyze_dataframe(df, primary_kpi=selected_kpi)
metrics = result["metrics"]

st.markdown(
    f'<span class="mode-pill">Detected mode: {result["mode"].replace("_", " ")}</span>',
    unsafe_allow_html=True,
)
st.caption(f"Source: {source_label} · {len(df)} rows · {df.shape[1]} columns")

if result["errors"]:
    for message in result["errors"]:
        st.error(message)
if result["warnings"]:
    for message in result["warnings"]:
        st.warning(message)

if result["blocked"]:
    st.markdown("### Decision blocked")
    st.write(
        "The engine will show the data and quality findings, but it will not generate operational recommendations until blocking issues are resolved."
    )

preview_col, metric_col = st.columns([1.05, 1.35])

with preview_col:
    st.markdown("#### Data preview")
    st.dataframe(df.head(12), use_container_width=True, hide_index=True)
    quality = result["data_quality"]
    st.markdown("#### Data-quality gate")
    st.markdown(
        f"""
        <div class="guardrail">
          Exact duplicate rows: <b>{quality["duplicate_row_count"]}</b><br>
          Duplicate entities: <b>{quality["duplicate_entity_count"]}</b><br>
          Conflicting entities: <b>{quality["conflicting_entity_count"]}</b><br>
          Missing cells: <b>{quality["missing_cell_count"]}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

with metric_col:
    st.markdown("#### Operating snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", metrics["row_count"])
    c2.metric(
        f"Total {result.get('primary_kpi') or 'KPI'}",
        format_value(
            metrics.get("kpi_sum"),
            result.get("kpi_kind"),
            result.get("currency"),
        ),
    )
    if result["mode"] == "inventory_operations":
        c3.metric("Stockouts", metrics.get("stockout_count", "—"))
        c4.metric("Below target", metrics.get("below_target_count", "—"))
    else:
        c3.metric(
            "Average",
            format_value(metrics.get("kpi_average"), result.get("kpi_kind"), result.get("currency")),
        )
        share = metrics.get("top_group_share_pct")
        c4.metric("Top-group share", "—" if share is None else f"{share:.1f}%")

    if result["trend"] is None:
        st.info("No trustworthy time comparison was generated because the dataset does not contain enough usable dated observations.")
    else:
        change = result["trend"]["change_pct"]
        st.metric(
            "Chronological change",
            "Unavailable" if change is None else f"{change:+.1f}%",
            "Calculated only after sorting the detected date field",
        )

    group_col = metrics.get("group_column")
    kpi = result.get("primary_kpi")
    if group_col and kpi and not result["blocked"]:
        chart_data = (
            df.assign(_value=pd.to_numeric(df[kpi], errors="coerce"))
            .dropna(subset=["_value"])
            .groupby(group_col)["_value"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        if len(chart_data):
            st.markdown(f"#### {kpi} by {group_col}")
            st.bar_chart(chart_data)

st.divider()
st.markdown("### Decision brief")

fact_col, action_col = st.columns(2)
with fact_col:
    st.markdown("#### Observed facts")
    if result["facts"]:
        for item in result["facts"]:
            st.write(f"• {item}")
    else:
        st.write("No facts generated while the analysis is blocked.")

    st.markdown("#### Hypotheses")
    if result["hypotheses"]:
        for item in result["hypotheses"]:
            st.write(f"• {item}")
    else:
        st.write("No hypothesis is supported by the supplied evidence.")

with action_col:
    st.markdown("#### Recommended actions")
    if result["actions"]:
        for item in result["actions"]:
            st.write(f"• {item}")
    else:
        st.write("No action generated while the data-quality gate is blocking the decision.")

    st.markdown("#### Risks & unknowns")
    if result["unknowns"]:
        for item in result["unknowns"]:
            st.write(f"• {item}")
    st.caption(f"Confidence: {result['confidence'].upper()}")

download_text = brief_text(result, source_label)
st.download_button(
    "Download decision brief",
    data=download_text,
    file_name="decision_brief.txt",
    mime="text/plain",
    use_container_width=True,
)

with st.expander("Optional AI reasoning layer"):
    st.write(
        "The calculations and evidence above are deterministic. The prompt below is an optional reasoning layer for an LLM. "
        "Dataset-derived text is explicitly treated as untrusted data, not as model instructions."
    )
    st.code(build_reasoning_prompt(result), language="text")

with st.expander("Why this architecture"):
    st.markdown(
        """
        **1. Measure first.** CSV parsing, data-quality checks and KPI calculations are deterministic.

        **2. Separate fact from inference.** Observations, hypotheses and recommended actions are rendered independently.

        **3. Fail closed.** Conflicting entity records block recommendations instead of being silently averaged.

        **4. Treat uploaded text as data.** Dataset-derived labels are bounded and the optional LLM prompt places them behind an explicit instruction/data boundary.

        **5. Use AI as leverage.** An LLM can compress the evidence into an executive narrative, but it does not calculate the facts and it does not own the final decision.
        """
    )

st.caption(
    "The built-in sample is representative and transformed: no ASINs, SKUs, product names, customer data, credentials, or original commercial figures are included."
)
