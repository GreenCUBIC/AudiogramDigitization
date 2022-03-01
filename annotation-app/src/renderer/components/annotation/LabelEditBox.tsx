/**
 * Copyright (c) Carleton University Biomedical Informatics Collaboratory
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { useState } from "react"
import styles from "./LabelEditBox.module.scss"

interface Props {
  editedLabel: { audiogramIndex: number; labelIndex: number }
  setValue: (value: string) => void
}

function LabelEditBox(props: Props) {
  const [labelType, setLabelType] = useState("frequency")

  if (!props.editedLabel) return null

  return (
    <foreignObject x={120} y={120} height={300} width={600}>
      <div className={styles.container}>
        <div className={styles.labelTypeSelectors}>
          <button
            className={`${styles.labelTypeButton} ${
              labelType === "frequency" && styles.selected
            }`}
            onClick={() => setLabelType("frequency")}
          >
            Frequency
          </button>
          <button
            className={`${styles.labelTypeButton} ${
              labelType === "threshold" && styles.selected
            }`}
            onClick={() => setLabelType("threshold")}
          >
            Threshold
          </button>
        </div>
        {labelType === "frequency" && (
          <div className={styles.labelOptions}>
            <div className={styles.row}>
              {["250", "500", "1000", "2000", "4000", "8000"].map((label) => (
                <button
                  className={styles.labelButton}
                  onClick={() => props.setValue(label)}
                >
                  {label}
                </button>
              ))}
            </div>
            <div className={styles.row}>
              {[".25", ".5", "1", "2", "4", "8"].map((label) => (
                <button
                  className={styles.labelButton}
                  onClick={() => props.setValue(label)}
                >
                  {label}
                </button>
              ))}
            </div>
            <div className={styles.row}>
              {["1K", "2K", "4K", "8K"].map((label) => (
                <button
                  className={styles.labelButton}
                  onClick={() => props.setValue(label)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}
        {labelType === "threshold" && (
          <div className={styles.labelOptions}>
            <div className={styles.row}>
              {["0", "20", "40", "60", "80", "100", "120"].map((label) => (
                <button
                  className={styles.labelButton}
                  onClick={() => props.setValue(label)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </foreignObject>
  )
}

export default LabelEditBox
