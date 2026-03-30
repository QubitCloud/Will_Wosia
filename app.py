from flask import Flask, render_template, request, jsonify, send_file
import json, os, uuid, io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

app = Flask(__name__)
app.secret_key = "wosia-tz-2024"

FOLDA_HIFADHI = "submissions"
os.makedirs(FOLDA_HIFADHI, exist_ok=True)


@app.route("/")
def ukurasa_nyumbani():
    return render_template("index.html")


@app.route("/fomu")
def ukurasa_fomu():
    return render_template("form.html")


@app.route("/tuma", methods=["POST"])
def pokea_fomu():
    try:
        data = request.get_json()
        kumbukumbu = str(uuid.uuid4())[:8].upper()
        wakati = datetime.now().isoformat()
        rekodi = {"ref_id": kumbukumbu, "submitted_at": wakati, "data": data}
        njia = os.path.join(FOLDA_HIFADHI, f"wosia_{kumbukumbu}.json")
        with open(njia, "w") as f:
            json.dump(rekodi, f, indent=2, ensure_ascii=False)
        return jsonify({"mafanikio": True, "kumbukumbu": kumbukumbu})
    except Exception as e:
        return jsonify({"mafanikio": False, "kosa": str(e)}), 500


@app.route("/mapitio/<kumbukumbu>")
def ukurasa_mapitio(kumbukumbu):
    njia = os.path.join(FOLDA_HIFADHI, f"wosia_{kumbukumbu}.json")
    if not os.path.exists(njia):
        return "Rekodi haikupatikana", 404
    with open(njia) as f:
        rekodi = json.load(f)
    return render_template("review.html", record=rekodi)


@app.route("/pdf/<kumbukumbu>")
def tengeneza_pdf(kumbukumbu):
    njia = os.path.join(FOLDA_HIFADHI, f"wosia_{kumbukumbu}.json")
    if not os.path.exists(njia):
        return "Rekodi haikupatikana", 404
    with open(njia) as f:
        rekodi = json.load(f)
    buffer = io.BytesIO()
    jenga_pdf_wosia(rekodi, buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Wosia_{kumbukumbu}.pdf"
    )


# ─── TENGENEZA PDF ──────────────────────────────────────────────────────────

RANGI_RUST   = colors.Color(0.545, 0.145, 0)
RANGI_DHAHABU = colors.Color(0.722, 0.525, 0.043)
RANGI_DHAHABU_LT = colors.Color(0.831, 0.627, 0.090)
RANGI_INK    = colors.Color(0.102, 0.063, 0.031)
RANGI_MID    = colors.Color(0.420, 0.361, 0.243)
RANGI_NYEPESI = colors.Color(0.961, 0.941, 0.910)
RANGI_MIPAKA = colors.Color(0.784, 0.722, 0.604)

