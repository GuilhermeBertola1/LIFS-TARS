# S_python

## Objetivo

Backend responsável pelo gerenciamento documental do sistema.

## Funcionalidades

* Upload de arquivos;
* Download de arquivos;
* Criação de diretórios;
* Geração de PDFs;
* Organização de experimentos.

## Estrutura

```text
uploads/
pdfs/
relatorios/
json/
```

## Tecnologias

* Flask
* FPDF
* Werkzeug

## Endpoints

### Upload

POST /upload

### Download

GET /download/<arquivo>

### Gerar Relatório

POST /gerar_pdf

## Formatos

* PDF
* JSON
* ZIP
