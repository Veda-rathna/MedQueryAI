import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import UploadPanel from './components/UploadPanel';
import ChatPanel from './components/ChatPanel';
import Disclaimer from './components/Disclaimer';
import { checkHealth } from './services/api';
import './index.css';

function App() {
  const [sessionId] = useState(() => uuidv4());
  const [documentId, setDocumentId] = useState(null);
  const [documentInfo, setDocumentInfo] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState({ status: 'checking', lmStudioConnected: false });

  useEffect(() => {
    // Check API health on mount
    const checkApiHealth = async () => {
      try {
        const health = await checkHealth();
        setApiStatus({
          status: health.lm_studio_connected ? 'connected' : 'degraded',
          lmStudioConnected: health.lm_studio_connected
        });
      } catch (error) {
        setApiStatus({ status: 'error', lmStudioConnected: false });
      }
    };

    checkApiHealth();
  }, []);

  const handleUploadSuccess = (result) => {
    setDocumentId(result.document_id);
    setDocumentInfo(result);
    setError(null);
  };

  const handleUploadError = (errorMessage) => {
    setError(errorMessage);
    setDocumentId(null);
    setDocumentInfo(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🩺 Drug Information Chatbot
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                FDA Prescribing Information Assistant
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`h-3 w-3 rounded-full ${
                apiStatus.status === 'connected' ? 'bg-green-500' :
                apiStatus.status === 'degraded' ? 'bg-yellow-500' :
                apiStatus.status === 'error' ? 'bg-red-500' :
                'bg-gray-300'
              }`}></div>
              <span className="text-sm text-gray-600">
                {apiStatus.lmStudioConnected ? 'LM Studio Connected' : 'LM Studio Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Disclaimer */}
        <div className="mb-6">
          <Disclaimer />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Upload Panel */}
        <UploadPanel
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
          isProcessing={isProcessing}
          setIsProcessing={setIsProcessing}
        />

        {/* Document Info */}
        {documentInfo && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              📊 Document Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Filename</div>
                <div className="text-lg font-semibold text-gray-800 truncate">
                  {documentInfo.filename}
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Pages</div>
                <div className="text-lg font-semibold text-gray-800">
                  {documentInfo.page_count}
                </div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Chunks</div>
                <div className="text-lg font-semibold text-gray-800">
                  {documentInfo.chunk_count}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Chat Panel */}
        {documentId ? (
          <ChatPanel documentId={documentId} sessionId={sessionId} />
        ) : (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">📄</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              No Document Loaded
            </h3>
            <p className="text-gray-500">
              Please upload a prescribing information PDF to start asking questions.
            </p>
          </div>
        )}

        {/* Footer Info */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            ℹ️ How It Works
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-600">
            <div>
              <div className="font-semibold text-gray-800 mb-2">1. Upload PDF</div>
              <p>The system extracts and chunks the prescribing information while preserving structure, sections, and page numbers.</p>
            </div>
            <div>
              <div className="font-semibold text-gray-800 mb-2">2. Semantic Search</div>
              <p>Your question is matched against document chunks using vector similarity, with automatic boosting for dosage and safety queries.</p>
            </div>
            <div>
              <div className="font-semibold text-gray-800 mb-2">3. Local LLM</div>
              <p>A local language model (via LM Studio) generates answers using ONLY the retrieved context, with mandatory page citations.</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Regulatory-Grade Drug Information Chatbot • Built with RAG Architecture • Local LLM Inference
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
