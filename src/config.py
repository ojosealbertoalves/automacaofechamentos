"""
============================================
ARQUIVO: src/config.py
OBJETIVO: Configurações centralizadas do projeto
============================================

Este arquivo contém TODAS as configurações:
- Caminhos de pastas e arquivos
- Nomes das colunas da planilha
- Filtros a serem aplicados
- Configurações de imagem

VANTAGEM: Se mudar algo (ex: nome de coluna), 
          muda só aqui, não em todo o código!
============================================
"""

from pathlib import Path

# ============================================
# DIRETÓRIOS DO PROJETO
# ============================================

# BASE_DIR: Pasta raiz do projeto (onde está este arquivo)
# __file__ = caminho deste arquivo (config.py)
# .parent = volta uma pasta (de src/ para raiz)
BASE_DIR = Path(__file__).parent.parent

# DATA_DIR: Pasta onde fica a planilha Excel
DATA_DIR = BASE_DIR / "data"

# RELATORIOS_DIR: Pasta onde salvamos as imagens geradas
RELATORIOS_DIR = BASE_DIR / "relatorios"

# Garante que a pasta de relatórios existe
# exist_ok=True: não dá erro se já existir
RELATORIOS_DIR.mkdir(exist_ok=True)

# ============================================
# ARQUIVOS
# ============================================

# Caminho completo da planilha Excel
CAMINHO_PLANILHA = DATA_DIR / "banco_dados.xlsx"

# ============================================
# NOMES DAS ABAS DA PLANILHA
# ============================================

# Aba com os pedidos/transações
ABA_TRANSACOES = "relatório_transacoes"

# Aba com dados dos gerentes (nome, whatsapp, operação)
ABA_GERENTES = "contatos_gerentes"

# Aba com lista de entregadores para excluir
ABA_EXCLUSOES = "excluir_entregadores"

# ============================================
# NOMES DAS COLUNAS DA PLANILHA
# ============================================

# Coluna que tem a data da entrega (usada para filtrar período)
COLUNA_DATA_ENTREGA = "DATA ENTREGA"

# Coluna que identifica a operação (ex: GRANDE BELÉM)
COLUNA_OPERACAO = "OPERAÇÃO"

# Coluna com o nome do entregador
COLUNA_ENTREGADOR = "Entregador"

# Coluna com o valor faturado (R$)
COLUNA_VALOR = "Fatur.(R$)"

# Coluna com a forma de pagamento (Dinheiro, PIX, Cartão, etc)
COLUNA_PAGAMENTO = "Pgto."

# Coluna com o nome do operador (usado para fazer match com gerentes)
COLUNA_OPERADOR = "Operador"

# ============================================
# FILTROS
# ============================================

# Filtrar apenas pagamentos em dinheiro
# Vai procurar "dinheiro" no texto (case-insensitive)
FORMA_PAGAMENTO_FILTRO = "dinheiro"

# ============================================
# CONFIGURAÇÕES DE IMAGEM
# ============================================

# Formato da imagem de saída
FORMATO_IMAGEM = "png"

# DPI (dots per inch): Qualidade da imagem
# 300 = Alta qualidade (profissional)
# 150 = Qualidade média
# 72 = Qualidade baixa (tela)
DPI = 300

# ============================================
# DEBUG
# ============================================

# Se True: mostra mais informações de erro
# Se False: mostra menos detalhes
DEBUG = True

# ============================================
# FIM DO ARQUIVO DE CONFIGURAÇÃO
# ============================================