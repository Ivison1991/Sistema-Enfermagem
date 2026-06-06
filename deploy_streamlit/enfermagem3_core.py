"""
Lógica compartilhada — Sistema SUS educacional (versão web).
"""

from __future__ import annotations

import json
import unicodedata
from collections import Counter
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

PASTA_APP = Path(__file__).resolve().parent
DADOS_FILE = PASTA_APP / "data" / "dados_sus.json"
LOGO_IMET = PASTA_APP / "assets" / "logo_imet.png"
LOGO_PROGRAMA = PASTA_APP / "assets" / "Logo-Programa.png"

DESENVOLVIMENTO = {
    "integrantes": [
        "EMANUELA ALMEIDA DE OLIVEIRA",
        "MARIA ELIZABETE ALVES LOPES",
        "MARIA LUIZA DE LIMA GOMES",
        "MARIA TARCIANE DA SILVA LIMA",
        "TAMIRIS ALICE RAMOS DA SILVA",
    ],
    "turma": "16",
    "instituicao": "IMET",
    "instituicao_completa": "Instituto Moura de Educação e Tecnologia",
    "professor": "Fernando",
}

SENHA_SISTEMA = "240991"

PROFISSAO_FUNCIONARIO = "TECNICO(A) EM ENFERMAGEM"

COREN_FUNCIONARIOS = {
    "EMANUELA ALMEIDA DE OLIVEIRA": "20250141",
    "MARIA LUIZA DE LIMA GOMES": "20210080",
    "MARIA TARCIANE DA SILVA LIMA": "20250211",
    "TAMIRIS ALICE RAMOS DA SILVA": "20250177",
}


def usuario_pode_entrar(nome: str, senha: str) -> bool:
    return nome in DESENVOLVIMENTO["integrantes"] and senha == SENHA_SISTEMA


def info_funcionario(nome: str) -> dict:
    coren = COREN_FUNCIONARIOS.get(nome, "")
    return {
        "nome": nome,
        "profissao": PROFISSAO_FUNCIONARIO,
        "coren": coren,
        "coren_rotulo": f"Coren - {coren}" if coren else "Coren - —",
    }


def dados_profissional_cadastro(funcionario_logado: str) -> dict | None:
    if not funcionario_logado or funcionario_logado not in DESENVOLVIMENTO["integrantes"]:
        return None
    info = info_funcionario(funcionario_logado)
    return {
        "funcionario": info["nome"],
        "profissao": info["profissao"],
        "coren": info["coren"],
    }

PROCEDIMENTOS_SIA = [
    "Vacinação",
    "Curativo",
    "Aferição de Pressão Arterial",
    "Administração de Medicamentos",
    "Consulta de Enfermagem",
    "Coleta de Exames",
]

DIAGNOSTICOS_SIH = [
    "Pneumonia",
    "Dengue",
    "Hipertensão",
    "Diabetes",
    "Infecção Urinária",
]

LOCAIS_ATENDIMENTO = [
    "UBS Centro",
    "UBS GAMELEIRA",
    "UBS ROSARIO",
    "HOSPITAL JESUS PEQUENINO",
    "UPA BEZERROS",
    "UPA CARUARU",
]

LABEL_SEXO = {
    "M": "Masculino (M)",
    "F": "Feminino (F)",
    "I": "Indeterminado (I)",
}

SEXOS_VALIDOS = frozenset(LABEL_SEXO.keys())


class DadosSUS:
    def __init__(self):
        self.sia: list[dict] = []
        self.sih: list[dict] = []
        self.carregar()

    def carregar(self):
        if not DADOS_FILE.exists():
            self.sia = []
            self.sih = []
            self.salvar()
            return
        try:
            conteudo = json.loads(DADOS_FILE.read_text(encoding="utf-8"))
            self.sia = list(conteudo.get("sia", []))
            self.sih = list(conteudo.get("sih", []))
        except (json.JSONDecodeError, OSError, TypeError):
            self.sia = []
            self.sih = []
            self.salvar()

    def salvar(self):
        payload = {
            "versao": 1,
            "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "sia": self.sia,
            "sih": self.sih,
        }
        DADOS_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def todos(self) -> list[dict]:
        return self.sia + self.sih


