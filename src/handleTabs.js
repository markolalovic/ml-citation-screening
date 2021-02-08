function openTab(evt, tabName) {
  const rowsPerPage = 10;
  selected = tabName;
  let i, tabcontent, tablinks;

  removeTable();
  removeTime();

  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";

  let articles = data[tabName];
  createTable(tabName);
  loadTable(articles);
  addPagerToTables('#table', rowsPerPage);
  addTime();
}

