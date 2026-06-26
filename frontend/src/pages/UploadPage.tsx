import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, ArrowUp } from 'lucide-react';
import { useUpload } from '../hooks/useUpload';
import { useNavigate } from 'react-router-dom';

export default function UploadPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { upload, isLoading, error } = useUpload();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
      return;
    }
    setSelectedFile(file);
  };

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    e.target.value = '';
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;
    const result = await upload(selectedFile);
    if (result) {
      navigate('/query');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div
      className="flex h-screen bg-white overflow-hidden"
      style={{ fontFamily: "'Inter', system-ui, -apple-system, sans-serif" }}
    >
      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center bg-white px-6">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="flex items-center justify-center gap-2 mb-8">
            <div 
              className="w-4 h-4 rounded flex items-center justify-center shrink-0"
              style={{ backgroundColor: '#2563EB' }}
            >
              <span className="text-white text-xs font-bold">T</span>
            </div>
            <span className="text-sm font-semibold text-gray-900 tracking-tight">TallyQuery</span>
          </div>

          {/* Upload Area */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
            className="border-2 border-dashed rounded-lg px-6 py-12 text-center cursor-pointer transition-all duration-150"
            style={{
              borderColor: isDragging ? '#2563EB' : '#D1D5DB',
              backgroundColor: isDragging ? '#EFF6FF' : 'transparent'
            }}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="mx-auto mb-3" size={32} style={{ color: '#9CA3AF' }} />
            <p className="text-sm text-gray-700 font-medium mb-1">
              Drop your CSV or Excel file here
            </p>
            <p className="text-xs text-gray-500">
              or click to browse (max 10MB)
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx"
              className="hidden"
              onChange={onFileChange}
            />
          </div>

          {/* Selected File */}
          {selectedFile && (
            <div className="mt-4 p-4 rounded-lg border" style={{ backgroundColor: '#F9FAFB', borderColor: '#E5E7EB' }}>
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-gray-600">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="ml-3 text-xs hover:text-gray-900 transition-colors"
                  style={{ color: '#6B7280' }}
                >
                  Remove
                </button>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 rounded-lg border" style={{ backgroundColor: '#FEE2E2', borderColor: '#FECACA' }}>
              <p className="text-xs" style={{ color: '#991B1B' }}>{error}</p>
            </div>
          )}

          {/* Submit Button */}
          {selectedFile && (
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="mt-6 w-full flex items-center justify-center gap-2 px-4 py-3 rounded-md text-sm font-medium transition-colors"
              style={{
                backgroundColor: isLoading ? '#1D4ED8' : '#2563EB',
                color: 'white',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.75 : 1
              }}
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  Upload File
                  <ArrowUp size={16} />
                </>
              )}
            </button>
          )}

          {/* Info */}
          <p className="mt-6 text-center text-xs" style={{ color: '#9CA3AF' }}>
            Your data will be processed securely in memory only.
          </p>
        </div>
      </main>
    </div>
  );
}
