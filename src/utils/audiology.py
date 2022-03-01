#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import List
import numpy as np

VALID_FREQUENCIES = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000, 16000]
VALID_THRESHOLDS = list(range(-10, 135, 5))
THRESHOLDS = list(range(-10, 130, 10))
OCTAVE_FREQS_HZ = [125, 250, 500, 1000, 2000, 4000, 8000]
INTEROCTAVE_FREQS_HZ = [750, 1500, 3000, 6000]
OCTAVE_FREQS_KHZ = [0.125, 0.25, 0.5, 1, 2, 4, 8]
INTEROCTAVE_FREQS_KHZ = [0.750, 1.5, 3, 6]

def round_threshold(threshold: float) -> int:
    """Returns the nearest multiple of 5 for the threshold input.

    Parameters
    ----------
    threshold : float
    The threshold snapped to the nearest multiple of 5 along the y-axis.

    Returns
    -------
    float
    A ``snapped`` threshold value.
    """
    return VALID_THRESHOLDS[np.argmin([abs(threshold - t) for t in VALID_THRESHOLDS])]

def round_frequency(frequency: float) -> int:
    """Returns the nearest audiologically meaningful frequency.
    Parameters
    ----------
    frequency : float
    The frequency to be snapped to the nearest clinically meaningful frequency.
    Returns
    -------
    float
    A ``snapped`` frequency value.
    """
    return VALID_FREQUENCIES[np.argmin([abs(frequency - f) for f in VALID_FREQUENCIES])]

def round_frequency_bone(frequency: float, direction: str, epsilon: float = 0.15) -> int:
    """Returns the nearest audiologically meaningful frequency.

    Parameters
    ----------
    frequency : float
    The frequency to be snapped to the nearest clinically meaningful frequency.

    epsilon: float
    Distance (in octaves) below which a frequency is considered to be
    exactly on the nearest valid frequency. (default: 0.15 octaves)

    direction: str
    This parameter will influence the snapping behavior as some
    audiologists draw bone conduction symbols next to the target frequency,
    while other draw it right on it.

    epsilon: float
    The frequency will be snapped in to the nearest frequency in the
    provided direction, unless the distance to the nearest
    frequency is < ε (some small distance (IN OCTAVE UNITS), in which
    case the frequency will be snapped to that value.

    Eg:

     1K         2K                   1K        2K
      |         |                     |         |
      | >       | will be snapped to  >         |
      |         |                     |         |

      but if the threshold fell directly (within a very small distance of
      1.5K, it would be snapped to that.

     1K        2K                    1K  1.5K  2K
      |         |                     |         |
      |    >    | will be snapped to  |    >    |
      |         |                     |         |

      because it is really close to 1.5 and the audiologist likely
      intentionally meant to indicate 1.5K rather than 1K.

      Note: ε is a tweakable parameter that can be optimized over the
      dataset.


    Returns
    -------
    float
    A ``snapped`` frequency value.
    """
    assert direction == "left" or direction == "right"

    distances = [abs(frequency_to_octave(frequency) - frequency_to_octave(f)) for f in VALID_FREQUENCIES]
    nearest_frequency_index = np.argmin(distances)

    snapped = None
    if distances[nearest_frequency_index] < epsilon:
        snapped = VALID_FREQUENCIES[nearest_frequency_index]
    elif direction == "left":
        if VALID_FREQUENCIES[nearest_frequency_index] > frequency:
            snapped = VALID_FREQUENCIES[nearest_frequency_index - 1] if nearest_frequency_index > 0 else VALID_FREQUENCIES[nearest_frequency_index]
        else:
            snapped = VALID_FREQUENCIES[nearest_frequency_index]
    else:
        if VALID_FREQUENCIES[nearest_frequency_index] > frequency:
            snapped = VALID_FREQUENCIES[nearest_frequency_index]
        else:
            snapped = VALID_FREQUENCIES[nearest_frequency_index + 1] if nearest_frequency_index < len(VALID_FREQUENCIES) - 1 else VALID_FREQUENCIES[nearest_frequency_index]

    return snapped

def frequency_to_octave(frequency: float) -> float:
    """Converts a frequency (in Hz) to an octave value (linear units).

    By convention, the 0th octave is 125Hz.

    Parameters
    ----------
    frequency : float
    The frequency (a positive real) to be converted to an octave value.

    Returns
    -------
    float
    The octave corresponding to the input frequency.
    """
    return np.log(frequency / 125) / np.log(2)

def octave_to_frequency(octave: float) -> float:
    """Converts an octave to its corresponding frequency value (in Hz).

    By convention, the 0th octave is 125Hz.

    Parameters
    ----------
    octave : float
    The octave to put on a frequency scale.

    Returns
    -------
    float
    The frequency value corresponding to the octave.
    """
    return 125 * 2 ** octave

def stringify_measurement(measurement: dict) -> str:
    """Returns a string describing the measurement type that is compatible
    with the NIHL portal format.

    eg. An air conduction threshold for the right ear with no masking
    would yield the string `AIR_UNMASKED_RIGHT`.

    Parameters
    ----------
    measurement: dict
    A dictionary describing a threshold. Should have the keys `ear`,
    `conduction` and `masking`.

    Returns
    -------
    str
    The string describing the measurement type in the NIHL portal format.
    """
    masking = "masked" if measurement["masking"] else "unmasked"
    return f"{measurement['conduction']}_{masking}_{measurement['ear']}".upper()


def measurement_string_to_dict(measurement_type: str) -> dict:
    """Converts a measurement type string in the NIHL portal format into
    a dictionary with the equivalent information for use with the digitizer.

    eg. `AIR_UNMASKED_RIGHT` would be equivalent to the dictionary:
    {`ear`: `right`, `conduction`: `air`, `masking`: False}

    Parameters
    ----------
    measurement: dict
    A dictionary describing a threshold. Should have the keys `ear`,
    `conduction` and `masking`.

    Returns
    -------
    str
    The string describing the measurement type in the NIHL portal format.
    """
    return {
        "ear": "left" if "LEFT" in measurement_type else "right",
        "conduction": "air" if "AIR" in measurement_type else "bone",
        "masking": False if "UNMASKED" in measurement_type else True
    }