dados = DadosSUS()


def data_hoje() -> str:
    return date.today().strftime("%d/%m/%Y")


def data_hora_agora() -> str:
    agora = datetime.now()
    return agora.strftime("%d/%m/%Y"), agora.strftime("%H:%M:%S")


def parse_data_nascimento(texto: str) -> date | None:
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def calcular_idade(nascimento: date, referencia: date | None = None) -> int:
    referencia = referencia or date.today()
    idade = referencia.year - nascimento.year
    if (referencia.month, referencia.day) < (nascimento.month, nascimento.day):
        idade -= 1
    return idade


def faixa_etaria(idade: int) -> str:
    if idade <= 12:
        return "0 a 12 anos"
    if idade <= 17:
        return "13 a 17 anos"
    if idade <= 39:
        return "18 a 39 anos"
    if idade <= 59:
        return "40 a 59 anos"
    return "60 anos ou mais"


def validar_nascimento(texto: str) -> tuple[bool, str, int, str]:
    if not texto.strip():
        return False, "", 0, "Informe a data de nascimento (DD/MM/AAAA)."
    if len(texto.strip()) != 10:
        return False, "", 0, "Data incompleta. Use DD/MM/AAAA."
    nascimento = parse_data_nascimento(texto)
    if nascimento is None:
        return False, "", 0, "Data de nascimento inválida."
    if nascimento > date.today():
        return False, "", 0, "A data de nascimento não pode ser futura."
    idade = calcular_idade(nascimento)
    return True, nascimento.strftime("%d/%m/%Y"), idade, ""


def validar_campos_base(nome: str, cns: str, sexo: str) -> str | None:
    if not nome.strip():
        return "Informe o nome do paciente."
    if not cns.strip():
        return "Informe o CPF ou CNS."
    if sexo not in SEXOS_VALIDOS:
        return "Selecione o sexo: M, F ou I."
    return None


def ranking_itens(registros: list[dict], campo: str, top: int = 5) -> list[dict]:
    if not registros:
        return []
    return [
        {"pos": pos, "nome": nome, "qtd": qtd}
        for pos, (nome, qtd) in enumerate(
            Counter(r[campo] for r in registros).most_common(top), 1
        )
    ]


def ranking_idades(top: int = 5) -> list[dict]:
    faixas = []
    for registro in dados.todos():
        nascimento = parse_data_nascimento(registro.get("nascimento", ""))
        if nascimento:
            faixas.append(faixa_etaria(calcular_idade(nascimento)))
    if not faixas:
        return []
    return [
        {"pos": pos, "nome": nome, "qtd": qtd}
        for pos, (nome, qtd) in enumerate(Counter(faixas).most_common(top), 1)
    ]


def ranking_sexo(top: int = 5) -> list[dict]:
    registros = [r for r in dados.todos() if r.get("sexo") in SEXOS_VALIDOS]
    if not registros:
        return []
    return [
        {"pos": pos, "nome": LABEL_SEXO[codigo], "qtd": qtd}
        for pos, (codigo, qtd) in enumerate(Counter(r["sexo"] for r in registros).most_common(top), 1)
    ]


def mais_frequente(registros: list[dict], campo: str) -> str:
    if not registros:
        return "—"
    return Counter(r[campo] for r in registros).most_common(1)[0][0]


def total_pacientes_unicos() -> int:
    identificadores = set()
    for registro in dados.todos():
        chave = registro.get("cns", "").strip() or registro.get("nome", "").strip()
        if chave:
            identificadores.add(chave.lower())
    return len(identificadores)


