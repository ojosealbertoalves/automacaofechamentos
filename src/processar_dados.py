"""
============================================
ARQUIVO: src/processar_dados.py
OBJETIVO: Processar dados da planilha Excel
============================================

Funções principais:
1. carregar_planilha(): Lê as 3 abas do Excel
2. preparar_gerentes(): Organiza dados dos gerentes
3. normalizar_whatsapp(): Padroniza números de telefone
4. filtrar_dados(): Aplica filtros (data, pagamento, exclusões)
5. agrupar_por_operacao(): Agrupa e soma valores
6. gerar_resumo_geral(): Cria resumo de todas operações

============================================
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
import config

# ============================================
# FUNÇÃO 1: CARREGAR PLANILHA
# ============================================

def carregar_planilha() -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Carrega as 3 abas da planilha Excel
    
    Returns:
        Tupla com 3 elementos:
        - DataFrame de transações
        - DataFrame de gerentes
        - Lista de entregadores para excluir
    
    Exemplo:
        transacoes, gerentes, exclusoes = carregar_planilha()
    """
    print("📊 Carregando planilha Excel...")
    
    # Ler aba de transações/pedidos
    # sheet_name: nome da aba a ser lida
    transacoes = pd.read_excel(
        config.CAMINHO_PLANILHA,
        sheet_name=config.ABA_TRANSACOES
    )
    
    # Ler aba de gerentes
    gerentes = pd.read_excel(
        config.CAMINHO_PLANILHA,
        sheet_name=config.ABA_GERENTES
    )
    
    # Ler aba de exclusões
    exclusoes_df = pd.read_excel(
        config.CAMINHO_PLANILHA,
        sheet_name=config.ABA_EXCLUSOES
    )
    
    # Converter DataFrame de exclusões em lista simples
    # iloc[:, 0]: pega primeira coluna (índice 0)
    # tolist(): converte para lista Python
    lista_exclusoes = exclusoes_df.iloc[:, 0].tolist()
    
    # Debug: mostrar quantos registros foram carregados
    print(f"   ✅ {len(transacoes)} transações carregadas")
    print(f"   ✅ {len(gerentes)} gerentes carregados")
    print(f"   ✅ {len(lista_exclusoes)} entregadores para excluir")
    
    return transacoes, gerentes, lista_exclusoes


# ============================================
# FUNÇÃO 2: NORMALIZAR WHATSAPP
# ============================================

def normalizar_whatsapp(numero: str) -> str:
    """
    Normaliza número de WhatsApp para formato padrão: 55DDNNNNNNNNN
    
    Remove espaços, traços, parênteses
    Garante que começa com 55 (código do Brasil)
    
    Exemplos:
        "41 92005-7292" -> "5541920057292"
        "91 8536-3030"  -> "559185363030"
        "5511999999999" -> "5511999999999" (já está ok)
    
    Args:
        numero: Número em qualquer formato
    
    Returns:
        Número normalizado (só dígitos, com 55 no início)
    """
    # Converter para string (caso seja número)
    numero_str = str(numero)
    
    # Remover tudo que não é número
    # filter(str.isdigit, ...): mantém só dígitos
    # ''.join(...): junta tudo numa string
    numeros = ''.join(filter(str.isdigit, numero_str))
    
    # Se não começa com 55, adiciona
    if not numeros.startswith('55'):
        numeros = '55' + numeros
    
    return numeros


# ============================================
# FUNÇÃO 3: PREPARAR GERENTES
# ============================================

def preparar_gerentes(df_gerentes: pd.DataFrame) -> Dict:
    """
    Transforma DataFrame de gerentes em dicionário
    organizado por operador (para busca rápida)
    
    Estrutura do dicionário:
    {
        "Gidalto Curitiba": {
            "nome": "Gidalto Dos santos",
            "operacao": "GRANDE CURITIBA",
            "whatsapp": "5541920057292",
            "whatsapp_original": "41 92005-7292"
        },
        ...
    }
    
    Args:
        df_gerentes: DataFrame com dados dos gerentes
    
    Returns:
        Dicionário indexado por operador
    """
    gerentes_dict = {}
    
    # Iterar por cada linha do DataFrame
    # iterrows(): retorna (índice, linha)
    # _: ignora o índice (não vamos usar)
    for _, row in df_gerentes.iterrows():
        # Pegar valor do operador (chave do dicionário)
        operador = row['operador']
        
        # Criar entrada no dicionário
        gerentes_dict[operador] = {
            'nome': row['NOME DO GERENTE'],
            'operacao': row['OPERAÇÃO'],
            'whatsapp': normalizar_whatsapp(row['WHATSAPP']),
            'whatsapp_original': row['WHATSAPP']  # Guardar formato original também
        }
    
    return gerentes_dict


