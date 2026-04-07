# Wosia Wangu — Mfumo wa Wosia wa Kisheria, Tanzania

Programu ya wavuti (Flask + PDF) inayowezesha Watanzania kuandika wosia wao kwa Kiswahili, kwa kuzingatia sheria za mirathi zinazotumika nchini Tanzania.

---

## Jinsi ya Kuendesha

```bash
cd wosia_app
pip install -r requirements.txt
python app.py
```

Fungua: http://localhost:5050

---

## Sheria Zinazosimamia

### Sheria Kuu
**Sheria ya Uthibitishaji Wosia na Usimamizi wa Mirathi, Sura ya 352 (R.E. 2023)**
*(Probate and Administration of Estates Act, Cap. 352 R.E. 2023)*

Hii ndiyo sheria kuu inayosimamia taratibu za uthibitisho wa wosia na usimamizi wa mali za marehemu nchini Tanzania. Inaweka masharti ya:
- Uhalali wa wosia (umri wa mwandishi, akili timamu, usainiaji)
- Uteuzi wa msimamizi (executor) na wajibu wake
- Taratibu za mahakama (probate) baada ya kifo
- Haki za wateule wa mirathi

### Sheria Nyingine Zinazohusiana

**Judicature and Application of Laws Act, Cap. 358 (R.E. 2019)**
Inatoa mfumo wa kutumia sheria ya kimila na sheria ya Kiislamu — inabainisha ni sheria ipi inatumika kulingana na dini na asili ya marehemu.

**Local Customary Law (Declaration) Order, GN 436 of 1963**
Inasimamia urithi kwa wanachama wa makabila ya Tanzania (wengi wao ni jamii za ukoo wa baba). Mara nyingi inawapa wanaume kipaumbele katika urithi, ikiacha wajane na watoto wa kike na haki ndogo — hali inayoweza kulindwa kwa wosia wa maandishi.

**The Land Act (1999) & Village Land Act (1999)**
Ardhi yote Tanzania ni mali ya Serikali — mtu anaweza kurithi *haki ya kumiliki ardhi* (Right of Occupancy) tu, si ardhi yenyewe. Sheria hizi zinatoa haki sawa za kumiliki na kurithi ardhi kwa wanawake. Warithi wasio raia wa Tanzania hawawezi kumiliki ardhi moja kwa moja.

**Law of Marriage Act, Cap. 29 (R.E. 2022)**
Inabainisha haki za mali ya ndoa (matrimonial property) pindi mwenzi wa ndoa anapokufa — inasaidia kulinda haki za mke au mume aliyebaki.

---

## Masharti ya Wosia Halali (Cap. 352)

| Sharti | Maelezo |
|--------|---------|
| Umri | Mwandishi lazima awe na miaka 18 au zaidi |
| Akili | Lazima awe na akili timamu wakati wa kuandika |
| Maandishi | Wosia lazima uandikwe — si wa mdomo |
| Mashahidi | Lazima usainiwe mbele ya mashahidi WAWILI wazima |
| Mashahidi | Mashahidi hawapaswi kuwa wateule wa wosia huo |
| Wakili | Usainiaji usimamie na wakili aliyesajiliwa (TLS au ZLS) |

---

## Muundo wa Programu

```
wosia_app/
├── app.py                  ← Flask routes + PDF builder (reportlab)
├── requirements.txt
├── submissions/            ← Hifadhi ya JSON (inaundwa otomatiki)
└── templates/
    ├── index.html          ← Ukurasa wa kwanza
    ├── form.html           ← Fomu ya hatua 6
    └── review.html         ← Ukurasa wa muhtasari
```

## Hatua za Fomu

1. **Taarifa za Mwandishi** — Jina, NIDA, anwani, dini, hali ya ndoa
2. **Mali na Rasilimali** — Ardhi, benki, magari, mali nyingine
3. **Wateule wa Mirathi** — Watu watakaopata mali na mgawanyo wao
4. **Msimamizi wa Wosia** — Executor wa kwanza na mbadala, mdhamini wa watoto
5. **Matakwa Maalum** — Mazishi, sadaka, masharti, madeni
6. **Kagua na Tuma** → Pakua PDF

---

## Onyo

Sheria za mirathi za Tanzania zinafanyiwa mapitio kuhusu ubaguzi dhidi ya wanawake. Mshauri wa kisheria (wakili aliyesajiliwa na Tanganyika Law Society au Zanzibar Law Society) anashauriwa sana ili kuhakikisha wosia unazingatia haki za kikatiba za wote wanaohusika.
