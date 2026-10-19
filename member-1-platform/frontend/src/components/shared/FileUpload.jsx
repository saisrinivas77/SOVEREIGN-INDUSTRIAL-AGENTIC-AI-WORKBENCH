import React, { useState, useRef, useCallback } from 'react';
import { Upload, X, FileText, Image } from 'lucide-react';
import { formatFileSize } from '../../utils/formatters';

/**
 * Drag-and-drop file upload component.
 * Supports documents and images for the workbench.
 */
export default function FileUpload({ files, onFilesChange, accept, multiple = true }) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const dropped = Array.from(e.dataTransfer.files);
    if (dropped.length > 0) {
      onFilesChange([...(files || []), ...dropped]);
    }
  }, [files, onFilesChange]);

  const handleChange = useCallback((e) => {
    const selected = Array.from(e.target.files);
    if (selected.length > 0) {
      onFilesChange([...(files || []), ...selected]);
    }
    // Reset input so same file can be selected again
    e.target.value = '';
  }, [files, onFilesChange]);

  const removeFile = useCallback((idx) => {
    const updated = [...files];
    updated.splice(idx, 1);
    onFilesChange(updated);
  }, [files, onFilesChange]);

  const getFileIcon = (file) => {
    if (file.type && file.type.startsWith('image/')) return Image;
    return FileText;
  };

  return (
    <div>
      <div
        className={`file-upload-zone ${dragActive ? 'file-upload-zone--active' : ''}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <div className="upload-icon">
          <Upload size={32} />
        </div>
        <div className="upload-text">
          Drop files here or click to browse
        </div>
        <div className="upload-hint">
          Supports documents, images, spreadsheets, and PDFs
        </div>
        <input
          ref={inputRef}
          type="file"
          multiple={multiple}
          accept={accept}
          onChange={handleChange}
          style={{ display: 'none' }}
        />
      </div>

      {files && files.length > 0 && (
        <div className="file-list">
          {files.map((file, idx) => {
            const FileIcon = getFileIcon(file);
            return (
              <div className="file-item" key={`${file.name}-${idx}`}>
                <FileIcon size={16} style={{ color: 'var(--color-text-accent)', flexShrink: 0 }} />
                <span className="file-name">{file.name}</span>
                <span className="file-size">{formatFileSize(file.size)}</span>
                <button className="file-remove" onClick={() => removeFile(idx)} title="Remove file">
                  <X size={14} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
