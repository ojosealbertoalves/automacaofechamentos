"""
============================================
ARQUIVO: src/gerar_planilhas.py
OBJETIVO: Gerar planilhas Excel filtradas por operação
============================================

Este arquivo cria planilhas Excel com dados filtrados:
- Por operação específica
- Forma de pagamento: dinheiro
- Período de datas
- Salva em: relatorios/planilhas/

COMO EXECUTAR:
    python src/gerar_planilhas.py

O script pergunta quais operações você quer:
- Digite nomes separados por ";" 
  Exemplo: grande fortaleza;grande natal
- Ou digite "todos" para gerar todas

============================================
"""

from datetime import datetime
import sys
from pathlib import Path
import pandas as pd

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar nossos módulos
import config
import processar_dados


# ============================================
# FUNÇÃO: LIMPAR TELA
# ============================================

def limpar_tela():
    """Limpa a tela do terminal"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


# ============================================
# FUNÇÃO: OBTER DATAS
# ============================================

def obter_datas():
    """
    Solicita datas início e fim do usuário
    
    Returns:
        Tupla (data_inicio, data_fim) em formato string DD/MM/YYYY
    """
    print("\n" + "="*60)
    print("  📅 DEFINIR PERÍODO")
    print("="*60 + "\n")
    
    # Data início
    while True:
        try:
            data_inicio = input("Data início (DD/MM/YYYY): ").strip()
            datetime.strptime(data_inicio, '%d/%m/%Y')
            break
        except ValueError:
            print("❌ Data inválida! Use DD/MM/YYYY (ex: 05/01/2026)")
    
    # Data fim
    while True:
        try:
            data_fim = input("Data fim (DD/MM/YYYY): ").strip()
            datetime.strptime(data_fim, '%d/%m/%Y')
            break
        except ValueError:
            print("❌ Data inválida! Use DD/MM/YYYY")
    
    return data_inicio, data_fim


# ============================================
# FUNÇÃO: OBTER OPERAÇÕES DESEJADAS
# ============================================

def obter_operacoes_desejadas(operacoes_disponiveis):
    """
    Pergunta ao usuário quais operações quer gerar planilhas
    
    Args:
        operacoes_disponiveis: Lista com todas as operações disponíveis
    
    Returns:
        Lista com operações selecionadas
    """
    print("\n" + "="*60)
    print("  🏢 SELECIONAR OPERAÇÕES")
    print("="*60 + "\n")
    
    print("Operações disponíveis:")
    print()
    
    # Mostrar lista numerada
    for idx, operacao in enumerate(sorted(operacoes_disponiveis), 1):
        print(f"   {idx}. {operacao}")
    
    print(f"\n   Total: {len(operacoes_disponiveis)} operações")
    
    print("\n" + "-"*60)
    print("Digite as operações que deseja (opções):")
    print()
    print("  • Separadas por ';'")
    print("    Exemplo: grande fortaleza;grande natal")
    print()
    print("  • Ou digite 'todos' para gerar todas")
    print("-"*60 + "\n")
    
    while True:
        entrada = input("Operações: ").strip()
        
        if not entrada:
            print("❌ Digite pelo menos uma operação ou 'todos'")
            continue
        
        # Se digitou "todos"
        if entrada.lower() == 'todos':
            print(f"\n✅ Todas as {len(operacoes_disponiveis)} operações selecionadas!")
            return list(operacoes_disponiveis)
        
        # Separar por ";"
        # split(';'): divide string
        # strip(): remove espaços extras
        # upper(): converte para maiúsculo (padronizar)
        operacoes_input = [op.strip().upper() for op in entrada.split(';')]
        
        # Validar se operações existem
        operacoes_validas = []
        operacoes_invalidas = []
        
        for op in operacoes_input:
            if op in operacoes_disponiveis:
                operacoes_validas.append(op)
            else:
                operacoes_invalidas.append(op)
        
        # Se tem inválidas, avisar
        if operacoes_invalidas:
            print(f"\n⚠️  Operações não encontradas:")
            for op in operacoes_invalidas:
                print(f"   • {op}")
            print("\nVerifique a lista acima e tente novamente.")
            continue
        
        # Se todas válidas
        if operacoes_validas:
            print(f"\n✅ {len(operacoes_validas)} operação(ões) selecionada(s):")
            for op in operacoes_validas:
                print(f"   • {op}")
            return operacoes_validas


# ============================================
# FUNÇÃO: GERAR PLANILHA DE OPERAÇÃO
# ============================================

def gerar_planilha_operacao(df_filtrado, operacao, data_inicio, data_fim, pasta_saida):
    """
    Gera planilha Excel de uma operação específica
    
    Args:
        df_filtrado: DataFrame já filtrado (dinheiro + período)
        operacao: Nome da operação
        data_inicio: Data início (string)
        data_fim: Data fim (string)
        pasta_saida: Path da pasta onde salvar
    
    Returns:
        Path do arquivo gerado
    """
    # Filtrar apenas esta operação
    df_operacao = df_filtrado[df_filtrado[config.COLUNA_OPERACAO] == operacao].copy()
    
    # Se não tem dados, não gera
    if len(df_operacao) == 0:
        print(f"   ⚠️  {operacao}: Sem dados (pulando)")
        return None
    
    # Ordenar por data
    df_operacao = df_operacao.sort_values(config.COLUNA_DATA_ENTREGA)
    
    # Formatar data para exibição (DD/MM/YYYY)
    df_operacao[config.COLUNA_DATA_ENTREGA] = df_operacao[config.COLUNA_DATA_ENTREGA].dt.strftime('%d/%m/%Y')
    
    # Nome do arquivo
    # Exemplo: "GRANDE FORTALEZA" -> "grande_fortaleza_05-01_a_07-01.xlsx"
    data_inicio_fmt = data_inicio.replace('/', '-')
    data_fim_fmt = data_fim.replace('/', '-')
    
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
        + f'_{data_inicio_fmt}_a_{data_fim_fmt}.xlsx'
    )
    
    # Caminho completo
    caminho = pasta_saida / nome_arquivo
    
    # Salvar Excel
    # engine='openpyxl': usa biblioteca openpyxl
    # index=False: não salva índice (números das linhas)
    df_operacao.to_excel(caminho, engine='openpyxl', index=False)
    
    # Mostrar estatística
    total_registros = len(df_operacao)
    total_valor = df_operacao[config.COLUNA_VALOR].sum()
    
    print(f"   ✅ {operacao}: {total_registros} registros | R$ {total_valor:,.2f}")
    
    return caminho


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================

def main():
    """
    Função principal do gerador de planilhas
    
    Fluxo:
    1. Carregar dados
    2. Pedir datas
    3. Filtrar dados
    4. Perguntar quais operações
    5. Gerar planilhas
    """
    
    # Banner
    limpar_tela()
    print("\n" + "="*60)
    print("  📊 GERADOR DE PLANILHAS EXCEL POR OPERAÇÃO")
    print("  💰 Filtro: Pagamentos em DINHEIRO")
    print("="*60 + "\n")
    
    try:
        # ========================================
        # ETAPA 1: CARREGAR DADOS
        # ========================================
        print("📂 ETAPA 1/5: Carregando planilha...")
        print(f"   Arquivo: {config.CAMINHO_PLANILHA.name}")
        print()
        
        # Verificar se existe
        if not config.CAMINHO_PLANILHA.exists():
            print(f"❌ ERRO: Planilha não encontrada!")
            print(f"   Esperado em: {config.CAMINHO_PLANILHA}")
            return
        
        # Carregar
        transacoes, gerentes_df, exclusoes = processar_dados.carregar_planilha()
        
        # ========================================
        # ETAPA 2: OBTER DATAS
        # ========================================
        print("\n📅 ETAPA 2/5: Definindo período...")
        data_inicio, data_fim = obter_datas()
        print(f"\n   ✅ Período: {data_inicio} a {data_fim}")
        
        # ========================================
        # ETAPA 3: FILTRAR DADOS
        # ========================================
        print(f"\n🔍 ETAPA 3/5: Filtrando dados...")
        
        df_filtrado = processar_dados.filtrar_dados(
            transacoes,
            data_inicio,
            data_fim,
            exclusoes
        )
        
        # Verificar se tem dados
        if len(df_filtrado) == 0:
            print("\n❌ Nenhum dado encontrado no período!")
            return
        
        print(f"\n   ✅ Total filtrado: {len(df_filtrado)} registros")
        
        # ========================================
        # ETAPA 4: SELECIONAR OPERAÇÕES
        # ========================================
        print(f"\n🏢 ETAPA 4/5: Selecionando operações...")
        
        # Pegar operações únicas dos dados filtrados
        operacoes_disponiveis = sorted(df_filtrado[config.COLUNA_OPERACAO].unique())
        
        if len(operacoes_disponiveis) == 0:
            print("\n❌ Nenhuma operação encontrada!")
            return
        
        # Perguntar quais quer
        operacoes_selecionadas = obter_operacoes_desejadas(operacoes_disponiveis)
        
        # ========================================
        # ETAPA 5: GERAR PLANILHAS
        # ========================================
        print(f"\n📊 ETAPA 5/5: Gerando planilhas Excel...")
        
        # Criar pasta de saída
        # relatorios/planilhas/
        pasta_planilhas = config.RELATORIOS_DIR / "planilhas"
        pasta_planilhas.mkdir(exist_ok=True)
        
        print(f"\n   Pasta: {pasta_planilhas}")
        print()
        
        # Gerar para cada operação selecionada
        planilhas_geradas = []
        
        for operacao in operacoes_selecionadas:
            caminho = gerar_planilha_operacao(
                df_filtrado,
                operacao,
                data_inicio,
                data_fim,
                pasta_planilhas
            )
            
            if caminho:
                planilhas_geradas.append(caminho)
        
        # ========================================
        # SUCESSO!
        # ========================================
        print("\n" + "="*60)
        print("  ✅ PLANILHAS GERADAS COM SUCESSO!")
        print("="*60)
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   • Operações selecionadas: {len(operacoes_selecionadas)}")
        print(f"   • Planilhas geradas: {len(planilhas_geradas)}")
        
        print(f"\n📁 LOCALIZAÇÃO:")
        print(f"   {pasta_planilhas.absolute()}")
        
        print(f"\n📄 ARQUIVOS:")
        for caminho in planilhas_geradas:
            print(f"   • {caminho.name}")
        
        print("\n" + "="*60 + "\n")
        
    # ========================================
    # TRATAMENTO DE ERROS
    # ========================================
    
    except KeyboardInterrupt:
        print("\n\n❌ Processo cancelado (Ctrl+C)\n")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        
        if config.DEBUG:
            print("\n📋 DETALHES (DEBUG):")
            import traceback
            traceback.print_exc()
        
        sys.exit(1)


# ============================================
# PONTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    main()

# ============================================
# FIM DO ARQUIVO
# ============================================