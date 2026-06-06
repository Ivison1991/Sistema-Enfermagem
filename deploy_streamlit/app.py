"""
Sistema SUS — Versão Streamlit Cloud (Enfermagem3).
Execute: streamlit run app.py
"""

import streamlit as st
from datetime import date
from pathlib import Path

import enfermagem3_core as core

# Configuração da página
st.set_page_config(
    page_title="SUS - Enfermagem3",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados
core.dados.carregar()

# Estado da sessão
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "aba" not in st.session_state:
    st.session_state.aba = "sia"


def mostrar_login():
    """Mostra a tela de login."""
    st.title("🏥 Sistema SUS - Enfermagem3")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Mostrar logos se existirem
        if core.LOGO_PROGRAMA.exists() and core.LOGO_IMET.exists():
            st.image([str(core.LOGO_PROGRAMA), str(core.LOGO_IMET)], width=150)
        
        st.markdown("### Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            if core.usuario_pode_entrar(usuario, senha):
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
        
        st.markdown("---")
        st.markdown("#### Desenvolvimento")
        st.markdown("**Equipe de Desenvolvimento:**")
        for nome in core.DESENVOLVIMENTO["integrantes"]:
            st.markdown(f"- {nome}")
        st.markdown(f"**Turma:** {core.DESENVOLVIMENTO['turma']}")
        st.markdown(f"**{core.DESENVOLVIMENTO['instituicao']}**")
        st.markdown(f"{core.DESENVOLVIMENTO['instituicao_completa']}")
        st.markdown(f"**Professor:** {core.DESENVOLVIMENTO['professor']}")


def mostrar_logout():
    """Mostra botão de logout na sidebar."""
    if st.sidebar.button("🚪 Sair"):
        st.session_state.usuario = None
        st.rerun()


def mostrar_sidebar():
    """Mostra a sidebar com navegação."""
    mostrar_logout()
    
    st.sidebar.title("🏥 Navegação")
    
    aba = st.sidebar.radio(
        "Selecione uma aba:",
        ["SIA/SUS", "SIH/SUS", "DATASUS"],
        key="aba_selecionada"
    )
    
    if aba == "SIA/SUS":
        st.session_state.aba = "sia"
    elif aba == "SIH/SUS":
        st.session_state.aba = "sih"
    else:
        st.session_state.aba = "datasus"
    
    # Informações do funcionário
    if st.session_state.usuario:
        info = core.info_funcionario(st.session_state.usuario)
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Profissional")
        st.sidebar.markdown(f"**Nome:** {info['nome']}")
        st.sidebar.markdown(f"**Profissão:** {info['profissao']}")
        st.sidebar.markdown(f"**{info['coren_rotulo']}**")


def mostrar_aba_sia():
    """Mostra a aba SIA/SUS."""
    st.header("📋 SIA/SUS - Sistema de Informações Ambulatoriais")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Novo Atendimento")
        with st.form("form_sia"):
            nome = st.text_input("Nome do paciente *")
            cns = st.text_input("CPF/CNS *")
            nascimento = st.text_input("Data de nascimento (DD/MM/AAAA) *")
            sexo = st.selectbox("Sexo *", ["M", "F", "I"], format_func=lambda x: core.LABEL_SEXO[x])
            procedimento = st.selectbox("Procedimento", core.PROCEDIMENTOS_SIA)
            local = st.selectbox("Local de atendimento", core.LOCAIS_ATENDIMENTO)
            
            submitted = st.form_submit_button("Salvar Atendimento")
            abrir_pdf = st.checkbox("Abrir PDF após salvar")
            
            if submitted:
                form_data = {
                    "nome": nome,
                    "cns": cns,
                    "nascimento": nascimento,
                    "sexo": sexo,
                    "procedimento": procedimento,
                    "local": local
                }
                
                ok, msg, registro = core.salvar_sia(form_data, st.session_state.usuario)
                if ok:
                    st.success(msg)
                    if abrir_pdf and registro:
                        mostrar_pdf_comprovante(registro, "SIA/SUS")
                else:
                    st.error(msg)
    
    with col2:
        st.subheader("Registros Recentes")
        if core.dados.sia:
            for reg in reversed(core.dados.sia[-5:]):
                with st.expander(f"{reg['protocolo']} - {reg['nome']}"):
                    st.write(f"**Procedimento:** {reg['procedimento']}")
                    st.write(f"**Local:** {reg['local']}")
                    st.write(f"**Data:** {reg['data']}")
                    st.write(f"**Profissional:** {reg['funcionario']}")
                    if st.button(f"PDF {reg['protocolo']}", key=f"pdf_sia_{reg['protocolo']}"):
                        mostrar_pdf_comprovante(registro, "SIA/SUS")
        else:
            st.info("Nenhum registro cadastrado.")


def mostrar_aba_sih():
    """Mostra a aba SIH/SUS."""
    st.header("🏥 SIH/SUS - Sistema de Informações Hospitalares")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Nova Internação")
        with st.form("form_sih"):
            nome = st.text_input("Nome do paciente *")
            cns = st.text_input("CPF/CNS *")
            nascimento = st.text_input("Data de nascimento (DD/MM/AAAA) *")
            sexo = st.selectbox("Sexo *", ["M", "F", "I"], format_func=lambda x: core.LABEL_SEXO[x])
            diagnostico = st.selectbox("Diagnóstico", core.DIAGNOSTICOS_SIH)
            local = st.selectbox("Local", core.LOCAIS_ATENDIMENTO)
            leito = st.text_input("Leito *")
            
            submitted = st.form_submit_button("Salvar Internação")
            abrir_pdf = st.checkbox("Abrir PDF após salvar")
            
            if submitted:
                form_data = {
                    "nome": nome,
                    "cns": cns,
                    "nascimento": nascimento,
                    "sexo": sexo,
                    "diagnostico": diagnostico,
                    "local": local,
                    "leito": leito
                }
                
                ok, msg, registro = core.salvar_sih(form_data, st.session_state.usuario)
                if ok:
                    st.success(msg)
                    if abrir_pdf and registro:
                        mostrar_pdf_comprovante(registro, "SIH/SUS")
                else:
                    st.error(msg)
    
    with col2:
        st.subheader("Registros Recentes")
        if core.dados.sih:
            for reg in reversed(core.dados.sih[-5:]):
                with st.expander(f"{reg['protocolo']} - {reg['nome']}"):
                    st.write(f"**Diagnóstico:** {reg['diagnostico']}")
                    st.write(f"**Local:** {reg['local']}")
                    st.write(f"**Leito:** {reg['leito']}")
                    st.write(f"**Entrada:** {reg['entrada']}")
                    st.write(f"**Profissional:** {reg['funcionario']}")
                    if st.button(f"PDF {reg['protocolo']}", key=f"pdf_sih_{reg['protocolo']}"):
                        mostrar_pdf_comprovante(registro, "SIH/SUS")
        else:
            st.info("Nenhum registro cadastrado.")


def mostrar_aba_datasus():
    """Mostra a aba DATASUS com estatísticas."""
    st.header("📊 DATASUS - Painel de Indicadores")
    
    stats = core.estatisticas_datasus()
    
    # Mostrar logos
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if core.LOGO_PROGRAMA.exists() and core.LOGO_IMET.exists():
            st.image([str(core.LOGO_PROGRAMA), str(core.LOGO_IMET)], width=120)
    
    st.markdown("---")
    
    # Indicadores principais
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Atendimentos", stats['atendimentos'])
    col2.metric("Internações", stats['internacoes'])
    col3.metric("Pacientes Únicos", stats['pacientes'])
    col4.metric("Alertas Ativos", stats['alertas_ativos'])
    
    st.markdown("---")
    
    # Alertas epidemiológicos
    st.subheader("🚨 Alertas Epidemiológicos")
    if stats["alertas_epi"]:
        for alerta in stats["alertas_epi"]:
            cor = "🔴" if alerta["nivel"] == "alerta" else "🟡"
            st.warning(f"{cor} **{alerta['rotulo']}** - {alerta['local']} - {alerta['qtd']} casos de {alerta['evento']}")
    else:
        st.info("Nenhum alerta ativo (5 casos ou mais no mesmo local).")
    
    st.markdown("---")
    
    # Destaques
    col1, col2 = st.columns(2)
    col1.info(f"**Procedimento mais realizado:** {stats['proc_top']}")
    col2.info(f"**Diagnóstico mais frequente:** {stats['diag_top']}")
    
    st.markdown("---")
    
    # Rankings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Top Procedimentos")
        if stats["rank_proc"]:
            for item in stats["rank_proc"]:
                st.write(f"{item['pos']}º {item['nome']} ({item['qtd']})")
        else:
            st.info("Nenhum registro.")
        
        st.subheader("🏥 Top Diagnósticos")
        if stats["rank_diag"]:
            for item in stats["rank_diag"]:
                st.write(f"{item['pos']}º {item['nome']} ({item['qtd']})")
        else:
            st.info("Nenhum registro.")
    
    with col2:
        st.subheader("👥 Distribuição por Sexo")
        if stats["rank_sexo"]:
            for item in stats["rank_sexo"]:
                st.write(f"{item['pos']}º {item['nome']} ({item['qtd']})")
        else:
            st.info("Sem dados.")
        
        st.subheader("📊 Rank por Idade")
        if stats["rank_idade"]:
            for item in stats["rank_idade"]:
                st.write(f"{item['pos']}º {item['nome']} ({item['qtd']})")
        else:
            st.info("Sem dados.")
    
    st.markdown("---")
    
    # Botão para gerar PDF
    if st.button("📄 Gerar PDF Completo"):
        try:
            conteudo = core.gerar_pdf_datasus()
            st.download_button(
                label="Baixar PDF",
                data=conteudo,
                file_name=f"DATASUS_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")
    
    # Rodapé de desenvolvimento
    st.markdown("---")
    st.markdown("### Desenvolvimento do Programa")
    st.markdown("**Equipe de Desenvolvimento:**")
    for nome in core.DESENVOLVIMENTO["integrantes"]:
        st.markdown(f"- {nome}")
    st.markdown(f"**Turma:** {core.DESENVOLVIMENTO['turma']}")
    st.markdown(f"**{core.DESENVOLVIMENTO['instituicao']}**")
    st.markdown(f"{core.DESENVOLVIMENTO['instituicao_completa']}")
    st.markdown(f"**Professor:** {core.DESENVOLVIMENTO['professor']}")


def mostrar_pdf_comprovante(registro: dict, sistema: str):
    """Mostra o PDF do comprovante."""
    try:
        conteudo = core.gerar_pdf_comprovante(registro, sistema)
        st.download_button(
            label=f"Baixar PDF {registro['protocolo']}",
            data=conteudo,
            file_name=f"{registro['protocolo']}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")


def main():
    """Função principal do aplicativo."""
    # Verificar login
    if not st.session_state.usuario:
        mostrar_login()
        return
    
    # Mostrar sidebar
    mostrar_sidebar()
    
    # Mostrar aba selecionada
    if st.session_state.aba == "sia":
        mostrar_aba_sia()
    elif st.session_state.aba == "sih":
        mostrar_aba_sih()
    else:
        mostrar_aba_datasus()


if __name__ == "__main__":
    main()
