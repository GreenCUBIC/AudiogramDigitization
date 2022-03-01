/**
 * Copyright (c) Carleton University Biomedical Informatics Collaboratory
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

export const FREQUENCY_OPTIONS = [
  { value: 125, label: "125Hz" },
  { value: 250, label: "250Hz" },
  { value: 500, label: "500Hz" },
  { value: 1000, label: "1000Hz" },
  { value: 2000, label: "2000Hz" },
  { value: 4000, label: "4000Hz" },
  { value: 8000, label: "8000Hz" },
]

export const MEASUREMENT_TYPE_OPTIONS = [
  { value: { masking: false, conduction: "air" }, label: "Air (no masking)" },
  {
    value: { masking: true, conduction: "air" },
    label: "Air (with masking)",
  },
  {
    value: { masking: false, conduction: "bone" },
    label: "Bone (no masking)",
  },
  {
    value: { masking: true, conduction: "bone" },
    label: "Bone (with masking)",
  },
]
