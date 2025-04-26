import React, { useState, ChangeEvent } from "react";

const Upload: React.FC = () => {
  const [fileName, setFileName] = useState<string>("");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === "application/pdf") {
        setFileName(file.name);
      } else {
        alert("Please upload a PDF file.");
      }
    }
  };

  const triggerFileInput = () => {
    const fileInput = document.getElementById("fileInput") as HTMLInputElement;
    fileInput?.click();
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>ULTIMATE</h1>
      <p style={styles.subtitle}>Check your rent contract</p>

      <div style={styles.uploadBox} onClick={triggerFileInput}>
        <div style={styles.document}>
          <div style={styles.uploadCircle}>
            <span style={styles.arrow}>↑</span>
          </div>
          <div style={styles.lines}>
            <div style={styles.line}></div>
            <div style={styles.line}></div>
            <div style={styles.line}></div>
            <div style={styles.line}></div>
          </div>
        </div>
      </div>

      <input
        id="fileInput"
        type="file"
        accept="application/pdf"
        style={{ display: "none" }}
        onChange={handleFileChange}
      />

      <button style={styles.uploadButton} onClick={triggerFileInput}>
        Upload
      </button>

      {fileName && <p style={styles.fileName}>{fileName}</p>}
    </div>
  );
};

export default Upload;

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    fontFamily: "'Roboto', sans-serif",
    minHeight: "100vh",
    backgroundColor: "#f8fafa",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    fontSize: "36px",
    color: "#72dedf",
    letterSpacing: "5px",
    margin: "0",
    fontWeight: "500",
  },
  subtitle: {
    marginTop: "10px",
    marginBottom: "30px",
    color: "#555",
    fontSize: "18px",
  },
  uploadBox: {
    backgroundColor: "#e7e8e9",
    borderRadius: "15px",
    padding: "40px",
    cursor: "pointer",
  },
  document: {
    backgroundColor: "#fff",
    borderRadius: "15px",
    padding: "30px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "180px",
    height: "220px",
    justifyContent: "center",
    position: "relative",
  },
  uploadCircle: {
    backgroundColor: "#72dedf",
    borderRadius: "50%",
    width: "50px",
    height: "50px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "20px",
  },
  arrow: {
    fontSize: "24px",
    color: "#000",
  },
  lines: {
    width: "80%",
  },
  line: {
    height: "2px",
    backgroundColor: "#000",
    margin: "8px 0",
  },
  uploadButton: {
    marginTop: "30px",
    backgroundColor: "#72dedf",
    color: "#fff",
    border: "none",
    padding: "12px 24px",
    fontSize: "16px",
    borderRadius: "8px",
    cursor: "pointer",
  },
  fileName: {
    marginTop: "20px",
    color: "#333",
    fontSize: "14px",
  },
};
