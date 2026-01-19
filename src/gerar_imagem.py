"""
============================================
ARQUIVO: src/gerar_imagem.py
OBJETIVO: Gerar imagens PNG dos relatórios
============================================

Este arquivo cria imagens bonitas e profissionais
das tabelas de dados usando matplotlib.

Funções principais:
1. formatar_valor(): Formata números para exibição (R$ 1.234,56)
2. gerar_imagem_relatorio(): Cria imagem de uma operação
3. gerar_imagem_resumo(): Cria imagem do resumo geral
4. gerar_todas_imagens(): Gera todas as imagens de uma vez

AJUSTES:
- Fonte aumentada para 12 (relatórios) e 13 (resumo)
- Coluna "#" adicionada no resumo geral (posição/ranking)
- ⭐ NOVO: Largura da coluna "Entregador" ajustada para evitar cortes

============================================
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict
import config

# ============================================
# FUNÇÃO 1: FORMATAR VALOR
# ============================================

def formatar_valor(valor: float) -> str:
    """
    Formata valor numérico para padrão brasileiro
    
    Converte: 1234.56 -> "R$ 1.234,56"
    
    Args:
        valor: Número a ser formatado
    
    Returns:
        String formatada com R$
    
    Exemplo:
        >>> formatar_valor(1234.56)
        'R$ 1.234,56'
    """
    # :,.2f = formato com separador de milhar e 2 casas decimais
    # Exemplo: 1234.56 -> "1,234.56"
    formatado = f"R$ {valor:,.2f}"
    
    # Trocar vírgula por underscore temporário
    # "1,234.56" -> "1_234.56"
    formatado = formatado.replace(',', '_')
    
    # Trocar ponto por vírgula (padrão brasileiro)
    # "1_234.56" -> "1_234,56"
    formatado = formatado.replace('.', ',')
    
    # Trocar underscore por ponto
    # "1_234,56" -> "1.234,56"
    formatado = formatado.replace('_', '.')
    
    return formatado


# ============================================
# FUNÇÃO 2: GERAR IMAGEM DE RELATÓRIO
# ============================================

def gerar_imagem_relatorio(df: pd.DataFrame, operacao: str, periodo: str, 
                           caminho_saida: Path) -> Path:
    """
    Gera imagem PNG de um relatório de operação
    
    Cria uma tabela visual com:
    - Cabeçalho azul
    - Entregadores nas linhas
    - Datas nas colunas
    - Valores formatados
    - Linha de total destacada
    
    Args:
        df: DataFrame pivotado (entregadores x datas)
        operacao: Nome da operação (ex: "GRANDE BELÉM")
        periodo: String do período (ex: "05/01/2026 a 07/01/2026")
        caminho_saida: Onde salvar a imagem
    
    Returns:
        Path do arquivo gerado
    """
    print(f"   🖼️  Gerando: {operacao}...", end=" ")
    
    # ========================================
    # CONFIGURAR FIGURA
    # ========================================
    # ⭐ Aumentado de 14 para 16 para mais espaço horizontal
    fig, ax = plt.subplots(figsize=(16, max(8, len(df) * 0.4)))
    
    # Desligar eixos (não queremos gráfico, só tabela)
    ax.axis('tight')
    ax.axis('off')
    
    # ========================================
    # TÍTULO
    # ========================================
    titulo = f"RELATÓRIO - {operacao}\nPeríodo: {periodo}"
    plt.title(titulo, fontsize=16, fontweight='bold', pad=20)
    
    # ========================================
    # PREPARAR DADOS PARA EXIBIÇÃO
    # ========================================
    # Copiar DataFrame para não modificar original
    df_display = df.copy()
    
    # Formatar nomes das colunas (datas)
    colunas_formatadas = []
    for col in df_display.columns:
        if col == 'Total':
            # Manter "Total" como está
            colunas_formatadas.append('Total')
        else:
            # Converter timestamp para string "DD/MM/YYYY"
            try:
                # strftime: converte datetime para string
                data_str = col.strftime('%d/%m/%Y')
                colunas_formatadas.append(data_str)
            except:
                # Se der erro (não é datetime), usar como string
                colunas_formatadas.append(str(col))
    
    # Aplicar novos nomes às colunas
    df_display.columns = colunas_formatadas
    
    # ========================================
    # FORMATAR VALORES
    # ========================================
    # applymap: aplica função a cada célula do DataFrame
    # lambda x: função anônima que recebe valor x
    # isinstance(x, (int, float)): verifica se é número
    df_display = df_display.applymap(
        lambda x: formatar_valor(x) if isinstance(x, (int, float)) else x
    )
    
    # ========================================
    # PREPARAR TABELA FINAL
    # ========================================
    # Resetar índice: transforma entregadores (índice) em coluna
    df_display = df_display.reset_index()
    
    # Renomear primeira coluna para "Entregador"
    # list(...)[1:]: pega todas colunas exceto a primeira
    df_display.columns = ['Entregador'] + list(df_display.columns[1:])
    
    # ========================================
    # CRIAR TABELA VISUAL
    # ========================================
    # ax.table: cria tabela no plot matplotlib
    table = ax.table(
        cellText=df_display.values,      # Dados das células
        colLabels=df_display.columns,    # Nomes das colunas
        cellLoc='center',                 # Alinhamento do texto
        loc='center',                     # Posição da tabela
        bbox=[0, 0, 1, 1]                # Tamanho (x, y, largura, altura)
    )
    
    # ========================================
    # ESTILIZAR TABELA
    # ========================================
    # Desabilitar tamanho automático de fonte
    table.auto_set_font_size(False)
    # Fonte aumentada: 12
    table.set_fontsize(12)
    
    # ⭐ AJUSTAR LARGURAS DAS COLUNAS
    num_colunas = len(df_display.columns)
    
    # Primeira coluna (Entregador): 30% da largura total
    largura_entregador = 0.30
    # Demais colunas: dividem os 70% restantes
    largura_outras = (1 - largura_entregador) / (num_colunas - 1)
    
    # Aplicar larguras customizadas
    for j in range(num_colunas):
        for i in range(len(df_display) + 1):  # +1 para incluir cabeçalho
            cell = table[(i, j)]
            if j == 0:
                # Primeira coluna: mais larga
                cell.set_width(largura_entregador)
            else:
                # Outras colunas: largura padrão
                cell.set_width(largura_outras)
    
    # Ajustar altura das células
    table.scale(1, 2)
    
    # ========================================
    # COLORIR CÉLULAS
    # ========================================
    # get_celld(): retorna dicionário de células
    # Formato: {(linha, coluna): célula}
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            # ===== LINHA 0: CABEÇALHO =====
            # weight='bold': texto em negrito
            # color='white': texto branco
            cell.set_text_props(weight='bold', color='white')
            # Fundo azul
            cell.set_facecolor('#4472C4')
            
        elif i == len(df_display):
            # ===== ÚLTIMA LINHA: TOTAL =====
            cell.set_text_props(weight='bold')
            # Fundo cinza claro
            cell.set_facecolor('#E7E6E6')
            
        else:
            # ===== LINHAS NORMAIS =====
            if j == 0:
                # ⭐ Primeira coluna (nomes): alinhar à esquerda + padding
                cell.set_text_props(ha='left')  # horizontal alignment = left
                cell.set_facecolor('#F2F2F2')
                cell.PAD = 0.05  # Padding à esquerda
            else:
                # Outras colunas: fundo branco, centralizado
                cell.set_facecolor('white')
    
    # ========================================
    # SALVAR IMAGEM
    # ========================================
    # tight_layout: ajusta espaçamentos automaticamente
    plt.tight_layout()
    
    # savefig: salva figura como arquivo
    # dpi: qualidade (dots per inch)
    # bbox_inches='tight': remove margens extras
    # facecolor='white': fundo branco
    plt.savefig(
        caminho_saida, 
        dpi=config.DPI, 
        bbox_inches='tight', 
        facecolor='white', 
        edgecolor='none'
    )
    
    # Fechar figura para liberar memória
    plt.close()
    
    print(f"✅")
    
    return caminho_saida


# ============================================
# FUNÇÃO 3: GERAR IMAGEM DE RESUMO
# ============================================

def gerar_imagem_resumo(df_resumo: pd.DataFrame, periodo: str, 
                        caminho_saida: Path) -> Path:
    """
    Gera imagem PNG do resumo geral (todas operações)
    
    Adiciona coluna "#" com posição/ranking
    Similar ao relatório, mas mais simples:
    - 3 colunas: # (posição), Operação, Valor
    - Lista todas as operações
    - Total geral no final
    
    Args:
        df_resumo: DataFrame com resumo
        periodo: String do período
        caminho_saida: Onde salvar
    
    Returns:
        Path do arquivo gerado
    """
    print(f"   🖼️  Gerando: RESUMO GERAL...", end=" ")
    
    # ========================================
    # CONFIGURAR FIGURA
    # ========================================
    fig, ax = plt.subplots(figsize=(10, max(8, len(df_resumo) * 0.4)))
    ax.axis('tight')
    ax.axis('off')
    
    # ========================================
    # TÍTULO
    # ========================================
    titulo = f"RESUMO GERAL - TODAS AS OPERAÇÕES\nPeríodo: {periodo}"
    plt.title(titulo, fontsize=16, fontweight='bold', pad=20)
    
    # ========================================
    # PREPARAR DADOS COM COLUNA DE POSIÇÃO
    # ========================================
    df_display = df_resumo.copy()
    
    # ⭐ ADICIONAR COLUNA DE POSIÇÃO
    # Criar lista de números: 1, 2, 3, ..., (vazio para TOTAL)
    posicoes = []
    for idx in range(len(df_display)):
        # Se for última linha (TOTAL), deixa vazio
        if df_display.iloc[idx]['Nome da Região'] == 'TOTAL':
            posicoes.append('')
        else:
            # Caso contrário, adiciona número sequencial
            posicoes.append(str(idx + 1))
    
    # Inserir coluna "#" no início
    # insert(posição, nome_coluna, valores)
    df_display.insert(0, '#', posicoes)
    
    # Agora df_display tem 3 colunas:
    # #  |  Nome da Região  |  Sum of Fatur.(R$)
    # 1  |  GRANDE SÃO PAULO  |  R$ 76.721,39
    # 2  |  GRANDE BELÉM      |  R$ 7.690,50
    # ...
    #    |  TOTAL            |  R$ 254.046,44
    
    # ========================================
    # FORMATAR VALORES
    # ========================================
    # Formatar coluna de valores (índice 2)
    df_display['Sum of Fatur.(R$)'] = df_display['Sum of Fatur.(R$)'].apply(
        lambda x: formatar_valor(x) if isinstance(x, (int, float)) else x
    )
    
    # ========================================
    # CRIAR TABELA
    # ========================================
    table = ax.table(
        cellText=df_display.values,
        colLabels=df_display.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )
    
    # ========================================
    # ESTILIZAR
    # ========================================
    table.auto_set_font_size(False)
    # Fonte aumentada: 13
    table.set_fontsize(13)
    table.scale(1, 2.5)
    
    # Colorir células
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            # ===== CABEÇALHO =====
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#4472C4')
            
        elif i == len(df_display):
            # ===== LINHA TOTAL =====
            cell.set_text_props(weight='bold', fontsize=14)  # Ainda maior
            cell.set_facecolor('#E7E6E6')
            
        else:
            # ===== DADOS NORMAIS =====
            if j == 0:
                # Coluna "#": fundo azul claro
                cell.set_facecolor('#D9E2F3')
                cell.set_text_props(weight='bold')
            elif j == 1:
                # Coluna "Nome da Região": fundo cinza
                cell.set_facecolor('#F2F2F2')
            else:
                # Coluna "Valor": fundo branco
                cell.set_facecolor('white')
    
    # ========================================
    # SALVAR
    # ========================================
    plt.tight_layout()
    plt.savefig(
        caminho_saida, 
        dpi=config.DPI, 
        bbox_inches='tight',
        facecolor='white', 
        edgecolor='none'
    )
    plt.close()
    
    print(f"✅")
    
    return caminho_saida


# ============================================
# FUNÇÃO 4: GERAR TODAS AS IMAGENS
# ============================================

def gerar_todas_imagens(relatorios: Dict[str, pd.DataFrame], 
                        df_resumo: pd.DataFrame, 
                        periodo: str) -> Dict[str, Path]:
    """
    Gera todas as imagens de uma vez
    
    Para cada operação:
    - Gera imagem individual
    - Nome do arquivo: operacao_formatada.png
    
    Também gera:
    - resumo_geral.png (com coluna de posição)
    
    Args:
        relatorios: Dicionário {operacao: DataFrame}
        df_resumo: DataFrame do resumo
        periodo: String do período
    
    Returns:
        Dicionário {operacao: caminho_imagem}
    """
    print("\n🖼️  Gerando imagens dos relatórios...")
    
    # Dicionário para armazenar caminhos
    caminhos = {}
    
    # ========================================
    # GERAR IMAGEM PARA CADA OPERAÇÃO
    # ========================================
    # Ordenar operações alfabeticamente
    for operacao in sorted(relatorios.keys()):
        df = relatorios[operacao]
        
        # Criar nome do arquivo
        # Exemplo: "GRANDE BELÉM" -> "grande_belem.png"
        # lower(): minúsculo
        # replace(' ', '_'): espaços viram underscores
        # replace('ã', 'a'): remove acentos (opcional)
        nome_arquivo = (
            operacao
            .lower()
            .replace(' ', '_')
            .replace('ã', 'a')
            .replace('á', 'a')
            .replace('é', 'e')
            .replace('í', 'i')
            .replace('ó', 'o')
            .replace('ú', 'u')
            + '.png'
        )
        
        # Caminho completo
        caminho = config.RELATORIOS_DIR / nome_arquivo
        
        # Gerar imagem
        gerar_imagem_relatorio(df, operacao, periodo, caminho)
        
        # Guardar caminho
        caminhos[operacao] = caminho
    
    # ========================================
    # GERAR RESUMO GERAL (COM COLUNA #)
    # ========================================
    caminho_resumo = config.RELATORIOS_DIR / 'resumo_geral.png'
    gerar_imagem_resumo(df_resumo, periodo, caminho_resumo)
    caminhos['RESUMO_GERAL'] = caminho_resumo
    
    # ========================================
    # MENSAGEM FINAL
    # ========================================
    print(f"\n✅ {len(caminhos)} imagens geradas!")
    print(f"📁 Localização: {config.RELATORIOS_DIR.absolute()}")
    
    return caminhos


# ============================================
# TESTE (se rodar este arquivo diretamente)
# ============================================

if __name__ == "__main__":
    """
    Código de teste
    """
    print("=== TESTE DO MÓDULO ===\n")
    print("Este módulo deve ser importado, não executado diretamente.")
    print("Execute: python src/main.py")
    print("\n=== FIM DO TESTE ===")

# ============================================
# FIM DO ARQUIVO
# ============================================