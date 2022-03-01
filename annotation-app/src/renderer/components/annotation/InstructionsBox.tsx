/**
 * Copyright (c) Carleton University Biomedical Informatics Collaboratory
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react"
import styles from "./InstructionsBox.module.scss"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import {
  faArrowLeft,
  faArrowRight,
  faCheckCircle,
} from "@fortawesome/free-solid-svg-icons"
import { Annotation, AnnotationStep, Report } from "../../constants/types"

const DEFAULT_STATE: any = {
  step: 0,
  zoomFactor: 0.6,
  selectedMeasurementType: null,
  editedLabel: null,
  offset: {
    x: 0,
    y: 0,
  },
  isDraggingImage: false,
  isDraggingBoundingBox: false,
  origin: {
    x: 0,
    y: 0,
  },
  annotation: {
    valid: true,
    reason: null,
    comment: "",
    audiograms: [],
  },
}

interface Props {
  report: Report
  loadReport: () => void
  step: AnnotationStep
  annotation: Annotation
  initializeAnnotation: (annotation: string) => void
  comment: string
  onUpdateComment: (e: React.ChangeEvent<HTMLInputElement>) => void
  onNextStep: () => void
  onPreviousStep: () => void
  onSubmit: (e: React.MouseEvent) => void
  runDigitizer: () => void
}

function InstructionsBox(props: Props) {
  const instructions = (() => {
    switch (props.step) {
      case AnnotationStep.AnnotationSelection:
        return (
          <div>
            <button onClick={props.loadReport}>Load report</button>
            <p className={`${styles.instructionsDetails}`}>
              {/*Click below to attempt to generate a seed annotation with the digitizer.
              <button onClick={props.runDigitizer}>Start from digitizer</button> */}
            </p>
          </div>
        )
      case AnnotationStep.AudiogramAnnotation:
        return (
          <div>
            <div className={`${styles.instructionsTitle}`}>
              Please draw bounding boxes around the audiogram(s) in the report
            </div>
            <p className={`${styles.instructionsDetails}`}>
              The bounding boxes must capture all the audiogram, ie. include the
              axes title and labels. left-click and drag to draw the boxes, and
              right-click and drag to move the image.
            </p>
          </div>
        )
      case AnnotationStep.LabelAnnotation:
        return (
          <div>
            <div className={`${styles.instructionsTitle}`}>
              Please draw bounding boxes around the axes labels that fall{" "}
              <b>along major lines</b>.
            </div>
            <p className={`${styles.instructionsDetails}`}>
              Please draw bounding boxes around the axes labels and select the
              matching label value from the appearing menu. For frequencies (x
              axis), only annotate 250, 500, 1000, 2000, 4000 and 8000 Hz. For
              thresholds (y axis) only label 0, 20, 40, 60, 80, 100 and 120 dB.
              You can change the label value with a left click and delete a
              label with a right click.
              <br />
              <b>
                If a label is completely obstructed or is indistinguishable,
                skip it. If it appears more than once, annotate all occurences
                in the audiogram(s).
              </b>
            </p>
          </div>
        )
      case AnnotationStep.CornerAnnotation:
        return (
          <div>
            <div className={`${styles.instructionsTitle}`}>
              Please click on the four corners in all audiograms
            </div>
            <p className={`${styles.instructionsDetails}`}>
              <ul>
                <li>
                  Click on the four outermost corners of the audiogram and set
                  the corresponding frequency/threshold values by clicking on
                  the values until the correct values are set.
                </li>
                <li>
                  These may or may not be line intersections. If they are not,
                  please use your best judgement to indicate these locations.
                </li>
                <li>Right-click on a corner to delete it.</li>
              </ul>
            </p>
          </div>
        )
      case AnnotationStep.SymbolAnnotation:
        return (
          <div>
            <div className={`${styles.instructionsTitle}`}>
              Please indicate the position of the audiogram symbols
            </div>
            <p className={`${styles.instructionsDetails}`}>
              <ul className={`${styles.noMargin}`}>
                <li>
                  Select a symbol that appears in the audiograms from the
                  toolbars.
                </li>
                <li>
                  Click on the center of the symbol and scroll to adjust the
                  bounding box size, so that the symbol fits correctly in the
                  bounding box (you can also drag the marker to adjust its
                  position). You may also delete it by right-clicking.
                </li>
                <li>Do not include no response arrows in the bounding boxes</li>
                <li>
                  To indicate that no response was recorded (denoted by a small
                  arrow), double click on the circle to make it hollow.
                </li>
              </ul>
            </p>
          </div>
        )
      case AnnotationStep.Review:
        return (
          <div>
            <div className={`${styles.instructionsTitle}`}>
              Please review the annotation
            </div>
            <p className={`${styles.instructionsDetails}`}>
              The annotation will be saved to the file {props.report && props.report.filepath.split(".")[0] + ".json "}
              when you click to save.
            </p>
          </div>
        )

      default:
        return null
    }
  })()
  return (
    <div className={`${styles.instructionsContainer}`}>
      <div
        className={`${styles.iconWrapper} ${
          props.step === AnnotationStep.AnnotationSelection && styles.hidden
        }`}
        onClick={props.onPreviousStep}
      >
        <FontAwesomeIcon size="lg" icon={faArrowLeft} />
      </div>
      <div>{instructions}</div>

      {props.step !== AnnotationStep.Review && (
        <div className={`${styles.iconWrapper}`} onClick={props.onNextStep}>
          <FontAwesomeIcon size="lg" icon={faArrowRight} />
        </div>
      )}
      {props.step === AnnotationStep.Review && (
        <div className={`${styles.iconWrapper}`} onClick={props.onSubmit}>
          <FontAwesomeIcon size="lg" icon={faCheckCircle} />
        </div>
      )}
    </div>
  )
}

export default InstructionsBox
