// data
const filename = 'rec-gens.json'
let data = await d3.json(`data/${filename}`);


const xVar = 'recipient generations';
const yVar = 'clumpiness';
data = makeLong(data, yVar);


// plot
let fig = Plot.plot({
	grid: true,
	margin: 50,
	y: {domain: [0, 1]},
	marks: [
		Plot.frame(),
		Plot.boxY(
			data,
			{
				x: xVar,
				y: yVar,
				fx: 'direction',
				fill: 'direction'
			}
		)
	]
});

document.querySelector('body').append(fig);


// helpers
function makeLong(data, variable) {
	let longData = [];
	data.forEach(d => {
		let same = {};
		let different = [];
		for (const [key, value] of Object.entries(d)) {
			if (key.includes(variable)) {
				const words = key.split(' ');
				const direction = words[words.length - 1];
				different.push({
					direction: direction,
					[variable]: d[`${variable} ${direction}`]
				});
			} else {
				same[key] = value;
			}

		}

		for (let observation of different) {
			longData.push({...same, ...observation});
		}
	});

	return longData;
}
