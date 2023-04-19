/**
 * Copyright (c) Carleton University Biomedical Informatics Collaboratory
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { useRef, useEffect, useState } from 'react';
import { useImmerReducer } from 'use-immer';
import {
  Label,
  Coordinates,
  Report,
  Annotation,
  Audiogram,
  Corner,
  Symbol,
  MeasurementType,
  AnnotationStep,
} from '../../constants/types';
import Symbols from '../../constants/symbols';
import styles from './AnnotationBox.module.scss';
import AudiogramComp from './Audiogram';
import CornerComponent from './CornerComponent';
import InstructionsBox from './InstructionsBox';
import SymbolBar from './SymbolBar';
import LabelEditBox from './LabelEditBox';

interface Props {
  height: number;
  width: number;
  report: Report;
  onSubmit: (annotation: Annotation) => void;
  loadReport: () => void;
}
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
    comment: '',
    audiograms: [],
  },
};

const EMPTY_AUDIOGRAM: Audiogram = {
  boundingBox: { x: 0, y: 0, height: 0, width: 0 },
  corners: [],
  symbols: [],
  labels: [],
};

const STEPS: any = {
  // TODO fix type
  0: AnnotationStep.AnnotationSelection,
  1: AnnotationStep.AudiogramAnnotation,
  2: AnnotationStep.CornerAnnotation,
  3: AnnotationStep.LabelAnnotation,
  4: AnnotationStep.SymbolAnnotation,
  5: AnnotationStep.Review,
};

function reducer(state: any, action: any) {
  let audiogram: Audiogram;
  let lastAudiogramIndex = state.annotation.audiograms.length - 1;
  let corners: Corner[];

  switch (action.actionType) {
    case 'RESET':
      return DEFAULT_STATE;
    case 'SET_MEASUREMENT_TYPE':
      if (state.selectedMeasurementType === action.payload) {
        state.selectedMeasurementType = null;
        return state;
      }
      state.selectedMeasurementType = action.payload;
      return state;

    case 'ADD_AUDIOGRAM':
      if (
        STEPS[state.step] !== AnnotationStep.AudiogramAnnotation ||
        state.annotation.audiograms.length === 2
      )
        return;
      state.isDraggingBoundingBox = true;
      state.annotation.audiograms.push({
        ...EMPTY_AUDIOGRAM,
        boundingBox: {
          ...action.payload.origin,
          width: 0,
          height: 0,
        },
      });
      return state;

    case 'ADD_LABEL':
      if (STEPS[state.step] !== AnnotationStep.LabelAnnotation) return state;
      state.isDraggingBoundingBox = true;
      state.annotation.audiograms[action.payload.audiogramIndex].labels.push({
        value: 'unlabeled', // TODO
        boundingBox: {
          ...action.payload.origin,
          width: 0,
          height: 0,
        },
      });
      return state;

    case 'RESIZE_LABEL_BOUNDING_BOX':
      if (STEPS[state.step] !== AnnotationStep.LabelAnnotation) return state;
      const audioIndex = action.payload.audiogramIndex;

      const lastIndex =
        state.annotation.audiograms[audioIndex].labels.length - 1;
      state.annotation.audiograms[audioIndex].labels[lastIndex].boundingBox = {
        ...state.annotation.audiograms[audioIndex].labels[lastIndex]
          .boundingBox,
        width: action.payload.width,
        height: action.payload.height,
      };
      return state;

    case 'REMOVE_LABEL':
      if (STEPS[state.step] !== AnnotationStep.LabelAnnotation) return state;
      const labels = [
        ...state.annotation.audiograms[action.payload.audiogramIndex].labels,
      ];
      state.annotation.audiograms[action.payload.audiogramIndex].labels = [
        ...labels.slice(0, action.payload.labelIndex),
        ...labels.slice(action.payload.labelIndex + 1),
      ];
      state.editedLabel = null;
      return state;

    case 'SET_EDITED_LABEL_VALUE':
      if (STEPS[state.step] !== AnnotationStep.LabelAnnotation) return state;
      state.annotation.audiograms[state.editedLabel.audiogramIndex].labels[
        state.editedLabel.labelIndex
      ].value = action.payload.value;
      state.editedLabel = null;
      return state;

    case 'TOGGLE_LABEL_EDIT_BOX':
      if (STEPS[state.step] !== AnnotationStep.LabelAnnotation) return state;
      if (!state.editedLabel) {
        state.editedLabel = {
          audiogramIndex: action.payload.audiogramIndex,
          labelIndex: action.payload.labelIndex,
        };
      } else {
        state.editedLabel = null;
      }
      return state;

    case 'INITIATE_IMAGE_DRAGGING':
      state.isDraggingImage = true;
      state.origin = { ...action.payload.origin };
      return state;

    case 'RESIZE_AUDIOGRAM_BOUNDING_BOX':
      if (STEPS[state.step] !== AnnotationStep.AudiogramAnnotation)
        return state;
      state.annotation.audiograms[lastAudiogramIndex].boundingBox = {
        ...state.annotation.audiograms[lastAudiogramIndex].boundingBox,
        ...action.payload,
      };
      return state;

    case 'REMOVE_AUDIOGRAM':
      if (STEPS[state.step] !== AnnotationStep.AudiogramAnnotation)
        return state;
      state.annotation.audiograms = [
        ...state.annotation.audiograms.slice(0, action.payload.audiogramIndex),
        ...state.annotation.audiograms.slice(action.payload.audiogramIndex + 1),
      ];
      return state;

    case 'TOGGLE_MOUSEUP':
      // Remove the last bounding box if it is unreasonably small < 50px width/height
      if (
        state.isDraggingBoundingBox &&
        STEPS[state.step] === AnnotationStep.AudiogramAnnotation
      ) {
        let { height, width } =
          state.annotation.audiograms[lastAudiogramIndex].boundingBox;
        if (height < 50 || width < 50) {
          state.annotation.audiograms = state.annotation.audiograms.slice(
            0,
            -1
          );
        }
      }
      if (
        STEPS[state.step] === AnnotationStep.LabelAnnotation &&
        action.payload.audiogramIndex !== -1 &&
        state.isDraggingBoundingBox
      ) {
        let lastLabelIndex =
          state.annotation.audiograms[action.payload.audiogramIndex].labels
            .length - 1;
        let { height, width } =
          state.annotation.audiograms[action.payload.audiogramIndex].labels[
            lastLabelIndex
          ].boundingBox;
        if (height < 25 || width < 25) {
          state.annotation.audiograms[action.payload.audiogramIndex].labels =
            state.annotation.audiograms[
              action.payload.audiogramIndex
            ].labels.slice(0, -1);
        } else {
          state.editedLabel = {
            audiogramIndex: action.payload.audiogramIndex,
            labelIndex: lastLabelIndex,
          };
        }
      }
      state.isDraggingBoundingBox = false;
      state.isDraggingImage = false;
      return state;

    case 'UPDATE_OFFSET':
      state.offset = { ...action.payload.offset };
      return state;

    case 'UPDATE_ZOOM_FACTOR':
      state.zoomFactor = action.payload.zoomFactor;
      state.offset = { ...action.payload.offset };
      return state;

    case 'ADD_CORNER':
      if (
        state.annotation.audiograms[action.payload.audiogramIndex].corners
          .length === 4
      )
        return state;
      let { coordinates } = action.payload;
      audiogram = state.annotation.audiograms[action.payload.audiogramIndex];
      corners = [...audiogram.corners];
      let distanceToLeftEdge = Math.abs(
        coordinates.x - audiogram.boundingBox.x
      );
      let distanceToRightEdge = Math.abs(
        coordinates.x - (audiogram.boundingBox.x + audiogram.boundingBox.width)
      );
      let distanceToTopEdge = Math.abs(coordinates.y - audiogram.boundingBox.y);
      let distanceToBottomEdge = Math.abs(
        coordinates.y - (audiogram.boundingBox.y + audiogram.boundingBox.height)
      );
      const initialFrequency =
        distanceToLeftEdge < distanceToRightEdge ? 125 : 8000;
      const initialThreshold =
        distanceToTopEdge < distanceToBottomEdge ? -10 : 120;
      const top = distanceToTopEdge < distanceToBottomEdge ? 'top' : 'bottom';
      const left = distanceToLeftEdge < distanceToRightEdge ? 'left' : 'right';
      state.annotation.audiograms[action.payload.audiogramIndex].corners = [
        ...state.annotation.audiograms[action.payload.audiogramIndex].corners,
        {
          position: {
            horizontal: left,
            vertical: top,
          },
          x: coordinates.x,
          y: coordinates.y,
          frequency: initialFrequency,
          threshold: initialThreshold,
        },
      ];
      return state;

    case 'UPDATE_CORNER':
      state.annotation.audiograms[action.payload.audiogramIndex].corners[
        action.payload.cornerIndex
      ].frequency = action.payload.frequency;
      state.annotation.audiograms[action.payload.audiogramIndex].corners[
        action.payload.cornerIndex
      ].threshold = action.payload.threshold;
      return state;

    case 'REMOVE_CORNER':
      if (STEPS[state.step] !== AnnotationStep.CornerAnnotation) return state;
      corners = [
        ...state.annotation.audiograms[action.payload.audiogramIndex].corners,
      ];
      state.annotation.audiograms[action.payload.audiogramIndex].corners = [
        ...corners.slice(0, action.payload.cornerIndex),
        ...corners.slice(action.payload.cornerIndex + 1),
      ];
      return state;

    case 'ADD_SYMBOL':
      if (STEPS[state.step] !== AnnotationStep.SymbolAnnotation) return state;
      if (!state.selectedMeasurementType) return state;

      state.annotation.audiograms[action.payload.audiogramIndex].symbols = [
        ...state.annotation.audiograms[action.payload.audiogramIndex].symbols,
        action.payload.symbol,
      ];
      return state;

    case 'RESIZE_SYMBOL_BOUNDING_BOX':
      if (STEPS[state.step] !== AnnotationStep.SymbolAnnotation) return state;
      state.annotation.audiograms[action.payload.audiogramIndex].symbols[
        action.payload.symbolIndex
      ].boundingBox = action.payload.boundingBox;
      return state;

    case 'TOGGLE_SYMBOL_RESPONSE':
      if (STEPS[state.step] !== AnnotationStep.SymbolAnnotation) return state;
      state.annotation.audiograms[action.payload.audiogramIndex].symbols[
        action.payload.symbolIndex
      ].response =
        !state.annotation.audiograms[action.payload.audiogramIndex].symbols[
          action.payload.symbolIndex
        ].response;
      return state;

    case 'START_SYMBOL_DRAGGING':
      if (STEPS[state.step] !== AnnotationStep.SymbolAnnotation) return state;
      state.isDraggingBoundingBox = true;
      state.origin = { ...action.payload.origin };
      return state;

    case 'DRAG_SYMBOL':
      if (STEPS[state.step] !== AnnotationStep.SymbolAnnotation) return state;
      let boundingBox =
        state.annotation.audiograms[action.payload.audiogramIndex].symbols[
          action.payload.symbolIndex
        ].boundingBox;
      state.annotation.audiograms[action.payload.audiogramIndex].symbols[
        action.payload.symbolIndex
      ].boundingBox = {
        ...boundingBox,
        x: boundingBox.x + (action.payload.mouseCoordinates.x - state.origin.x),
        y: boundingBox.y + (action.payload.mouseCoordinates.y - state.origin.y),
      };
      state.origin = { ...action.payload.mouseCoordinates };
      return state;

    case 'END_SYMBOL_DRAG':
      state.isDraggingBoundingBox = false;
      return state;

    case 'REMOVE_SYMBOL':
      if (STEPS[state.step] !== AnnotationStep.SymbolAnnotation) return state;
      let symbols = [
        ...state.annotation.audiograms[action.payload.audiogramIndex].symbols,
      ];
      state.annotation.audiograms[action.payload.audiogramIndex].symbols = [
        ...symbols.slice(0, action.payload.symbolIndex),
        ...symbols.slice(action.payload.symbolIndex + 1),
      ];
      return state;

    case 'NEXT_STEP':
      if (
        STEPS[state.step] === AnnotationStep.AudiogramAnnotation &&
        state.annotation.audiograms.length === 0
      )
        return state;
      if (
        STEPS[state.step] === AnnotationStep.CornerAnnotation &&
        !state.annotation.audiograms.every(
          (audiogram: Audiogram) => audiogram.corners.length === 4
        )
      )
        return state;
      state.step += 1;
      state.selectedMeasurementType = null;
      return state;

    case 'PREVIOUS_STEP':
      state.step -= 1;
      state.selectedMeasurementType = null;
      return state;

    case 'UPDATE_COMMENT':
      state.annotation.comment = action.payload;
      return state;

    case 'INITIALIZE_ANNOTATION':
      state.annotation = action.payload;
      return state;

    case 'INITIALIZE_ANNOTATION_FROM_DIGITIZER':
      state.annotation.audiograms = action.payload;
      return state;

    default:
      throw new Error();
  }
}

/**
 * Returns the mouse button that was clicked.
 *
 * @param {React.MouseEvent} e The mouse event whose button is to be identified.
 * @returns `left` or `right` depending on the mouse button that triggered the event.
 */
