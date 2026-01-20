import React, { useEffect, useState } from 'react';
import { listDocuments, deleteDocument } from '../services/api';

const DocumentList = ({ currentDocumentId, onDocumentSelect, onDocumentDeleted }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await listDocuments();
      setDocuments(response.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleDelete = async (documentId, filename) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      setDeleting(documentId);
      await deleteDocument(documentId);
      
      // Remove from local state
      setDocuments(docs => docs.filter(doc => doc.document_id !== documentId));
      
      // Notify parent
      if (onDocumentDeleted) {
        onDocumentDeleted(documentId);
      }
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('Failed to delete document: ' + (error.response?.data?.detail || error.message));
    } finally {
      setDeleting(null);
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">📚 Your Documents</h2>
        <div className="text-center py-8 text-gray-500">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full"></div>
          <p className="mt-2">Loading documents...</p>
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">📚 Your Documents</h2>
        <div className="text-center py-8 text-gray-500">
          <p>No documents uploaded yet.</p>
          <p className="text-sm mt-1">Upload a PDF to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">
        📚 Your Documents ({documents.length})
      </h2>

      <div className="space-y-3">
        {documents.map((doc) => (
          <div
            key={doc.document_id}
            className={`
              border rounded-lg p-4 transition-all
              ${currentDocumentId === doc.document_id 
                ? 'border-primary bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
              }
            `}
          >
            <div className="flex items-start justify-between">
              <div 
                className="flex-1 cursor-pointer"
                onClick={() => onDocumentSelect && onDocumentSelect(doc.document_id)}
              >
                <div className="flex items-center gap-2">
                  <span className="text-2xl">📄</span>
                  <div>
                    <h3 className="font-semibold text-gray-800 hover:text-primary">
                      {doc.filename}
                    </h3>
                    <div className="flex gap-4 text-sm text-gray-500 mt-1">
                      <span>📅 {formatDate(doc.upload_date)}</span>
                      <span>📖 {doc.page_count} pages</span>
                      <span>🔢 {doc.chunk_count} chunks</span>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleDelete(doc.document_id, doc.filename)}
                disabled={deleting === doc.document_id}
                className={`
                  ml-4 px-3 py-1 rounded text-sm font-medium
                  transition-colors
                  ${deleting === doc.document_id
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-red-100 text-red-700 hover:bg-red-200'
                  }
                `}
                title="Delete document"
              >
                {deleting === doc.document_id ? '⏳' : '🗑️'} Delete
              </button>
            </div>

            {currentDocumentId === doc.document_id && (
              <div className="mt-2 text-xs text-primary font-medium">
                ✓ Currently active
              </div>
            )}
          </div>
        ))}
      </div>

      <button
        onClick={fetchDocuments}
        className="mt-4 w-full py-2 text-sm text-gray-600 hover:text-primary transition-colors"
      >
        🔄 Refresh List
      </button>
    </div>
  );
};

export default DocumentList;
