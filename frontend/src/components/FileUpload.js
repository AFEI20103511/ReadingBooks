import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUploadCloud, FiUsers, FiLink } from 'react-icons/fi'; // Modern Apple-style icons
import axios from 'axios'; // Added axios for real backend call

function FileUpload() {
  // State to track upload progress and status messages
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState('');
  const [results, setResults] = useState(null);

  // Callback function that handles file upload when files are dropped or selected
  const onDrop = useCallback(async (acceptedFiles) => {
    // If no files were accepted, exit early
    if (acceptedFiles.length === 0) return;
    
    // Get the first file (we only accept one file at a time)
    const file = acceptedFiles[0];
    
    // Create FormData to send file to backend
    const formData = new FormData();
    formData.append('file', file);
    
    // Update UI to show upload in progress
    setUploading(true);
    setStatus('Uploading...');
    
    try {
      // Send file to backend API endpoint
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      // Show success message and store results
      setStatus('Upload successful!');
      setResults(response.data);
      console.log('Backend response:', response.data);
    } catch (error) {
      // Show error message if upload fails
      setStatus('Upload failed.');
      console.error('Upload error:', error);
    } finally {
      // Always reset upload state when done
      setUploading(false);
    }
  }, []);

  // Configure dropzone with specific settings
  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,                                    // Function to call when files are dropped
    accept: { 'application/pdf': ['.pdf'] },   // Only accept PDF files
    multiple: false,                           // Only allow one file at a time
    noClick: true,                            // Disable click to open file dialog (we use custom button)
  });

  return (
    <div {...getRootProps()} className={`upload-area${isDragActive ? ' drag-active' : ''}`}>
      {/* Hidden file input that dropzone manages */}
      <input {...getInputProps()} />
      
      {/* Upload icon */}
      <FiUploadCloud className="upload-icon" />
      
      {/* Instructions for user */}
      <p>
        Drag & drop a PDF file here
        <br />
        <span style={{ color: '#888', fontSize: '0.95em' }}>or</span>
      </p>
      
      {/* Custom button to open file dialog */}
      <button type="button" className="upload-btn" onClick={open} disabled={uploading}>
        Choose File
      </button>
      
      {/* Show upload progress */}
      {uploading && <div className="upload-status">Uploading…</div>}
      
      {/* Show status message (success/error) */}
      {status && !uploading && <div className="upload-status">{status}</div>}
      
      {/* Display results if available */}
      {results && (
        <div className="results-container">
          {/* Entities Section */}
          <div className="results-section">
            <h3 className="results-title">
              <FiUsers className="section-icon" />
              People Found ({results.entities?.length || 0})
            </h3>
            {results.entities && results.entities.length > 0 ? (
              <div className="entities-list">
                {results.entities.map((name, index) => (
                  <div key={index} className="entity-item">
                    <span className="entity-name">{name}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-results">No people found in the document.</p>
            )}
          </div>

          {/* Relationships Section */}
          <div className="results-section">
            <h3 className="results-title">
              <FiLink className="section-icon" />
              Relationships Found ({results.relationships?.length || 0})
            </h3>
            {results.relationships && results.relationships.length > 0 ? (
              <div className="relationships-list">
                {results.relationships.map((relationship, index) => (
                  <div key={index} className="relationship-item">
                    <span className="relationship-source">{relationship.source}</span>
                    <span className="relationship-arrow">→</span>
                    <span className="relationship-target">{relationship.target}</span>
                    <span className="relationship-type">({relationship.type})</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-results">No relationships found between people.</p>
            )}
          </div>

          {/* Summary */}
          <div className="results-summary">
            <p>Processed {results.text_length?.toLocaleString() || 0} characters of text.</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default FileUpload; 