function getMouseSide(e: React.MouseEvent): string {
  if (e.nativeEvent.which === 1) {
    return 'left';
  } else {
    return 'right';
  }
}

function AnnotationBox(props: Props) {
  const [state, dispatch] = useImmerReducer(reducer, DEFAULT_STATE);
  const svg = useRef<SVGSVGElement>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (svg && svg.current) {
      svg.current.addEventListener('wheel', (event) => event.preventDefault());
    }
  }, [svg]);

  const runDigitizer = async () => {
    try {
      setLoading(true);
      ////const response: any = await API.getDigitizerAnnotation(
      ////  props.report.reportId
      ////)
      //dispatch({
      //  actionType: "INITIALIZE_ANNOTATION_FROM_DIGITIZER",
      //  payload: response.data,
      //})
      //setLoading(false)
    } catch (e) {
      // TODO display modal
    } finally {
      setLoading(false);
    }
  };

  /**
   * Retrieves the coordinates of the mouse in the image domain, i.e. with
   * respect to the top-left corner of the image at 1x zoom factor, NOT
   * with respect to the top-left corner of the SVG canvas.
   *
   * @param {React.MouseEvent} e A mouse event with information about the cursor locator.
   * @returns {Coordinates} An object corresponding to the cursor position with respect to the top left corner of the image at 1X.
   */
  const getImageDomainCoordinates = (e: React.MouseEvent): Coordinates => {
    e.preventDefault();
    const svgEl = document.getElementById('svg-box');
    const svgRect = svgEl?.getBoundingClientRect() || { left: 0, top: 0 }; // svgEl is undefined before component is mounted, so just give dumb value before mounting
    return {
      x: (e.clientX - svgRect.left - state.offset.x - 1) / state.zoomFactor,
      y: (e.clientY - svgRect.top - state.offset.y - 1) / state.zoomFactor,
    };
  };

  /**
   * Retrieves the coordinates of the mouse in the SVG canvas domain, i.e. with
   * respect to the top-left corner of the SVG.
   *
   * @param {React.MouseEvent} e A mouse event with information about the cursor locator.
   * @returns {Coordinates} An object corresponding to the cursor position with respect to the top left corner of the SVG canvas.
   */
  const getSvgDomainCoordinates = (e: React.MouseEvent): Coordinates => {
    const svgEl = document.getElementById('svg-box');
    const svgRect = svgEl?.getBoundingClientRect() || { left: 0, top: 0 }; // svgEl is undefined before component is mounted, so just give dumb value before mounting
    return {
      x: e.clientX - svgRect.left - 1,
      y: e.clientY - svgRect.top - 1,
    };
  };

  /**
   * Converts coordinates in the image domain (i.e. with respect to the top left of the
   * image at 1X zoom) to coordinates in the SVG canvas.
   *
   * @param {Coordinates} coordinates The coordinates in the image domain.
   * @returns {Coordinates} The coordinates with respect to the top left of the SVG canvas at the current zoom factor.
   */
  const imageToSvg = ({ x, y }: Coordinates): Coordinates => {
    return {
      x: x * state.zoomFactor + state.offset.x,
      y: y * state.zoomFactor + state.offset.y,
    };
  };

  /**
   * Selects the appropriate action for a click event on the image.
   *
   * @param {React.MouseEvent} e The mouse event.
   */
  const handleImageMouseDown = (e: React.MouseEvent): void => {
    e.preventDefault();
    const side = getMouseSide(e);
    if (side === 'right') {
      onStartImageDragging(e);
    } else if (STEPS[state.step] === AnnotationStep.AudiogramAnnotation) {
      addAudiogram(e);
    }
  };

  /**
   * Initiates the dragging of the image.
   *
   */
  const onStartImageDragging = (e: React.MouseEvent): void => {
    e.preventDefault();
    const coordinates = getImageDomainCoordinates(e);
    const svgCoordinates = imageToSvg(coordinates);
    dispatch({
      actionType: 'INITIATE_IMAGE_DRAGGING',
      payload: {
        isDraggingImage: true,
        origin: {
          x: svgCoordinates.x - state.offset.x,
          y: svgCoordinates.y - state.offset.y,
        },
      },
    });
  };

  const handleImageMouseMove = (
    e: React.MouseEvent,
    audiogramIndex: number
  ): void => {
    e.preventDefault();
    if (state.isDraggingImage) {
      handleImageDrag(e);
    } else if (
      STEPS[state.step] === AnnotationStep.AudiogramAnnotation &&
      state.isDraggingBoundingBox
    ) {
      updateAudiogramBoundingBox(e);
    } else if (
      STEPS[state.step] === AnnotationStep.LabelAnnotation &&
      state.isDraggingBoundingBox
    ) {
      updateLabelBoundingBox(e, audiogramIndex);
    }
  };

  /**
   * Updates the offset of the image within the SVG canvas. Does nothing, except
   * when the user has triggered the image dragging even by right-clicking on the
   * image.
   *
   * @param {React.MouseEvent} e The mouse event corresponding to motion of the cursor on the image.
   */
  const handleImageDrag = (e: React.MouseEvent): void => {
    e.preventDefault();
    if (!state.isDraggingImage) return;
    const newImageDomainPosition: Coordinates = getImageDomainCoordinates(e);
    const newSvgDomainPosition: Coordinates = imageToSvg(
      newImageDomainPosition
    );
    dispatch({
      actionType: 'UPDATE_OFFSET',
      payload: {
        offset: {
          x: newSvgDomainPosition.x - state.origin.x,
          y: newSvgDomainPosition.y - state.origin.y,
        },
      },
    });
  };

  /**
   * Handles the zooming logic upon scrolling the mouse on the image of the
   * report. The zooming is around the cursor.
   *
   * @param {React.WheelEvent} e The wheel event that triggers the zoom change.
   */
  const handleZooming = (e: React.WheelEvent): void => {
    e.preventDefault();
    const UPDATE_RATE = 0.05;
    const MAX_FACTOR = 10;
    const MIN_FACTOR = 0.05;
    e.preventDefault();
    e.stopPropagation();
    const zoomFactor = state.zoomFactor + -Math.sign(e.deltaY) * UPDATE_RATE;
    if (zoomFactor > MAX_FACTOR || zoomFactor < MIN_FACTOR) return;
    const imageCoordinates = getImageDomainCoordinates(e);
    const svgCoordinates = getSvgDomainCoordinates(e);
    const x2svg = imageCoordinates.x * zoomFactor + state.offset.x;
    const y2svg = imageCoordinates.y * zoomFactor + state.offset.y;
    const dx = x2svg - svgCoordinates.x;
    const dy = y2svg - svgCoordinates.y;
    dispatch({
      actionType: 'UPDATE_ZOOM_FACTOR',
      payload: {
        offset: {
          x: state.offset.x - dx,
          y: state.offset.y - dy,
        },
        zoomFactor,
      },
    });
  };

  const addAudiogram = (e: React.MouseEvent): void => {
    e.preventDefault();
    // There cannot be more than two audiograms per report.
    if (state.annotation.audiograms.length === 2) return;
    dispatch({
      actionType: 'ADD_AUDIOGRAM',
      payload: {
        isDraggingBoundingBox: true,
        origin: getImageDomainCoordinates(e),
      },
    });
  };

  const updateAudiogramBoundingBox = (e: React.MouseEvent): void => {
    e.preventDefault();
    const audiogram = state.annotation.audiograms.slice(-1)[0];
    const topLeft = imageToSvg({ ...audiogram.boundingBox });
    const bottomRight = getSvgDomainCoordinates(e);
    const width = (bottomRight.x - topLeft.x) / state.zoomFactor;
    const height = (bottomRight.y - topLeft.y) / state.zoomFactor;
    dispatch({
      actionType: 'RESIZE_AUDIOGRAM_BOUNDING_BOX',
      payload: {
        width,
        height,
      },
    });
  };

  const removeAudiogram = (audiogramIndex: number): void => {
    dispatch({ actionType: 'REMOVE_AUDIOGRAM', payload: { audiogramIndex } });
  };

  const onAudiogramMouseDown = (
    e: React.MouseEvent,
    audiogramIndex: number
  ): void => {
    if (getMouseSide(e) === 'right') {
      const { x, y } = getSvgDomainCoordinates(e);
      const { offset } = state;
      dispatch({
        actionType: 'INITIATE_IMAGE_DRAGGING',
        payload: {
          origin: {
            x: x - offset.x,
            y: y - offset.y,
          },
        },
      });
      return;
    }
    if (STEPS[state.step] === AnnotationStep.CornerAnnotation)
      addCorner(e, audiogramIndex);
    else if (STEPS[state.step] === AnnotationStep.SymbolAnnotation)
      addSymbol(e, audiogramIndex);
    else if (STEPS[state.step] === AnnotationStep.LabelAnnotation)
      addLabel(e, audiogramIndex);
  };

  const addLabel = (e: React.MouseEvent, audiogramIndex: number): void => {
    e.preventDefault();
    dispatch({
      actionType: 'ADD_LABEL',
      payload: {
        audiogramIndex,
        isDraggingBoundingBox: true,
        origin: getImageDomainCoordinates(e),
      },
    });
  };

  const updateLabelBoundingBox = (
    e: React.MouseEvent,
    audiogramIndex: number
  ): void => {
    e.preventDefault();
    if (audiogramIndex === -1 || audiogramIndex === undefined) {
      return;
    }
    const label =
      state.annotation.audiograms[audiogramIndex].labels.slice(-1)[0];
    const topLeft = imageToSvg({ ...label.boundingBox });
    const bottomRight = getSvgDomainCoordinates(e);
    const width = (bottomRight.x - topLeft.x) / state.zoomFactor;
    const height = (bottomRight.y - topLeft.y) / state.zoomFactor;
    dispatch({
      actionType: 'RESIZE_LABEL_BOUNDING_BOX',
      payload: {
        audiogramIndex,
        width,
        height,
      },
    });
  };

  const addCorner = (e: React.MouseEvent, audiogramIndex: number): void => {
    if (getMouseSide(e) === 'right') return;
    const coordinates = getImageDomainCoordinates(e);
    dispatch({
      actionType: 'ADD_CORNER',
      payload: {
        audiogramIndex,
        coordinates,
      },
    });
  };

  const onMouseUp = (e: React.MouseEvent, audiogramIndex: number) => {
    dispatch({ actionType: 'TOGGLE_MOUSEUP', payload: { audiogramIndex } });
  };

  const onCornerClick = (
    e: React.MouseEvent,
    audiogramIndex: number,
    cornerIndex: number
  ): void => {
    if (getMouseSide(e) === 'left') return;
    dispatch({
      actionType: 'REMOVE_CORNER',
      payload: { audiogramIndex, cornerIndex },
    });
  };

  const updateCornerFrequency = (
    sign: number,
    audiogramIndex: number,
    cornerIndex: number
  ): void => {
    const previousFreq =
      state.annotation.audiograms[audiogramIndex].corners[cornerIndex]
        .frequency;
    const increase = sign > 0 ? true : false;
    let newFreq = increase ? previousFreq * 2 : previousFreq / 2;
    if (newFreq < 125) {
      newFreq = 16000;
    }
    if (newFreq > 16000) {
      newFreq = 125;
    }
    dispatch({
      actionType: 'UPDATE_CORNER',
      payload: {
        audiogramIndex,
        cornerIndex,
        frequency: newFreq,
        threshold:
          state.annotation.audiograms[audiogramIndex].corners[cornerIndex]
            .threshold,
      },
    });
  };

  const updateCornerThreshold = (
    sign: number,
    audiogramIndex: number,
    cornerIndex: number
  ): void => {
    const oldThreshold =
      state.annotation.audiograms[audiogramIndex].corners[cornerIndex]
        .threshold;
    let newThreshold = sign > 0 ? oldThreshold + 5 : oldThreshold - 5;
    if (newThreshold < -10) {
      newThreshold = 130;
    }
    if (newThreshold > 130) {
      newThreshold = -10;
    }
    dispatch({
      actionType: 'UPDATE_CORNER',
      payload: {
        audiogramIndex,
        cornerIndex,
        threshold: newThreshold,
        frequency:
          state.annotation.audiograms[audiogramIndex].corners[cornerIndex]
            .frequency,
      },
    });
  };

  const addSymbol = (e: React.MouseEvent, audiogramIndex: number): void => {
    const INITIAL_SIDE_LENGTH = 30;
    const coordinates = getImageDomainCoordinates(e);
    dispatch({
      actionType: 'ADD_SYMBOL',
      payload: {
        audiogramIndex,
        symbol: {
          response: true,
          measurementType: state.selectedMeasurementType, //TODO change
          boundingBox: {
            x: coordinates.x - INITIAL_SIDE_LENGTH / 2,
            y: coordinates.y - INITIAL_SIDE_LENGTH / 2,
            height: INITIAL_SIDE_LENGTH,
            width: INITIAL_SIDE_LENGTH,
          },
        },
      },
    });
  };

  const resizeSymbolBoundingBox = (
    e: React.WheelEvent,
    audiogramIndex: number,
    symbolIndex: number
  ): void => {
    const RESIZE_RATE = 1;
    const resize = e.deltaY < 0 ? 1 : -1;
    const { boundingBox } =
      state.annotation.audiograms[audiogramIndex].symbols[symbolIndex];
    const x = boundingBox.x - (resize * RESIZE_RATE) / 2;
    const y = boundingBox.y - (resize * RESIZE_RATE) / 2;
    const height = boundingBox.height + resize * RESIZE_RATE;
    const width = boundingBox.width + resize * RESIZE_RATE;
    // Don't allow excessively small boxes
    if (height < 30 || width < 30) return;
    dispatch({
      actionType: 'RESIZE_SYMBOL_BOUNDING_BOX',
      payload: {
        audiogramIndex,
        symbolIndex,
        boundingBox: {
          x,
          y,
          height,
          width,
        },
      },
    });
  };

  const handleSymbolDoubleClick = (
    audiogramIndex: number,
    symbolIndex: number
  ): void => {
    dispatch({
      actionType: 'TOGGLE_SYMBOL_RESPONSE',
      payload: {
        audiogramIndex,
        symbolIndex,
      },
    });
  };

  const handleSymbolMouseDown = (
    e: React.MouseEvent,
    audiogramIndex: number,
    symbolIndex: number
  ): void => {
    if (getMouseSide(e) === 'left') {
      const origin = getImageDomainCoordinates(e);
      dispatch({
        actionType: 'START_SYMBOL_DRAGGING',
        payload: {
          audiogramIndex,
          symbolIndex,
          origin,
        },
      });
    } else {
      dispatch({
        actionType: 'REMOVE_SYMBOL',
        payload: {
          audiogramIndex,
          symbolIndex,
        },
      });
    }
  };

  const handleSymbolMouseMove = (
    e: React.MouseEvent,
    audiogramIndex: number,
    symbolIndex: number
  ): void => {
    if (!state.isDraggingBoundingBox) return;
    dispatch({
      actionType: 'DRAG_SYMBOL',
      payload: {
        audiogramIndex,
        symbolIndex,
        mouseCoordinates: getImageDomainCoordinates(e),
      },
    });
  };

  const handleLabelClick = (
    e: React.MouseEvent,
    audiogramIndex: number,
    labelIndex: number
  ): void => {
    if (getMouseSide(e) === 'right') {
      dispatch({
        actionType: 'REMOVE_LABEL',
        payload: {
          audiogramIndex,
          labelIndex,
        },
      });
    } else if (getMouseSide(e) === 'left') {
      dispatch({
        actionType: 'TOGGLE_LABEL_EDIT_BOX',
        payload: {
          audiogramIndex,
          labelIndex,
        },
      });
    }
  };

  const setMeasurementType = (
    measurementType: MeasurementType | null
  ): void => {
    dispatch({ actionType: 'SET_MEASUREMENT_TYPE', payload: measurementType });
  };

  const setEditedLabelValue = (value: string) => {
    dispatch({ actionType: 'SET_EDITED_LABEL_VALUE', payload: { value } });
  };

  const isSymbolDisplayed = (
    audiogramIndex: number,
    symbolIndex: number
  ): boolean => {
    const symbol =
      state.annotation.audiograms[audiogramIndex].symbols[symbolIndex];
    if (!state.selectedMeasurementType) return true;
    if (state.selectedMeasurementType === symbol.measurementType) return true;
    if (
      STEPS[state.step] === AnnotationStep.SymbolAnnotation &&
      state.selectedMeasurementType
    )
      return state.selectedMeasurementType === symbol.measurementType;
    return false;
  };

  const updateComment = (e: React.ChangeEvent<HTMLInputElement>): void => {
    dispatch({ actionType: 'UPDATE_COMMENT', payload: e.target.value });
  };

  const markAs = (reason: string) => {
    const annotation = JSON.parse(JSON.stringify(state.annotation));
    annotation.valid = false;
    annotation.reason = reason;
    props.onSubmit(annotation);
  };

  const initializeAnnotation = (annotation: string): void => {
    dispatch({
      actionType: 'INITIALIZE_ANNOTATION',
      payload: JSON.parse(annotation),
    });
  };

  return (
    <div className={`${styles.container}`}>
      {/*<LoadingModal loading={loading} message="Please wait..." />*/}
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <SymbolBar
          display={[
            AnnotationStep.SymbolAnnotation,
            AnnotationStep.Review,
          ].includes(STEPS[state.step])}
          ear="left"
          selectedMeasurementType={state.selectedMeasurementType}
          setMeasurementType={setMeasurementType}
        />
        <div>
          <InstructionsBox
            report={props.report}
            loadReport={props.loadReport}
            initializeAnnotation={initializeAnnotation}
            annotation={state.annotation}
            step={STEPS[state.step]}
            comment={state.annotation.comment}
            onUpdateComment={updateComment}
            onPreviousStep={() => dispatch({ actionType: 'PREVIOUS_STEP' })}
            onNextStep={() => dispatch({ actionType: 'NEXT_STEP' })}
            onSubmit={() => {
              props.onSubmit(state.annotation);
              dispatch({ actionType: 'RESET' });
            }}
            runDigitizer={runDigitizer}
          />
          <svg
            id="svg-box"
            ref={svg}
            className={`${styles.svgBox}`}
            height={props.height}
            width={props.width}
            onContextMenu={(e) => e.preventDefault()}
            onMouseUp={(e) => onMouseUp(e, -1)}
            onMouseMove={(e) => e.preventDefault()}
            onWheel={(e) => e.preventDefault()}
          >
            {props.report && (
              <image
                x={state.offset.x}
                y={state.offset.y}
                height={props.report.height * state.zoomFactor}
                width={props.report.width * state.zoomFactor}
                href={`data:image/jpg;base64,${props.report.base64}`}
                onMouseDown={handleImageMouseDown}
                onMouseMove={(e) => handleImageMouseMove(e, -1)}
                onMouseUp={(e) => onMouseUp(e, -1)}
                onWheel={handleZooming}
              />
            )}

            {state.annotation.audiograms.map(
              (audiogram: Audiogram, index: number) => (
                <AudiogramComp
                  key={`audiogram-${index}`}
                  index={index}
                  offset={state.offset}
                  zoomFactor={state.zoomFactor}
                  updateAudiogramBoundingBox={(e) =>
                    handleImageMouseMove(e, index)
                  }
                  removeAudiogram={removeAudiogram}
                  audiogram={audiogram}
                  onMouseDown={onAudiogramMouseDown}
                  onMouseMove={(e) => handleImageMouseMove(e, index)}
                  onMouseUp={(e) => onMouseUp(e, index)}
                  removeCorner={onCornerClick}
                  dispatch={dispatch}
                  showRemoveButton={
                    STEPS[state.step] === AnnotationStep.AudiogramAnnotation
                  }
                  onWheel={handleZooming}
                >
                  {audiogram.corners.map((corner: Corner, i: number) => (
                    <CornerComponent
                      audiogramIndex={index}
                      cornerIndex={i}
                      corner={corner}
                      x={state.zoomFactor * corner.x + state.offset.x}
                      y={state.zoomFactor * corner.y + state.offset.y}
                      onRemoveCorner={onCornerClick}
                      showEditBox={
                        STEPS[state.step] === AnnotationStep.CornerAnnotation
                      }
                      updateCornerFrequency={updateCornerFrequency}
                      updateCornerThreshold={updateCornerThreshold}
                    />
                  ))}
                  {audiogram.symbols.map(
                    (symbol: Symbol, symbolIndex: number) => {
                      const { color } = Symbols[symbol.measurementType];
                      if (!isSymbolDisplayed(index, symbolIndex)) return null;
                      return (
                        <g>
                          <circle
                            fill={symbol.response ? color : 'transparent'}
                            stroke={color}
                            className={`${styles.symbolCircle}`}
                            cx={
                              (symbol.boundingBox.x +
                                symbol.boundingBox.width / 2) *
                                state.zoomFactor +
                              state.offset.x
                            }
                            cy={
                              (symbol.boundingBox.y +
                                symbol.boundingBox.height / 2) *
                                state.zoomFactor +
                              state.offset.y
                            }
                            r={5}
                          />
                          <rect
                            fill="transparent"
                            stroke={color}
                            className={`${styles.symbolBoundingBox}`}
                            x={
                              symbol.boundingBox.x * state.zoomFactor +
                              state.offset.x
                            }
                            y={
                              symbol.boundingBox.y * state.zoomFactor +
                              state.offset.y
                            }
                            width={symbol.boundingBox.width * state.zoomFactor}
                            height={
                              symbol.boundingBox.height * state.zoomFactor
                            }
                            onMouseDown={(e) =>
                              handleSymbolMouseDown(e, index, symbolIndex)
                            }
                            onMouseMove={(e) =>
                              handleSymbolMouseMove(e, index, symbolIndex)
                            }
                            onMouseUp={(e) => onMouseUp(e, index)}
                            onDoubleClick={() =>
                              handleSymbolDoubleClick(index, symbolIndex)
                            }
                            onWheel={(e) =>
                              resizeSymbolBoundingBox(e, index, symbolIndex)
                            }
                          />
                        </g>
                      );
                    }
                  )}
                </AudiogramComp>
              )
            )}
            {[
              AnnotationStep.AnnotationSelection,
              AnnotationStep.LabelAnnotation,
              AnnotationStep.Review,
            ].includes(STEPS[state.step]) &&
              state.annotation.audiograms.map(
                (audiogram: Audiogram, audiogramIndex: number) => {
                  const rects = audiogram.labels.map(
                    (label: Label, labelIndex: number) => {
                      const x =
                        state.zoomFactor * label.boundingBox.x + state.offset.x;
                      const y =
                        state.zoomFactor * label.boundingBox.y + state.offset.y;
                      return (
                        <g>
                          <rect
                            x={x}
                            y={y - 20}
                            width={label.boundingBox.width * state.zoomFactor}
                            height={20}
                            fill="white"
                          />
                          <text
                            className={styles.labelFont}
                            x={x}
                            y={y - 5}
                            fill="blue"
                          >
                            {label.value}
                          </text>
                          <rect
                            x={x}
                            y={y}
                            width={label.boundingBox.width * state.zoomFactor}
                            height={label.boundingBox.height * state.zoomFactor}
                            fill="transparent"
                            stroke="blue"
                            strokeWidth={3}
                            onMouseUp={(e) => onMouseUp(e, audiogramIndex)}
                            onMouseDown={(e) =>
                              handleLabelClick(e, audiogramIndex, labelIndex)
                            }
                            onMouseMove={(e) =>
                              handleImageMouseMove(e, audiogramIndex)
                            }
                          />
                        </g>
                      );
                    }
                  );
                  return rects;
                }
              )}
            <LabelEditBox
              setValue={setEditedLabelValue}
              editedLabel={state.editedLabel}
            />
          </svg>
        </div>
        <SymbolBar
          display={[
            AnnotationStep.SymbolAnnotation,
            AnnotationStep.Review,
          ].includes(STEPS[state.step])}
          ear="right"
          selectedMeasurementType={state.selectedMeasurementType}
          setMeasurementType={setMeasurementType}
        />
      </div>
    </div>
  );
}

export default AnnotationBox;
