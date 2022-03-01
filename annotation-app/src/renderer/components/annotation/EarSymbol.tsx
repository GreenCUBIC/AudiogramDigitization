import * as React from "react"
import styles from "./EarSymbol.module.scss"
import { MeasurementType } from "../../constants/types"

interface Props {
  symbol: any // fix
  selected: boolean
  path: string
  color: string
  setMeasurementType: (measurementType: MeasurementType) => void
}

function EarSymbol(props: Props) {
  return (
    <div
      className={`${styles.symbolWrapper} ${props.selected && styles.selected}`}
      onClick={() => props.setMeasurementType(props.symbol.string)}
    >
      <svg viewBox="0 0 64 64" width={20} height={20}>
        <path
          fill="transparent"
          stroke={props.color}
          strokeWidth={15}
          d={props.path}
        />
      </svg>
    </div>
  )
}

export default EarSymbol
