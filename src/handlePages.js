// Based on: https://stackoverflow.com/a/52356138/3997185

function addPagerToTables(tables, rowsPerPage = 10) {
  tables =
    typeof tables == "string" ?
    document.querySelectorAll(tables) :
    tables;

  for (let table of tables) {
    addPagerToTable(table, rowsPerPage);
  }
}

function addPagerToTable(table, rowsPerPage = 10) {
  let tBodyRows = table.querySelectorAll('tBody tr');
  let numPages = Math.ceil(tBodyRows.length / rowsPerPage);

  let colCount = [].slice.call(
    table.querySelector('tr').cells
  ).reduce((a, b) => a + parseInt(b.colSpan), 0);

  table
    .createTFoot()
    .insertRow()
    .innerHTML = `
    <td style="background-color: rgba(220, 220, 220, 0.7)" colspan=${colCount}>
      <div class="nav">
          Page: 
      </div>
    </td>`;

  if (numPages == 1)
    return;

  for (i = 0; i < numPages; i++) {
    let pageNum = i + 1;

    table.querySelector('.nav')
      .insertAdjacentHTML(
        'beforeend',
        `<a 
              class="changeable" 
              href="#" 
              rel="${i}"
             >${pageNum}</a> `
      );
  }

  changeToPage(table, 1, rowsPerPage);

  for (let navA of table.querySelectorAll('.nav a')) {
    navA.addEventListener(
      'click',
      e => changeToPage(
        table,
        parseInt(e.target.innerHTML),
        rowsPerPage
      )
    );
  }
}

function changeToPage(table, page, rowsPerPage) {
  let startItem = (page - 1) * rowsPerPage;
  let endItem = startItem + rowsPerPage;
  let navAs = table.querySelectorAll('.nav a');
  let tBodyRows = table.querySelectorAll('tBody tr');

  for (let nix = 0; nix < navAs.length; nix++) {
    if (nix == page - 1)
      navAs[nix].classList.add('active');
    else
      navAs[nix].classList.remove('active');

    for (let trix = 0; trix < tBodyRows.length; trix++)
      tBodyRows[trix].style.display =
      (trix >= startItem && trix < endItem) ?
      'table-row' :
      'none';
  }
}