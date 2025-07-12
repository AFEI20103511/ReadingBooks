import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUploadCloud } from 'react-icons/fi'; // Modern Apple-style icon

function FileUpload() {
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState('');

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    setUploading(true);
    setStatus('Uploading...');
    // Simulate upload
    setTimeout(() => {
      setUploading(false);
      setStatus('Upload successful!');
    }, 1200);
  }, []);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
    noClick: true, // We'll use a custom button
  });

  return (
    <div {...getRootProps()} className={`upload-area${isDragActive ? ' drag-active' : ''}`}>
      <input {...getInputProps()} />
      <FiUploadCloud className="upload-icon" />
      <p>
        Drag & drop a PDF file here
        <br />
        <span style={{ color: '#888', fontSize: '0.95em' }}>or</span>
      </p>
      <button type="button" className="upload-btn" onClick={open} disabled={uploading}>
        Choose File
      </button>
      {uploading && <div className="upload-status">Uploading…</div>}
      {status && !uploading && <div className="upload-status">{status}</div>}
    </div>
  );
}

export default FileUpload; 