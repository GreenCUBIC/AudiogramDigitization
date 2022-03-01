/**
 * Copyright (c) Carleton University Biomedical Informatics Collaboratory
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react"
import styles from "./Audiogram.module.scss"
import { Audiogram } from "../../constants/types"

interface Props {
  index: number
  offset: { x: number; y: number }
  audiogram: Audiogram
  zoomFactor: number
  dispatch: (action: any) => void
  updateAudiogramBoundingBox: (e: React.MouseEvent) => void
  removeAudiogram: (index: number) => void
  onMouseMove: (e: React.MouseEvent, index: number) => void
  showRemoveButton: boolean
  onMouseDown: (e: React.MouseEvent, index: number) => void
  removeCorner: (
    e: React.MouseEvent,
    audiogramIndex: number,
    cornerIndex: number
  ) => void
  onMouseUp: (e: React.MouseEvent, audiogramIndex: number) => void
  onWheel: (e: React.WheelEvent) => void
  children: any
}

function AudiogramComp(props: Props) {
  const {
    index,
    audiogram,
    zoomFactor,
    offset,
    onMouseDown,
    removeAudiogram,
    onMouseUp,
    onMouseMove,
    onWheel,
    showRemoveButton,
  } = props
  return (
    <g>
      {/* The audiogram's bounding box */}
      <rect
        className={`${styles.audiogramBoundingBox}`}
        x={zoomFactor * audiogram.boundingBox.x + offset.x}
        y={zoomFactor * audiogram.boundingBox.y + offset.y}
        height={audiogram.boundingBox.height * zoomFactor}
        width={audiogram.boundingBox.width * zoomFactor}
        onMouseMove={(e) => onMouseMove(e, index)}
        onMouseUp={(e) => onMouseUp(e, index)}
        onMouseDown={(e) => onMouseDown(e, index)}
        onWheel={onWheel}
      />

      {showRemoveButton && (
        <g
          className={`${styles.deleteBox}`}
          onClick={() => removeAudiogram(index)}
        >
          <circle
            r={10}
            cx={
              zoomFactor *
                (audiogram.boundingBox.x + audiogram.boundingBox.width) +
              offset.x -
              10
            }
            cy={zoomFactor * audiogram.boundingBox.y + offset.y - 10}
            fill="red"
          />
          <text
            x={
              zoomFactor *
                (audiogram.boundingBox.x + audiogram.boundingBox.width) +
              offset.x -
              5 -
              10
            }
            y={zoomFactor * audiogram.boundingBox.y + offset.y - 5}
          >
            X
          </text>
        </g>
      )}
      {props.children}
    </g>
  )
}

export default AudiogramComp
