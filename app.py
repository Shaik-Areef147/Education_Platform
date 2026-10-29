"""EduPro - Learner Demographics & Course Enrollment Behavior Analytics (Streamlit)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src import analysis as A
from src import charts as C
from src import data as D
from src import ui

st.set_page_config(page_title="EduPro Learner Analytics", page_icon="🎓", layout="wide",
                   initial_sidebar_state="expanded")
ui.inject_css()

PAGES = ["Overview", "Learner Demographics", "Enrollment Distribution", "Demographics x Preference",
         "Behavioral Insights", "Insights & Recommendations", "Data Explorer"]


# ----------------------------------------------------------------------------- data
def get_data():
    with st.sidebar.expander("Data source", expanded=False):
        up = st.file_uploader("Optional: upload a replacement EduPro .xlsx", type=["xlsx"])
        st.caption("Needs sheets Users, Courses, Transactions. Leave empty to use the bundled dataset.")
    try:
        if up is not None:
            return D.load_uploaded(up.getvalue()), "uploaded workbook"
        return D.load_default(), "bundled EduPro_Online_Platform.xlsx"
    except D.DataError as e:
        st.error(f"Data problem: {e}")
    except Exception as e:  # noqa: BLE001
        st.error(f"Could not read the data file: {e}")
    st.stop()


st.sidebar.markdown("## 🎓 EduPro Analytics")
page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")
(enr_all, users_all, quality), source = get_data()

# ----------------------------------------------------------------------------- filters
st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")
age_opts = A.present_age_groups(enr_all)
gen_opts = sorted(enr_all["Gender"].unique())
cat_opts = sorted(enr_all["CourseCategory"].unique())
lvl_opts = [l for l in D.LEVEL_ORDER if l in set(enr_all["CourseLevel"])]
typ_opts = sorted(enr_all["CourseType"].unique())

f_age = st.sidebar.multiselect("Age group", age_opts, default=age_opts)
f_gen = st.sidebar.multiselect("Gender", gen_opts, default=gen_opts)
f_cat = st.sidebar.multiselect("Course category", cat_opts, default=cat_opts)
f_lvl = st.sidebar.multiselect("Course level", lvl_opts, default=lvl_opts)
f_typ = st.sidebar.multiselect("Course type", typ_opts, default=typ_opts)
dmin, dmax = enr_all["TransactionDate"].min().date(), enr_all["TransactionDate"].max().date()
f_date = st.sidebar.date_input("Enrollment date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)
if isinstance(f_date, (tuple, list)):
    d0, d1 = (f_date[0], f_date[1]) if len(f_date) == 2 else (f_date[0], f_date[0])
else:
    d0 = d1 = f_date

enr = enr_all[
    enr_all["AgeGroup"].isin(f_age) & enr_all["Gender"].isin(f_gen) & enr_all["CourseCategory"].isin(f_cat)
    & enr_all["CourseLevel"].isin(f_lvl) & enr_all["CourseType"].isin(f_typ)
    & (enr_all["TransactionDate"].dt.date >= d0) & (enr_all["TransactionDate"].dt.date <= d1)
]
st.sidebar.caption(f"{len(enr):,} of {len(enr_all):,} enrollments match filters")
st.sidebar.caption(f"Source: {source}")

ui.hero("EduPro Learner Intelligence",
        "Who our learners are and how they choose courses - descriptive analytics for data-driven course planning.")

if enr.empty:
    st.warning("No enrollments match the current filters. Widen the filters in the sidebar.")
    st.stop()

users_f = enr.drop_duplicates("UserID")[["UserID", "Age", "Gender", "AgeGroup"]]
K = A.kpis(enr, users_all)
PL = A.per_learner(enr)


def chart(fig, key):
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False})


def show_table(df: pd.DataFrame, fmt: dict | None = None):
    with st.expander("View data table"):
        st.dataframe(df.style.format(fmt or {}), width="stretch", hide_index=True)


# ----------------------------------------------------------------------------- pages
if page == "Overview":
    c = st.columns(5)
    ui.kpi(c[0], "Total enrollments", f"{K['total_enrollments']:,}", "Platform engagement")
    ui.kpi(c[1], "Active learners", f"{K['active_learners']:,}", f"of {len(users_all):,} registered", C.ORANGE)
    ui.kpi(c[2], "Avg courses/learner", f"{K['avg_per_learner']:.2f}", "per active learner", C.AQUA)
    ui.kpi(c[3], "Gender ratio (F:M)", f"{K['gender_ratio']:.2f}" if K["gender_ratio"] == K["gender_ratio"] else "n/a",
           f"{K['female_pct']:.1f}% F / {K['male_pct']:.1f}% M", C.VIOLET)
    ui.kpi(c[4], "Free-course share", f"{K['free_pct']:.1f}%", "of enrollments", C.YELLOW)
    st.write("")
    c = st.columns(3)
    ui.kpi(c[0], "Most active age group", K["top_age"], "by enrollments")
    ui.kpi(c[1], "Most popular category", K["top_category"], "by enrollments", C.ORANGE)
    ui.kpi(c[2], "Most popular level", K["top_level"], "by enrollments", C.AQUA)
    st.write("")
    a, b = st.columns(2)
    ea = A.enrollments_by_age(enr)
    with a:
        chart(C.bar(ea, "AgeGroup", "Enrollments", "Enrollments by age group"), "ov_age")
    with b:
        g = A.gender_summary(enr)
        chart(C.donut(g["Gender"], g["Learners"], "Gender participation (learners)", C.GENDER_COLORS), "ov_gen")
    a, b = st.columns(2)
    with a:
        cp = A.category_popularity(enr)
        chart(C.bar(cp, "CourseCategory", "Enrollments", "Category popularity", C.ORANGE, horizontal=True,
                    height=460), "ov_cat")
    with b:
        lv = A.level_distribution(enr)
        chart(C.donut(lv["CourseLevel"], lv["Enrollments"], "Level preference distribution", C.LEVEL_COLORS), "ov_lvl")
        chart(C.line(A.monthly(enr), "Month", "Enrollments", "Monthly enrollment trend"), "ov_month")

elif page == "Learner Demographics":
    st.subheader("Learner demographic overview")
    c = st.columns(4)
    ui.kpi(c[0], "Learners (filtered)", f"{len(users_f):,}")
    ui.kpi(c[1], "Median age", f"{users_f['Age'].median():.0f}", "years", C.ORANGE)
    ui.kpi(c[2], "Mean age", f"{users_f['Age'].mean():.1f}", "years", C.AQUA)
    ui.kpi(c[3], "Age range", f"{users_f['Age'].min()}-{users_f['Age'].max()}", "years", C.VIOLET)
    st.write("")
    a, b = st.columns(2)
    with a:
        ad = A.age_distribution(users_f)
        chart(C.bar(ad, "AgeGroup", "Learners", "Learners by age band"), "dm_band")
        show_table(ad, {"Share %": "{:.1f}"})
    with b:
        hist = users_f.groupby("Age").size().reset_index(name="Learners")
        chart(C.bar(hist, "Age", "Learners", "Learners by exact age", C.AQUA), "dm_age")
    a, b = st.columns(2)
    with a:
        ct = A.crosstab(users_f.assign(_n=1), "AgeGroup", "Gender")
        chart(C.grouped_bar(ct, "Age band x gender (learners)", C.GENDER_COLORS), "dm_ag")
    with b:
        g = A.gender_summary(enr)
        chart(C.bar(g, "Gender", "Enrollments per learner", "Participation level by gender", C.VIOLET, fmt=".2f"), "dm_gp")
        show_table(g, {"Learner share %": "{:.1f}", "Enrollments per learner": "{:.2f}"})
    st.markdown("#### Participation level per age group")
    ea = A.enrollments_by_age(enr)
    a, b = st.columns(2)
    with a:
        chart(C.bar(ea, "AgeGroup", "Enrollments", "Enrollments by age group", C.ORANGE), "dm_ea")
    with b:
        chart(C.bar(ea, "AgeGroup", "Enrollments per learner", "Enrollments per learner by age group", C.AQUA,
                    fmt=".2f"), "dm_ep")
    show_table(ea, {"Share %": "{:.1f}", "Enrollments per learner": "{:.2f}"})

elif page == "Enrollment Distribution":
    st.subheader("Enrollment distribution")
    a, b = st.columns(2)
    cp = A.category_popularity(enr)
    with a:
        chart(C.bar(cp, "CourseCategory", "Enrollments", "Enrollments by course category", C.BLUE,
                    horizontal=True, height=480), "ed_cat")
    with b:
        chart(C.bar(cp, "CourseCategory", "Popularity Index", "Category Popularity Index (100 = average)",
                    C.ORANGE, horizontal=True, fmt=".0f", height=480), "ed_idx")
    show_table(cp, {"Share %": "{:.1f}", "Popularity Index": "{:.0f}"})
    a, b = st.columns(2)
    with a:
        t = A.count_by(enr, "CourseType")
        chart(C.donut(t["CourseType"], t["Enrollments"], "Enrollments by course type", C.TYPE_COLORS), "ed_type")
    with b:
        lv = A.level_distribution(enr)
        chart(C.donut(lv["CourseLevel"], lv["Enrollments"], "Enrollments by course level", C.LEVEL_COLORS), "ed_lvl")
    top, bot = cp.iloc[0], cp.iloc[-1]
    ui.insight(f"<b>Most popular:</b> {top['CourseCategory']} ({top['Enrollments']:,} enrollments, "
               f"{top['Share %']:.1f}%). <b>Least popular:</b> {bot['CourseCategory']} "
               f"({bot['Enrollments']:,}, {bot['Share %']:.1f}%).")
    st.markdown("#### Top courses")
    tc = A.count_by(enr, "CourseName").head(10)
    chart(C.bar(tc, "CourseName", "Enrollments", "Top 10 courses by enrollments", C.VIOLET, horizontal=True,
                height=440), "ed_top")

elif page == "Demographics x Preference":
    st.subheader("Demographics x course preference")
    mode = st.radio("Heatmap values", ["% within age group (row)", "Enrollment counts"], horizontal=True)
    pct = mode.startswith("%")
    ct = A.crosstab(enr, "AgeGroup", "CourseCategory", "row" if pct else None)
    chart(C.heatmap(ct, "Age group x course category", pct), "dp_hm")
    show_table(ct.round(1).reset_index(), None)
    a, b = st.columns(2)
    with a:
        ct2 = A.crosstab(enr, "Gender", "CourseLevel", "row")
        chart(C.grouped_bar(ct2, "Gender vs course level (% within gender)", C.LEVEL_COLORS, pct=True), "dp_gl")
    with b:
        ct3 = A.crosstab(enr, "AgeGroup", "CourseLevel", "row")
        chart(C.grouped_bar(ct3, "Age group vs course level (% within age group)", C.LEVEL_COLORS, pct=True,
                            stacked=True), "dp_al")
    a, b = st.columns(2)
    with a:
        ct4 = A.crosstab(enr, "Gender", "CourseCategory", "row")
        chart(C.heatmap(ct4, "Gender x category (% within gender)", True, height=300), "dp_gc")
    with b:
        ct5 = A.crosstab(enr, "AgeGroup", "CourseType", "row")
        chart(C.grouped_bar(ct5, "Age group vs free/paid (% within age group)", C.TYPE_COLORS, pct=True), "dp_at")
    st.markdown("#### Segments with the strongest category preference")
    tp = A.top_pairs(enr)
    if tp.empty:
        st.info("Not enough data in the selected segments (needs at least 30 enrollments per segment).")
    else:
        st.dataframe(tp.style.format({"Segment share %": "{:.1f}", "Platform share %": "{:.1f}", "Lift": "{:.2f}x"}),
                     width="stretch", hide_index=True)
        st.caption("Lift = segment's share of a category divided by the platform-wide share. 1.0x = no difference.")
    v1 = A.cramers_v(A.crosstab(enr, "AgeGroup", "CourseCategory"))
    v2 = A.cramers_v(A.crosstab(enr, "Gender", "CourseCategory"))
    v3 = A.cramers_v(A.crosstab(enr, "AgeGroup", "CourseLevel"))
    ui.insight(f"<b>Association strength (Cramer's V, 0 = none, 1 = perfect):</b> age group vs category "
               f"{v1:.3f} - gender vs category {v2:.3f} - age group vs level {v3:.3f}. "
               "Values near zero mean preferences are broadly similar across segments.")

elif page == "Behavioral Insights":
    st.subheader("Behavioral insights")
    c = st.columns(4)
    ui.kpi(c[0], "Avg courses / learner", f"{PL['Courses'].mean():.2f}")
    ui.kpi(c[1], "Median courses", f"{PL['Courses'].median():.0f}", "", C.ORANGE)
    ui.kpi(c[2], "Top 10% learners' share", f"{A.share_of_top(PL, 10):.1f}%", "of all enrollments", C.AQUA)
    ui.kpi(c[3], "One-course learners", f"{(PL['Courses'] == 1).mean() * 100:.1f}%", "", C.VIOLET)
    st.write("")
    a, b = st.columns(2)
    with a:
        h = A.courses_per_learner_hist(PL)
        hf = C.bar(h.assign(Courses=h["Courses"].astype(str)), "Courses", "Learners", "Distribution of courses taken per learner")
        hf.update_xaxes(type="category", title="Courses taken")
        chart(hf, "bh_hist")
    with b:
        chart(C.lorenz(A.concentration(PL), "Enrollment concentration among active users"), "bh_lor")
    ui.insight(f"<b>Concentration:</b> the most active 10% of learners account for "
               f"{A.share_of_top(PL, 10):.1f}% of enrollments; the top 20% account for {A.share_of_top(PL, 20):.1f}%.")
    st.markdown("#### Beginner vs advanced learner behavior")
    PL2 = PL.assign(Stage=A.learner_stage(PL))
    stage_order = ["Beginner only", "Reached Intermediate", "Reached Advanced"]
    sg = PL2.groupby("Stage").agg(Learners=("UserID", "count"), AvgCourses=("Courses", "mean"),
                                  AvgAge=("Age", "mean"), FreePct=("Free", "sum"))
    sg["FreePct"] = sg["FreePct"] / PL2.groupby("Stage")["Courses"].sum() * 100
    sg = sg.reindex([s for s in stage_order if s in sg.index]).reset_index()
    sg.columns = ["Learner stage", "Learners", "Avg courses", "Avg age", "Free-course %"]
    a, b = st.columns(2)
    with a:
        chart(C.bar(sg, "Learner stage", "Learners", "Learners by highest level reached", C.VIOLET), "bh_stage")
    with b:
        chart(C.bar(sg, "Learner stage", "Avg courses", "Average courses taken by stage", C.AQUA, fmt=".2f"), "bh_avg")
    st.dataframe(sg.style.format({"Avg courses": "{:.2f}", "Avg age": "{:.1f}", "Free-course %": "{:.1f}"}),
                 width="stretch", hide_index=True)
    st.markdown("#### Level mix by learner activity")
    PL2["Activity"] = pd.cut(PL2["Courses"], [0, 1, 3, 6, 1000], labels=["1 course", "2-3", "4-6", "7+"]).astype(str)
    mix = PL2.groupby("Activity")[["Beginner", "Intermediate", "Advanced"]].sum()
    mix = mix.reindex([a for a in ["1 course", "2-3", "4-6", "7+"] if a in mix.index])
    mix = mix.div(mix.sum(axis=1), axis=0) * 100
    chart(C.grouped_bar(mix, "Share of enrollments by level, per activity band (%)", C.LEVEL_COLORS, stacked=True,
                        pct=True), "bh_mix")

elif page == "Insights & Recommendations":
    st.subheader("Key findings (update live with your filters)")
    ea = A.enrollments_by_age(enr)
    g = A.gender_summary(enr)
    cp = A.category_popularity(enr)
    lv = A.level_distribution(enr)
    tp = A.top_pairs(enr, 3)
    ui.insight(f"<b>Age:</b> {K['top_age']} is the most active group "
               f"({ea.loc[ea['AgeGroup'] == K['top_age'], 'Share %'].iloc[0]:.1f}% of enrollments). "
               f"Highest intensity: {ea.sort_values('Enrollments per learner').iloc[-1]['AgeGroup']} "
               f"({ea['Enrollments per learner'].max():.2f} courses per learner).")
    ui.insight(f"<b>Gender:</b> {K['female_pct']:.1f}% female / {K['male_pct']:.1f}% male learners; "
               + "; ".join(f"{a} learners take {b:.2f} courses each" for a, b in
                           zip(g["Gender"], g["Enrollments per learner"])) + ".")
    ui.insight(f"<b>Category demand:</b> {cp.iloc[0]['CourseCategory']} leads with "
               f"{cp.iloc[0]['Share %']:.1f}% of enrollments; {cp.iloc[-1]['CourseCategory']} trails with "
               f"{cp.iloc[-1]['Share %']:.1f}%.")
    ui.insight("<b>Level:</b> " + ", ".join(f"{a} {b:.1f}%" for a, b in zip(lv["CourseLevel"], lv["Share %"])) + ".")
    ui.insight(f"<b>Free vs paid:</b> {K['free_pct']:.1f}% of enrollments are in free courses.")
    ui.insight(f"<b>Concentration:</b> top 10% of learners generate {A.share_of_top(PL, 10):.1f}% of enrollments.")
    if not tp.empty:
        r = tp.iloc[0]
        ui.insight(f"<b>Strongest segment preference:</b> {r['Segment']} over-index on {r['Category']} "
                   f"({r['Lift']:.2f}x the platform share).")
    st.subheader("Recommendations")
    st.markdown(f"""