def classificar_tipo_local(nome_local: str) -> str:
    nome = nome_local.upper()
    if "HOSPITAL" in nome or "UPA" in nome:
        return "Hospital"
    return "Unidade de Saude"


def nivel_alerta_epidemiologico(qtd: int) -> dict:
    if qtd >= 10:
        return {
            "nivel": "alerta",
            "rotulo": "ALERTA",
            "icone": "🔴",
            "classe": "alerta-vermelho",
        }
    if qtd >= 5:
        return {
            "nivel": "atencao",
            "rotulo": "ATENCAO",
            "icone": "🟡",
            "classe": "alerta-amarelo",
        }
    return {
        "nivel": "normal",
        "rotulo": "NORMAL",
        "icone": "🟢",
        "classe": "alerta-verde",
    }


def _contagem_por_local_e_evento(
    registros: list[dict], campo_evento: str, origem: str
) -> Counter:
    contagem: Counter = Counter()
    for registro in registros:
        local = registro.get("local", "").strip()
        evento = registro.get(campo_evento, "").strip()
        if local and evento:
            contagem[(local, evento, origem)] += 1
    return contagem


def alertas_epidemiologicos() -> list[dict]:
    """Agrupa SIA (procedimento) e SIH (diagnostico) por local e evento de saude."""
    contagem = _contagem_por_local_e_evento(dados.sia, "procedimento", "SIA/SUS")
    contagem.update(_contagem_por_local_e_evento(dados.sih, "diagnostico", "SIH/SUS"))

    alertas: list[dict] = []
    for (local, evento, origem), qtd in contagem.items():
        info = nivel_alerta_epidemiologico(qtd)
        tipo_local = classificar_tipo_local(local)
        alertas.append(
            {
                "local": local,
                "tipo_local": tipo_local,
                "evento": evento,
                "origem": origem,
                "qtd": qtd,
                **info,
            }
        )

    ordem = {"alerta": 0, "atencao": 1, "normal": 2}
    alertas.sort(key=lambda item: (ordem[item["nivel"]], -item["qtd"], item["local"]))
    return alertas


def alertas_epidemiologicos_ativos() -> list[dict]:
    return [item for item in alertas_epidemiologicos() if item["nivel"] != "normal"]


def ranking_doencas_frequentes(top: int = 10) -> list[dict]:
    return ranking_itens(dados.sih, "diagnostico", top)


def estatisticas_datasus() -> dict:
    alertas = alertas_epidemiologicos()
    alertas_ativos = alertas_epidemiologicos_ativos()
    return {
        "atendimentos": len(dados.sia),
        "internacoes": len(dados.sih),
        "pacientes": total_pacientes_unicos(),
        "alertas_ativos": len(alertas_ativos),
        "proc_top": mais_frequente(dados.sia, "procedimento"),
        "diag_top": mais_frequente(dados.sih, "diagnostico"),
        "rank_proc": ranking_itens(dados.sia, "procedimento"),
        "rank_diag": ranking_itens(dados.sih, "diagnostico"),
        "rank_doencas": ranking_doencas_frequentes(),
        "alertas_epi": alertas_ativos,
        "rank_idade": ranking_idades(),
        "rank_sexo": ranking_sexo(),
        "rank_local": ranking_itens(
            [r for r in dados.todos() if r.get("local")], "local"
        ),
    }


def salvar_sia(form: dict, funcionario_logado: str = "") -> tuple[bool, str, dict | None]:
    erro = validar_campos_base(form.get("nome", ""), form.get("cns", ""), form.get("sexo", ""))
    if erro:
        return False, erro, None
    profissional = dados_profissional_cadastro(funcionario_logado)
    if not profissional:
        return False, "Sessao invalida. Faca login novamente.", None
    ok, nascimento, idade, msg = validar_nascimento(form.get("nascimento", ""))
    if not ok:
        return False, msg, None

    protocolo = f"SIA-{len(dados.sia) + 1:03d}"
    registro = {
        "protocolo": protocolo,
        "nome": form["nome"].strip(),
        "cns": form["cns"].strip(),
        "nascimento": nascimento,
        "sexo": form["sexo"],
        "idade": idade,
        "procedimento": form.get("procedimento", PROCEDIMENTOS_SIA[0]),
        "local": form.get("local", LOCAIS_ATENDIMENTO[0]),
        "data": data_hoje(),
        **profissional,
    }
    dados.sia.append(registro)
    dados.salvar()
    return True, f"Atendimento {protocolo} registrado.", registro


