"""
Script para criar estrutura completa do projeto
"""
import os
from pathlib import Path

# Diretório base (onde este script está)
BASE_DIR = Path(__file__).parent

print("=" * 60)
print("  CRIANDO ESTRUTURA DO PROJETO")
print("=" * 60)
print()

# 1. Criar pastas
pastas = [
    "src",
    "relatorios",
]

print("📁 Criando pastas...")
for pasta in pastas:
    caminho = BASE_DIR / pasta
    caminho.mkdir(exist_ok=True)
    print(f"   ✅ {pasta}/")

# 2. Criar arquivos vazios
arquivos = [
    "src/__init__.py",
    "src/main.py",
    "src/config.py",
    "src/processar_dados.py",
    "src/gerar_imagem.py",
    "requirements.txt",
    "setup.bat",
    "README.md",
    "INICIO_RAPIDO.md",
    ".gitignore",
    "relatorios/.gitkeep",
]

print("\n📄 Criando arquivos vazios...")
for arquivo in arquivos:
    caminho = BASE_DIR / arquivo
    caminho.parent.mkdir(exist_ok=True)
    caminho.touch()
    print(f"   ✅ {arquivo}")

print("\n" + "=" * 60)
print("  ✅ ESTRUTURA CRIADA COM SUCESSO!")
print("=" * 60)
print()
print("Estrutura final:")
print()
print("AUTOMAÇÃO FECHAMENTOS/")
print("├── src/")
print("│   ├── __init__.py")
print("│   ├── main.py")
print("│   ├── config.py")
print("│   ├── processar_dados.py")
print("│   └── gerar_imagem.py")
print("├── data/")
print("│   └── banco_dados.xlsx  (já existe)")
print("├── relatorios/")
print("├── requirements.txt")
print("├── setup.bat")
print("├── README.md")
print("├── INICIO_RAPIDO.md")
print("└── .gitignore")
print()
print("Próximo passo: Preencher os arquivos com o código!")
print()