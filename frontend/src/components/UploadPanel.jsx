import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadPDF } from '../services/api';

const UploadPanel = ({ onUploadSuccess, onUploadError, isProcessing, setIsProcessing }) => {
  const [uploadProgress, setUploadProgress] = React.useState(0);
  const [uploadedFile, setUploadedFile] = React.useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploadedFile(file);
    setIsProcessing(true);
    setUploadProgress(0);

    try {
      const result = await uploadPDF(file, (progress) => {
        setUploadProgress(progress);
      });

      onUploadSuccess(result);
      setUploadProgress(100);
    } catch (error) {
      console.error('Upload error:', error);
      onUploadError(error.response?.data?.detail || 'Failed to upload PDF');
      setUploadedFile(null);
    } finally {
      setTimeout(() => {
        setIsProcessing(false);
        setUploadProgress(0);
      }, 1000);
    }
  }, [onUploadSuccess, onUploadError, setIsProcessing]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: isProcessing
  });

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">
        📄 Upload Prescribing Information PDF
      </h2>

      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-primary bg-blue-50' : 'border-gray-300 hover:border-primary'}
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />

        {isProcessing ? (
          <div className="space-y-3">
            <div className="text-4xl">⏳</div>
            <p className="text-gray-600 font-medium">Processing PDF...</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-primary h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500">{uploadProgress}% complete</p>
          </div>
        ) : uploadedFile ? (
          <div className="space-y-2">
            <div className="text-4xl">✅</div>
            <p className="text-gray-600 font-medium">
              {uploadedFile.name}
            </p>
            <p className="text-sm text-gray-500">Successfully processed!</p>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-4xl">📎</div>
            <p className="text-gray-600 font-medium">
              {isDragActive
                ? 'Drop the PDF here...'
                : 'Drag & drop a PDF here, or click to select'}
            </p>
            <p className="text-sm text-gray-500">
              Only FDA prescribing information PDFs
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadPanel;
