async function gerarPDF() {
  const textareas = document.querySelectorAll("#inputs textarea");
  const texto = Array.from(textareas).map(t => t.value).join("\n");
  const reator = document.getElementById("reator-select").value;
  const nomeArquivoInput = document.getElementById("nomeArquivo");
  const nomeArquivo = nomeArquivoInput.value.trim();

  if (!nomeArquivo) {
    alert("Por favor, preencha o nome do arquivo antes de gerar o PDF.");
    nomeArquivoInput.focus();
    return;
  }

  const tabelas = coletarDadosDoFormulario().tabelas;

  const response = await fetch('/api/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: texto,
      reator: reator,
      tabelas: tabelas,
      nome_arquivo: nomeArquivo
    })
  });

  if (response.ok) {
    console.log("Gerou o pdf!");
    alert("PDF Gerado");
    textareas.forEach(t => t.value = '');
    document.querySelectorAll('.tabela input').forEach(i => i.value = '');
  } else {
    alert("Erro ao gerar PDF");
  }
}

function addLinha(tabelaId) {
  const tabela = document.querySelector(`#${tabelaId} table`);
  const tbody = tabela.querySelector('tbody');
  const linha = document.createElement('tr');

  let colunas = 0;
  const thead = tabela.querySelector('thead');
  if (thead) {
    colunas = thead.rows[0].cells.length;
  } else if (tbody.rows.length > 0) {
    colunas = tbody.rows[0].cells.length;
  } else {
    colunas = 2;
  }

  for (let i = 0; i < colunas; i++) {
    const cell = document.createElement('td');
    const input = document.createElement('input');
    input.type = 'text';
    cell.appendChild(input);
    linha.appendChild(cell);
  }

  tbody.appendChild(linha);
}

function addColuna(tabelaId) {
  const tabela = document.querySelector(`#${tabelaId} table tbody`);
  for (let i = 0; i < tabela.rows.length; i++) {
    const row = tabela.rows[i];
    const cell = row.insertCell();
    const input = document.createElement("input");
    input.type = "text";
    cell.appendChild(input);
  }
}

function removerLinha(tabelaId) {
  const tabela = document.querySelector(`#${tabelaId} table`);
  if (tabela.rows.length > 1) {
    tabela.deleteRow(tabela.rows.length - 1);
  }
}

function removerColuna(tabelaId) {
  const tabela = document.querySelector(`#${tabelaId} table`);
  const colunas = tabela.rows[0].cells.length;
  if (colunas > 1) {
    for (let row of tabela.rows) {
      row.deleteCell(colunas - 1);
    }
  }
}

async function carregarArquivos() {
  const reator = document.getElementById('reator').value;
  const lista = document.getElementById('lista-arquivos');
  lista.innerHTML = "Carregando...";

  const res = await fetch(`/api/arquivos/${reator}`);
  const arquivos = await res.json();

  lista.innerHTML = arquivos.length === 0 ? "Nenhum arquivo encontrado" : "";

  arquivos.forEach(nome => {
    const container = document.createElement('div');
    container.classList.add('arquivo-item');

    const link = document.createElement('a');
    link.href = `/api/visualizar/${reator}/${nome}`;
    link.innerText = nome;
    link.target = '_blank';
    link.style.marginRight = '10px';

    const botaoEditar = document.createElement('button');
    botaoEditar.innerText = "Editar";
    botaoEditar.onclick = () => {
        window.location.href = `gerador.html?reator=${reator}&arquivo=${nome}`;
    };

    const botaoRemover = document.createElement('button');
    botaoRemover.innerText = "Remover";
    botaoRemover.style.marginLeft = '10px';
    botaoRemover.onclick = async () => {
        const confirmar = confirm(`Tem certeza que deseja remover "${nome}"?`);
        if (confirmar) {
            const response = await fetch(`/api/remover/${reator}/${nome}`, { method: 'DELETE' });
            if (response.ok) {
                alert("Arquivo removido com sucesso.");
                carregarArquivos();
            } else {
                alert("Erro ao remover arquivo.");
            }
        }
    };

    container.appendChild(link);
    container.appendChild(botaoEditar);
    container.appendChild(botaoRemover);
    lista.appendChild(container);
  });
}

