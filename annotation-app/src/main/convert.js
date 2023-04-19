/**
 * Rounds a frequency to one of the cannonical frequencies tested in
 * pure-tone audiometry.
 *
 * @param {*} freq
 */
function roundFrequency(freq) {
  const STANDARD_FREQUENCIES = [
    125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000,
  ];

  let minDist = 100000;
  let indexOfClosestFrequency = -1;
  for (let i = 0; i < STANDARD_FREQUENCIES.length; i++) {
    const dist = Math.abs(freq - STANDARD_FREQUENCIES[i]);
    if (dist < minDist) {
      minDist = dist;
      indexOfClosestFrequency = i;
    }
  }

  return STANDARD_FREQUENCIES[indexOfClosestFrequency];
}

/**
 * Rounds a threshold value to the nearest multiple of 5.
 *
 * @param {*} threshold
 */
function roundThreshold(threshold) {
  function numberRange(start, end) {
    return new Array(end - start).fill().map((d, i) => i + start);
  }

  const STANDARD_THRESHOLDS = numberRange(-4, 27).map((x) => x * 5);
  let minDist = 100000;
  let indexOfClosestThreshold = -1;
  for (let i = 0; i < STANDARD_THRESHOLDS.length; i++) {
    const dist = Math.abs(threshold - STANDARD_THRESHOLDS[i]);
    if (dist < minDist) {
      minDist = dist;
      indexOfClosestThreshold = i;
    }
  }

  return STANDARD_THRESHOLDS[indexOfClosestThreshold];
}

/**
 * Converts the frequency to an octave value (125 being the 0th octave.)
 *
 * @param {*} freq
 * @returns The frequency in octave domain.
 */
function frequencyToOctave(freq) {
  return Math.log(freq / 125) / Math.log(2);
}

/**
 * Converts the octave to a frequency value (125 being the 0th octave.)
 *
 * @param {*} octave
 * @returns The octave in frequency domain.
 */
function octaveToFrequency(octave) {
  return 125 * Math.pow(2, octave);
}

/**
 * Gets the x-location -> frequency and y-location to threshold value
 * conversion maps
 */
function extractMaps(annotation, audiogramIndex) {
  const topLeftCorner = annotation.audiograms[audiogramIndex].corners.filter(
    (c) => c.position.horizontal === 'left' && c.position.vertical === 'top'
  )[0];
  const topRightCorner = annotation.audiograms[audiogramIndex].corners.filter(
    (c) => c.position.horizontal === 'right' && c.position.vertical === 'top'
  )[0];
  const bottomLeftCorner = annotation.audiograms[audiogramIndex].corners.filter(
    (c) => c.position.horizontal === 'left' && c.position.vertical === 'bottom'
  )[0];

  const oMin = frequencyToOctave(topLeftCorner.frequency);
  const xMin = topLeftCorner.x;
  const oMax = frequencyToOctave(topRightCorner.frequency);
  const xMax = topRightCorner.x;
  const freqMap = (xPos) =>
    octaveToFrequency(oMin + ((oMax - oMin) * (xPos - xMin)) / (xMax - xMin));

  const tMin = topLeftCorner.threshold;
  const yMin = topLeftCorner.y;
  const tMax = bottomLeftCorner.threshold;
  const yMax = bottomLeftCorner.y;
  const thresholdMap = (yPos) =>
    tMin + ((tMax - tMin) * (yPos - yMin)) / (yMax - yMin);

  return [freqMap, thresholdMap];
}

/**
 * Converts an annotation generated with the annotation software
 * to a list of thresholds.
 *
 * @param annotation
 */
export function extractThresholdsFromAnnotation(annotation) {
  const thresholdsList = [];
  const [freqMap, thresholdMap] = extractMaps(annotation, 0);
  for (let aid = 0; aid < annotation.audiograms.length; aid++) {
    for (let i = 0; i < annotation.audiograms[aid].symbols.length; i++) {
      const symbol = annotation.audiograms[aid].symbols[i];
      let x = symbol.boundingBox.x + symbol.boundingBox.width / 2;
      let y = symbol.boundingBox.y + symbol.boundingBox.height / 2;
      const frequency = roundFrequency(freqMap(x));
      const threshold = roundThreshold(thresholdMap(y));
      thresholdsList.push({
        ear: symbol.measurementType.split('_')[2].toLowerCase(),
        conduction: symbol.measurementType.split('_')[0].toLowerCase(),
        masking:
          symbol.measurementType.split('_')[1].toLowerCase() === 'unmasked'
            ? false
            : true,
        frequency,
        threshold,
        responseRecorded: symbol.response,
      });
    }
  }
  return thresholdsList;
}

export function thresholdListAsCSVString(thresholdsList) {
  let header = 'ear,conduction,masking,frequency,threshold,response\n';
  thresholdsList.forEach((threshold) => {
    header += `${threshold.ear},${threshold.conduction},${threshold.masking},${threshold.frequency},${threshold.threshold},${threshold.responseRecorded}\n`;
  });
  return header;
}
