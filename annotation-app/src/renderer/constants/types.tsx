/**
 * Copyright (c) Carleton University Biomedical Informatics Collaboratory
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

export type User = "user"
export type Admin = "admin"

/**
 * The type of measurement.
 */
export enum MeasurementType {
  LeftAirUnmasked = "AIR_UNMASKED_LEFT",
  RightAirUnmasked = "AIR_UNMASKED_RIGHT",
  LeftAirMasked = "AIR_MASKED_LEFT",
  RightAirMasked = "AIR_MASKED_RIGHT",
  LeftBoneUnmasked = "BONE_UNMASKED_LEFT",
  RightBoneUnmasked = "BONE_UNMASKED_RIGHT",
  LeftBoneMasked = "BONE_MASKED_LEFT",
  RightBoneMasked = "BONE_MASKED_RIGHT",
}

/**
 * Steps in the annotation process
 */
export enum AnnotationStep {
  AnnotationSelection = "ANNOTATION_SELECTION",
  AudiogramAnnotation = "AUDIOGRAM_SELECTION",
  CornerAnnotation = "CORNER_IDENTIFICATION",
  SymbolAnnotation = "SYMBOL_SELECTION",
  LabelAnnotation = "LABEL_ANNOTATION",
  Review = "REVIEW",
}

/**
 * The possible account types. `Admin` accounts get access to the
 * administration panel and can upload audiograms to the database.
 */
export enum Role {
  Admin = "admin",
  User = "user",
}

/**
 * Login credentials that are sent to the server to log in
 * and to `refresh` a session (get a fresh JWT token).
 */
export interface LoginCredentials {
  /** The username */
  username: null | string
  /** The password */
  password: null | string
}

/**
 * Response data sent back by the server upon authentication check
 * and upon login.
 */
export interface LoginResponse {
  /** The user's username as returned by the server */
  username: string
  /** The account type of the user (admin or user) */
  admin: boolean
}

/**
 * Bounding box object for an audiogram and for threshold objects.
 */
export interface BoundingBox {
  /** The x coordinate of the upper-leftmost corner. */
  x: number
  /** The y coordinate of the upper-leftmost corner. */
  y: number
  /** The width of the bounding box */
  width: number
  /** The height of the bounding box */
  height: number
  /** The magnification factor at which the bounding box was determined. */
  originalMagnificationFactor?: number
}

/** A corner object representing the corner coordinates. */
export interface Corner {
  /** Position (top-left, top-right, etc.)*/
  position: {
    horizontal: string
    vertical: string
  }
  /** The frequency of the corner. */
  frequency: number
  /** The threshold of the corner. */
  threshold: number
  /** Its pixel x-coordinate location. */
  x: number
  /** Its pixel y-coordinate location. */
  y: number
}

/** A symbol object, representing a symbol measurement. */
export interface Symbol {
  /** The x coordinate of the threshold. */
  x: number
  /** The y coordinate of the threshold. */
  y: number
  /** The bounding box drawn around the threshold symbol */
  boundingBox: BoundingBox
  /** Whether a response was recorded by the subject, as represented by the
   * ABSENCE of a downward-pointing arrow */
  response: boolean
  /** The threshold measurement type (air/bone/unmasked/masked/side) */
  measurementType: MeasurementType
}

/** A threshold object, representing a threshold measurement. */
export interface Threshold {
  /** The frequency in Hz of the threshold. */
  frequency: number
  /** The threshold value in dB of the threshold. */
  threshold: number
  /** The ear */
  ear: string
  /** Whether a response was recorded for the threshold */
  response?: boolean
  /** Whether masking was applied */
  masking: boolean
  /** Conduction mode (air or bone) */
  conduction: string
  /** The threshold measurement type (air/bone/unmasked/masked/side) in a string format */
  measurementType: MeasurementType
}

/** A threshold object, representing a threshold measurement. */
export interface Label {
  /** The bounding box drawn around the label */
  boundingBox: BoundingBox
  /** The string of the label*/
  value: string
}

/** An audiogram object */
export interface Audiogram {
  /** The bounding box that surrounds the audiogram. */
  boundingBox: BoundingBox
  /** The corners that calibrate the audiogram rotation/position. */
  corners: Corner[]
  /** Symbols detected in the audiogram */
  symbols: Symbol[]
  /** Axes labels for the x (frequency) and y axes (threshold) */
  labels: Label[]
}

/**
 * The annotation object which represents the annotation associated with
 * an audiogram report.
 */
export interface Annotation {
  /** The unique ID associated with the annotation */
  annotationId?: number
  /** The username of the annotator who submitted the annotation (not available
   * to client upon creation of an annotation, assigned by server). */
  username?: string
  /** The date at which the audiogram was received by the server (not available
   * to client upon creation of an annotation, assigned by server). */
  dateAdded?: string
  /** Whether the report is valid (ie. contains a sufficient-quality audiogram) */
  valid: boolean
  /** The reason why the audiogram does not have sufficient quality */
  reason: string
  /** A string saying why the annotation needs review */
  comment: string
  /** The actual locations of the audiograms associated with the annotation */
  audiograms: Audiogram[]
}

/**
 * A report object representing an audiogram report.
 */
export interface Report {
  /** The unique report ID */
  reportId: number
  /** Path of the report file */
  filepath?: string
  /** The file name of the report*/
  filename?: string
  /** The date at which the audiogram was added to the database. */
  dateAdded: string
  /** The report height in pixels. */
  height: number
  /** The report width in pixels. */
  width: number
  /** The actual image in base64 encoded format. */
  base64?: string
  /** The annotations associated with the report. */
  annotations: Annotation[]
  /** Validated thresholds associated with the audiogram in the report */
  validatedAudiograms: any[] // TODO fix
  /** Last annotator */
  lastAnnotator?: string
  /** Whether the report contains a valid audiogram */
  valid?: boolean
  /** The comment associated with the last annotation provided for the report */
  comment?: string
  /** The decision that was taken for the claim */
  decision: any | null
}

export interface Coordinates {
  x: number
  y: number
}

export interface ReportStats {
  annotatedReports: number
  invalidReports: number
  numReports: number
  reportsNeedingReview: number
  validReports: number
}
