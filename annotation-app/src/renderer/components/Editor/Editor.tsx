/* global pywebview */
import * as React from 'react'
import AnnotationBox from '../annotation/AnnotationBox';

import './Editor.scss'


export default function Header() {
  const [report, setReport] = React.useState<any>(null);
  const [annotationPath, setAnnotationPath] = React.useState<any>(null);

  const loadReport = async () => {
    const report = JSON.parse((await (window as any).pywebview.api.load_report()))
    setReport(report)
    setAnnotationPath(report.filepath.split(".")[0] + ".json")
  }

  const saveAnnotation = async (annotation: any) => {
    (window as any).pywebview.api.save_annotation(annotationPath, JSON.stringify(annotation))
    setReport(null)
    setAnnotationPath(null)
  }

  return (
    <div>
      <div className="header">
        <h1>Audiology Report Annotation Interface</h1>
      </div>
      <div className="report-loading">
        <button onClick={loadReport}>Load an audiology report</button>
        <div>{report ? `Report file: ${report.filepath}` : ""}</div>
        <div>{report ? `Annotation file: ${annotationPath}` : ""}</div>
      </div>
        <div style={{ display: "flex", justifyContent: "center" }}>
        {report && (
          <AnnotationBox
            height={400}
            width={700}
            onSubmit={saveAnnotation}
            report={report}
          />
        )}
      </div>
    </div>
  )
}