1. **Course creation** - expand the catalogue where demand is highest ({cp.iloc[0]['CourseCategory']}, {cp.iloc[1]['CourseCategory'] if len(cp) > 1 else ''}) and review low-demand areas ({cp.iloc[-1]['CourseCategory']}) for relevance or positioning.
2. **Marketing** - target the {K['top_age']} segment first, and test campaigns for under-represented age groups.
3. **Inclusivity** - monitor the gender participation ratio ({K['female_pct']:.0f}% F / {K['male_pct']:.0f}% M) and keep gender-neutral messaging.
4. **Learning paths** - create beginner-to-advanced bundles to move learners up levels and raise courses per learner.
5. **Retention** - the most active learners drive a disproportionate share of enrollments; reward them and nudge one-course learners with next-step recommendations.
""")

else:  # Data Explorer
    st.subheader("Data explorer")
    t1, t2, t3 = st.tabs(["Filtered enrollments", "Learner summary", "Data quality"])
    cols = ["TransactionID", "TransactionDate", "UserID", "UserName", "Age", "AgeGroup", "Gender",
            "CourseID", "CourseName", "CourseCategory", "CourseType", "CourseLevel"]
    with t1:
        st.dataframe(enr[cols], width="stretch", hide_index=True, height=420)
        st.download_button("Download filtered enrollments (CSV)", enr[cols].to_csv(index=False).encode("utf-8"),
                           "edupro_filtered_enrollments.csv", "text/csv")
    with t2:
        st.dataframe(PL, width="stretch", hide_index=True, height=420)
        st.download_button("Download learner summary (CSV)", PL.to_csv(index=False).encode("utf-8"),
                           "edupro_learner_summary.csv", "text/csv")
    with t3:
        q = quality
        ok = (q["duplicate_users"] == q["duplicate_courses"] == q["duplicate_transactions"]
              == q["orphan_user_ids"] == q["orphan_course_ids"] == q["dropped_rows"] == 0)
        (st.success if ok else st.warning)(
            "Referential integrity verified: every transaction maps to a valid user and course." if ok
            else "Some records were dropped during integration - see counts below.")
        st.table(pd.DataFrame({"Check": ["Users", "Courses", "Transactions", "Duplicate users", "Duplicate courses",
                                         "Duplicate transactions", "Orphan UserIDs in transactions",
                                         "Orphan CourseIDs in transactions", "Missing values (key fields)",
                                         "Rows dropped in join", "Date range"],
                               "Value": [q["users"], q["courses"], q["transactions"], q["duplicate_users"],
                                         q["duplicate_courses"], q["duplicate_transactions"], q["orphan_user_ids"],
                                         q["orphan_course_ids"], q["missing_values"], q["dropped_rows"],
                                         f"{q['date_min']:%Y-%m-%d} to {q['date_max']:%Y-%m-%d}"]}).astype(str))

st.markdown("---")
st.caption("EduPro Learner Demographics & Course Enrollment Behavior Analysis - descriptive analytics - Unified Mentor project.")
