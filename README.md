# 🎨 RO Pallet Editor

**Editor de Paletas para Ragnarok Online** - Uma ferramenta visual para criar variações de cores em sprites do jogo Ragnarok Online.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
  - [Carregando um Sprite](#1-carregando-um-sprite)
  - [Selecionando Cores](#2-selecionando-cores)
  - [Criando Grupos](#3-criando-grupos)
  - [Configurando a Geração](#4-configurando-a-geração)
  - [Gerando Paletas](#5-gerando-paletas)
  - [Modo Preview](#6-modo-preview)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Formatos Suportados](#-formatos-suportados)
- [Dicas e Truques](#-dicas-e-truques)
- [Solução de Problemas](#-solução-de-problemas)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

O **RO Pallet Editor** é uma ferramenta desenvolvida para facilitar a criação de variações de paletas de cores para sprites do Ragnarok Online. Com esta ferramenta, você pode:

- Visualizar sprites (.spr) com suas paletas originais
- Selecionar grupos de cores específicos (roupas, cabelo, acessórios, etc.)
- Gerar automaticamente centenas de variações de cores únicas
- Pré-visualizar as paletas antes de exportar
- Restringir a gama de cores geradas (apenas azuis, vermelhos, etc.)

Ideal para **desenvolvedores de servidores privados**, **designers de customização** e **entusiastas de modding** do Ragnarok Online.

---

## ✨ Funcionalidades

### 🖼️ Visualização de Sprites
- Carregamento de arquivos `.spr` (Sprite do RO)
- Visualização de todos os frames do sprite
- Navegação entre frames com botões ◀ ▶
- Preview em tempo real das alterações

### 🎨 Seleção Inteligente de Cores
- **Grid de paleta 16x16** mostrando todas as 256 cores
- **Seleção por clique e arraste** no grid de paleta
- **Clique no sprite** para selecionar automaticamente a faixa de 8 cores correspondente
- Seleção múltipla de índices de cores

### 📁 Gerenciamento de Grupos
- Crie grupos nomeados (ex: "Roupas", "Cabelo", "Armadura")
- Cada grupo pode ter configurações independentes
- Fácil remoção e edição de grupos

### ⚙️ Configurações de Geração
- **Faixa de Cores**: Escolha cor inicial e final usando seletores visuais
  - Cores iguais = espectro completo (360 variações únicas)
  - Cores diferentes = apenas variações entre as duas cores
- **Saturação**: Ajuste a intensidade das cores (-1.0 a +1.0)
- **Brilho**: Ajuste a luminosidade das cores (-1.0 a +1.0)
- **Quantidade**: Gere de 1 até 1000+ paletas únicas

### 🔄 Modo Colorir
- Modo especial para recolorir áreas brancas/cinzas
- Define cor alvo e saturação específica
- Ideal para sprites com áreas neutras

### 👁️ Modo Preview
- **Janela separada** para visualização
- Carregue uma pasta com arquivos `.pal`
- Navegue entre paletas com ◀ ▶
- Veja o resultado aplicado ao sprite em tempo real

---

## 📦 Requisitos

### Sistema Operacional
- **Windows 10** ou superior (recomendado)
- Windows 7/8 (compatível)

### Python
O projeto requer **Python 3.8 ou superior**.

#### Verificando se o Python está instalado

Abra o **Prompt de Comando** (cmd) ou **PowerShell** e digite:

```bash
python --version
```

Se aparecer algo como `Python 3.12.0`, você já tem o Python instalado. Caso contrário, siga as instruções abaixo.

#### Instalando o Python

1. Acesse o site oficial: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Clique no botão **"Download Python 3.x.x"** (versão mais recente)
3. Execute o instalador baixado
4. **IMPORTANTE**: Marque a opção ✅ **"Add Python to PATH"** antes de clicar em "Install Now"
5. Clique em **"Install Now"**
6. Aguarde a instalação completar
7. Reinicie o computador (recomendado)

### Bibliotecas Python

O projeto utiliza as seguintes bibliotecas:

| Biblioteca | Versão | Descrição |
|------------|--------|-----------|
| customtkinter | >= 5.0 | Interface gráfica moderna |
| Pillow | >= 9.0 | Manipulação de imagens |

---

## 🚀 Instalação

### Passo 1: Baixar o Projeto

**Opção A - Via Git (recomendado):**
```bash
git clone https://github.com/seu-usuario/palleteditor.git
cd palleteditor
```

**Opção B - Download ZIP:**
1. Clique no botão verde **"Code"** no GitHub
2. Selecione **"Download ZIP"**
3. Extraia o arquivo para uma pasta de sua preferência

### Passo 2: Instalar Dependências

Abra o **Prompt de Comando** ou **PowerShell** na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

Ou instale manualmente:

```bash
pip install customtkinter pillow
```

### Passo 3: Executar o Programa

```bash
python main.py
```

O programa abrirá uma janela com a interface do RO Pallet Editor.

---

## 📖 Como Usar

### 1. Carregando um Sprite

1. Clique no botão **"Carregar SPR"** no canto superior esquerdo
2. Navegue até o arquivo `.spr` desejado
3. Selecione o arquivo e clique em **"Abrir"**

O sprite será carregado e você verá:
- A **paleta de 256 cores** no grid à esquerda
- O **preview do sprite** à direita
- Os **controles de frame** (◀ ▶) para navegar entre frames

### 2. Selecionando Cores

Existem **duas formas** de selecionar cores:

#### Método 1: Grid de Paleta
- **Clique** em uma cor para selecioná-la/desselecioná-la
- **Clique e arraste** para selecionar múltiplas cores
- Cores selecionadas ficam destacadas em **verde**

#### Método 2: Clique no Sprite (Recomendado)
- **Clique em qualquer parte do sprite** na área de preview
- O programa automaticamente seleciona a **faixa de 8 cores** (ramp) correspondente
- Isso facilita selecionar grupos como "toda a roupa" ou "todo o cabelo"

### 3. Criando Grupos

1. Selecione as cores desejadas (usando os métodos acima)
2. Clique no botão **"Criar Grupo da Seleção"**
3. Digite um nome para o grupo (ex: "Roupas", "Cabelo")
4. Clique em **OK**

O grupo aparecerá na lista de **Grupos de Cores** no canto superior esquerdo.

### 4. Configurando a Geração

Com um grupo selecionado, você verá as **Configurações do Grupo**:

#### 🎨 Cor (Visualização)
- Slider para visualizar diferentes cores no preview
- Apenas para visualização, não afeta a geração

#### 🌈 Faixa de Cores (Geração)
- **De**: Cor inicial do espectro
- **Até**: Cor final do espectro
- Clique nos botões coloridos para abrir o **seletor de cor**

**Exemplos:**
| De | Até | Resultado |
|----|-----|-----------|
| Vermelho | Vermelho | Espectro completo (todas as cores) |
| Azul | Verde | Apenas tons de azul a verde |
| Amarelo | Laranja | Apenas tons quentes |

#### 💧 Saturação
- **-1.0**: Cores desaturadas (cinza)
- **0**: Sem alteração
- **+1.0**: Cores mais vibrantes

#### ☀️ Brilho
- **-1.0**: Cores mais escuras
- **0**: Sem alteração
- **+1.0**: Cores mais claras

#### Quantidade
- Digite o número de paletas a gerar (1-1000+)
- Cada paleta terá uma cor única dentro do espectro escolhido

### 5. Gerando Paletas

1. Configure as opções desejadas
2. Clique no botão **"Gerar Paletas"** (laranja)
3. Selecione a **pasta de destino** onde os arquivos serão salvos
4. Aguarde a geração completar

**Arquivos gerados:**
- `NomeDoSprite_NomeDoGrupo_0.pal`
- `NomeDoSprite_NomeDoGrupo_1.pal`
- `NomeDoSprite_NomeDoGrupo_2.pal`
- ... (até a quantidade especificada)
- `NomeDoSprite_NomeDoGrupo_X.png` (preview de cada paleta)

### 6. Modo Preview

O **Modo Preview** permite visualizar paletas geradas aplicadas ao sprite:

1. Clique no botão **"🎨 Modo Preview"** (laranja)
2. Uma nova janela será aberta
3. Clique em **"📁 Carregar SPR"** para selecionar um sprite
4. Clique em **"📂 Carregar Pasta de Paletas"** para selecionar a pasta com os `.pal`
5. Use os botões **◀ ▶** para navegar:
   - **Paleta**: Alterna entre os arquivos de paleta
   - **Frame**: Alterna entre os frames do sprite

---

## 📂 Estrutura do Projeto

```
palleteditor/
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências do projeto
├── README.md              # Este arquivo
├── .gitignore             # Arquivos ignorados pelo Git
├── assets/                # Recursos (ícones, imagens)
└── src/
    ├── core/              # Lógica de negócio
    │   ├── color_math.py  # Funções de manipulação de cores (HSV)
    │   ├── generator.py   # Gerador de paletas em lote
    │   ├── pal_handler.py # Leitura/escrita de arquivos .pal
    │   ├── logic/
    │   │   └── state.py   # Estado do projeto (grupos, paletas)
    │   └── parsers/
    │       ├── spr.py     # Parser de arquivos .spr
    │       └── act.py     # Parser de arquivos .act
    └── ui/                # Interface gráfica
        ├── main_window.py    # Janela principal
        ├── preview.py        # Componente de preview de sprite
        ├── preview_window.py # Janela do Modo Preview
        ├── visualizer.py     # Grid de visualização de paleta
        └── components_v2.py  # Componentes de UI (grupos, configurações)
```

---

## 📄 Formatos Suportados

### Entrada

| Formato | Extensão | Descrição |
|---------|----------|-----------|
| Sprite RO | `.spr` | Arquivo de sprite do Ragnarok Online |

### Saída

| Formato | Extensão | Descrição |
|---------|----------|-----------|
| Paleta RO | `.pal` | Arquivo de paleta (256 cores RGBA) |
| Imagem | `.png` | Preview da paleta (grid 16x16) |

### Especificações Técnicas

**Arquivo .pal:**
- 1024 bytes (256 cores × 4 bytes)
- Formato: RGBX (Red, Green, Blue, Reserved)
- Índice 0: Alpha = 0 (transparente)
- Índices 1-255: Alpha = 255 (opaco)

**Arquivo .spr:**
- Suporta versões 1.0, 2.0 e 2.1
- Imagens indexadas com paleta de 256 cores
- Compressão RLE para versão 2.1+

---

## 💡 Dicas e Truques

### Seleção Rápida
- **Clique no sprite** ao invés do grid para selecionar cores relacionadas automaticamente
- Use **clique e arraste** no grid para seleções grandes

### Cores Únicas Garantidas
- Para gerar 100 cores completamente diferentes, deixe as cores "De" e "Até" **iguais** (vermelho/vermelho)
- O sistema distribuirá automaticamente em 360° do espectro

### Tons Específicos
- Para gerar **apenas azuis**: De = Azul Claro, Até = Azul Escuro
- Para gerar **apenas verdes**: De = Verde Claro, Até = Verde Escuro
- Para gerar **cores quentes**: De = Amarelo, Até = Vermelho

### Preview Eficiente
- Use o **Modo Preview** para testar paletas antes de usar no jogo
- Navegue pelos frames para ver como a paleta fica em diferentes poses

### Grupos Múltiplos
- Crie grupos separados para diferentes partes (Roupa, Cabelo, Capa)
- Gere paletas para cada grupo separadamente
- Combine manualmente para criar variações complexas

---

## ❓ Solução de Problemas

### "Python não é reconhecido como comando"

**Causa:** Python não foi adicionado ao PATH durante a instalação.

**Solução:**
1. Reinstale o Python marcando a opção **"Add Python to PATH"**
2. Ou adicione manualmente:
   - Abra "Variáveis de Ambiente" no Windows
   - Em "Path", adicione o caminho do Python (ex: `C:\Python312\`)

### "ModuleNotFoundError: No module named 'customtkinter'"

**Causa:** Dependências não instaladas.

**Solução:**
```bash
pip install customtkinter pillow
```

### "Falha ao carregar SPR"

**Possíveis causas:**
- Arquivo corrompido
- Versão do sprite não suportada
- Arquivo não é um .spr válido

**Solução:** Verifique se o arquivo é um sprite válido do Ragnarok Online.

### "Nenhum arquivo .pal encontrado"

**Causa:** A pasta selecionada não contém arquivos .pal.

**Solução:** Certifique-se de gerar as paletas primeiro, depois use o Modo Preview na pasta onde foram salvas.

### Programa não abre / Tela em branco

**Solução:**
1. Verifique a versão do Python: `python --version` (deve ser 3.8+)
2. Reinstale as dependências: `pip install --upgrade customtkinter pillow`
3. Execute pelo terminal para ver erros: `python main.py`

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um **Fork** do projeto
2. Criar uma **Branch** para sua feature (`git checkout -b feature/NovaFeature`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. **Push** para a branch (`git push origin feature/NovaFeature`)
5. Abrir um **Pull Request**

### Reportando Bugs

Use a aba **Issues** do GitHub para reportar bugs. Inclua:
- Descrição do problema
- Passos para reproduzir
- Sistema operacional e versão do Python
- Mensagens de erro (se houver)

---

## 📜 Licença

Ainda não tem licença. Mas se tu for vender isso, tu é muito corno.

---

## 👨‍💻 Autor

Desenvolvido com ❤️ por Lumen para a comunidade de Ragnarok Online.

---

**Última atualização:** Janeiro 2026
