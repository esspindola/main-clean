import React, { useState } from 'react';

const OCRResultPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/process-document', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data.data);
      }
    } catch (err) {
      setError('Error de conexión con el backend OCR');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto p-4 bg-white rounded shadow mt-8">
      <h2 className="text-2xl font-bold mb-4">Procesar documento con OCR</h2>
      <input
        type="file"
        accept=".pdf,image/*"
        onChange={handleFileChange}
        className="mb-2"
      />
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Procesando...' : 'Subir y procesar'}
      </button>
      {error && <div className="text-red-600 mt-2">{error}</div>}
      {result && (
        <div className="mt-4 text-left bg-gray-100 p-3 rounded overflow-x-auto">
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default OCRResultPage; 