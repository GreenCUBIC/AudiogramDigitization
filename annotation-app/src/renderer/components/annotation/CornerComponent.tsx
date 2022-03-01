/**
 * Copyright (c) Carleton University Biomedical Informatics Collaboratory
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react"
import styles from "./CornerComponent.module.scss"
import { Corner } from "../../constants/types"

interface Props {
  x: number
  y: number
  audiogramIndex: number
  cornerIndex: number
  corner: Corner
  showEditBox: boolean
  updateCornerFrequency: (
    sign: number,
    audiogramIndex: number,
    cornerIndex: number
  ) => void
  updateCornerThreshold: (
    sign: number,
    audiogramIndex: number,
    cornerIndex: number
  ) => void
  onRemoveCorner: (
    e: React.MouseEvent,
    audiogramIndex: number,
    cornerIndex: number
  ) => void
}

function CornerComponent(props: Props) {
  const {
    x,
    y,
    corner,
    audiogramIndex,
    cornerIndex,
    updateCornerFrequency,
    updateCornerThreshold,
    showEditBox,
  } = props

  return (
    <g>
      {showEditBox ? (
        <foreignObject
          className={styles.foreignObj}
          x={corner.position.horizontal === "right" ? x + 10 : x - 170}
          y={y - 25}
        >
          <div className={`${styles.cornerCoordinatesContainer}`}>
            <button
              onClick={() =>
                updateCornerFrequency(-1, audiogramIndex, cornerIndex)
              }
            >
              -
            </button>
            <input
              className={`${styles.coordinateInput}`}
              value={corner.frequency + " Hz"}
            />
            <button
              onClick={() =>
                updateCornerFrequency(1, audiogramIndex, cornerIndex)
              }
            >
              +
            </button>
            <br />
            <button
              onClick={() =>
                updateCornerThreshold(-1, audiogramIndex, cornerIndex)
              }
            >
              -
            </button>
            <input
              className={`${styles.coordinateInput}`}
              value={corner.threshold + " dB"}
            />
            <button
              onClick={() =>
                updateCornerThreshold(1, audiogramIndex, cornerIndex)
              }
            >
              +
            </button>
          </div>
        </foreignObject>
      ) : (
        /*<foreignObject height={60} width={100} x={x - 50} y={y - 25}>
          <div
            className={`${styles.cornerLabel}`}
          >{`(${corner.frequency}Hz, ${corner.threshold}dB)`}</div>
      </foreignObject>*/
        <text className={styles.cornerLabel} x={x - 50} y={y - 10}>
          {`(${corner.frequency}Hz, ${corner.threshold}dB)`}
        </text>
      )}
      <circle
        className={`${styles.cornerCircle}`}
        cx={props.x}
        cy={props.y}
        r={4}
        onMouseDown={(e) =>
          props.onRemoveCorner(e, props.audiogramIndex, props.cornerIndex)
        }
      />
    </g>
  )
}

export default CornerComponent
