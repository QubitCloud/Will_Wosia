from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import json, os, uuid, io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

app = Flask(__name__)
app.secret_key = "wosia-tz-2024"

SUBMISSIONS_DIR = "submissions"
os.makedirs(SUBMISSIONS_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()
        ref_id = str(uuid.uuid4())[:8].upper()
        timestamp = datetime.now().isoformat()
        record = {"ref_id": ref_id, "submitted_at": timestamp, "data": data}
        filepath = os.path.join(SUBMISSIONS_DIR, f"will_{ref_id}.json")
        with open(filepath, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        return jsonify({"success": True, "ref_id": ref_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/review/<ref_id>")
def review(ref_id):
    filepath = os.path.join(SUBMISSIONS_DIR, f"will_{ref_id}.json")
    if not os.path.exists(filepath):
        return "Record not found", 404
    with open(filepath) as f:
        record = json.load(f)
    return render_template("review.html", record=record)


@app.route("/pdf/<ref_id>")
def generate_pdf(ref_id):
    filepath = os.path.join(SUBMISSIONS_DIR, f"will_{ref_id}.json")
    if not os.path.exists(filepath):
        return "Record not found", 404
    with open(filepath) as f:
        record = json.load(f)

    buffer = io.BytesIO()
    build_will_pdf(record, buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Wosia_{ref_id}.pdf"
    )


# ─── PDF BUILDER ────────────────────────────────────────────────────────────

RUST   = colors.Color(0.545, 0.145, 0)
GOLD   = colors.Color(0.722, 0.525, 0.043)
INK    = colors.Color(0.102, 0.063, 0.031)
MID    = colors.Color(0.420, 0.361, 0.243)
LIGHT  = colors.Color(0.961, 0.941, 0.910)
BORDER = colors.Color(0.784, 0.722, 0.604)

def build_will_pdf(record, buffer):
    d   = record["data"]
    t   = d["testator"]
    ref = record["ref_id"]
    sub = record["submitted_at"][:10]

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Wosia wa {t.get('fname','')} {t.get('lname','')}",
        author="Wosia Wangu System — Tanzania"
    )

    W = A4[0] - 5*cm  # usable width

    styles = getSampleStyleSheet()
    def S(name, **kw):
        base = styles["Normal"]
        return ParagraphStyle(name, parent=base, **kw)

    sTitle  = S("sTitle",  fontName="Times-Bold",   fontSize=18, textColor=RUST,  spaceAfter=4,  alignment=TA_CENTER)
    sSub    = S("sSub",    fontName="Times-Italic",  fontSize=10, textColor=MID,   spaceAfter=2,  alignment=TA_CENTER)
    sRef    = S("sRef",    fontName="Helvetica",     fontSize=8,  textColor=MID,   spaceAfter=12, alignment=TA_CENTER)
    sSecHd  = S("sSecHd",  fontName="Times-Bold",   fontSize=12, textColor=RUST,  spaceBefore=14, spaceAfter=4)
    sLabel  = S("sLabel",  fontName="Helvetica-Bold",fontSize=7.5,textColor=MID,   spaceAfter=1, leading=10)
    sVal    = S("sVal",    fontName="Helvetica",     fontSize=9.5,textColor=INK,   spaceAfter=6, leading=13)
    sBody   = S("sBody",   fontName="Helvetica",     fontSize=9,  textColor=INK,   spaceAfter=4, leading=13)
    sLegal  = S("sLegal",  fontName="Helvetica-Oblique", fontSize=7.5, textColor=MID, spaceAfter=3, leading=11)
    sSigLbl = S("sSigLbl", fontName="Helvetica",    fontSize=7.5,textColor=MID,   alignment=TA_CENTER)

    story = []

    # ── HEADER ──────────────────────────────────────────────
    story.append(Paragraph("HATI YA WOSIA WA MWISHO", sTitle))
    story.append(Paragraph("Last Will and Testament", sSub))
    story.append(Paragraph(f"Nambari ya Kumbukumbu / Reference No: <b>{ref}</b>  |  Tarehe / Date: {sub}", sRef))
    story.append(HRFlowable(width=W, thickness=1.5, color=RUST, spaceAfter=10))

    # ── OPENING DECLARATION ─────────────────────────────────
    fname = t.get('fname',''); mname = t.get('mname',''); lname = t.get('lname','')
    full  = f"{fname} {mname} {lname}".strip()
    nid   = t.get('nid','_______________')
    addr  = t.get('address','_______________')

    story.append(Paragraph(
        f"Mimi, <b>{full}</b>, mwenye Kitambulisho Namba <b>{nid}</b>, mwenye makazi "
        f"katika <b>{addr}</b>, nikiwa na akili timamu na uwezo wa kisheria, natoa Wosia "
        f"huu wa Mwisho na kufuta wosia wote wa awali.",
        sBody
    ))
    story.append(Paragraph(
        f"I, <b>{full}</b>, holding National ID No. <b>{nid}</b>, residing at "
        f"<b>{addr}</b>, being of sound mind and legal capacity, hereby make this Last "
        f"Will and Testament and revoke all prior wills.",
        sBody
    ))
    story.append(Spacer(1, 6))

    def section(title_sw, title_en):
        story.append(HRFlowable(width=W, thickness=0.5, color=BORDER, spaceBefore=6, spaceAfter=0))
        story.append(Paragraph(f"{title_sw} / {title_en}", sSecHd))

    def row(label, value):
        if value and value.strip():
            story.append(Paragraph(label.upper(), sLabel))
            story.append(Paragraph(str(value), sVal))

    # ── SECTION 1: TESTATOR ─────────────────────────────────
    section("TAARIFA ZA MWANDISHI", "TESTATOR INFORMATION")
    data_rows = [
        ("Jina Kamili / Full Name", full),
        ("Tarehe ya Kuzaliwa / Date of Birth", t.get('dob','')),
        ("Kitambulisho (NIDA) / National ID", nid),
        ("Jinsi / Gender", t.get('gender','')),
        ("Simu / Phone", t.get('phone','')),
        ("Barua Pepe / Email", t.get('email','')),
        ("Anwani / Address", addr),
        ("Hali ya Ndoa / Marital Status", t.get('marital','')),
        ("Dini / Religion", t.get('religion','')),
    ]
    tbl_data = [[Paragraph(l, sLabel), Paragraph(v or "—", sVal)] for l, v in data_rows]
    tbl = Table(tbl_data, colWidths=[5.5*cm, W-5.5*cm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, LIGHT]),
        ("GRID", (0,0), (-1,-1), 0.3, BORDER),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(tbl)

    # ── SECTION 2: ASSETS ───────────────────────────────────
    assets = d.get("assets", {})
    section("MALI NA RASILIMALI", "ESTATE & ASSETS")

    props = assets.get("properties", [])
    if props:
        story.append(Paragraph("A. Ardhi na Nyumba / Land & Property", S("sh2", fontName="Helvetica-Bold", fontSize=9, textColor=INK, spaceAfter=3)))
        for i, p in enumerate(props, 1):
            story.append(Paragraph(
                f"{i}. <b>{p.get('prop-type','').upper()}</b> — Hati: {p.get('prop-title','—')} | "
                f"Mahali: {p.get('prop-location','—')} | Thamani: TZS {p.get('prop-value','—')} | "
                f"Mrithi: {p.get('prop-heir','—')}",
                sBody
            ))

    banks = assets.get("banks", [])
    if banks:
        story.append(Paragraph("B. Akaunti za Benki / Bank Accounts", S("sh2b", fontName="Helvetica-Bold", fontSize=9, textColor=INK, spaceAfter=3, spaceBefore=6)))
        for i, b in enumerate(banks, 1):
            story.append(Paragraph(
                f"{i}. <b>{b.get('bank-name','—')}</b> — Akaunti: {b.get('bank-acc','—')} | "
                f"Tawi: {b.get('bank-branch','—')} | Mrithi: {b.get('bank-heir','—')}",
                sBody
            ))

    vehicles = assets.get("vehicles", [])
    if vehicles:
        story.append(Paragraph("C. Magari / Vehicles", S("sh2c", fontName="Helvetica-Bold", fontSize=9, textColor=INK, spaceAfter=3, spaceBefore=6)))
        for i, v in enumerate(vehicles, 1):
            story.append(Paragraph(
                f"{i}. <b>{v.get('veh-model','—')}</b> ({v.get('veh-year','—')}) — "
                f"Reg: {v.get('veh-reg','—')} | Mrithi: {v.get('veh-heir','—')}",
                sBody
            ))

    other = assets.get("other", "")
    if other:
        story.append(Paragraph("D. Mali Nyingine / Other Assets", S("sh2d", fontName="Helvetica-Bold", fontSize=9, textColor=INK, spaceAfter=3, spaceBefore=6)))
        story.append(Paragraph(other, sBody))

    # ── SECTION 3: BENEFICIARIES ────────────────────────────
    bens = d.get("beneficiaries", [])
    section("WATEULE WA MIRATHI", "BENEFICIARIES")
    if bens:
        ben_data = [
            [Paragraph(h, S(f"bh{i}", fontName="Helvetica-Bold", fontSize=8, textColor=INK))
             for i, h in enumerate(["#", "Jina / Name", "Uhusiano / Rel.", "Mgawanyo / Share", "Kitambulisho / ID", "Simu / Phone"])]
        ]
        for i, b in enumerate(bens, 1):
            ben_data.append([
                Paragraph(str(i), sBody),
                Paragraph(b.get("ben-name","—"), sBody),
                Paragraph(b.get("ben-rel","—"), sBody),
                Paragraph(f"{b.get('ben-share','—')}%", sBody),
                Paragraph(b.get("ben-nid","—"), sBody),
                Paragraph(b.get("ben-phone","—"), sBody),
            ])
        col_w = [0.6*cm, 3.8*cm, 2.5*cm, 2.2*cm, 3.5*cm, 3*cm]
        bt = Table(ben_data, colWidths=col_w)
        bt.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), RUST),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]),
            ("GRID", (0,0), (-1,-1), 0.3, BORDER),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        story.append(bt)
    else:
        story.append(Paragraph("Hakuna mrithi aliyeandikwa. / No beneficiaries recorded.", sBody))

    # ── SECTION 4: EXECUTOR ─────────────────────────────────
    ex = d.get("executor", {})
    gu = d.get("guardian", {})
    section("MSIMAMIZI NA MDHAMINI", "EXECUTOR & GUARDIAN")
    row("Msimamizi Mkuu / Primary Executor", f"{ex.get('name','—')}  |  Simu: {ex.get('phone','—')}  |  Uhusiano: {ex.get('rel','—')}  |  NIDA: {ex.get('nid','—')}")
    row("Msimamizi Mbadala / Reserve Executor", f"{ex.get('reserve_name','—')}  |  Simu: {ex.get('reserve_phone','—')}")
    if gu.get("name"):
        row("Mdhamini wa Watoto / Children's Guardian", f"{gu.get('name','—')}  |  Uhusiano: {gu.get('rel','—')}  |  Simu: {gu.get('phone','—')}  |  NIDA: {gu.get('nid','—')}")

    # ── SECTION 5: WISHES ───────────────────────────────────
    wishes = d.get("wishes", {})
    section("MATAKWA MAALUM", "SPECIAL WISHES")
    row("Maelekezo ya Mazishi / Funeral Instructions", wishes.get("funeral",""))
    row("Sadaka / Charitable Donations", wishes.get("charity",""))
    row("Masharti Maalum / Special Conditions", wishes.get("special",""))
    row("Madeni ya Kulipwa / Debts to Settle", wishes.get("debts",""))

    # ── SECTION 6: WITNESSES ────────────────────────────────
    wi = d.get("witnesses", {})
    section("MASHAHIDI", "WITNESSES")
    story.append(Paragraph(
        "Wosia huu umesainiwa mbele ya mashahidi wafuatao wazima, ambao si wateule wa wosia huu, "
        "kwa mujibu wa Kifungu cha 11 cha Law of Succession Act, Cap. 865.",
        sBody
    ))
    story.append(Paragraph(
        "This will was signed in the presence of the following adult witnesses, who are not beneficiaries "
        "under this will, pursuant to Section 11 of the Law of Succession Act, Cap. 865.",
        sBody
    ))
    row("Shahidi wa 1 / Witness 1", f"{wi.get('w1_name','—')}  |  NIDA: {wi.get('w1_nid','—')}")
    row("Shahidi wa 2 / Witness 2", f"{wi.get('w2_name','—')}  |  NIDA: {wi.get('w2_nid','—')}")

    # ── SIGNATURE BLOCK ─────────────────────────────────────
    story.append(Spacer(1, 18))
    story.append(HRFlowable(width=W, thickness=0.5, color=BORDER, spaceAfter=10))

    col = W / 3
    sig_data = [[
        Paragraph("_______________________", sSigLbl),
        Paragraph("_______________________", sSigLbl),
        Paragraph("_______________________", sSigLbl),
    ],[
        Paragraph(f"<b>{full}</b>", sSigLbl),
        Paragraph("<b>Wakili / Advocate</b>", sSigLbl),
        Paragraph(f"<b>{wi.get('w1_name','Shahidi 1')}</b>", sSigLbl),
    ],[
        Paragraph("Mwandishi wa Wosia<br/>Testator", sSigLbl),
        Paragraph("Jina: _________________<br/>Reg No: ________________<br/>Muhuri / Stamp:", sSigLbl),
        Paragraph(f"Shahidi wa 1 / Witness 1<br/>NIDA: {wi.get('w1_nid','—')}", sSigLbl),
    ],[
        Paragraph("Tarehe: _______________", sSigLbl),
        Paragraph("Tarehe: _______________", sSigLbl),
        Paragraph("Tarehe: _______________", sSigLbl),
    ]]
    # add a 4th col for witness 2
    for i, row_d in enumerate(sig_data):
        row_d.append([
            Paragraph("_______________________", sSigLbl),
            Paragraph(f"<b>{wi.get('w2_name','Shahidi 2')}</b>", sSigLbl),
            Paragraph(f"Shahidi wa 2 / Witness 2<br/>NIDA: {wi.get('w2_nid','—')}", sSigLbl),
            Paragraph("Tarehe: _______________", sSigLbl),
        ][i])

    sig_tbl = Table(sig_data, colWidths=[col, col, col*0.55, col*0.45])
    sig_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(sig_tbl)

    # ── LEGAL FOOTER ────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width=W, thickness=0.5, color=BORDER, spaceAfter=6))
    story.append(Paragraph(
        "<b>Tangazo la Kisheria / Legal Disclaimer:</b> Hati hii imeandaliwa kwa msaada wa mfumo wa "
        "kompyuta na inazingatia miongozo ya Law of Succession Act, Cap. 865 (Tanzania). Hata hivyo, "
        "hati hii haina nguvu ya kisheria hadi itakaposainiwa mbele ya mashahidi wawili wazima na wakili "
        "aliyesajiliwa na Tanganyika Law Society (au Zanzibar Law Society kwa wakazi wa Zanzibar).",
        sLegal
    ))
    story.append(Paragraph(
        "This document was prepared with computer system assistance and follows the Law of Succession Act, "
        "Cap. 865 (Tanzania). It has no legal force until signed before two adult witnesses and an advocate "
        "registered with the Tanganyika Law Society or Zanzibar Law Society. Legal counsel is strongly advised.",
        sLegal
    ))

    doc.build(story)


if __name__ == "__main__":
    app.run(debug=True, port=5050)
