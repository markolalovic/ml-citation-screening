function createTable(tabName) {
    const header = ['PMID', 'Date', 'Title', 'Abstract', 'Expand', 'Permalink', 'Relevance'];
    let body = document.getElementsByTagName('body')[0];
    let table = document.createElement('table');
    table.id = 'table';

    let caption = table.createCaption();
    caption.textContent = captions[tabName];
  
    let tHead = table.createTHead();
    let row = tHead.insertRow();
    
    for (let i = 0; i < header.length; i++) {
      let th = document.createElement('th');
      th.innerHTML = header[i];
      row.appendChild(th);
    }
    let tBody = table.createTBody();
    tBody.id = 'tableBody';
    body.appendChild(table)
  }
  
function removeTable() {
  let table = document.getElementById('table');
  if (table) {
    table.parentNode.removeChild(table);
  }
}
  
function addTime() {
  let body = document.getElementsByTagName('body')[0];
  let timeOfUpdate = document.createElement('p');
  timeOfUpdate.id = 'time';
  timeOfUpdate.appendChild(document.createTextNode('**Last updated: So 7. Feb 23:39:50 CET 2021**'));
  body.appendChild(timeOfUpdate);
}

function removeTime() {
  let timeOfUpdate = document.getElementById('time');
  if (timeOfUpdate) {
    timeOfUpdate.parentNode.removeChild(timeOfUpdate);
  }
}

function getId(rowNumber, colNumber) {
  return 'row' + rowNumber + 'Col' + colNumber;
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
  
function loadTable(articles) {
  const table = document.getElementById("tableBody");
  for (let i = 0; i < articles.length; i++) {
    let row = table.insertRow();
    
    let pmid = row.insertCell(0);
    pmid.innerHTML = articles[i].pmid;

    let date = row.insertCell(1);
    date.innerHTML = articles[i].date;

    let title = row.insertCell(2);
    title.id = getId(i+1, 2);
    title.height = '20';
    const titleText = articles[i].title;
    title.innerHTML = '<div style="height: 20px; overflow:hidden;">' + titleText + '</div>';

    let abstract = row.insertCell(3);
    abstract.id = getId(i+1, 3);
    abstract.height = '20';
    const abstractText = getTruncated(articles[i].abstract);
    abstract.innerHTML = '<div style="height: 20px; overflow:hidden;">' + abstractText + '</div>';

    let expandButton = row.insertCell(4);
    expandButton.innerHTML = `<input type="button" value="+" id="switch${i+1}" onclick="switchFun(${i+1});"></input>`;

    let linkButton = row.insertCell(5);
    linkButton.innerHTML = '<a target="_blank" rel="noopener noreferrer" href="https://pubmed.ncbi.nlm.nih.gov/' 
      + articles[i].pmid + '/">' + 'link' + '</a>';

    let relevance = row.insertCell(6);
    relevance.innerHTML = articles[i].relevance;
  }
}
  
function switchFun(rowNumber) {
  // button to expand / collapse row

  const idSwitch = 'switch' + rowNumber;
  currentValue = document.getElementById(idSwitch).value;

  if(currentValue == '+') {
    document.getElementById(idSwitch).value= '-';
    expand(rowNumber);
  } else {
    document.getElementById(idSwitch).value= '+';
    collapse(rowNumber);
  }
}
  
function expand(rowNumber) {
  // title = title + abstract

  let title = document.getElementById(getId(rowNumber, 2));
  let abstract = document.getElementById(getId(rowNumber, 3));

  title.colSpan = '2'; 
  
  title.innerHTML = '<b>' + data[selected][rowNumber-1].title + '</b>'
    + '<p><b>Abstract</b><br>' + data[selected][rowNumber-1].abstract + '</p>';
  // transitions
    
  title.style.height = Math.round(3 * title.scrollHeight / 4) + 'px';
  abstract.style.display = 'none';
}
  
function collapse(rowNumber) {
  // title = title
  
  let title = document.getElementById(getId(rowNumber, 2));
  let abstract = document.getElementById(getId(rowNumber, 3));

  title.colSpan = '1';

  const titleText = data[selected][rowNumber-1].title;
  title.innerHTML = '<div style="height: 20px; overflow:hidden;">' + titleText + '</div>';

  abstract.style.display = '';

  // transitions
  title.style.height = "20px";
}