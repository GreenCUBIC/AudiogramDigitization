import { useState } from 'react';
import { MemoryRouter as Router, Routes, Route } from 'react-router-dom';
import icon from '../../assets/icon.svg';
import './App.css';
import AnnotationBox from './components/annotation/AnnotationBox';

const AnnotationPage = () => {
  const [report, setReport] = useState<any>(null);
  const [annotationPath, setAnnotationPath] = useState<any>(null);

  const loadReport = async () => {
    const report = await window.electron.ipcRenderer.loadReport();
    console.log(report)
    //const report = JSON.parse((await (window as any).pywebview.api.load_report()))
    setReport(report)
    setAnnotationPath(report.filepath.split(".")[0] + ".json")
  }

  const saveAnnotation = async (annotation: any) => {
    await window.electron.ipcRenderer.saveAnnotation(report, annotation);
    setReport(null)
    setAnnotationPath(null)
  }
  return (
    <div>
      <div className="header" style={{ marginBottom: "10px"}}><h1>Audiology Report Annotation Interface</h1></div>
      <AnnotationBox 
        loadReport={loadReport}
          height={400}
          width={700}
          onSubmit={saveAnnotation}
          report={report}
      />
    </div>
  );
};

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AnnotationPage />} />
      </Routes>
    </Router>
  );
}