def jenga_pdf_wosia(rekodi, buffer):
    d   = rekodi["data"]
    m   = d["mwandishi"]
    ref = rekodi["ref_id"]
    tar = rekodi["submitted_at"][:10]

    jina_kamili = f"{m.get('fname','')} {m.get('mname','')} {m.get('lname','')}".strip()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Wosia wa {jina_kamili}",
        author="Wosia Wangu — Tanzania"
    )
    upana = A4[0] - 5*cm

    sty = getSampleStyleSheet()
    def ST(jina, **kw):
        return ParagraphStyle(jina, parent=sty["Normal"], **kw)

    s_kichwa  = ST("sk", fontName="Times-Bold",     fontSize=18, textColor=RANGI_RUST,      spaceAfter=4,  alignment=TA_CENTER)
    s_chini   = ST("sc", fontName="Times-Italic",   fontSize=10, textColor=RANGI_MID,       spaceAfter=2,  alignment=TA_CENTER)
    s_ref     = ST("sr", fontName="Helvetica",      fontSize=8,  textColor=RANGI_MID,       spaceAfter=12, alignment=TA_CENTER)
    s_sehemu  = ST("ss", fontName="Times-Bold",     fontSize=12, textColor=RANGI_RUST,      spaceBefore=14, spaceAfter=4)
    s_lebo    = ST("sl", fontName="Helvetica-Bold", fontSize=7.5,textColor=RANGI_MID,       spaceAfter=1,  leading=10)
    s_thamani = ST("st", fontName="Helvetica",      fontSize=9.5,textColor=RANGI_INK,       spaceAfter=6,  leading=13)
    s_mwili   = ST("sm", fontName="Helvetica",      fontSize=9,  textColor=RANGI_INK,       spaceAfter=4,  leading=13)
    s_kisheria= ST("sh", fontName="Helvetica-Oblique", fontSize=7.5, textColor=RANGI_MID,   spaceAfter=3,  leading=11)
    s_saini   = ST("si", fontName="Helvetica",      fontSize=7.5,textColor=RANGI_MID,       alignment=TA_CENTER)

    hadithi = []

    # ── KICHWA ────────────────────────────────────────────
    hadithi.append(Paragraph("HATI YA WOSIA WA MWISHO", s_kichwa))
    hadithi.append(Paragraph("Imetolewa kwa mujibu wa Sheria ya Mirathi, Cap. 865 — Jamhuri ya Muungano wa Tanzania", s_chini))
    hadithi.append(Paragraph(f"Namba ya Kumbukumbu: <b>{ref}</b>  |  Tarehe ya Kusajiliwa: {tar}", s_ref))
    hadithi.append(HRFlowable(width=upana, thickness=1.5, color=RANGI_RUST, spaceAfter=10))

    # ── TAMKO LA AWALI ────────────────────────────────────
    nida  = m.get('nid','_______________')
    anwani = m.get('anwani','_______________')
    hadithi.append(Paragraph(
        f"Mimi, <b>{jina_kamili}</b>, mwenye Kitambulisho Namba <b>{nida}</b>, "
        f"mwenye makazi katika <b>{anwani}</b>, nikiwa na akili timamu na uwezo kamili wa "
        f"kisheria, natoa Wosia huu wa Mwisho na kufuta wosia na maagizo yote ya awali "
        f"niliyowahi kutoa.",
        s_mwili
    ))
    hadithi.append(Spacer(1, 6))

    def sehemu(kichwa):
        hadithi.append(HRFlowable(width=upana, thickness=0.5, color=RANGI_MIPAKA, spaceBefore=6, spaceAfter=0))
        hadithi.append(Paragraph(kichwa, s_sehemu))

    def safu(lebo, thamani):
        if thamani and str(thamani).strip():
            hadithi.append(Paragraph(lebo.upper(), s_lebo))
            hadithi.append(Paragraph(str(thamani), s_thamani))

    # ── SEHEMU 1: MWANDISHI ───────────────────────────────
    sehemu("1. TAARIFA ZA MWANDISHI WA WOSIA")
    safu_data = [
        ("Jina Kamili", jina_kamili),
        ("Tarehe ya Kuzaliwa", m.get('dob','')),
        ("Kitambulisho (NIDA)", nida),
        ("Jinsi", m.get('jinsi','')),
        ("Simu", m.get('simu','')),
        ("Barua Pepe", m.get('barua_pepe','')),
        ("Anwani ya Makazi", anwani),
        ("Hali ya Ndoa", m.get('hali_ndoa','')),
        ("Dini", m.get('dini','')),
    ]
    jedwali_data = [[Paragraph(l, s_lebo), Paragraph(v or "—", s_thamani)] for l, v in safu_data]
    jedwali = Table(jedwali_data, colWidths=[5.5*cm, upana-5.5*cm])
    jedwali.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, RANGI_NYEPESI]),
        ("GRID", (0,0), (-1,-1), 0.3, RANGI_MIPAKA),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    hadithi.append(jedwali)

    # ── SEHEMU 2: MALI ────────────────────────────────────
    mali = d.get("mali", {})
    sehemu("2. MALI NA RASILIMALI")

    ardhi_orodha = mali.get("ardhi", [])
    if ardhi_orodha:
        hadithi.append(Paragraph("A. Ardhi na Nyumba", ST("h2a", fontName="Helvetica-Bold", fontSize=9, textColor=RANGI_INK, spaceAfter=3)))
        for i, p in enumerate(ardhi_orodha, 1):
            hadithi.append(Paragraph(
                f"{i}. <b>{p.get('aina-ardhi','').upper()}</b> — Hati: {p.get('hati-ardhi','—')} | "
                f"Mahali: {p.get('mahali-ardhi','—')} | Thamani: TZS {p.get('thamani-ardhi','—')} | "
                f"Mrithi: {p.get('mrithi-ardhi','—')}",
                s_mwili
            ))

    benki_orodha = mali.get("benki", [])
    if benki_orodha:
        hadithi.append(Paragraph("B. Akaunti za Benki", ST("h2b", fontName="Helvetica-Bold", fontSize=9, textColor=RANGI_INK, spaceAfter=3, spaceBefore=6)))
        for i, b in enumerate(benki_orodha, 1):
            hadithi.append(Paragraph(
                f"{i}. <b>{b.get('jina-benki','—')}</b> — Akaunti: {b.get('namba-benki','—')} | "
                f"Tawi: {b.get('tawi-benki','—')} | Mrithi: {b.get('mrithi-benki','—')}",
                s_mwili
            ))

    magari_orodha = mali.get("magari", [])
    if magari_orodha:
        hadithi.append(Paragraph("C. Magari", ST("h2c", fontName="Helvetica-Bold", fontSize=9, textColor=RANGI_INK, spaceAfter=3, spaceBefore=6)))
        for i, v in enumerate(magari_orodha, 1):
            hadithi.append(Paragraph(
                f"{i}. <b>{v.get('aina-gari','—')}</b> ({v.get('mwaka-gari','—')}) — "
                f"Usajili: {v.get('usajili-gari','—')} | Mrithi: {v.get('mrithi-gari','—')}",
                s_mwili
            ))

    nyingine = mali.get("nyingine", "")
    if nyingine:
        hadithi.append(Paragraph("D. Mali Nyingine", ST("h2d", fontName="Helvetica-Bold", fontSize=9, textColor=RANGI_INK, spaceAfter=3, spaceBefore=6)))
        hadithi.append(Paragraph(nyingine, s_mwili))

    # ── SEHEMU 3: WATEULE ─────────────────────────────────
    wateule = d.get("wateule", [])
    sehemu("3. WATEULE WA MIRATHI")
    if wateule:
        vichwa = [Paragraph(h, ST(f"wh{i}", fontName="Helvetica-Bold", fontSize=8, textColor=RANGI_INK))
                  for i, h in enumerate(["#", "Jina", "Uhusiano", "Mgawanyo", "NIDA", "Simu"])]
        jedwali_wateule = [vichwa]
        for i, b in enumerate(wateule, 1):
            jedwali_wateule.append([
                Paragraph(str(i), s_mwili),
                Paragraph(b.get("jina-mrithi","—"), s_mwili),
                Paragraph(b.get("uhusiano-mrithi","—"), s_mwili),
                Paragraph(f"{b.get('mgawanyo-mrithi','—')}%", s_mwili),
                Paragraph(b.get("nida-mrithi","—"), s_mwili),
                Paragraph(b.get("simu-mrithi","—"), s_mwili),
            ])
        upana_safu = [0.6*cm, 3.8*cm, 2.5*cm, 2.2*cm, 3.5*cm, 3*cm]
        jt = Table(jedwali_wateule, colWidths=upana_safu)
        jt.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), RANGI_RUST),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, RANGI_NYEPESI]),
            ("GRID", (0,0), (-1,-1), 0.3, RANGI_MIPAKA),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        hadithi.append(jt)
    else:
        hadithi.append(Paragraph("Hakuna mrithi aliyeandikwa.", s_mwili))

    # ── SEHEMU 4: MSIMAMIZI ───────────────────────────────
    ms = d.get("msimamizi", {})
    md = d.get("mdhamini", {})
    sehemu("4. MSIMAMIZI WA WOSIA NA MDHAMINI")
    safu("Msimamizi Mkuu", f"{ms.get('jina','—')}  |  Simu: {ms.get('simu','—')}  |  Uhusiano: {ms.get('uhusiano','—')}  |  NIDA: {ms.get('nida','—')}")
    safu("Msimamizi Mbadala", f"{ms.get('mbadala_jina','—')}  |  Simu: {ms.get('mbadala_simu','—')}")
    if md.get("jina"):
        safu("Mdhamini wa Watoto", f"{md.get('jina','—')}  |  Uhusiano: {md.get('uhusiano','—')}  |  Simu: {md.get('simu','—')}  |  NIDA: {md.get('nida','—')}")

    # ── SEHEMU 5: MATAKWA ─────────────────────────────────
    mt = d.get("matakwa", {})
    sehemu("5. MATAKWA MAALUM")
    safu("Maelekezo ya Mazishi", mt.get("mazishi",""))
    safu("Misaada ya Hisani / Sadaka", mt.get("sadaka",""))
    safu("Masharti Maalum", mt.get("masharti",""))
    safu("Madeni ya Kulipwa", mt.get("madeni",""))

    # ── SEHEMU 6: MASHAHIDI ───────────────────────────────
    sh = d.get("mashahidi", {})
    sehemu("6. MASHAHIDI")
    hadithi.append(Paragraph(
        "Wosia huu umesainiwa mbele ya mashahidi wafuatao wazima, ambao si wateule wa wosia huu, "
        "kwa mujibu wa Kifungu cha 11 cha Sheria ya Mirathi, Cap. 865.",
        s_mwili
    ))
    safu("Shahidi wa 1", f"{sh.get('shahidi1_jina','—')}  |  NIDA: {sh.get('shahidi1_nida','—')}")
    safu("Shahidi wa 2", f"{sh.get('shahidi2_jina','—')}  |  NIDA: {sh.get('shahidi2_nida','—')}")

    # ── SAINI ─────────────────────────────────────────────
    hadithi.append(Spacer(1, 18))
    hadithi.append(HRFlowable(width=upana, thickness=0.5, color=RANGI_MIPAKA, spaceAfter=10))

    safu_saini = [
        [Paragraph("_______________________", s_saini), Paragraph("_______________________", s_saini),
         Paragraph("_______________________", s_saini), Paragraph("_______________________", s_saini)],
        [Paragraph(f"<b>{jina_kamili}</b>", s_saini), Paragraph("<b>Wakili / Advocate</b>", s_saini),
         Paragraph(f"<b>{sh.get('shahidi1_jina','Shahidi 1')}</b>", s_saini),
         Paragraph(f"<b>{sh.get('shahidi2_jina','Shahidi 2')}</b>", s_saini)],
        [Paragraph("Mwandishi wa Wosia", s_saini),
         Paragraph("Jina: _________________<br/>Namba ya Usajili: ________<br/>Muhuri:", s_saini),
         Paragraph(f"Shahidi wa 1<br/>NIDA: {sh.get('shahidi1_nida','—')}", s_saini),
         Paragraph(f"Shahidi wa 2<br/>NIDA: {sh.get('shahidi2_nida','—')}", s_saini)],
        [Paragraph("Tarehe: _______________", s_saini), Paragraph("Tarehe: _______________", s_saini),
         Paragraph("Tarehe: _______________", s_saini), Paragraph("Tarehe: _______________", s_saini)],
    ]
    upana_safu_saini = [upana/4] * 4
    js = Table(safu_saini, colWidths=upana_safu_saini)
    js.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    hadithi.append(js)

    # ── TANGAZO LA KISHERIA ───────────────────────────────
    hadithi.append(Spacer(1, 14))
    hadithi.append(HRFlowable(width=upana, thickness=0.5, color=RANGI_MIPAKA, spaceAfter=6))
    hadithi.append(Paragraph(
        "<b>Tangazo la Kisheria:</b> Hati hii imeandaliwa kwa msaada wa mfumo wa kompyuta "
        "na inazingatia miongozo ya Sheria ya Mirathi, Cap. 865 (Tanzania). Hata hivyo, "
        "hati hii haina nguvu ya kisheria hadi itakaposainiwa mbele ya mashahidi wawili wazima "
        "na wakili aliyesajiliwa na Tanganyika Law Society (au Zanzibar Law Society kwa wakazi "
        "wa Zanzibar). Mshauri wa kisheria anashauriwa sana.",
        s_kisheria
    ))

    doc.build(hadithi)


if __name__ == "__main__":
    app.run(debug=True, port=5050)