# ============================================
# FUNÇÃO 4: FILTRAR DADOS
# ============================================

def filtrar_dados(df: pd.DataFrame, data_inicio: str, data_fim: str, 
                  exclusoes: List[str]) -> pd.DataFrame:
    """
    Aplica 4 filtros nos dados:
    1. Forma de pagamento = "dinheiro"
    2. Data dentro do período
    3. Remove entregadores da lista de exclusão
    4. Remove registros com data inválida
    
    Args:
        df: DataFrame com todas as transações
        data_inicio: Data início no formato "DD/MM/YYYY"
        data_fim: Data fim no formato "DD/MM/YYYY"
        exclusoes: Lista de nomes para excluir
    
    Returns:
        DataFrame filtrado
    """
    print(f"\n🔍 Aplicando filtros...")
    print(f"   Período: {data_inicio} até {data_fim}")
    
    # Copiar DataFrame para não modificar o original
    df_filtrado = df.copy()
    total_inicial = len(df_filtrado)
    
    # ========================================
    # FILTRO 1: Forma de Pagamento
    # ========================================
    # str.lower(): converte para minúsculo
    # str.contains('dinheiro'): verifica se contém a palavra
    # na=False: se for NaN, considera False
    df_filtrado = df_filtrado[
        df_filtrado[config.COLUNA_PAGAMENTO]
        .str.lower()
        .str.contains('dinheiro', na=False)
    ]
    print(f"   ✅ Após filtro 'dinheiro': {len(df_filtrado)} registros")
    
    # ========================================
    # FILTRO 2: Converter Datas
    # ========================================
    # pd.to_datetime(): converte string para datetime
    # format='%d/%m/%Y': especifica formato da data
    # errors='coerce': se der erro, vira NaT (Not a Time)
    df_filtrado[config.COLUNA_DATA_ENTREGA] = pd.to_datetime(
        df_filtrado[config.COLUNA_DATA_ENTREGA], 
        format='%d/%m/%Y',
        errors='coerce'
    )
    
    # Remover linhas com data inválida (NaT)
    antes_remover_nat = len(df_filtrado)
    df_filtrado = df_filtrado.dropna(subset=[config.COLUNA_DATA_ENTREGA])
    removidos_nat = antes_remover_nat - len(df_filtrado)
    if removidos_nat > 0:
        print(f"   ⚠️  {removidos_nat} registros com data inválida removidos")
    
    # Converter strings de data do usuário para datetime
    data_inicio_dt = datetime.strptime(data_inicio, '%d/%m/%Y')
    data_fim_dt = datetime.strptime(data_fim, '%d/%m/%Y')
    
    # ========================================
    # FILTRO 3: Período de Datas
    # ========================================
    # Manter apenas registros dentro do período
    df_filtrado = df_filtrado[
        (df_filtrado[config.COLUNA_DATA_ENTREGA] >= data_inicio_dt) &
        (df_filtrado[config.COLUNA_DATA_ENTREGA] <= data_fim_dt)
    ]
    print(f"   ✅ Após filtro de período: {len(df_filtrado)} registros")
    
    # ========================================
    # FILTRO 4: Exclusões
    # ========================================
    # ~: operador NOT (nega a condição)
    # isin(exclusoes): verifica se está na lista
    antes_exclusao = len(df_filtrado)
    df_filtrado = df_filtrado[
        ~df_filtrado[config.COLUNA_ENTREGADOR].isin(exclusoes)
    ]
    excluidos = antes_exclusao - len(df_filtrado)
    print(f"   ✅ Após exclusões: {len(df_filtrado)} registros ({excluidos} excluídos)")
    
    # Debug: mostrar total removido
    total_removido = total_inicial - len(df_filtrado)
    print(f"   📊 Total removido: {total_removido} de {total_inicial} registros")
    
    return df_filtrado


# ============================================
# FUNÇÃO 5: AGRUPAR POR OPERAÇÃO
# ============================================

