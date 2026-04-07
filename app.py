from flask import Flask, render_template, request, jsonify, send_file
import json, os, io
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
        wakati = datetime.now().isoformat()
        faili_id = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        rekodi = {"submitted_at": wakati, "data": data}
        njia = os.path.join(FOLDA_HIFADHI, f"wosia_{faili_id}.json")
        with open(njia, "w") as f:
            json.dump(rekodi, f, indent=2, ensure_ascii=False)
        return jsonify({"mafanikio": True, "faili_id": faili_id})
    except Exception as e:
        return jsonify({"mafanikio": False, "kosa": str(e)}), 500



@app.route("/pdf/<faili_id>")
def tengeneza_pdf(faili_id):
    njia = os.path.join(FOLDA_HIFADHI, f"wosia_{faili_id}.json")
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
        download_name=f"Wosia_Wangu.pdf"
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

    s_kichwa  = ST("sk", fontName="Times-Bold",        fontSize=18, textColor=RANGI_RUST,  spaceAfter=4,  alignment=TA_CENTER)
    s_chini   = ST("sc", fontName="Times-Italic",      fontSize=10, textColor=RANGI_MID,   spaceAfter=2,  alignment=TA_CENTER)
    s_ref     = ST("sr", fontName="Helvetica",         fontSize=8,  textColor=RANGI_MID,   spaceAfter=12, alignment=TA_CENTER)
    s_sehemu  = ST("ss", fontName="Times-Bold",        fontSize=12, textColor=RANGI_RUST,  spaceBefore=14, spaceAfter=4)
    s_lebo    = ST("sl", fontName="Helvetica-Bold",    fontSize=7.5,textColor=RANGI_MID,   spaceAfter=1,  leading=10)
    s_thamani = ST("st", fontName="Helvetica",         fontSize=9.5,textColor=RANGI_INK,   spaceAfter=6,  leading=13)
    s_mwili   = ST("sm", fontName="Helvetica",         fontSize=9,  textColor=RANGI_INK,   spaceAfter=4,  leading=13)
    s_kisheria= ST("sh", fontName="Helvetica-Oblique", fontSize=7.5,textColor=RANGI_MID,   spaceAfter=3,  leading=11)
    s_saini   = ST("si", fontName="Helvetica",         fontSize=7.5,textColor=RANGI_MID,   alignment=TA_CENTER)

    hadithi = []

    # helpers
    def v(val):
        """Rudisha thamani au tupu — si '—'"""
        return str(val).strip() if val and str(val).strip() else ""

    nambari_sehemu = [0]  # counter inayoendelea

    def sehemu(kichwa):
        nambari_sehemu[0] += 1
        kichwa_kamili = f"{nambari_sehemu[0]}. {kichwa}"
        hadithi.append(HRFlowable(width=upana, thickness=0.5, color=RANGI_MIPAKA, spaceBefore=6, spaceAfter=0))
        hadithi.append(Paragraph(kichwa_kamili, s_sehemu))

    def safu(lebo, thamani):
        """Onyesha safu tu kama thamani ipo"""
        if thamani and str(thamani).strip():
            hadithi.append(Paragraph(lebo.upper(), s_lebo))
            hadithi.append(Paragraph(str(thamani), s_thamani))

    def jedwali_mwandishi(safu_data):
        """Tengeneza jedwali la safu zilizojazwa tu"""
        safu_zilizojazwa = [(l, val) for l, val in safu_data if v(val)]
        if not safu_zilizojazwa:
            return
        data = [[Paragraph(l, s_lebo), Paragraph(val, s_thamani)] for l, val in safu_zilizojazwa]
        jed = Table(data, colWidths=[5.5*cm, upana-5.5*cm])
        jed.setStyle(TableStyle([
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("ROWBACKGROUNDS",(0,0), (-1,-1), [colors.white, RANGI_NYEPESI]),
            ("GRID",          (0,0), (-1,-1), 0.3, RANGI_MIPAKA),
            ("LEFTPADDING",   (0,0), (-1,-1), 5),
            ("RIGHTPADDING",  (0,0), (-1,-1), 5),
            ("TOPPADDING",    (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        hadithi.append(jed)

    # ── KICHWA ────────────────────────────────────────────
    hadithi.append(Paragraph("HATI YA WOSIA WA MWISHO", s_kichwa))
    hadithi.append(Paragraph("Imetolewa kwa mujibu wa Probate and Administration of Estates Act, Cap. 352 (R.E. 2023) — Jamhuri ya Muungano wa Tanzania", s_chini))
    hadithi.append(Paragraph(f"Tarehe ya Kutolewa: {tar}", s_ref))
    hadithi.append(HRFlowable(width=upana, thickness=1.5, color=RANGI_RUST, spaceAfter=10))

    # ── TAMKO LA AWALI ────────────────────────────────────
    nida   = v(m.get('nid')) or '_______________'
    anwani = v(m.get('anwani')) or '_______________'
    hadithi.append(Paragraph(
        f"Mimi, <b>{jina_kamili}</b>, mwenye Kitambulisho Namba <b>{nida}</b>, "
        f"mwenye makazi <b>{anwani}</b>, nikiwa na akili timamu "
        f"natoa Wosia huu wa Mwisho na kufuta wosia na maagizo yote ya awali niliyowahi kutoa.",
        s_mwili
    ))
    hadithi.append(Spacer(1, 6))

    # ── SEHEMU 1: MWANDISHI ───────────────────────────────
    sehemu("TAARIFA ZA MWANDISHI WA WOSIA")
    jedwali_mwandishi([
        ("Jina Kamili",       jina_kamili),
        ("Tarehe ya Kuzaliwa",m.get('dob','')),
        ("Kitambulisho (NIDA)",nida if nida != '_______________' else ''),
        ("Jinsi",             m.get('jinsi','').capitalize()),
        ("Simu",              m.get('simu','')),
        ("Barua Pepe",        m.get('barua_pepe','')),
        ("Anwani ya Makazi",  anwani if anwani != '_______________' else ''),
        ("Hali ya Ndoa",      m.get('hali_ndoa','').capitalize()),
        ("Dini",              m.get('dini','').capitalize()),
    ])

    # ── SEHEMU 2: MALI — inaonekana tu kama kuna kitu ────
    mali = d.get("mali", {})
    ardhi_orodha  = mali.get("ardhi", [])
    benki_orodha  = mali.get("benki", [])
    magari_orodha = mali.get("magari", [])
    nyingine      = v(mali.get("nyingine",""))
    kuna_mali     = any([ardhi_orodha, benki_orodha, magari_orodha, nyingine])

    if kuna_mali:
        sehemu("MALI NA RASILIMALI")
        if ardhi_orodha:
            hadithi.append(Paragraph("A. Ardhi na Nyumba", ST("h2a", fontName="Helvetica-Bold", fontSize=9, textColor=RANGI_INK, spaceAfter=3)))
            for i, p in enumerate(ardhi_orodha, 1):
                sehemu_parts = []
                if v(p.get('aina-ardhi')): sehemu_parts.append(f"<b>{v(p.get('aina-ardhi')).capitalize()}</b>")
                if v(p.get('hati-ardhi')): sehemu_parts.append(f"Hati: {v(p.get('hati-ardhi'))}")
                if v(p.get('mahali-ardhi')): sehemu_parts.append(f"Mahali: {v(p.get('mahali-ardhi'))}")
                if v(p.get('thamani-ardhi')): sehemu_parts.append(f"Thamani: TZS {v(p.get('thamani-ardhi'))}")
                if v(p.get('mrithi-ardhi')): sehemu_parts.append(f"Mrithi: {v(p.get('mrithi-ardhi'))}")
                hadithi.append(Paragraph(f"{i}. {' — '.join(sehemu_parts)}", s_mwili))

        if benki_orodha:
            hadithi.append(Paragraph("B. Akaunti za Benki", ST("h2b", fontName="Helvetica-Bold", fontSize=9, textColor=RANGI_INK, spaceAfter=3, spaceBefore=6)))
            for i, b in enumerate(benki_orodha, 1):
                sehemu_parts = []
                if v(b.get('jina-benki')): sehemu_parts.append(f"<b>{v(b.get('jina-benki'))}</b>")
                if v(b.get('namba-benki')): sehemu_parts.append(f"Akaunti: {v(b.get('namba-benki'))}")
                if v(b.get('tawi-benki')): sehemu_parts.append(f"Tawi: {v(b.get('tawi-benki'))}")
                if v(b.get('mrithi-benki')): sehemu_parts.append(f"Mrithi: {v(b.get('mrithi-benki'))}")
                hadithi.append(Paragraph(f"{i}. {' — '.join(sehemu_parts)}", s_mwili))

        if magari_orodha:
            hadithi.append(Paragraph("C. Magari", ST("h2c", fontName="Helvetica-Bold", fontSize=9, textColor=RANGI_INK, spaceAfter=3, spaceBefore=6)))
            for i, g in enumerate(magari_orodha, 1):
                sehemu_parts = []
                if v(g.get('aina-gari')): sehemu_parts.append(f"<b>{v(g.get('aina-gari'))}</b>")
                if v(g.get('mwaka-gari')): sehemu_parts.append(f"({v(g.get('mwaka-gari'))})")
                if v(g.get('usajili-gari')): sehemu_parts.append(f"Usajili: {v(g.get('usajili-gari'))}")
                if v(g.get('mrithi-gari')): sehemu_parts.append(f"Mrithi: {v(g.get('mrithi-gari'))}")
                hadithi.append(Paragraph(f"{i}. {' '.join(sehemu_parts)}", s_mwili))

        if nyingine:
            hadithi.append(Paragraph("D. Mali Nyingine", ST("h2d", fontName="Helvetica-Bold", fontSize=9, textColor=RANGI_INK, spaceAfter=3, spaceBefore=6)))
            hadithi.append(Paragraph(nyingine, s_mwili))

    # ── SEHEMU 3: WATEULE — inaonekana tu kama kuna wateule
    wateule = [b for b in d.get("wateule", []) if v(b.get("jina-mrithi",""))]
    if wateule:
        sehemu("WATEULE WA MIRATHI")
        # Safu za kuonyesha — ondoa safu tupu
        vichwa_base = ["#", "Jina", "Uhusiano", "Mgawanyo"]
        onyesha_nida = any(v(b.get("nida-mrithi","")) for b in wateule)
        onyesha_simu = any(v(b.get("simu-mrithi","")) for b in wateule)
        vichwa = vichwa_base[:]
        if onyesha_nida: vichwa.append("NIDA")
        if onyesha_simu: vichwa.append("Simu")

        vichwa_row = [Paragraph(h, ST(f"wh{i}", fontName="Helvetica-Bold", fontSize=8, textColor=RANGI_INK)) for i, h in enumerate(vichwa)]
        jedwali_wateule = [vichwa_row]
        for i, b in enumerate(wateule, 1):
            row = [
                Paragraph(str(i), s_mwili),
                Paragraph(v(b.get("jina-mrithi")) or "—", s_mwili),
                Paragraph((v(b.get("uhusiano-mrithi")) or "—").capitalize(), s_mwili),
                Paragraph(f"{v(b.get('mgawanyo-mrithi')) or '—'}%", s_mwili),
            ]
            if onyesha_nida: row.append(Paragraph(v(b.get("nida-mrithi")) or "—", s_mwili))
            if onyesha_simu: row.append(Paragraph(v(b.get("simu-mrithi")) or "—", s_mwili))
            jedwali_wateule.append(row)

        n = len(vichwa)
        upana_kila = upana / n
        jt = Table(jedwali_wateule, colWidths=[upana_kila]*n)
        jt.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), RANGI_RUST),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, RANGI_NYEPESI]),
            ("GRID",          (0,0), (-1,-1), 0.3, RANGI_MIPAKA),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING",   (0,0), (-1,-1), 4),
            ("RIGHTPADDING",  (0,0), (-1,-1), 4),
            ("TOPPADDING",    (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        hadithi.append(jt)

    # ── SEHEMU 4: MSIMAMIZI — inaonekana tu kama imejazwa
    ms = d.get("msimamizi", {})
    md = d.get("mdhamini", {})
    kuna_msimamizi = v(ms.get("jina",""))
    kuna_mbadala   = v(ms.get("mbadala_jina",""))
    kuna_mdhamini  = v(md.get("jina",""))

    if kuna_msimamizi:
        sehemu("MSIMAMIZI WA WOSIA NA MDHAMINI")
        ms_parts = [v(ms.get("jina",""))]
        if v(ms.get("uhusiano","")): ms_parts.append(f"Uhusiano: {v(ms.get('uhusiano'))}")
        if v(ms.get("simu","")): ms_parts.append(f"Simu: {v(ms.get('simu'))}")
        if v(ms.get("nida","")): ms_parts.append(f"NIDA: {v(ms.get('nida'))}")
        safu("Msimamizi Mkuu", "  |  ".join(ms_parts))

        if kuna_mbadala:
            mb_parts = [v(ms.get("mbadala_jina",""))]
            if v(ms.get("mbadala_simu","")): mb_parts.append(f"Simu: {v(ms.get('mbadala_simu'))}")
            safu("Msimamizi Mbadala", "  |  ".join(mb_parts))

        if kuna_mdhamini:
            md_parts = [v(md.get("jina",""))]
            if v(md.get("uhusiano","")): md_parts.append(f"Uhusiano: {v(md.get('uhusiano'))}")
            if v(md.get("simu","")): md_parts.append(f"Simu: {v(md.get('simu'))}")
            if v(md.get("nida","")): md_parts.append(f"NIDA: {v(md.get('nida'))}")
            safu("Mdhamini wa Watoto", "  |  ".join(md_parts))

    # ── SEHEMU 5: MATAKWA — inaonekana tu kama kuna kitu
    mt = d.get("matakwa", {})
    matakwa_yaliyojazwa = {k: v(val) for k, val in mt.items() if v(val)}
    if matakwa_yaliyojazwa:
        sehemu("MATAKWA MAALUM")
        if matakwa_yaliyojazwa.get("mazishi"):  safu("Maelekezo ya Mazishi",        matakwa_yaliyojazwa["mazishi"])
        if matakwa_yaliyojazwa.get("sadaka"):   safu("Misaada ya Hisani / Sadaka",  matakwa_yaliyojazwa["sadaka"])
        if matakwa_yaliyojazwa.get("masharti"): safu("Masharti Maalum",             matakwa_yaliyojazwa["masharti"])
        if matakwa_yaliyojazwa.get("madeni"):   safu("Madeni ya Kulipwa",           matakwa_yaliyojazwa["madeni"])

    # ── SEHEMU 6: MASHAHIDI — inaonekana tu kama imejazwa
    sh = d.get("mashahidi", {})
    kuna_shahidi1 = v(sh.get("shahidi1_jina",""))
    kuna_shahidi2 = v(sh.get("shahidi2_jina",""))
    if kuna_shahidi1 or kuna_shahidi2:
        sehemu("MASHAHIDI")
        hadithi.append(Paragraph(
            "Wosia huu umesainiwa mbele ya mashahidi wafuatao wazima, ambao si wateule wa wosia huu "
            "wala wasiokuwa wawakilishi wa wateule, kwa mujibu wa "
            "Probate and Administration of Estates Act, Cap. 352 (R.E. 2023).",
            s_mwili
        ))
        if kuna_shahidi1:
            sh1_parts = [kuna_shahidi1]
            if v(sh.get("shahidi1_nida","")): sh1_parts.append(f"NIDA: {v(sh.get('shahidi1_nida'))}")
            safu("Shahidi wa 1", "  |  ".join(sh1_parts))
        if kuna_shahidi2:
            sh2_parts = [kuna_shahidi2]
            if v(sh.get("shahidi2_nida","")): sh2_parts.append(f"NIDA: {v(sh.get('shahidi2_nida'))}")
            safu("Shahidi wa 2", "  |  ".join(sh2_parts))

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
        "<b>Sheria Zinazosimamia Wosia Huu:</b> "
        "Probate and Administration of Estates Act, Cap. 352 (R.E. 2023) · "
        "Judicature and Application of Laws Act, Cap. 358 (R.E. 2019) · "
        "Local Customary Law (Declaration) Order, GN 436 of 1963 · "
        "The Land Act (1999) &amp; Village Land Act (1999) · "
        "Law of Marriage Act, Cap. 29 (R.E. 2022).",
        s_kisheria
    ))
    hadithi.append(Paragraph(
        "<b>Tangazo la Kisheria:</b> Hati hii imeandaliwa kwa msaada wa mfumo wa kompyuta. "
        "Haina nguvu ya kisheria hadi itakaposainiwa mbele ya mashahidi wawili wazima na "
        "wakili aliyesajiliwa na Tanganyika Law Society (au Zanzibar Law Society kwa wakazi wa Zanzibar). "
        "Sheria za mirathi za Tanzania zinafanyiwa mapitio kuhusu haki za wanawake — "
        "mshauri wa kisheria anashauriwa sana.",
        s_kisheria
    ))

    doc.build(hadithi)


if __name__ == "__main__":
    app.run(debug=True, port=5050)
