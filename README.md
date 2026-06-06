# Sistema SUS - Enfermagem3

Sistema educacional para gestão de informações do SUS (Sistema Único de Saúde), desenvolvido para o curso de Técnico em Enfermagem.

## 📋 Descrição

O Sistema SUS - Enfermagem3 é uma aplicação web que permite:
- Registro de atendimentos ambulatoriais (SIA/SUS)
- Registro de internações hospitalares (SIH/SUS)
- Geração de comprovantes em PDF
- Dashboard com estatísticas e indicadores
- Alertas epidemiológicos
- Relatórios com gráficos

## 👥 Equipe de Desenvolvimento

**Turma 16** - Instituto Moura de Educação e Tecnologia (IMET)

- EMANUELA ALMEIDA DE OLIVEIRA
- MARIA ELIZABETE ALVES LOPES
- MARIA LUIZA DE LIMA GOMES
- MARIA TARCIANE DA SILVA LIMA
- TAMIRIS ALICE RAMOS DA SILVA

**Professor:** Fernando

## 🚀 Como Executar Localmente

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone ou baixe este repositório
2. Navegue até a pasta do projeto:
   ```bash
   cd deploy_streamlit
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Execução

Execute o aplicativo com Streamlit:
```bash
streamlit run app.py
```

O aplicativo abrirá automaticamente no navegador em `http://localhost:8501`

## 🌐 Como Publicar no Streamlit Cloud

### Passo 1: Preparar o Repositório no GitHub

1. Crie um novo repositório no GitHub
2. Faça upload da pasta `deploy_streamlit` inteira para o repositório
3. Certifique-se de que os seguintes arquivos estão incluídos:
   - `app.py`
   - `enfermagem3_core.py`
   - `requirements.txt`
   - `README.md`
   - `assets/` (com as logos)
   - `data/` (com dados_sus.json)

### Passo 2: Publicar no Streamlit Cloud

1. Acesse [https://share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta do GitHub
3. Clique em "New app"
4. Selecione o repositório que você criou
5. Selecione o arquivo principal: `app.py`
6. Clique em "Deploy"

O Streamlit Cloud irá automaticamente:
- Instalar as dependências do `requirements.txt`
- Executar o aplicativo
- Fornecer uma URL pública para acesso

## 📁 Estrutura do Projeto

```
deploy_streamlit/
├── app.py                      # Arquivo principal Streamlit
├── enfermagem3_core.py         # Lógica compartilhada do sistema
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
├── assets/                     # Imagens e logos
│   ├── Logo-Programa.png
│   └── logo_imet.png
└── data/                       # Dados do sistema
    └── dados_sus.json
```

## 📦 Dependências

- **streamlit** - Framework para aplicações web
- **fpdf2** - Geração de PDFs
- **Pillow** - Manipulação de imagens
- **matplotlib** - Geração de gráficos

## 🔐 Credenciais Padrão

**Usuário:** Qualquer nome da equipe de desenvolvimento  
**Senha:** 240991

## 📄 Funcionalidades

### SIA/SUS - Sistema de Informações Ambulatoriais
- Cadastro de atendimentos ambulatoriais
- Registro de procedimentos realizados
- Geração de comprovantes em PDF

### SIH/SUS - Sistema de Informações Hospitalares
- Cadastro de internações hospitalares
- Registro de diagnósticos
- Geração de comprovantes em PDF

### DATASUS - Painel de Indicadores
- Dashboard com estatísticas em tempo real
- Gráficos de procedimentos e diagnósticos
- Alertas epidemiológicos
- Relatórios em PDF com visualizações

## 🎨 Recursos Visuais

- Interface moderna e responsiva
- Logos do programa e da instituição
- Gráficos interativos
- PDFs com design profissional
- Seções coloridas para melhor visualização

## 📝 Notas

- Os dados são armazenados localmente no arquivo `data/dados_sus.json`
- No Streamlit Cloud, os dados são resetados a cada novo deploy (uso educacional)
- Para persistência de dados em produção, considere integrar um banco de dados

## 📧 Suporte

Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento ou o professor responsável.

---

**Desenvolvido com ❤️ pela Turma 16 do IMET**