def salvar_sih(form: dict, funcionario_logado: str = "") -> tuple[bool, str, dict | None]:
    erro = validar_campos_base(form.get("nome", ""), form.get("cns", ""), form.get("sexo", ""))
    if erro:
        return False, erro, None
    profissional = dados_profissional_cadastro(funcionario_logado)
    if not profissional:
        return False, "Sessao invalida. Faca login novamente.", None
    if not form.get("leito", "").strip():
        return False, "Informe o leito da internação.", None
    ok, nascimento, idade, msg = validar_nascimento(form.get("nascimento", ""))
    if not ok:
        return False, msg, None

    protocolo = f"SIH-{len(dados.sih) + 1:03d}"
    registro = {
        "protocolo": protocolo,
        "nome": form["nome"].strip(),
        "cns": form["cns"].strip(),
        "nascimento": nascimento,
        "sexo": form["sexo"],
        "idade": idade,
        "diagnostico": form.get("diagnostico", DIAGNOSTICOS_SIH[0]),
        "local": form.get("local", LOCAIS_ATENDIMENTO[0]),
        "leito": form["leito"].strip(),
        "entrada": data_hoje(),
        **profissional,
    }
    dados.sih.append(registro)
    dados.salvar()
    return True, f"Internação {protocolo} registrada.", registro


def texto_pdf(texto: str) -> str:
    for antigo, novo in (
        ("\u2014", "-"),
        ("\u2013", "-"),
        ("\u00ba", "o."),
        ("\u00aa", "a."),
        ("—", "-"),
        ("º", "o."),
    ):
        texto = texto.replace(antigo, novo)
    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in normalizado if not unicodedata.combining(c))


def buscar_registro_sia(protocolo: str) -> dict | None:
    for registro in dados.sia:
        if registro.get("protocolo") == protocolo:
            return registro
    return None


def buscar_registro_sih(protocolo: str) -> dict | None:
    for registro in dados.sih:
        if registro.get("protocolo") == protocolo:
            return registro
    return None


def excluir_registro_sia(protocolo: str) -> tuple[bool, str]:
    for indice, registro in enumerate(dados.sia):
        if registro.get("protocolo") == protocolo:
            dados.sia.pop(indice)
            dados.salvar()
            return True, f"Registro {protocolo} excluido."
    return False, "Registro nao encontrado."


def excluir_registro_sih(protocolo: str) -> tuple[bool, str]:
    for indice, registro in enumerate(dados.sih):
        if registro.get("protocolo") == protocolo:
            dados.sih.pop(indice)
            dados.salvar()
            return True, f"Registro {protocolo} excluido."
    return False, "Registro nao encontrado."


def _campos_profissional_pdf(registro: dict) -> list[tuple[str, str]]:
    coren = registro.get("coren", "")
    return [
        ("Profissional", registro.get("funcionario", "—")),
        ("Profissao", registro.get("profissao", PROFISSAO_FUNCIONARIO)),
        ("Coren", f"Coren - {coren}" if coren else "Coren - —"),
    ]


def _pdf_linha_campo(pdf: FPDF, rotulo: str, valor: str) -> None:
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(55, 8, texto_pdf(rotulo), ln=False)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8, texto_pdf(valor))


def _altura_logo(caminho: Path, largura: float) -> float:
    from PIL import Image

    with Image.open(caminho) as img:
        return largura * (img.height / img.width)