def agrupar_por_operacao(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Agrupa dados por operação e cria tabelas pivotadas
    
    Para cada operação:
    - Agrupa por entregador e data
    - Soma os valores
    - Cria tabela: entregadores x datas
    - Adiciona coluna de total
    - Adiciona linha de total
    
    Args:
        df: DataFrame filtrado
    
    Returns:
        Dicionário {operacao: DataFrame pivotado}
    
    Exemplo de DataFrame retornado:
                          2026-01-05  2026-01-06  2026-01-07  Total
        João Silva          1000.00     1500.00     2000.00  4500.00
        Maria Costa          500.00      800.00      600.00  1900.00
        TOTAL               1500.00     2300.00     2600.00  6400.00
    """
    print(f"\n📦 Agrupando dados por operação...")
    
    # Dicionário para armazenar resultado
    relatorios = {}
    
    # Pegar lista de operações únicas
    # unique(): retorna array com valores únicos
    operacoes = df[config.COLUNA_OPERACAO].unique()
    
    # Processar cada operação
    for operacao in operacoes:
        # Filtrar dados desta operação
        df_operacao = df[df[config.COLUNA_OPERACAO] == operacao]
        
        # ========================================
        # PASSO 1: Agrupar e Somar
        # ========================================
        # groupby: agrupa por entregador e data
        # [coluna].sum(): soma os valores
        # reset_index(): transforma índices em colunas
        agrupado = df_operacao.groupby(
            [config.COLUNA_ENTREGADOR, config.COLUNA_DATA_ENTREGA]
        )[config.COLUNA_VALOR].sum().reset_index()
        
        # ========================================
        # PASSO 2: Pivotar (entregadores x datas)
        # ========================================
        # pivot_table: reorganiza dados
        # index: o que vai nas linhas (entregadores)
        # columns: o que vai nas colunas (datas)
        # values: os valores (faturamento)
        # aggfunc='sum': se tiver duplicata, soma
        # fill_value=0: preenche vazios com 0
        pivot = agrupado.pivot_table(
            index=config.COLUNA_ENTREGADOR,
            columns=config.COLUNA_DATA_ENTREGA,
            values=config.COLUNA_VALOR,
            aggfunc='sum',
            fill_value=0
        )
        
        # ========================================
        # PASSO 3: Adicionar Coluna Total
        # ========================================
        # sum(axis=1): soma ao longo das colunas (horizontal)
        pivot['Total'] = pivot.sum(axis=1)
        
        # ========================================
        # PASSO 4: Adicionar Linha TOTAL
        # ========================================
        # sum(axis=0): soma ao longo das linhas (vertical)
        # loc['TOTAL']: cria nova linha com nome 'TOTAL'
        pivot.loc['TOTAL'] = pivot.sum(axis=0)
        
        # Guardar no dicionário
        relatorios[operacao] = pivot
        
        # Debug: mostrar total desta operação
        valor_total = pivot.loc['TOTAL', 'Total']
        print(f"   ✅ {operacao}: R$ {valor_total:,.2f}")
    
    return relatorios


# ============================================
# FUNÇÃO 6: GERAR RESUMO GERAL
# ============================================

def gerar_resumo_geral(relatorios: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Cria resumo com total de cada operação
    
    Args:
        relatorios: Dicionário com DataFrames de cada operação
    
    Returns:
        DataFrame com 2 colunas:
        - Nome da Região
        - Sum of Fatur.(R$)
    """
    # Lista para acumular dados
    resumo = []
    
    # Para cada operação, pegar o total
    for operacao, df in relatorios.items():
        # df.loc['TOTAL', 'Total']: valor da célula TOTAL x Total
        total = df.loc['TOTAL', 'Total']
        
        # Adicionar à lista
        resumo.append({
            'Nome da Região': operacao,
            'Sum of Fatur.(R$)': total
        })
    
    # Criar DataFrame do resumo
    df_resumo = pd.DataFrame(resumo)
    
    # Ordenar por valor (maior para menor)
    # ascending=False: ordem decrescente
    df_resumo = df_resumo.sort_values('Sum of Fatur.(R$)', ascending=False)
    
    # ========================================
    # Adicionar Linha de TOTAL GERAL
    # ========================================
    total_geral = df_resumo['Sum of Fatur.(R$)'].sum()
    
    # loc[len(df_resumo)]: adiciona nova linha no final
    df_resumo.loc[len(df_resumo)] = ['TOTAL', total_geral]
    
    return df_resumo


# ============================================
# TESTE (se rodar este arquivo diretamente)
# ============================================

if __name__ == "__main__":
    """
    Código de teste para verificar se funções funcionam
    
    Execute: python src/processar_dados.py
    """
    print("=== TESTE DO MÓDULO ===\n")
    
    # Testar carregamento
    transacoes, gerentes, exclusoes = carregar_planilha()
    gerentes_dict = preparar_gerentes(gerentes)
    
    print(f"\n✅ Total transações: {len(transacoes)}")
    print(f"✅ Total gerentes: {len(gerentes_dict)}")
    print(f"✅ Exemplo gerente: {list(gerentes_dict.values())[0]}")
    
    print("\n=== FIM DO TESTE ===")

# ============================================
# FIM DO ARQUIVO
# ============================================