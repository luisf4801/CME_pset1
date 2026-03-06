# CME_pset1
# Replication Package for: *Problem Set 1 - Computational Methods in Economics*

**Authors:**  
Luis felipe Porro, Sao Paulo School of Economics - FGV, Luisfelipe.porro@gmail.com

---

## 1. Overview

This repository contains the analysis code and instructions to obtain the data necessary to replicate the results in the report named:

> *Luisporro_pset1_CME*  
> Luis felipe Porro

The replication package reproduces **all tables, figures, and numbers** in the report.

---

## 2. Repository Structure

```text

meu_projeto/
├── final_code.py         # O script principal
├── requirements.txt      # Arquivo de dependências enviado
├── Raw/                  # Pasta com os dados brutos
│   └── Mega-Sena.xlsx    # O arquivo de dados
└── output/               # Pasta onde os resultados serão salvos
└──Readme.md
```

## 3. Computational Environment

The analysis was conducted using 3.13.5, packaged by Anaconda, Inc. (main, Jun 12 2025, 16:37:03) [MSC v.1929 64 bit (AMD64)] All the required Python packages and their versions are listed in the requirements.txt file located in the main directory.

## 4. Data access
Given the absence of a licence from the data provider, the data used in this project is not avalable on the present directory. In this directory i Posted 
a data frame with the columns witch allows the conference with the data set downloaded on:
https://loterias.caixa.gov.br/Paginas/Mega-Sena.aspx, where a button named 
"Download de resultados" allows you to download it. A snapshot of the page is found in
https://web.archive.org/web/20260102020959/https://loterias.caixa.gov.br/Paginas/Mega-Sena.aspx, 
where we can see such source existed by January 14th, 2026. The sample used as input for the code goes from 11/03/1996 to 28/02/2026

Data for historical lottery ticket prices can be found in https://graficos.poder360.com.br/PEXGE/1/.
An archived version of this is found in https://web.archive.org/web/20250707005543/https://graficos.poder360.com.br/PEXGE/1/.
Before the last announcement date available, the ticket price was R$ 2. This information is used directy on the code on the function .

## 5. Reproducing results

To set up the environment and ensure Python correctly interprets the project dependencies, follow these steps:

1. Navigate to the project folder: Open the Anaconda Prompt and use the cd command to enter the directory where your final code.py and requirements.txt files are located.

2. Create and activate the environment: Run conda create --name mega_env python=3.13.5 to create a fresh environment, then type conda activate mega_env to join it.

3. Install dependencies: Once inside the project folder and with the environment active, run the following command to have Python interpret and install the library list:
pip install -r requirements.txt


```text
conda create --name mega_env python=3.13.5
(Siga as instruções na tela para confirmar a instalação)

conda activate mega_env

pip install -r requirements.txt
```

After downloading the results data and ensuring the spreadsheet has the same structure as in the example in `data/raw`, the results in the report can be reproduced running `data_treatment.py`, then `analysis.py` afterwards in the `code` folder. This will populate the `output` folder with the results. 
