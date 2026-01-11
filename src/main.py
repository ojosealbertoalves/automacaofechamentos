"""
============================================
ARQUIVO: src/main.py
OBJETIVO: Aplicação principal - Orquestrador
============================================

Este é o arquivo PRINCIPAL do projeto.
Ele coordena todas as etapas:

1. Carregar dados da planilha
2. Solicitar datas do usuário
3. Filtrar e processar dados
4. Agrupar por operação
5. Gerar imagens dos relatórios
6. Mostrar resumo final

COMO EXECUTAR:
    python src/main.py

============================================
"""

from datetime import datetime
import sys
from pathlib import Path

# Adicionar diretório src ao path para imports funcionarem
# Isso permite importar módulos como: import config
sys.path.insert(0, str(Path(__file__).parent))

# Importar nossos módulos
import config
import processar_dados
import gerar_imagem


# ============================================
# FUNÇÃO: LIMPAR TELA
# ============================================

def limpar_tela():
    """
    Limpa a tela do terminal
    
    Windows: usa comando 'cls'
    Linux/Mac: usa comando 'clear'
    """
    import os
    # os.name: retorna 'nt' no Windows, 'posix' no Linux/Mac
    os.system('cls' if os.name == 'nt' else 'clear')


# ============================================
# FUNÇÃO: OBTER DATAS DO USUÁRIO
# ============================================

def obter_datas():
    """
    Solicita datas início e fim do usuário via input
    
    Valida se a data está no formato correto (DD/MM/YYYY)
    Se estiver errada, pede novamente
    
    Returns:
        Tupla com (data_inicio, data_fim)
        Ambas no formato string "DD/MM/YYYY"
    
    Exemplo:
        >>> data_inicio, data_fim = obter_datas()
        Data início (DD/MM/YYYY): 05/01/2026
        Data fim (DD/MM/YYYY): 07/01/2026
    """
    print("\n" + "="*60)
    print("  📅 DEFINIR PERÍODO DO RELATÓRIO")
    print("="*60 + "\n")
    
    # ========================================
    # PEDIR DATA INÍCIO
    # ========================================
    while True:  # Loop infinito até data válida
        try:
            # input: solicita entrada do usuário
            # strip(): remove espaços extras nas pontas
            data_inicio = input("Data início (DD/MM/YYYY): ").strip()
            
            # Tentar converter para validar formato
            # Se der erro, vai para except
            datetime.strptime(data_inicio, '%d/%m/%Y')
            
            # Se chegou aqui, data é válida
            break  # Sai do loop
            
        except ValueError:
            # ValueError: formato inválido
            print("❌ Data inválida! Use o formato DD/MM/YYYY (ex: 05/01/2026)")
            # Volta para o início do loop (pede novamente)
    
    # ========================================
    # PEDIR DATA FIM
    # ========================================
    while True:
        try:
            data_fim = input("Data fim (DD/MM/YYYY): ").strip()
            datetime.strptime(data_fim, '%d/%m/%Y')
            break
        except ValueError:
            print("❌ Data inválida! Use o formato DD/MM/YYYY")
    
    # ========================================
    # VALIDAR QUE DATA FIM >= DATA INÍCIO
    # ========================================
    dt_inicio = datetime.strptime(data_inicio, '%d/%m/%Y')
    dt_fim = datetime.strptime(data_fim, '%d/%m/%Y')
    
    if dt_fim < dt_inicio:
        print("\n⚠️  ATENÇÃO: Data fim é anterior à data início!")
        print(f"   Início: {data_inicio}")
        print(f"   Fim: {data_fim}")
        print("\n   Continuando mesmo assim...\n")
    
    return data_inicio, data_fim


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================

