# Wild West - OpenGL Scene Renderer

Este projeto é um simulador de cena 3D com temática de Velho Oeste, desenvolvido em Python utilizando a API **OpenGL**. O foco principal da aplicação é demonstrar técnicas de otimização de renderização em tempo real, como **LOD (Level of Detail)**, **Frustum Culling** e **Batching**.

## 📋 Funcionalidades
* **Sistema de Câmera FPS:** Movimentação livre pelo cenário.
* **Otimizações Dinâmicas:** Alternância em tempo real entre implementações corretas e "ruins" (para fins de comparação de performance).
* **LOD (Nível de Detalhe):** Troca automática de malhas baseada na distância da câmera.
* **Frustum Culling:** Descarta objetos que estão fora do campo de visão da câmera.
* **Static Batching:** Agrupa geometrias estáticas para reduzir o número de Draw Calls.
* **Debug Visual:** Visualização de Bounding Boxes e cores indicativas de LOD.

## 🛠️ Pré-requisitos e Dependências

Para executar este projeto, você precisará do **Python 3.8+** instalado.

As dependências necessárias são:
* **NumPy:** Para cálculos matriciais e vetoriais.
* **PyOpenGL:** Wrapper Python para OpenGL.
* **glfw:** Gerenciamento de janelas e inputs.

### Instalação das dependências:
Abra o seu terminal e execute:
```bash
pip install numpy PyOpenGL glfw
```

> **Nota:** Em alguns sistemas (especialmente Windows), pode ser necessário instalar os binários do PyOpenGL manualmente ou via `pip install PyOpenGL_accelerate`.

## 🚀 Como Executar

1. Certifique-se de que a pasta `assets/` contendo os modelos `.obj` está no mesmo diretório que os scripts.
2. Execute o script principal (geralmente onde o loop `Window.run()` é chamado, ex: `main.py` ou similar):
```bash
python main.py
```

## 🎮 Controles

### Movimentação
* **W, A, S, D**: Movimentar a câmera.
* **Shift (Hold)**: Aumentar velocidade de movimento.
* **Mouse**: Rotacionar a câmera (Yaw/Pitch).
* **ESC**: Fechar a aplicação.

### Otimizações (Teclas Numéricas)
O sistema permite comparar a performance de técnicas otimizadas vs. implementações ingênuas:

| Tecla | Função |
| :--- | :--- |
| **1** | Ativa/Desativa TODAS as otimizações corretas |
| **2** | Alterna **LOD** (Nível de Detalhe) Correto |
| **3** | Alterna **Frustum Culling** Correto |
| **4** | Alterna **Batching** (Agrupamento por tipo) |
| **5** | Ativa/Desativa TODAS as versões "ruins" (Anti-patterns) |
| **6** | Ativa LOD Ruim (Fixa tudo em High Poly) |
| **7** | Ativa Frustum Culling Ruim (Margem de erro excessiva) |
| **8** | Ativa Batching Ruim (VAO Único sem culling individual) |

### Debug
* **9**: Exibe as **Bounding Boxes** (AABB) em wireframe branco.
* **0**: Exibe o **LOD Colorido** (Verde: High, Amarelo: Medium, Vermelho: Low).

## 📂 Estrutura do Código

* `window.py`: Gerencia a janela GLFW, inputs e o loop principal.
* `render.py`: O "coração" do projeto; decide o que e como renderizar.
* `batching.py`: Lógica para mesclar geometrias e reduzir Draw Calls.
* `bounding.py`: Cálculos de volumes delimitadores e interseção com o frustum.
* `camera.py`: Gerencia matrizes de Projeção e Visão.
* `loader.py`: Parser de arquivos `.obj` e upload de dados para a GPU.
* `fabric.py`: Fábrica de objetos com caminhos de LOD pré-definidos.

---
**Desenvolvido por:** Abrahão Gonçalves Dias e Gabriel Ponzoni  
**Ambiente Acadêmico:** Unisinos - Bacharelado em Jogos Digitais

