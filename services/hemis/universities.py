# O'zbekiston Oliy Ta'lim Muassasalari (HEMIS domenlari bilan)

UNIVERSITIES = [
    {"name": "TATU (Muhammad al-Xorazmiy nomidagi Toshkent axborot texnologiyalari universiteti)", "domain": "student.tuit.uz", "short": "tuit"},
    {"name": "O'zMU (Mirzo Ulug'bek nomidagi O'zbekiston Milliy universiteti)", "domain": "student.nuu.uz", "short": "nuu"},
    {"name": "TDIU (Toshkent davlat iqtisodiyot universiteti)", "domain": "student.tsue.uz", "short": "tsue"},
    {"name": "TDTU (Islom Karimov nomidagi Toshkent davlat texnika universiteti)", "domain": "student.tdtu.uz", "short": "tdtu"},
    {"name": "TDYU (Toshkent davlat yuridik universiteti)", "domain": "student.tsul.uz", "short": "tsul"},
    {"name": "SamDU (Sharof Rashidov nomidagi Samarqand davlat universiteti)", "domain": "student.samdu.uz", "short": "samdu"},
    {"name": "O'zDJTU (O'zbekiston davlat jahon tillari universiteti)", "domain": "student.uzswlu.uz", "short": "uzswlu"},
    {"name": "FarDU (Farg'ona davlat universiteti)", "domain": "student.fardu.uz", "short": "fardu"},
    {"name": "AndDU (Andijon davlat universiteti)", "domain": "student.adu.uz", "short": "adu"},
    {"name": "NamDU (Namangan davlat universiteti)", "domain": "student.namdu.uz", "short": "namdu"},
    {"name": "BuxDU (Buxoro davlat universiteti)", "domain": "student.buxdu.uz", "short": "buxdu"},
    {"name": "QarDU (Qarshi davlat universiteti)", "domain": "student.qarshidu.uz", "short": "qarshidu"},
    {"name": "UrDU (Urganch davlat universiteti)", "domain": "student.urdu.uz", "short": "urdu"},
    {"name": "TerDU (Termiz davlat universiteti)", "domain": "student.tersu.uz", "short": "tersu"},
    {"name": "ToshPFI (Toshkent pediatriya tibbiyot instituti)", "domain": "student.tashpmi.uz", "short": "tashpmi"},
    {"name": "TMA (Toshkent tibbiyot akademiyasi)", "domain": "student.tma.uz", "short": "tma"},
    {"name": "Jizzax Politexnika Instituti (JizPI)", "domain": "student.jizpi.uz", "short": "jizpi"},
    {"name": "Toshkent Kimyo-Texnologiya Instituti (TKTI)", "domain": "student.tkti.uz", "short": "tkti"},
]

def search_university(query: str):
    q = query.strip().lower()
    results = []
    for u in UNIVERSITIES:
        if q in u["name"].lower() or q in u["short"].lower() or q in u["domain"].lower():
            results.append(u)
    return results[:5]