def main():
    """
    Função principal que executa todo o fluxo
    
    Fluxo:
    1. Mostrar banner
    2. Carregar planilha
    3. Pedir datas
    4. Filtrar dados
    5. Agrupar por operação
    6. Gerar resumo
    7. Gerar imagens
    8. Mostrar resultado
    
    Tratamento de erros:
    - KeyboardInterrupt: Ctrl+C (cancela execução)
    - Exception: Qualquer outro erro (mostra mensagem)
    """
    
    # ========================================
    # BANNER INICIAL
    # ========================================
    limpar_tela()
    print("\n" + "="*60)
    print("  🚀 GERADOR DE RELATÓRIOS - VERSÃO MANUAL")
    print("  📊 Gera imagens PNG dos relatórios")
    print("="*60 + "\n")
    
    try:
        # ========================================
        # ETAPA 1: CARREGAR PLANILHA
        # ========================================
        print("📂 ETAPA 1/6: Carregando dados da planilha...")
        print(f"   Arquivo: {config.CAMINHO_PLANILHA.name}")
        print()
        
        # Verificar se arquivo existe
        if not config.CAMINHO_PLANILHA.exists():
            print(f"❌ ERRO: Planilha não encontrada!")
            print(f"   Esperado em: {config.CAMINHO_PLANILHA}")
            print(f"\n   Coloque o arquivo 'banco_dados.xlsx' na pasta 'data/'")
            return  # Sai da função (encerra programa)
        
        # Carregar as 3 abas
        transacoes, gerentes_df, exclusoes = processar_dados.carregar_planilha()
        
        # Preparar dicionário de gerentes
        gerentes_dict = processar_dados.preparar_gerentes(gerentes_df)
        
        # ========================================
        # ETAPA 2: OBTER DATAS
        # ========================================
        print("\n📅 ETAPA 2/6: Definindo período...")
        data_inicio, data_fim = obter_datas()
        
        # Criar string do período para usar nas imagens
        periodo_str = f"{data_inicio} a {data_fim}"
        print(f"\n   ✅ Período definido: {periodo_str}")
        
        # ========================================
        # ETAPA 3: FILTRAR DADOS
        # ========================================
        print(f"\n📊 ETAPA 3/6: Filtrando e processando dados...")
        
        df_filtrado = processar_dados.filtrar_dados(
            transacoes, 
            data_inicio, 
            data_fim, 
            exclusoes
        )
        
        # Verificar se há dados após filtros
        if len(df_filtrado) == 0:
            print("\n❌ NENHUM DADO ENCONTRADO!")
            print("\n   Possíveis causas:")
            print("   • Não há pedidos 'dinheiro' no período")
            print("   • Todas as datas foram filtradas")
            print("   • Todos os entregadores foram excluídos")
            print("\n   Tente outro período ou verifique os filtros.")
            return
        
        print(f"\n   ✅ Total de registros após filtros: {len(df_filtrado)}")
        
        # ========================================
        # ETAPA 4: AGRUPAR POR OPERAÇÃO
        # ========================================
        print(f"\n📦 ETAPA 4/6: Agrupando por operação...")
        
        relatorios = processar_dados.agrupar_por_operacao(df_filtrado)
        
        # Verificar se gerou relatórios
        if len(relatorios) == 0:
            print("\n❌ NENHUM RELATÓRIO GERADO!")
            print("   Verifique se há dados válidos na planilha.")
            return
        
        print(f"\n   ✅ Total de operações: {len(relatorios)}")
        
        # ========================================
        # ETAPA 5: GERAR RESUMO GERAL
        # ========================================
        print(f"\n📋 ETAPA 5/6: Gerando resumo geral...")
        
        df_resumo = processar_dados.gerar_resumo_geral(relatorios)
        
        # Calcular total geral
        # iloc[-1]: última linha (TOTAL)
        # ['Sum of Fatur.(R$)']: coluna do valor
        total_geral = df_resumo.iloc[-1]['Sum of Fatur.(R$)']
        
        print(f"   ✅ Resumo gerado")
        print(f"   💰 Valor total geral: R$ {total_geral:,.2f}")
        
        # ========================================
        # ETAPA 6: GERAR IMAGENS
        # ========================================
        print(f"\n🖼️  ETAPA 6/6: Gerando imagens...")
        
        caminhos_imagens = gerar_imagem.gerar_todas_imagens(
            relatorios,
            df_resumo,
            periodo_str
        )
        
        # ========================================
        # SUCESSO! MOSTRAR RESUMO FINAL
        # ========================================
        print("\n" + "="*60)
        print("  ✅ RELATÓRIOS GERADOS COM SUCESSO!")
        print("="*60)
        
        # Mostrar estatísticas
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   • Total de operações: {len(relatorios)}")
        print(f"   • Total de imagens: {len(caminhos_imagens)}")
        print(f"   • Valor total geral: R$ {total_geral:,.2f}")
        
        # Mostrar localização dos arquivos
        print(f"\n📁 LOCALIZAÇÃO DOS ARQUIVOS:")
        print(f"   {config.RELATORIOS_DIR.absolute()}")
        
        # Listar arquivos gerados
        print(f"\n📄 ARQUIVOS GERADOS:")
        for operacao in sorted(caminhos_imagens.keys()):
            caminho = caminhos_imagens[operacao]
            # Mostrar apenas nome do arquivo (não caminho completo)
            print(f"   • {caminho.name}")
        
        # ========================================
        # PRÓXIMOS PASSOS
        # ========================================
        print(f"\n📝 PRÓXIMOS PASSOS:")
        print(f"   1. Abra a pasta: {config.RELATORIOS_DIR}")
        print(f"   2. Envie cada imagem para o gerente correspondente")
        print(f"   3. Use WhatsApp para enviar manualmente")
        
        # Mostrar exemplo de mensagem
        print(f"\n💬 EXEMPLO DE MENSAGEM:")
        # Pegar primeira operação como exemplo
        primeira_operacao = sorted(relatorios.keys())[0]
        if primeira_operacao in gerentes_dict:
            gerente_exemplo = gerentes_dict[primeira_operacao]
            valor_exemplo = relatorios[primeira_operacao].loc['TOTAL', 'Total']
            
            print(f"   ---")
            print(f"   Olá, {gerente_exemplo['nome']}!")
            print(f"   ")
            print(f"   Segue o relatório da operação {primeira_operacao}")
            print(f"   referente ao período de {periodo_str}.")
            print(f"   ")
            valor_fmt = f"{valor_exemplo:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
            print(f"   Valor total para devolução: R$ {valor_fmt}")
            print(f"   ")
            print(f"   Por favor, confirme o recebimento.")
            print(f"   ---")
        
        print("\n" + "="*60 + "\n")
        
    # ========================================
    # TRATAMENTO DE ERROS
    # ========================================
    
    except KeyboardInterrupt:
        # Usuário apertou Ctrl+C
        print("\n\n❌ Processo cancelado pelo usuário (Ctrl+C)")
        print("   Nenhum arquivo foi gerado.\n")
        sys.exit(0)  # Encerra com código 0 (normal)
        
    except FileNotFoundError as e:
        # Arquivo não encontrado
        print(f"\n❌ ERRO: Arquivo não encontrado!")
        print(f"   Detalhes: {e}")
        print(f"\n   Verifique se a planilha está em: {config.DATA_DIR}")
        if config.DEBUG:
            import traceback
            traceback.print_exc()
        sys.exit(1)  # Encerra com código 1 (erro)
        
    except PermissionError as e:
        # Sem permissão (arquivo aberto, por exemplo)
        print(f"\n❌ ERRO: Sem permissão para acessar arquivo!")
        print(f"   Detalhes: {e}")
        print(f"\n   Possíveis causas:")
        print(f"   • Planilha está aberta no Excel")
        print(f"   • Sem permissão para ler/escrever")
        print(f"\n   Feche a planilha e tente novamente.")
        if config.DEBUG:
            import traceback
            traceback.print_exc()
        sys.exit(1)
        
    except Exception as e:
        # Qualquer outro erro
        print(f"\n❌ ERRO INESPERADO!")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {e}")
        
        # Se DEBUG=True, mostrar stack trace completo
        if config.DEBUG:
            print(f"\n📋 DETALHES DO ERRO (DEBUG):")
            import traceback
            traceback.print_exc()
        
        print(f"\n   Se o erro persistir, verifique:")
        print(f"   • Planilha está no formato correto")
        print(f"   • Todas as abas existem")
        print(f"   • Nomes das colunas estão corretos")
        
        sys.exit(1)


# ============================================
# PONTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    """
    Este bloco só executa se o arquivo for rodado diretamente
    
    Se importar (import main), não executa
    Se rodar (python src/main.py), executa
    """
    main()

# ============================================
# FIM DO ARQUIVO PRINCIPAL
# ============================================