function coletarDadosDoFormulario() {
  const textareas = document.querySelectorAll("#inputs textarea");
  const linhasTexto = Array.from(textareas).map(t => t.value.trim());
  const textoUnico = linhasTexto.join("\n");

  const todasTabelas = document.querySelectorAll("table[id^='tabela']");
  const tabelas = {};

  todasTabelas.forEach(tabela => {
    const idTabela = tabela.id;
    const linhas = tabela.querySelectorAll("tbody tr");
    const dadosTabela = [];

    linhas.forEach((linha) => {
      const linhaValores = [];

      if (idTabela === 'tabela1') {
        const th = linha.querySelector('th');
        if (th) {
          linhaValores.push(th.innerText.trim());
        }
      }

      const inputs = linha.querySelectorAll('td input');
      inputs.forEach(input => {
        linhaValores.push(input.value.trim());
      });

      if (linhaValores.length > 0) {
        dadosTabela.push(linhaValores);
      }
    });

    if (dadosTabela.length > 0) {
      tabelas[idTabela] = dadosTabela;
    }
  });

  return {
    text: textoUnico,
    tabelas: tabelas
  };
}

document.addEventListener('DOMContentLoaded', () => {
  const reatorSelect = document.getElementById('reator');
  if (reatorSelect) {
    carregarArquivos();
  }
});

window.addEventListener("DOMContentLoaded", async () => {
  if (!window.location.href.includes("gerador.html")) return;

  const botaoGerar = document.getElementById("btnGerar");
  const botaoSalvar = document.getElementById("btnSalvar");
  const controleReator = document.getElementById("controle");

  const params = new URLSearchParams(window.location.search);
  const reator = params.get("reator");
  const arquivo = params.get("arquivo");

  if (reator && arquivo) {
    botaoGerar.style.display = "none";
    botaoSalvar.style.display = "block";
    controleReator.style.display = "none";

    try {
      const res = await fetch(`/api/json/${reator}/${arquivo}`);
      const dados = await res.json();
      const valores = dados.text.split('\n');
      const campos = document.querySelectorAll("#inputs textarea");
      for (let i = 0; i < valores.length && i < campos.length; i++) {
        campos[i].value = valores[i].trim();
      }

      const tabelas = dados.tabelas;
      Object.entries(tabelas).forEach(([nomeTabela, tabela]) => {
        const tabelaHtml = document.getElementById(nomeTabela);
        if (!tabelaHtml) return;
        const tbody = tabelaHtml.querySelector("tbody");
        tbody.innerHTML = "";

        let colunas = 0;
        tabela.forEach((linha, i) => {
          if (i === 0) {
            colunas = nomeTabela === 'tabela1' && linha.length > 1 ? linha.length - 1 : linha.length;
          }

          const tr = document.createElement("tr");
          const dados = nomeTabela === 'tabela1' && linha.length > 1 ? linha.slice(1) : linha;

          if (nomeTabela === 'tabela1') {
            const th = document.createElement("th");
            th.innerText = linha[0] || "";
            tr.appendChild(th);
          }

          for (let c = 0; c < colunas; c++) {
            const td = document.createElement("td");
            const input = document.createElement("input");
            input.type = "text";
            input.value = dados[c] || "";
            td.appendChild(input);
            tr.appendChild(td);
          }

          tbody.appendChild(tr);
        });
      });
    } catch (e) {
      alert("Erro ao carregar dados para edição.");
      console.error(e);
    }

    botaoSalvar.onclick = async () => {
      const nomeNovo = document.getElementById("nomeArquivo").value.trim();
      if (!nomeNovo) {
        alert("Por favor, preencha o nome do arquivo.");
        return;
      }

      const dadosAtualizados = coletarDadosDoFormulario();

      const resposta = await fetch(`/api/salvar_pdf/${reator}/${arquivo}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          novo_nome: nomeNovo,
          ...dadosAtualizados
        })
      });

      if (resposta.ok) {
        alert('Arquivo atualizado com sucesso!');
        window.location.href = '/';
      } else {
        alert('Erro ao atualizar o arquivo.');
      }
    };

  }
});