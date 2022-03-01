/**
 * Copyright (c) Carleton University Biomedical Informatics Collaboratory
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { MeasurementType } from "./types"

export default {
  [MeasurementType.LeftAirUnmasked]: {
    string: MeasurementType.LeftAirUnmasked,
    type: "air",
    masking: false,
    ear: "left",
    path: "M3.7 4.4l56.6 55.8M60.3 4.4L3.7 60.2",
    color: "blue",
  },
  [MeasurementType.LeftAirMasked]: {
    string: MeasurementType.LeftAirMasked,
    type: "air",
    masking: true,
    ear: "left",
    path: "M8.3 7.6h47.5v48.7H8.3z",
    color: "green",
  },
  [MeasurementType.LeftBoneUnmasked]: {
    string: MeasurementType.LeftBoneUnmasked,
    type: "bone",
    masking: false,
    ear: "left",
    path: "M22 5.4l21.9 27.3-21.9 27",
    color: "orange",
  },
  [MeasurementType.LeftBoneMasked]: {
    string: MeasurementType.LeftBoneMasked,
    type: "bone",
    masking: true,
    ear: "left",
    path: "M20.2 7.2h22.1v49.6H20.2",
    color: "violet",
  },
  [MeasurementType.RightAirUnmasked]: {
    string: MeasurementType.RightAirUnmasked,
    type: "air",
    masking: false,
    ear: "right",
    path:
      "M32 6.4c14.1 0 25.6 11.5 25.6 25.6S46.1 57.6 32 57.6 6.4 46.1 6.4 32 17.9 6.4 32 6.4z",
    color: "#a432a8",
  },
  [MeasurementType.RightAirMasked]: {
    string: MeasurementType.RightAirMasked,
    type: "air",
    masking: true,
    ear: "right",
    path: "M32.7 13.6L10 54.1h44.2z",
    color: "#32a883",
  },
  [MeasurementType.RightBoneUnmasked]: {
    string: MeasurementType.RightBoneUnmasked,
    type: "bone",
    masking: false,
    ear: "right",
    path: "M43.9 5.4L22 32.7l21.9 27",
    color: "#b00552",
  },
  [MeasurementType.RightBoneMasked]: {
    string: MeasurementType.RightBoneMasked,
    type: "bone",
    masking: true,
    ear: "right",
    path: "M45.6 7.2H23.5v49.6h22.1",
    color: "#adb005",
  },
}