def _pdf_logos_topo(pdf: FPDF, largura_cada: float = 48, espaco: float = 12) -> None:
    logos: list[Path] = []
    if LOGO_PROGRAMA.exists():
        logos.append(LOGO_PROGRAMA)
    if LOGO_IMET.exists():
        logos.append(LOGO_IMET)
    if not logos:
        return

    altura_max = max(_altura_logo(logo, largura_cada) for logo in logos)
    largura_total = len(logos) * largura_cada + max(0, len(logos) - 1) * espaco
    x_inicio = (pdf.w - largura_total) / 2
    y = pdf.get_y()

    for indice, logo in enumerate(logos):
        x = x_inicio + indice * (largura_cada + espaco)
        pdf.image(str(logo), x=x, y=y, w=largura_cada)

    pdf.set_y(y + altura_max + 10)


def _criar_grafico_barra(dados: list[dict], titulo: str, cor: str = "#1f538d") -> BytesIO:
    """Cria um gráfico de barras e retorna como BytesIO."""
    if not MATPLOTLIB_AVAILABLE or not dados:
        return None
    
    fig, ax = plt.subplots(figsize=(9, 4))
    nomes = [item['nome'][:25] for item in dados]
    valores = [item['qtd'] for item in dados]
    
    bars = ax.barh(nomes, valores, color=cor, edgecolor='black', linewidth=0.5)
    ax.set_xlabel('Quantidade', fontsize=9, fontweight='bold')
    ax.tick_params(axis='y', labelsize=8)
    ax.tick_params(axis='x', labelsize=8)
    ax.invert_yaxis()
    
    for bar, val in zip(bars, valores):
        ax.text(val + 0.1, bar.get_y() + bar.get_height()/2, 
                str(val), va='center', fontsize=8)
    
    plt.tight_layout(pad=1.5)
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def _criar_grafico_pie(dados: list[dict], titulo: str) -> BytesIO:
    """Cria um gráfico de pizza e retorna como BytesIO."""
    if not MATPLOTLIB_AVAILABLE or not dados:
        return None
    
    fig, ax = plt.subplots(figsize=(7, 7))
    nomes = [item['nome'] for item in dados]
    valores = [item['qtd'] for item in dados]
    cores = ['#1f538d', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6']
    
    wedges, texts, autotexts = ax.pie(valores, labels=nomes, autopct='%1.1f%%',
                                       colors=cores[:len(nomes)], startangle=90,
                                       textprops={'fontsize': 10})
    
    plt.tight_layout(pad=1.5)
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def _pdf_rodape_desenvolvimento(pdf: FPDF) -> None:
    if pdf.get_y() > pdf.h - 85:
        pdf.add_page()

    pdf.ln(8)
    pdf.set_fill_color(240, 244, 248)
    pdf.rect(10, pdf.get_y(), pdf.w - 20, 70, 'F')
    pdf.set_y(pdf.get_y() + 5)
    
    _pdf_logos_topo(pdf, largura_cada=35, espaco=15)
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(31, 83, 141)
    pdf.cell(0, 8, texto_pdf("Desenvolvimento do Programa"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, texto_pdf("Equipe de Desenvolvimento:"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    
    for i, nome in enumerate(DESENVOLVIMENTO["integrantes"]):
        pdf.cell(0, 5, texto_pdf(nome), ln=True, align="C")

    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, texto_pdf(f"Turma: {DESENVOLVIMENTO['turma']}"), ln=True, align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(31, 83, 141)
    pdf.cell(0, 7, texto_pdf(DESENVOLVIMENTO["instituicao"]), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 4, texto_pdf(DESENVOLVIMENTO["instituicao_completa"]), align="C")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, texto_pdf(f"Professor: {DESENVOLVIMENTO['professor']}"), ln=True, align="C")


def gerar_pdf_comprovante(registro: dict, sistema: str) -> bytes:
    if FPDF is None:
        raise RuntimeError("Instale fpdf2: pip install fpdf2")

    if sistema == "SIA/SUS":
        titulo = "Comprovante de Atendimento Ambulatorial"
        subtitulo = "SIA/SUS - Sistema de Informacoes Ambulatoriais"
        campos = [
            ("Protocolo", registro["protocolo"]),
            ("Nome", registro["nome"]),
            ("CPF/CNS", registro["cns"]),
            ("Data de nascimento", registro["nascimento"]),
            ("Sexo", LABEL_SEXO.get(registro.get("sexo", ""), registro.get("sexo", ""))),
            ("Idade", f"{registro['idade']} anos"),
            ("Procedimento", registro["procedimento"]),
            ("Local do atendimento", registro.get("local", "")),
            ("Data do atendimento", registro.get("data", "")),
        ]
    else:
        titulo = "Comprovante de Internacao Hospitalar"
        subtitulo = "SIH/SUS - Sistema de Informacoes Hospitalares"
        campos = [
            ("Protocolo", registro["protocolo"]),
            ("Nome", registro["nome"]),
            ("CPF/CNS", registro["cns"]),
            ("Data de nascimento", registro["nascimento"]),
            ("Sexo", LABEL_SEXO.get(registro.get("sexo", ""), registro.get("sexo", ""))),
            ("Idade", f"{registro['idade']} anos"),
            ("Diagnostico", registro["diagnostico"]),
            ("Local", registro.get("local", "")),
            ("Leito", registro.get("leito", "")),
            ("Data de entrada", registro.get("entrada", "")),
        ]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    _pdf_logos_topo(pdf)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, texto_pdf(sistema), ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, texto_pdf(titulo), ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 7, texto_pdf(subtitulo), ln=True, align="C")
    pdf.ln(6)

    pdf.set_draw_color(31, 83, 141)
    pdf.set_line_width(0.4)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    for rotulo, valor in campos:
        _pdf_linha_campo(pdf, rotulo, str(valor))
        pdf.ln(1)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, texto_pdf("Profissional responsavel pelo cadastro"), ln=True)
    pdf.ln(2)
    for rotulo, valor in _campos_profissional_pdf(registro):
        _pdf_linha_campo(pdf, rotulo, str(valor))
        pdf.ln(1)

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(
        0,
        6,
        texto_pdf(f"Documento gerado em {data_hoje()}"),
        ln=True,
        align="C",
    )

    _pdf_rodape_desenvolvimento(pdf)

    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


def gerar_pdf_datasus() -> bytes:
    if FPDF is None:
        raise RuntimeError("Instale fpdf2: pip install fpdf2")

    stats = estatisticas_datasus()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header com logos
    _pdf_logos_topo(pdf, largura_cada=40, espaco=15)
    pdf.ln(5)

    # Título principal com cor
    pdf.set_fill_color(31, 83, 141)
    pdf.rect(10, pdf.get_y(), pdf.w - 20, 12, 'F')
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, texto_pdf("DATASUS - Painel de Indicadores"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Informações gerais
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, texto_pdf("Dashboard - versao web local (Enfermagem3)."), align="C")
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, texto_pdf(f"Gerado em: {data_hoje()}"), ln=True, align="C")
    pdf.ln(5)

    # Indicadores principais em boxes coloridos
    pdf.set_fill_color(240, 244, 248)
    pdf.rect(10, pdf.get_y(), pdf.w - 20, 35, 'F')
    pdf.set_y(pdf.get_y() + 3)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 83, 141)
    pdf.cell(0, 7, texto_pdf("Indicadores Principais"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)
    
    indicadores = [
        f"Atendimentos ambulatoriais: {stats['atendimentos']}",
        f"Internacoes hospitalares: {stats['internacoes']}",
        f"Pacientes unicos: {stats['pacientes']}",
        f"Alertas epidemiologicos ativos: {stats['alertas_ativos']}"
    ]
    
    for i, indicador in enumerate(indicadores):
        pdf.cell(0, 6, texto_pdf(indicador), ln=True, align="C")
    pdf.ln(5)

    # Gráficos se matplotlib disponível
    if MATPLOTLIB_AVAILABLE:
        # Gráfico de barras para procedimentos
        if stats["rank_proc"]:
            grafico_proc = _criar_grafico_barra(stats["rank_proc"], "Top Procedimentos", "#1f538d")
            if grafico_proc:
                pdf.ln(5)
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 10, texto_pdf("Top Procedimentos"), ln=True)
                pdf.ln(3)
                y_grafico = pdf.get_y()
                pdf.image(grafico_proc, x=15, y=y_grafico, w=180)
                pdf.set_y(y_grafico + 55)
                pdf.ln(5)
        
        # Gráfico de barras para diagnósticos
        if stats["rank_diag"]:
            grafico_diag = _criar_grafico_barra(stats["rank_diag"], "Top Diagnósticos", "#e74c3c")
            if grafico_diag:
                pdf.ln(5)
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 10, texto_pdf("Top Diagnósticos"), ln=True)
                pdf.ln(3)
                y_grafico = pdf.get_y()
                pdf.image(grafico_diag, x=15, y=y_grafico, w=180)
                pdf.set_y(y_grafico + 55)
                pdf.ln(5)
        
        # Gráfico de pizza para sexo
        if stats["rank_sexo"]:
            grafico_sexo = _criar_grafico_pie(stats["rank_sexo"], "Distribuição por Sexo")
            if grafico_sexo:
                pdf.ln(5)
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 10, texto_pdf("Distribuição por Sexo"), ln=True)
                pdf.ln(3)
                y_grafico = pdf.get_y()
                pdf.image(grafico_sexo, x=40, y=y_grafico, w=130)
                pdf.set_y(y_grafico + 85)
                pdf.ln(5)

    # Alertas Epidemiológicos
    pdf.set_fill_color(255, 243, 224)
    pdf.rect(10, pdf.get_y(), pdf.w - 20, 25, 'F')
    pdf.set_y(pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(211, 84, 0)
    pdf.cell(0, 7, texto_pdf("Alertas Epidemiológicos"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    
    if not stats["alertas_epi"]:
        pdf.cell(0, 6, texto_pdf("Nenhum alerta ativo (5 casos ou mais no mesmo local)."), ln=True, align="C")
    else:
        for item in stats["alertas_epi"]:
            pdf.cell(
                0,
                6,
                texto_pdf(
                    f"{item['rotulo']} - {item['local']} - {item['qtd']} casos de {item['evento']}"
                ),
                ln=True,
                align="C"
            )
    pdf.ln(5)

    # Destaques
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, texto_pdf("Destaques"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, texto_pdf(f"Procedimento mais realizado: {stats['proc_top']}"), ln=True)
    pdf.cell(0, 6, texto_pdf(f"Diagnostico mais frequente: {stats['diag_top']}"), ln=True)
    pdf.ln(5)

    # Rankings textuais
    def secao(titulo: str, itens: list[dict], vazio: str):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(240, 244, 248)
        pdf.cell(0, 7, texto_pdf(titulo), ln=True, fill=True)
        pdf.set_font("Helvetica", "", 10)
        if not itens:
            pdf.cell(0, 6, texto_pdf(vazio), ln=True)
        else:
            for item in itens:
                pdf.cell(
                    0,
                    6,
                    texto_pdf(f"{item['pos']}º  {item['nome']}  ({item['qtd']})"),
                    ln=True,
                )
        pdf.ln(3)

    secao("Doencas mais frequentes", stats["rank_doencas"], "Nenhum diagnostico cadastrado.")
    secao("Rank por Idade (faixas)", stats["rank_idade"], "Sem dados de nascimento.")
    secao("Rank por Local", stats["rank_local"], "Sem dados de local.")

    # Rodapé de desenvolvimento com logos e equipe
    _pdf_rodape_desenvolvimento(pdf)

    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
