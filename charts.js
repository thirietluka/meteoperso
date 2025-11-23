// Récupération des éléments canvas pour les graphiques
var cpu_ctx = document.getElementById('cpu_chart');
var ram_ctx = document.getElementById('ram_chart');
var disk_ctx = document.getElementById('disk_chart');

// Création du graphique CPU
var cpu_chart = new Chart(cpu_ctx, {
	type: 'line', 
	data: { labels: [], datasets: [{
		label: '% CPU',
		data: [],
		borderColor: 'red',
		fill: false,
		tension: 0.4
	}]},
	options: {
		responsive: true, // Le graphique s'adapte à la taille de lécran
		animation: false, // Désactive l'animation (rafraîchissement rapide)
		scales: { y: { min: 0, max: 100 } } // axe Y entre 0 et 100 %
	}
});

// Création du graphique RAM
var ram_chart = new Chart(ram_ctx, {
	type: 'line',
	data: { labels: [], datasets: [{
		label: '% RAM',
		data: [],
		borderColor: 'green',
		fill: false,
		tension: 0.4
	}]},
	options: {
		responsive: true,
		animation: false,
		scales: { y: { min: 0, max: 100 } }

	}
});

// Création du graphique disk
var disk_chart = new Chart(disk_ctx, {
	type: 'line',
	data: { labels: [], datasets: [{
		label: '% DISK',
		data: [],
		borderColor: 'blue',
		fill: false,
		tension: 0.4
	}]},
	options: {
		responsive: true,
		animation: false,
		scales: { y: { min: 0, max: 100 } }

	}
});




//Fonction pour récupérer les données depuis le serveur
async function refreshData() {
	try {
		var response = await fetch("/data"); // requête HTTP GET vers la route /data
		var data = await response.json();
		data = data.reverse(); // inverse l'ordre
		console.log(data); // affichage pour debug

		// Création des labels X à partir de la date
		var labels = data.map(item => new Date(item.created_at).toLocaleTimeString());
		console.log(labels);
		
		// Création des valeurs Y pour chaque graphique
		var cpu_values = data.map(item => item.CPU);
		console.log(cpu_values);
		var ram_values = data.map(item => item.RAM); 
		console.log(ram_values);
		var disk_values = data.map(item => item.DISK);
		console.log(disk_values);

		//Mise à jour des graphiques
		cpu_chart.data.labels = labels;
		cpu_chart.data.datasets[0].data = cpu_values;
		cpu_chart.update();

		ram_chart.data.labels = labels;
		ram_chart.data.datasets[0].data = ram_values;
		ram_chart.update();

		disk_chart.data.labels = labels;
		disk_chart.data.datasets[0].data = disk_values;
		disk_chart.update();

	} catch (err) {
		console.error("Erreur lors du fetch:", err);
	}
}

refreshData();
setInterval(refreshData, 2000);

