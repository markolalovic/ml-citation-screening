function initialize() {
  for (key of Object.keys(data)) {
    createTable(key);
    loadTable(key);
    const tableName = '#table' + upperFirst(key);
    addPagerToTables(tableName, rowsPerPage);
  }
}

function createTable(tabName) {
  // add header to table
  // Relevance, Date, Title, Abstract, Expand, PMID
  const header = ['Relevance', 'Date', 'Title', 'Abstract', 'Expand', 'PMID'];
  const tableName = 'table' + upperFirst(tabName);
  let table = document.getElementById(tableName)

  let caption = table.createCaption();
  const content = `Table ${captionsTable[tabName]}: ${captionsText[tabName]}`;
  caption.textContent = content;

  let tHead = table.createTHead();
  let row = tHead.insertRow();

  for (let i = 0; i < header.length; i++) {
    let th = document.createElement('th');
    th.innerHTML = header[i];
    row.appendChild(th);
  }

  // create table body for data
  let tBody = table.createTBody();
  tBody.id = 'tableBody' + upperFirst(tabName);
}

function loadTable(tabName) {
  const tableBodyName = 'tableBody' + upperFirst(tabName);
  let table = document.getElementById(tableBodyName);
  const articles = data[tabName];

  for (let i = 0; i < articles.length; i++) {
    let row = table.insertRow();

    let relevance = row.insertCell(0);
    relevance.innerHTML = articles[i].relevance;

    let date = row.insertCell(1);
    let dateText = articles[i].date;
    dateText = removeFirstZero(dateText.trim());
    dateText = dateText.split(' ');
    dateText = `${dateText[0]}. ${dateText[1]} ${dateText[2]}`;
    date.innerHTML = dateText;

    let title = row.insertCell(2);
    title.id = getCellId(tabName, i + 1, 2);
    title.height = '20';
    const titleText = articles[i].title;
    title.innerHTML = '<div class="nowrap padded" style="height: 20px; overflow:hidden;">' + titleText + '</div>';

    let abstract = row.insertCell(3);
    abstract.id = getCellId(tabName, i + 1, 3);
    abstract.height = '20';
    const abstractText = getTruncated(articles[i].abstract);
    abstract.innerHTML = '<div class="nowrap padded" style="height: 20px; overflow:hidden;">' + abstractText + '</div>';

    let expandButton = row.insertCell(4);
    const idSwitch = `tab${tableId[tabName]}Switch${i + 1}`;
    expandButton.innerHTML = `<input class="switch" type="button" value="+" id="${idSwitch}" onclick="switchFun(${i + 1});"></input>`;

    let linkButton = row.insertCell(5);
    linkButton.innerHTML = '<a target="_blank" rel="noopener noreferrer" href="https://pubmed.ncbi.nlm.nih.gov/' +
      articles[i].pmid + '/">' + articles[i].pmid + '</a>';
  }
}

function switchFun(rowNumber) {
  // button to expand / collapse row
  const idSwitch = `tab${tableId[selected]}Switch${rowNumber}`;
  currentValue = document.getElementById(idSwitch).value;

  if (currentValue == '+') {
    document.getElementById(idSwitch).value = '-';
    expand(rowNumber);
  } else {
    document.getElementById(idSwitch).value = '+';
    collapse(rowNumber);
  }
}

function expand(rowNumber) {
  // title = title + abstract

  let title = document.getElementById(getCellId(selected, rowNumber, 2));
  let abstract = document.getElementById(getCellId(selected, rowNumber, 3));

  title.colSpan = '2';

  title.innerHTML = '<div class="padded"><h3>' + data[selected][rowNumber - 1].title + '</h3>' +
    '<p><b>Abstract</b><br>' + data[selected][rowNumber - 1].abstract + '</p><div>';
  // transitions

  title.style.height = Math.round(3 * title.scrollHeight / 4) + 'px';
  abstract.style.display = 'none';
}

function collapse(rowNumber) {
  // title = title

  let title = document.getElementById(getCellId(selected, rowNumber, 2));
  let abstract = document.getElementById(getCellId(selected, rowNumber, 3));

  title.colSpan = '1';

  const titleText = data[selected][rowNumber - 1].title;
  title.innerHTML = '<div class="nowrap padded" style="height: 20px; overflow:hidden;">' + titleText + '</div>';

  abstract.style.display = '';

  // transitions
  title.style.height = "20px";
}

function getTruncated(text) {
  // number of characters of title and abstract in a collapsed row
  const MAX = 150;
  if (text.length <= MAX) {
    return text;
  } else {
    return text.substring(0, MAX) + ' ..';
  }
}

function getCellId(tabName, rowNumber, colNumber) {
  return 'tab' + tableId[tabName] + 'Row' + rowNumber + 'Col' + colNumber;
}

function addTime() {
  let body = document.getElementsByTagName('body')[0];
  let timeOfUpdate = document.createElement('p');
  timeOfUpdate.id = 'time';
  timeOfUpdate.appendChild(document.createTextNode('**Last updated: So 7. Feb 23:39:50 CET 2021**'));
  body.appendChild(timeOfUpdate);
}

function upperFirst(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function removeFirstZero(string) {
  if (string.charAt(0) === '0') {
    return string.slice(1);
  } else {
    return string;
  }
}