import React from "react";
import styles from "./SymbolBar.module.scss";
import { MeasurementType } from "../../constants/types";
import Symbols from "../../constants/symbols";
import EarSymbol from "../../components/annotation/EarSymbol";

interface Props {
  ear: string;
  display: boolean;
  selectedMeasurementType: MeasurementType | null;
  setMeasurementType: (measurementType: MeasurementType) => void;
}

function SymbolBar(props: Props) {
  return (
    <div className={`${styles.symbolBar} ${!props.display && styles.hidden}`}>
      {Object.entries(Symbols)
        .filter(symbol => symbol[1].ear === props.ear)
        .map((symbol, i) => (
          <EarSymbol
            key={`left-ear-symbol-${i}`}
            symbol={symbol[1]}
            selected={props.selectedMeasurementType === symbol[1].string}
            setMeasurementType={props.setMeasurementType}
            path={symbol[1].path}
            color={symbol[1].color}
          />
        ))}
    </div>
  );
}

export default SymbolBar;
