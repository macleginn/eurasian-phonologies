var colorNames = ["aquamarine", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkgrey", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "plum", "powderblue", "purple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell"];

// Store data for the list view and the report page.
var phyloData, groupData, isolates;
$.ajax({
		url: "http://eurasianphonology.info/jsonp",
		jsonp: "callback",
		dataType: "jsonp",
		data: {
			langlist: "true",
			dialects: "true",
			myCallback: "saveData"
		}
	});

function saveData(data) {
	phyloData = data[0];
	groupData = data[1];
	isolates  = data[2];
}

var currentMarker, currentMap;

var addEvent = function(elem, type, eventHandle) {
    if (elem == null || typeof(elem) == 'undefined') return;
    if ( elem.addEventListener ) {
        elem.addEventListener( type, eventHandle, false );
    } else if ( elem.attachEvent ) {
        elem.attachEvent( "on" + type, eventHandle );
    } else {
        elem["on"+type]=eventHandle;
    }
};

function injectStats(data) {
	$("span#nlangs").html(data["nlangs"]);
	$("span#nvars").html(data["nvars"]);
	$("span#ndials").html(data["ndials"]);
}

function clearHTML(divText) {
	var charArr = divText.split(""),
		result  = [];
	charArr.map(function(chr) {
		if (chr != "\\") {
			result.push(chr);
		}
	});
	return result.join("");
}

function resizeMap() {
	var height = $(window).height() - 115;
	$("#main").css({"height": height});
}

addEvent(window, "resize", resizeMap);

function showMapView() {
	$.ajax({
			url: "http://eurasianphonology.info/jsonp",
			dataType: "jsonp",
			data: {
				dataForMap: "true"
			}
		});
}

function displayTable(data) {
	$("#main").empty();
	$("#main").css({"height": "auto", "background-color": "white"});
	$("#main").append($("<input>").attr("type", "button").attr("value", "Back to map").attr("onclick", "showMapView()").css({"margin": "10px", "margin-left": "30px", "margin-bottom": "0", "font-family": "'open sans'", "font-size": "10pt"}));
	$("#main").append($("<br/>"));
	$("#main").append(clearHTML(data));
	$(".phono_tables").css({"margin-left": "30px"});
}

function addToMap(data) {
	$("#main").empty();
	var height = $(window).height() - 115;
	$("#main").css({"height": height});
	var center = new google.maps.LatLng(48, 87.637515);
	var mapOptions = {
			zoom: 3,
			center: center,
			mapTypeId: google.maps.MapTypeId.SATELLITE
		};
	var map = new google.maps.Map(document.getElementById('main'), mapOptions);
	currentMap = map;
	var familyDic = data[0];
	var coordDic = data[1];
	var marker_colors = {
			running_count: 0
		};
	for (var langId in coordDic) {
		var langName = langId.split('#')[0];
		var family = familyDic[langId][0];
		if (!marker_colors.hasOwnProperty(family)) {
				marker_colors[family] = marker_colors["running_count"];
				marker_colors["running_count"] += 1;
			}
		var colorIndex = marker_colors[family];
		var latLng = new google.maps.LatLng(coordDic[langId][0], coordDic[langId][1]);
		var marker = new google.maps.Marker({
			position: latLng,
			map: map,
			title: langName + ", " + familyDic[langId][1] + ", " + familyDic[langId][0],
			icon: {
				path: google.maps.SymbolPath.CIRCLE,
				fillColor: colorNames[colorIndex],
				fillOpacity: 1,
				scale: 6,
				strokeWeight: 1,
				strokeColor: "black"
			}
		});
		function makeTableDataFunction(langId) {
			return function() {
				currentMarker = marker;
				$.ajax({
					url: "http://eurasianphonology.info/jsonp",
					dataType: "jsonp",
					data: {
						provideInventoryTable: langId,
						myCallback: "displayTable"
					}
				});
		    }
		}
		google.maps.event.addListener(marker, 'click', makeTableDataFunction(langId));
	}
}

function zip(arr1, arr2) {
	result = [];
	for (var i = 0; i < arr1.length; i++) {
		result.push([arr1[i], arr2[i]]);
	}
	return result
}

function showReportPage() {
	$("#main").empty();
	$("#main").css({"height": "auto", "background-color": "white"});
	var main = $("<div>").attr("id", "reportHolder");
	$("#main").append(main);
	$(".phono_tables").css({"margin-left": "0"});
	main.empty();
	main.append($("<h1>").attr("id", "reportsTitle").text("Family and group reports"));
	main.append($("<select>").attr("id", "families").attr("onchange", "repopulateGroups()"));
	main.append($("<input>").attr("type", "button").attr("id", "familiesBtn").attr("value", "Show family report").attr("onclick", "fetchFamilyReport()"))
	main.append($("<br />"));
	main.append($("<select>").attr("id", "groups"));
	main.append($("<input>").attr("type", "button").attr("id", "groupsBtn").attr("value", "Show group report").attr("onclick", "fetchGroupReport()"))
	main.append($("<br/>"))
	main.append($("<div>").attr("id", "map_canvas").css({"width": "800px", "height": "400px", "margin-top": "30px"}))
	main.append($("<br/>"))
	// Внести сюда populateLangLists
	var data = phyloData;
	var fam_array = [];
	for (var family in data) {
		if (data.hasOwnProperty(family)) {
			fam_array.push(family);
		}
	}
	fam_array.sort();
	for (var i = 0; i < fam_array.length; i++) {
		$("#families").append($("<option>").attr("value", fam_array[i]).text(fam_array[i]));	
	}
	var currentFam = $("#families").val();
	if (data[currentFam].length == 0) {
		$("#groups").append($("<option>").attr("value", "—").text("—"));
		var groupsBtn = document.getElementById("groupsBtn");
		groupsBtn.disabled = true;
	} else {
		var groupsBtn = document.getElementById("groupsBtn");
		groupsBtn.disabled = false;
		var group_arr = [];
		phyloData[currentFam].map(function(group) {
			group_arr.push(group);
		});
		group_arr.sort()
		for (var i = 0; i < group_arr.length; i++) {
			$("#groups").append($("<option>").attr("value", group_arr[i]).text(group_arr[i]));
		}
	}
}

function repopulateGroups() {
	$("#groups").empty();
	var currentFam = $("#families").val();
	if (phyloData[currentFam].length == 0) {
		$("#groups").append($("<option>").attr("value", "—").text("—"));
		var groupsBtn = document.getElementById("groupsBtn");
		groupsBtn.disabled = true;
	} else {
		var groupsBtn = document.getElementById("groupsBtn");
		groupsBtn.disabled = false;
		phyloData[currentFam].map(function(group) {
			$("#groups").append($("<option>").attr("value", group).text(group));
		});
	}
}

function fetchFamilyReport(element) {
	var family = $("#families").val();
	$.ajax({
		url: "http://eurasianphonology.info/jsonp",
		dataType: "jsonp",
		data: {
			report_type: "family",
			family: family
		}
	});
}

function showFamilyReport(data) {
	$("#map_canvas").empty();
	$("div.phono_tables").remove();
	$("#histogramHolder").remove();
	$("h1.main_div_title").remove();
	var map_data = data["map_data"];
	var colorNames = ["aquamarine", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkgrey", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "plum", "powderblue", "purple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell"];
	var lats = [],
		lons = [];
	map_data.map(function (item) {
		lats.push(+item[2]);
		lons.push(+item[3]);
	});
	var centerLat = lats.reduce(function(a, b) { return a + b }, 0) / lats.length,
		centerLong = lons.reduce(function(a, b) { return a + b }, 0) / lons.length,
		minLat = lats.reduce(function(a, b) {return Math.min(a, b)}),
		minLon = lons.reduce(function(a, b) {return Math.min(a, b)}),
		maxLat = lats.reduce(function(a, b) {return Math.max(a, b)}),
		maxLon = lons.reduce(function(a, b) {return Math.max(a, b)});
	
	var center = new google.maps.LatLng(centerLat, centerLong);
	var mapOptions = {
		zoom: 4,
		center: center,
		mapTypeId: google.maps.MapTypeId.SATELLITE
	};
	var map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
	var marker_colors = {
		running_count: 0
	};
	map_data.map(function(item) {
		if (!marker_colors.hasOwnProperty(item[1])) {
			marker_colors[item[1]] = marker_colors["running_count"];
			marker_colors["running_count"] += 1;
		}
		var colorIndex = marker_colors[item[1]];
		var latLng = new google.maps.LatLng(item[2], item[3]);
		var marker = new google.maps.Marker({
			position: latLng,
			map: map,
			title: item[0],
			icon: {
				path: google.maps.SymbolPath.CIRCLE,
				fillColor: colorNames[colorIndex],
				fillOpacity: 1,
				scale: 6,
				strokeWeight: 1,
				strokeColor: "black"
			}
		})
	});
	addTheRest(data, map_data);
}

function fetchGroupReport(element) {
	var group = $("#groups").val();
	$.ajax({
		url: "http://eurasianphonology.info/jsonp",
		dataType: "jsonp",
		data: {
			report_type: "group",
			group: group
		}
	});
}

function showGroupReport(data) {
	$("#map_canvas").empty();
	$("div.phono_tables").remove();
	$("#histogramHolder").remove();
	$("h1.main_div_title").remove();
	var map_data = data["map_data"];
	var lats = [],
		lons = [];
	map_data.map(function (item) {
		lats.push(+item[1]);
		lons.push(+item[2]);
	});
	var centerLat = lats.reduce(function(a, b) { return a + b }, 0) / lats.length,
		centerLong = lons.reduce(function(a, b) { return a + b }, 0) / lons.length,
		minLat = lats.reduce(function(a, b) {return Math.min(a, b)}),
		minLon = lons.reduce(function(a, b) {return Math.min(a, b)}),
		maxLat = lats.reduce(function(a, b) {return Math.max(a, b)}),
		maxLon = lons.reduce(function(a, b) {return Math.max(a, b)});
	
	var center = new google.maps.LatLng(centerLat, centerLong);
	var mapOptions = {
		zoom: 4,
		center: center,
		mapTypeId: google.maps.MapTypeId.SATELLITE
	};
	var map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
	map_data.map(function(item) {
		var latLng = new google.maps.LatLng(item[1], item[2]);
		var marker = new google.maps.Marker({
			position: latLng,
			map: map,
			title: item[0],
			icon: {
				path: google.maps.SymbolPath.CIRCLE,
				fillColor: "yellow",
				fillOpacity: 1,
				scale: 6,
				strokeWeight: 1,
				strokeColor: "black"
			}
		})
	});
	addTheRest(data, map_data);
}

function addTheRest(data, map_data) {
	if (data["table_of_common_phons"] == "") {
		$("#reportHolder").append($("<div>").attr("class", "phono_tables"));
		$("div.phono_tables").append($("<h1>").attr("class", "main_div_title").text("Common phonemes"));
		$("div.phono_tables").append("<h4>No common phonemes found across all languages of the family</h4>");
	} else {
		addTableOfCommonPhons(data["table_of_common_phons"]);
	}
	if (data["inv_sizes"]["all"].length > 1) {
		$("#reportHolder").append("<br />")
		$("#reportHolder").append($("<div>").attr("id", "histogramHolder"));
		$("#histogramHolder").append($("<h1>").attr("class", "main_div_title").text("Inventory size breakdown"));
		var table = [["Language", "Inventory size"]];
		table.push.apply(table, zip(map_data.map(function(item) {return item[0]}), data["inv_sizes"]["all"]));
		addInventoryHistogram(table, "Inventory sizes: all segments");
		table = [["Language", "Consonant inventory size"]];
		table.push.apply(table, zip(map_data.map(function(item) {return item[0]}), data["inv_sizes"]["cons"]));
		addInventoryHistogram(table, "Inventory sizes: consonants");
		table = [["Language", "Vowel inventory size"]];
		table.push.apply(table, zip(map_data.map(function(item) {return item[0]}), data["inv_sizes"]["vows"]));
		addInventoryHistogram(table, "Inventory sizes: vowels");
	}
}

function addTableOfCommonPhons(divText) {
	var charArr = divText.split(""),
		result  = [];
	charArr.map(function(chr) {
		if (chr != "\\") {
			result.push(chr);
		}
	});
	var newDiv = result.join("");
	$("#reportHolder").append(newDiv);
}

function addInventoryHistogram(table, title) {
	var minVal = +Infinity,
		maxVal = -Infinity;
	for (var i = 1; i < table.length; i++) {
		var val = +table[i][1];
		if (val < minVal) {
			minVal = val;
		}
		if (val > maxVal) {
			maxVal = val;
		}
	}
	var newId = title.replace(" ", "_")
	$("#histogramHolder").append($("<div>").attr("id", newId).attr("class", "chartHolder"))
	var data = google.visualization.arrayToDataTable(table);
	var options = {
		// chartArea: {left: 35, width: 735, top: 35, height: 385},
		width: "100%",
		height: 450,
		colors: ['green'],
		titleTextStyle: {
			fontName: "open sans",
			fontSize: 16
		},
		histogram: {bucketSize: 5},
		title: title,
		legend: {position: "none"},
	};
	var chart = new google.visualization.Histogram(document.getElementById(newId));
	chart.draw(data, options);
}

function showSearchPage() {
	$("#main").empty();
	$("#main").css({"height": "auto", "background-color": "white"});
	var searchFields = $("<div>").attr("id", "searchFields");
	var reportCanvas = $("<div>").attr("id", "reportCanvas");
	$("#main").append(searchFields);
	searchFields.append($("<label>").attr("for", "include_dialects").text("Include dialects: "));
	searchFields.append($("<input>").attr("type", "checkbox").attr("id", "include_dialects"));
	searchFields.append($("<br/>"));
	searchFields.append($("<br/>"));
	
	searchFields.append($("<label>").attr("for", "exact_search").text("Exact phoneme search: ").attr("class", "search_label"));
	searchFields.append($("<input>").attr("type", "text").attr("id", "exact_search"));
	searchFields.append($("<input>").attr("type", "button").attr("id", "exact_search_btn").attr("value", "Sumbit").attr("onclick", "sendQuery(this)"));
	searchFields.append($("<p>").attr("class", "info").html(
		"Input a phoneme in terms of IPA symbols. Online tools such as <a href=\"http://ipa.typeit.org/full/\" target=\"_blank\">Type IPA</a> can be used for typing convenience. All inventories including exactly this phoneme will be returned. An example search: ‘t̪s̪ʰʷʲ’."
		))
	searchFields.append($("<br/>"));
	
	searchFields.append($("<label>").attr("for", "superset_search").text("Fuzzy phoneme search: ").attr("class", "search_label"));
	searchFields.append($("<input>").attr("type", "text").attr("id", "superset_search"));
	searchFields.append($("<input>").attr("type", "button").attr("id", "superset_search_btn").attr("value", "Sumbit").attr("onclick", "sendQuery(this)"));
	searchFields.append($("<p>").attr("class", "info").html(
		"Input a base phoneme in terms of IPA symbols. The search engine will provide all phonemes from the database which include all the features of the base phoneme along with their distributions. An example search: ‘p’."
		))
	searchFields.append($("<br/>"));
	
	searchFields.append($("<label>").attr("for", "multiple_search").text("Multiple phoneme search: ").attr("class", "search_label"));
	searchFields.append($("<input>").attr("type", "text").attr("id", "multiple_search"));
	searchFields.append($("<input>").attr("type", "button").attr("id", "multiple_search_btn").attr("value", "Sumbit").attr("onclick", "sendQuery(this)"));
	searchFields.append($("<p>").attr("class", "info").html(
		"Input a list of comma-separated phonemes in terms of IPA symbols. Some or all of the phonemes can be preceded by a ‘-’ symbol. A list of inventories having all the phonemes without ‘-’ and lacking all the phonemes with ‘-’ will be returned. An example search: ‘a, -b, cʰ, -dʲ’."
		))
	searchFields.append($("<br/>"));
	
	searchFields.append($("<label>").attr("for", "feature_search").text("Feature search: ").attr("class", "search_label"));
	searchFields.append($("<input>").attr("type", "text").attr("id", "feature_search"));
	searchFields.append($("<input>").attr("type", "button").attr("id", "feature_search_btn").attr("value", "Sumbit").attr("onclick", "sendQuery(this)"));
	searchFields.append($("<p>").attr("class", "info").html(
		"Input a list of comma-separated IPA features. Some or all of the features can be preceded by a ‘-’ symbol. A list of inventories having segments exhibiting all the features without ‘-’ and lacking all the features with ‘-’ will be returned. Features can be simple (‘plosive’, ‘glottalised’, 'triphthong') or composite (‘voiceless fricative’, ‘retroflex tap’). An example search: ‘voiced lateral fricative, -lateral affricate’.<br />The following features are supported: <em>advanced, advanced-tongue-root, affricate, affricated, alveolar, alveolo-palatal, apical, approximant, aspirated, back, bilabial, breathy-voiced, central, centralised, close, close-mid, creaky-voiced, dental, diphthong, epiglottal, faucalised, fricative, front, glottal, glottalised, half-long, hissing-hushing, implosive, labial-palatal, labial-velar, labialised, labiodental, lateral, lateral-released, less-rounded, long, lowered, mid, mid-centralised, more-rounded, nasal, nasalised, near-back, near-close, near-front, near-open, non-syllabic, open, open-mid, palatal, palatal-velar, palatalised, pharyngeal, pharyngealised, plosive, postalveolar, pre-aspirated, pre-glottalised, pre-labialised, pre-nasalised, raised, retracted, retracted-tongue-root, retroflex, rhotic, rounded, syllabic, tap, trill, triphthong, ultra-short, unreleased, unrounded, uvular, velar, velarised, voiced, voiceless, weakly-articulated</em>."
		))
	$("#main").append(reportCanvas);
}

function showSegmentView() {
	$("#main").empty();
	$("#main").css({"height": "auto", "background-color": "white", "overflow": "auto"});
	$.ajax({
		url: "http://eurasianphonology.info/jsonp",
		dataType: "jsonp",
		data: {
			requestAllSegments: "true",
			myCallback: "populateSegmentView"
		}
	});
}

function populateSegmentView(data) {
	$("#main").append(clearHTML(data));
	$(".phono_tables").css({"margin-left": "30px", "margin-right": "30px"});
}

function searchForThis(s) {
	var myCallback = "clearAndFormat";
	var query = $(s).text();
	$.ajax({
			url: "http://eurasianphonology.info/jsonp",
			dataType: "jsonp",
			data: {
				dialects: "dialects",
				search_type: "exact",
				myCallback: myCallback,
				query: query
			}	
		});
}

function clearAndFormat(data) {
	$("#main").empty();
	var reportCanvas = $("<div>").attr("id", "reportCanvas");
	$("#main").append(reportCanvas);
	formatList(data);
}

function sendQuery(btn) {
	var search_type;
	var query;
	switch (btn.id) {
		case "exact_search_btn":
			search_type = "exact";
			query = $("#exact_search").val();
			break;
		case "superset_search_btn":
			search_type = "superset";
			query = $("#superset_search").val();
			break;
		case "multiple_search_btn":
			search_type = "exact_multiple";
			query = $("#multiple_search").val();
			break
		case "feature_search_btn":
			search_type = "feature";
			query = $("#feature_search").val();
	}
	if (query === "") {
		return
	}
	var callback;
	if (search_type == "superset") {
		callback = "formatDictionary";
	} else {
		callback = "formatList";
	}
	if ($("#include_dialects").is(":checked")) {
		$.ajax({
			url: "http://eurasianphonology.info/jsonp",
			dataType: "jsonp",
			data: {
				dialects: "dialects",
				search_type: search_type,
				myCallback: callback,
				query: query
			}	
		});	
	} else {
		$.ajax({
			url: "http://eurasianphonology.info/jsonp",
			dataType: "jsonp",
			data: {
				search_type: search_type,
				myCallback: callback,
				query: query
			}	
		});	
	}
}

function formatList(data) {
	$("#reportCanvas").empty();
	var searchType = data[0];
	var query = data[1];
	var n_langs = data[2].length;
	var queryType;
	switch (searchType) {
		case "exact":
			queryType = "phoneme";
			break;
		case "superset":
			queryType = "base phoneme";
			break;
		case "exact_multiple":	
			queryType = "combination of phonemes";
			break;
		case "feature":	
			queryType = "combination of features";
			break;
	}
	if (n_langs == 0) {
		$("#reportCanvas").append($("<h4>").text("The " + queryType + " " + query + " was not found"));		
	} else {
		$("#reportCanvas").append($("<div>").attr("id", "map_canvas").css({"width": "800px", "height": "400px", "margin-top": "30px"}))
		var center = new google.maps.LatLng(48, 87.637515);
		var mapOptions = {
				zoom: 2,
				center: center,
				mapTypeId: google.maps.MapTypeId.SATELLITE
			};
		var map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
		$("#reportCanvas").append($("<h4>").text("The " + queryType + " " + query + " was found in " + n_langs + " languages:"));
		var t = $("<table>").attr("class", "languageList");
		$("#reportCanvas").append(t);
		for (var i = 0; i < data[2].length; i++) {
			var latLng = new google.maps.LatLng(data[2][i][2], data[2][i][3]);
			var marker = new google.maps.Marker({
				position: latLng,
				map: map,
				title: data[2][i][0] + ", " + data[2][i][5] + ", " + data[2][i][4],
				icon: {
					path: google.maps.SymbolPath.CIRCLE,
					fillColor: "yellow",
					fillOpacity: 1,
					scale: 6,
					strokeWeight: 1,
					strokeColor: "black"
				}
			});
			var row = $("<tr>");
			for (var j = 0; j < data[2][i].length; j++) {
				row.append($("<td>").text(data[2][i][j]));
			}
			t.append(row);
		}
	}

}

function formatDictionary(data) {
	$("#reportCanvas").empty();
	var query = data[0];
	var report = data[1];
	var keys = [];
	for (var key in report) {
		if (report.hasOwnProperty(key)) {
			keys.push(key);
		}
	}
	if (keys.length == 0) {
		$("#reportCanvas").append($("<h4>").text("The base phoneme " + query + " was not found"));		
	} else {
		$("#reportCanvas").append($("<h4>").text("The base phoneme " + query + " has " + keys.length + " variants:"));
		keys.sort();
		for (var i = 0; i < keys.length; i++) {
			addSubreport(keys[i], report[keys[i]]);
		}
	}
}

function addSubreport(phoneme, langTable) {
	var p = $("<p>")
	p.append($("<b>").text(phoneme + ", " + langTable.length + " languages: "))
	var langList = [];
	for (var i = 0; i < langTable.length; i++) {
		langList.push(langTable[i][0]);
	}
	p.append(langList.join(', '));
	$("#reportCanvas").append(p);
	var mapCanvasId = "map_canvas_" + phoneme;
	$("#reportCanvas").append($("<div>").attr("id", mapCanvasId).css({"width": "800px", "height": "400px", "margin-top": "30px"}))
	var center = new google.maps.LatLng(48, 87.637515);
	var mapOptions = {
			zoom: 2,
			center: center,
			mapTypeId: google.maps.MapTypeId.SATELLITE
		};
	var map = new google.maps.Map(document.getElementById(mapCanvasId), mapOptions);
	for (var i = 0; i < langTable.length; i++) {
		langList.push(langTable[i][0]);
		var latLng = new google.maps.LatLng(langTable[i][2], langTable[i][3]);
		var marker = new google.maps.Marker({
			position: latLng,
			map: map,
			title: langTable[i][0] + ", " + langTable[i][5] + ", " + langTable[i][4],
			icon: {
				path: google.maps.SymbolPath.CIRCLE,
				fillColor: "yellow",
				fillOpacity: 1,
				scale: 6,
				strokeWeight: 1,
				strokeColor: "black"
			}
		});
	}
}

function showListView() {
	$("#main").empty();
	$("#main").css({"height": "auto", "background-color": "white"});
	var container = $("<div>").css({"margin-left": "30px", "margin-top": "20px"});
	$("#main").append(container);
	
	var threeListsDiv = $("<div>").attr("id", "threeListsDiv").css({
		"width": "300px",
		"float": "left",
		"display": "inline-block"
	});
	var familyList = $("<select>").attr("id", "familyList").attr("class", "listViewList").attr("onchange", "repopulateListGroups()");
	var groupList  = $("<select>").attr("id", "groupList").attr("class", "listViewList").attr("onchange", "repopulateListLangs()");
	var langList   = $("<select>").attr("id", "langList").attr("class", "listViewList");
	var langBtn    = $("<input>").attr("type", "button").attr("onclick", "showDataBelow(this)").attr("id", "listViewBtn").attr("value", "Show data");
	threeListsDiv.append($("<p>").text("Languages by families and groups:").css({"margin": "0"}));
	threeListsDiv.append(familyList);
	threeListsDiv.append($("<br/>"));
	threeListsDiv.append(groupList);
	threeListsDiv.append($("<br/>"));
	threeListsDiv.append(langList);
	threeListsDiv.append($("<br/>"));
	threeListsDiv.append(langBtn);
	var fam_array = [];
	for (var family in phyloData) {
		if (phyloData.hasOwnProperty(family)) {
			fam_array.push(family);
		}
	}
	fam_array.sort();
	for (var i = 0; i < fam_array.length; i++) {
		familyList.append($("<option>").attr("value", fam_array[i]).text(fam_array[i]));	
	}
	var currentFam = familyList.val();
	if (phyloData[currentFam].length == 0) {
		groupList.append($("<option>").attr("value", "—").text("—"));
	} else {
		var group_arr = [];
		phyloData[currentFam].map(function(group) {
			group_arr.push(group);
		});
		group_arr.sort()
		for (var i = 0; i < group_arr.length; i++) {
			groupList.append($("<option>").attr("value", group_arr[i]).text(group_arr[i]));
		}
	}
	var currentGroup = groupList.val()
	if (currentGroup == '-') {
		isolates.sort();
		for (var i = 0; i < isolates.length; i++) {
			langList.append($("<option>").attr("value", isolates[i]).text(isolates[i]));
		}
	} else {
		var langsInGroup = groupData[currentGroup];
		langsInGroup.sort();
		for (var i = 0; i < langsInGroup.length; i++) {
			langList.append($("<option>").attr("value", langsInGroup[i]).text(langsInGroup[i].split("#")[0]));
		}
	}

	var alphaDiv = $("<div>").attr("id", "alphaDiv").css({
		"width": "300px",
		"float": "left",
		"display": "inline-block"
	})
	alphaDiv.append($("<p>").text("Languages in the alphabetical order:").css({"margin": "0"}));
	var alphaList = $("<select>").attr("id", "alphaList").attr("class", "listViewList");
	var alphaLangBtn   = $("<input>").attr("type", "button").attr("onclick", "showDataBelow(this)").attr("id", "listViewAlphaBtn").attr("value", "Show data");
	alphaDiv.append(alphaList);
	var alphaLangs = [];
	for (var i = 0; i < isolates.length; i++) {
		alphaLangs.push(isolates[i]);
	}
	for (var group in groupData) {
		for (var i = 0; i < groupData[group].length; i++) {
			alphaLangs.push(groupData[group][i]);
		}
	}
	alphaLangs.sort(function(a, b) {
		return a.toLowerCase().localeCompare(b.toLowerCase());
	});
	alphaLangs.map(function(lang) {
		alphaList.append($("<option>").attr("value", lang).text(lang.split("#")[0]))
	});
	alphaDiv.append($("<br/>"));
	alphaDiv.append(alphaLangBtn);

	var listReportDiv = $("<div>").attr("id", "listReport").css({"width": "100%", "display": "inline-block", "float": "left"});
	
	container.append(threeListsDiv);
	container.append(alphaDiv);
	container.append($("<br/>"));
	container.append(listReportDiv);
}

function repopulateListGroups(familyList) {
	var currentFam = $("#familyList").val();
	var groupList  = $("#groupList");
	groupList.empty();
	if (phyloData[currentFam].length == 0) {
		groupList.append($("<option>").attr("value", "—").text("—"));
	} else {
		var group_arr = [];
		phyloData[currentFam].map(function(group) {
			group_arr.push(group);
		});
		group_arr.sort()
		for (var i = 0; i < group_arr.length; i++) {
			groupList.append($("<option>").attr("value", group_arr[i]).text(group_arr[i]));
		}
	}
	repopulateListLangs();
}

function repopulateListLangs() {
	var currentGroup = $("#groupList").val();
	var langList  = $("#langList");
	langList.empty();
	if ($("#familyList").val() === 'Isolate') {
		isolates.sort();
		for (var i = 0; i < isolates.length; i++) {
			langList.append($("<option>").attr("value", isolates[i]).text(isolates[i].split("#")[0]));
		}
	} else {
		var langsInGroup = groupData[currentGroup];
		langsInGroup.sort();
		for (var i = 0; i < langsInGroup.length; i++) {
			langList.append($("<option>").attr("value", langsInGroup[i]).text(langsInGroup[i].split("#")[0]));
		}
	}
}

function showDataBelow(btn) {
	var lr = $("#listReport");
	lr.empty();
	if (btn.parentNode.id === "threeListsDiv") {
		var langId = $("#langList").val();
	} else {
		var langId = $("#alphaList").val();
	}
	$.ajax({
		url: "http://eurasianphonology.info/jsonp",
		dataType: "jsonp",
		data: {
			provideInventoryTable: langId,
			myCallback: "displayTableInListView"
		}
	});
}

function displayTableInListView(data) {
	$("#listReport").append(clearHTML(data));
}