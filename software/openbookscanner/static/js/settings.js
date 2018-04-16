
const SCANNER_1_SELECT_ID = "scanner-1";
const SCANNER_2_SELECT_ID = "scanner-2";


// display some more information about the scanner
function updateScannerSelection(select) {
  var informationId = select.id + "-info";
  var informaion = document.getElementById(informationId);
  // todo: add pictures of scan and more about the device
}

// fill a select with scanner information
function fillWithScannerInformation(select, scanners) {
  var selectedOption = select.selectedIndex && select.options[select.selectedIndex];
  removeAllChildren(select);
  forAttr(scanners, function(id, scanner) {
    var option = document.createElement("option");
    option.text = scanner.name;
    option.id = id;
    option.scanner = scanner;
    option.selected = selectedOption && selectedOption.id == id;
    select.appendChild(option);
  });
  updateScannerSelection(select);
}

// update all scanner entries with new information
function updateScanners() {
  getScanners(function(scanners) {
    fillWithScannerInformation(document.getElementById(SCANNER_1_SELECT_ID), scanners);
    fillWithScannerInformation(document.getElementById(SCANNER_2_SELECT_ID), scanners);
  })
}

// update all the settings
// This should be only necessary when the page loads
function updateAllSettings() {
  updateScanners();
}

window.addEventListener("load", updateAllSettings); 

